"""
Chat Controller
Xử lý requests cho AI chatbot endpoints
Section 2.6.1-2.6.5
"""

from typing import Dict, Optional
from fastapi import HTTPException, status
from datetime import datetime

from schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryListResponse,
    ConversationDetailResponse,
    ChatDeleteResponse,
    ChatDeleteAllResponse
)
from services import chat_service, course_service, enrollment_service
from services.ai_service import chat_with_course_context
from models.models import Conversation, generate_uuid


# ============================================================================
# Section 2.6.1: CHAT HỎI ĐÁP VỀ KHÓA HỌC
# ============================================================================

async def handle_send_chat_message(
    course_id: str,
    request: ChatMessageRequest,
    current_user: Dict
) -> ChatMessageResponse:
    """
    2.6.1: Chat hỏi đáp về khóa học
    
    Flow:
    1. Kiểm tra enrollment
    2. Tìm hoặc tạo conversation cho course này
    3. Gửi question đến AI với course context
    4. Lưu message vào conversation
    5. Return AI response
    
    Args:
        course_id: ID của course
        request: ChatMessageRequest
        current_user: User hiện tại
        
    Returns:
        ChatMessageResponse với AI answer
        
    Endpoint: POST /api/v1/chat/course/{course_id}
    """
    user_id = current_user.get("user_id")
    
    # Kiểm tra course tồn tại
    course = await course_service.get_course_by_id(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại"
        )
    
    # Kiểm tra enrollment (nếu không phải owner)
    if course.owner_id != user_id:
        enrollment = await enrollment_service.get_user_enrollment(user_id, course_id)
        if not enrollment or enrollment.status == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn cần đăng ký khóa học để sử dụng chatbot"
            )
    
    # Tìm hoặc tạo conversation
    if request.conversation_id:
        conversation = await Conversation.find_one(
            Conversation.id == request.conversation_id,
            Conversation.user_id == user_id
        )
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation không tồn tại"
            )
    else:
        # Tạo conversation mới
        conversation = Conversation(
            id=generate_uuid(),
            user_id=user_id,
            course_id=course_id,
            title="Chat về " + course.title[:50],
            messages=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        await conversation.insert()
    
    # Lưu user message
    user_message = {
        "id": generate_uuid(),
        "role": "user",
        "content": request.question,
        "created_at": datetime.utcnow()
    }
    conversation.messages.append(user_message)
    
    # Gọi AI với course context
    ai_response_text = await chat_with_course_context(
        course_id=course_id,
        question=request.question,
        conversation_history=conversation.messages
    )
    
    # Lưu AI response
    ai_message = {
        "id": generate_uuid(),
        "role": "assistant",
        "content": ai_response_text,
        "created_at": datetime.utcnow()
    }
    conversation.messages.append(ai_message)
    
    conversation.updated_at = datetime.utcnow()
    await conversation.save()
    
    return ChatMessageResponse(
        conversation_id=conversation.id,
        course_id=course_id,
        question=request.question,
        answer=ai_response_text,
        generated_at=ai_message["created_at"],
        sources=[]
    )


# ============================================================================
# Section 2.6.2: XEM LỊCH SỬ HỘI THOẠI
# ============================================================================

async def handle_get_chat_history(
    skip: int,
    limit: int,
    current_user: Dict
) -> ChatHistoryListResponse:
    """
    2.6.2: Lấy danh sách conversations
    
    Hiển thị:
    - Tất cả conversations của user
    - Nhóm theo course
    - Sorted by last_message_at
    
    Args:
        skip: Pagination skip
        limit: Pagination limit
        current_user: User hiện tại
        
    Returns:
        ChatHistoryListResponse
        
    Endpoint: GET /api/v1/chat/history?skip=0&limit=20
    """
    user_id = current_user.get("user_id")
    
    # Query conversations
    conversations = await Conversation.find(
        Conversation.user_id == user_id
    ).sort("-updated_at").skip(skip).limit(limit).to_list()
    
    # Build response
    conversations_data = []
    for conv in conversations:
        # Lấy course info
        course = await course_service.get_course_by_id(conv.course_id)
        course_title = course.title if course else "Unknown Course"
        
        # Tạo AI summary (simplified - lấy từ title hoặc first message)
        summary = conv.title
        if len(conv.messages) > 0:
            first_msg = conv.messages[0]
            if first_msg.get("role") == "user":
                summary = first_msg.get("content", "")[:100] + "..."
        
        last_message_at = conv.updated_at
        
        conversations_data.append({
            "id": conv.id,
            "course_id": conv.course_id,
            "course_title": course_title,
            "summary": summary,
            "last_message_at": last_message_at,
            "message_count": len(conv.messages)
        })
    
    # Count total
    total = await Conversation.find(Conversation.user_id == user_id).count()
    
    return ChatHistoryListResponse(
        conversations=conversations_data,
        total=total,
        skip=skip,
        limit=limit
    )


# ============================================================================
# Section 2.6.3: XEM CHI TIẾT CONVERSATION
# ============================================================================

async def handle_get_conversation_detail(
    conversation_id: str,
    current_user: Dict
) -> ConversationDetailResponse:
    """
    2.6.3: Xem chi tiết conversation
    
    Hiển thị:
    - Tất cả messages trong conversation
    - Course info
    - Timestamps
    
    Args:
        conversation_id: ID của conversation
        current_user: User hiện tại
        
    Returns:
        ConversationDetailResponse
        
    Raises:
        404: Conversation không tồn tại
        403: Không có quyền xem
        
    Endpoint: GET /api/v1/chat/conversations/{conversation_id}
    """
    user_id = current_user.get("user_id")
    
    # Query conversation
    conversation = await Conversation.find_one(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation không tồn tại hoặc bạn không có quyền xem"
        )
    
    # Lấy course info
    course = await course_service.get_course_by_id(conversation.course_id)
    course_title = course.title if course else "Unknown Course"
    
    # Build messages list
    messages = [
        {
            "id": msg.get("id", ""),
            "role": msg.get("role"),
            "content": msg.get("content"),
            "created_at": msg.get("created_at")
        }
        for msg in conversation.messages
    ]
    
    return ConversationDetailResponse(
        id=conversation.id,
        course_id=conversation.course_id,
        course_title=course_title,
        summary=conversation.title,
        messages=messages,
        total_messages=len(messages),
        created_at=conversation.created_at,
        last_updated=conversation.updated_at
    )


# ============================================================================
# Section 2.6.4: XÓA TẤT CẢ LỊCH SỬ CHAT
# ============================================================================

async def handle_delete_all_conversations(
    current_user: Dict
) -> ChatDeleteAllResponse:
    """
    2.6.4: Xóa tất cả conversations của user
    
    Xóa vĩnh viễn, không thể khôi phục
    
    Args:
        current_user: User hiện tại
        
    Returns:
        ChatDeleteAllResponse
        
    Endpoint: DELETE /api/v1/chat/conversations
    """
    user_id = current_user.get("user_id")
    
    # Query all conversations
    conversations = await Conversation.find(
        Conversation.user_id == user_id
    ).to_list()
    
    deleted_count = len(conversations)
    
    # Xóa từng conversation
    for conv in conversations:
        await conv.delete()
    
    return ChatDeleteAllResponse(
        message="Đã xóa tất cả lịch sử chat",
        deleted_count=deleted_count
    )


# ============================================================================
# Section 2.6.5: XÓA LỊCH SỬ CHAT TỪNG CONVERSATION
# ============================================================================

async def handle_delete_conversation(
    conversation_id: str,
    current_user: Dict
) -> ChatDeleteResponse:
    """
    2.6.5: Xóa một conversation cụ thể
    
    Xóa vĩnh viễn, không thể khôi phục
    
    Args:
        conversation_id: ID của conversation
        current_user: User hiện tại
        
    Returns:
        ChatDeleteResponse
        
    Raises:
        404: Conversation không tồn tại
        403: Không có quyền xóa
        
    Endpoint: DELETE /api/v1/chat/history/{conversation_id}
    """
    user_id = current_user.get("user_id")
    
    # Query conversation
    conversation = await Conversation.find_one(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation không tồn tại hoặc bạn không có quyền xóa"
        )
    
    # Xóa conversation
    await conversation.delete()
    
    return ChatDeleteResponse(
        message="Conversation đã được xóa thành công"
    )
