# TÀI LIỆU CHI TIẾT CHỨC NĂNG HỆ THỐNG AI LEARNING PLATFORM
> Người tạo: NGUYỄN NGỌC TUẤN ANH  
> Phân tích chi tiết chức năng theo vai trò và nhóm chức năng  
> Ngày cập nhật: 29/10/2025

## MỤC LỤC

1. [TỔNG QUAN PHÂN QUYỀN](#1-tổng-quan-phân-quyền)
2. [CHỨC NĂNG CHO HỌC VIÊN (STUDENT)](#2-chức-năng-cho-học-viên-student)
3. [CHỨC NĂNG CHO GIẢNG VIÊN (INSTRUCTOR)](#3-chức-năng-cho-giảng-viên-instructor)
4. [CHỨC NĂNG CHO QUẢN TRỊ VIÊN (ADMIN)](#4-chức-năng-cho-quản-trị-viên-admin)
5. [CHỨC NĂNG CHUNG (COMMON)](#5-chức-năng-chung-common)


---

## 1. TỔNG QUAN PHÂN QUYỀN

### 1.1 Cấu trúc vai trò

| Vai trò | Mã định danh | Mức độ quyền | Đối tượng chính |
|---------|--------------|--------------|-----------------|
| **Admin** | `admin` |  (Level 3) | Quản lý toàn hệ thống |
| **Instructor** | `instructor` |  (Level 2) | Giảng dạy và quản lý lớp học |
| **Student** | `student` | (Level 1) | Học tập và tự phát triển |


## 2. CHỨC NĂNG CHO HỌC VIÊN (STUDENT)

### 2.1 NHÓM CHỨC NĂNG: XÁC THỰC & QUẢN LÝ TÀI KHOẢN

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 2.1.1 | **Đăng ký tài khoản** | Tạo tài khoản mới với email, mật khẩu, tên đầy đủ, vai trò (mặc định là student). Hệ thống tự động gửi email xác nhận và tạo hồ sơ người dùng ban đầu. Thông tin bắt buộc: full_name (tối thiểu 2 từ), email (định dạng hợp lệ), password (tối thiểu 8 ký tự). | `POST /api/v1/auth/register` | Public |
| 2.1.2 | **Đăng nhập** | Xác thực người dùng với email và password. Trả về JWT access token (thời hạn 15 phút) và refresh token (thời hạn 7 ngày) để duy trì phiên đăng nhập. Hỗ trợ "Ghi nhớ đăng nhập" để gia hạn refresh token. | `POST /api/v1/auth/login` | Public |
| 2.1.3 | **Đăng xuất** | Vô hiệu hóa token hiện tại và xóa session trên client. Đồng thời hủy bỏ tất cả refresh token liên quan để đảm bảo bảo mật. Cập nhật thời gian đăng xuất cuối cùng. | `POST /api/v1/auth/logout` | Student |
| 2.1.4 | **Xem hồ sơ cá nhân** | Hiển thị thông tin chi tiết người dùng: tên đầy đủ, email, avatar, bio cá nhân, sở thích học tập, ngày tham gia hệ thống, lần đăng nhập cuối, số khóa học đã tham gia. | `GET /api/v1/users/me` | Student |
| 2.1.5 | **Cập nhật hồ sơ** | Chỉnh sửa thông tin cá nhân: tên đầy đủ, avatar, bio mô tả bản thân, thông tin liên hệ, sở thích học tập, cài đặt thông báo. | `PATCH /api/v1/users/me` | Student |

---

### 2.2 NHÓM CHỨC NĂNG: ĐÁNH GIÁ NĂNG LỰC (AI Dynamic Assessment)

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 2.2.1 | **Chọn phạm vi đánh giá năng lực** | Học viên chọn lĩnh vực và chủ đề cụ thể muốn đánh giá năng lực (ví dụ: Programming → Python → Web Development, Math → Đại số → Linear Algebra). Hệ thống hiển thị danh sách các danh mục có sẵn và cho phép chọn mức độ khó mong muốn (Beginner/Intermediate/Advanced). Thông tin này sẽ được gửi đến AI để tạo bộ câu hỏi phù hợp với năng lực và mục tiêu của học viên. | `POST /api/v1/assessments/generate` | Student |
| 2.2.2 | **Làm bài đánh giá năng lực** | AI tự động sinh ra bài quiz với các câu hỏi trắc nghiệm động, được sắp xếp theo độ khó từ dễ đến khó để đánh giá chính xác trình độ. Mỗi bài test có giới hạn thời gian phù hợp (15-30 phút tùy chủ đề). Trong mỗi bài có các "câu hỏi bắt buộc" (câu điểm liệt) để xác định kiến thức nền tảng - nếu sai các câu này sẽ ảnh hưởng lớn đến kết quả cuối. Học viên làm bài theo session_id được tạo và gửi kết quả lên hệ thống. | `POST /api/v1/assessments/{session_id}/submit` | Student |
| 2.2.3 | **Chấm điểm và phân tích năng lực** | AI tự động chấm điểm dựa trên thuật toán có trọng số (câu khó và câu bắt buộc có điểm cao hơn). Sau đó thực hiện phân tích sâu về năng lực theo từng mảng kiến thức: (1) Điểm tổng thể , (2) Phân loại trình độ chính xác (Beginner/Intermediate/Advanced), (3) Xác định điểm mạnh và điểm yếu cụ thể theo từng skill tag, (4) Phát hiện các "lỗ hổng kiến thức" - những khái niệm quan trọng mà học viên chưa nắm vững. | `GET /api/v1/assessments/{session_id}/results` | Student |
| 2.2.4 | **Đề xuất lộ trình học tập cá nhân hóa** | Dựa trên kết quả phân tích chi tiết, AI sinh ra lộ trình học tập được cá nhân hóa hoàn toàn cho từng học viên: danh sách các khóa học được đề xuất theo thứ tự ưu tiên (ưu tiên trước những khóa giải quyết lỗ hổng kiến thức), các module cần tập trung học đầu tiên, thứ tự học tối ưu để xây dựng kiến thức từ cơ bản đến nâng cao, và các bài tập ôn luyện để củng cố những kiến thức còn yếu. | `GET /api/v1/recommendations/from-assessment` | Student |

**Ghi chú về cơ chế sinh câu hỏi đánh giá:**

1. **Nguồn sinh câu hỏi:**
   - AI (Google Gemini API) sinh tự động các câu hỏi dựa trên chủ đề, cấp độ kiến thức, và mục tiêu học tập mà học viên đã chọn
   - Không sử dụng ngân hàng câu hỏi có sẵn, mà tạo động để đảm bảo tính đa dạng và phù hợp

2. **Cấu trúc mỗi câu hỏi:**
   - Đề bài rõ ràng, có ngữ cảnh thực tế
   - 4 đáp án lựa chọn (A, B, C, D) với 1 đáp án đúng
   - Mức độ khó được phân loại: Easy (20%), Medium (50%), Hard (30%)
   - Tag kỹ năng cụ thể (ví dụ: "python-syntax", "algorithm-complexity")  
   - Đánh dấu "câu bắt buộc" (câu điểm liệt) - những câu này kiểm tra kiến thức nền tảng quan trọng

3. **Quy tắc đánh giá:**
   - Câu hỏi bắt buộc 
   - Câu khó 
   - Phân tích theo từng skill tag để xác định điểm mạnh/yếu cụ thể


---


### 2.3 NHÓM CHỨC NĂNG: ĐĂNG KÝ KHÓA HỌC

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 2.3.1 | **Tìm kiếm khóa học** | Tìm kiếm khóa học theo từ khóa, danh mục, level, rating. Hỗ trợ filter và sort theo nhiều tiêu chí. | `GET /api/v1/courses/search` | Student |
| 2.3.2 | **Xem danh sách khóa học** | Hiển thị tất cả khóa học được publish bởi Admin. Mỗi khóa học hiển thị: tiêu đề, mô tả ngắn, hình ảnh, thời lượng, rating, giảng viên. | `GET /api/v1/courses/public` | Student |
| 2.3.3 | **Xem chi tiết khóa học** | Hiển thị thông tin đầy đủ: mô tả chi tiết, danh sách modules và lessons, learning outcomes, yêu cầu đầu vào, thông tin giảng viên, video preview. Nếu đã đăng ký sẽ hiển thị tiến độ học tập. | `GET /api/v1/courses/{id}` | Student |
| 2.3.4 | **Đăng ký khóa học** | Học viên đăng ký vào khóa học bằng course_id. Luồng: xem chi tiết khóa học → click "Đăng ký" → hệ thống kiểm tra điều kiện → tạo enrollment → trả về thông báo thành công. | `POST /api/v1/enrollments` | Student |
| 2.3.5 | **Xem khóa học đã đăng ký** | Hiển thị danh sách khóa học đã đăng ký với trạng thái: đang học, đã hoàn thành, bị hủy. Mỗi khóa hiển thị: tên, tiến độ (%), ngày đăng ký, điểm trung bình. | `GET /api/v1/enrollments/my-courses` | Student |
| 2.3.6 | **Hủy đăng ký khóa học** | Rút khỏi khóa học chưa hoàn thành. Cập nhật trạng thái enrollment thành "cancelled", dữ liệu học tập vẫn được lưu. | `DELETE /api/v1/enrollments/{id}` | Student |
---

### 2.4 NHÓM CHỨC NĂNG: HỌC TẬP & THEO DÕI TIẾN ĐỘ

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 2.4.1 | **Xem thông tin module** | Hiển thị chi tiết module: tên, mô tả, cấp độ, danh sách lessons, learning outcomes, thời lượng học, tài nguyên đính kèm. | `GET /api/v1/courses/{id}/modules/{moduleId}` | Student (enrolled) |
| 2.4.2 | **Xem nội dung bài học** | Đọc nội dung text, xem video bài giảng, tải tài liệu đính kèm. Hệ thống tracking thời gian học và đánh dấu phần đã hoàn thành. | `GET /api/v1/courses/{id}/lessons/{lessonId}` | Student (enrolled) |
| 2.4.3 | **Làm bài tập kèm theo bài học** | Sau khi hoàn thành nội dung bài học, học viên bắt buộc phải hoàn thành bài quiz đánh giá. Quiz bao gồm nhiều dạng câu hỏi: trắc nghiệm, điền khuyết, drag-and-drop, code completion. Có các câu hỏi "điểm liệt" (mandatory questions) - những kiến thức nền tảng quan trọng. Yêu cầu đạt tối thiểu 70% tổng điểm và phải trả lời đúng tất cả câu điểm liệt để được coi là pass. | `POST /api/v1/quizzes/{id}/attempt` | Student |
| 2.4.4 | **Xem kết quả quiz và giải thích** | Hiển thị kết quả chi tiết từng câu hỏi: điểm số, đáp án đã chọn vs đáp án đúng, giải thích chi tiết cho mỗi đáp án (tại sao đúng/sai), các concept liên quan, và gợi ý tài liệu để học thêm. Đặc biệt chú trọng giải thích các câu điểm liệt để học viên hiểu rõ kiến thức cốt lõi. Có link đến các phần trong bài học để ôn lại kiến thức. | `GET /api/v1/quizzes/{id}/results` | Student |
| 2.4.5 | **Làm lại quiz (nếu chưa đạt yêu cầu)** | Nếu không đạt ngưỡng 70% hoặc sai câu điểm liệt, học viên phải làm lại quiz. Hệ thống sinh ra bộ câu hỏi tương tự nhưng khác về chi tiết để tránh học thuộc lòng. Cho phép làm lại không giới hạn số lần. Mỗi lần làm lại sẽ ghi nhận thời gian và điểm số để theo dõi sự tiến bộ. Chỉ khi pass mới được phép tiếp tục lesson tiếp theo. | `POST /api/v1/quizzes/{id}/retake` | Student |
| 2.4.6 | **Nhận bài tập gợi ý cho câu sai** | AI phân tích chi tiết các câu trả lời sai và sinh ra bài tập luyện tập cá nhân hóa. Bài tập được tạo dựa trên: (1) Loại kiến thức bị thiếu, (2) Mức độ khó phù hợp, (3) Dạng bài tương tự trong module. AI không tạo hoàn toàn mới mà kết hợp từ ngân hàng câu hỏi có sẵn để đảm bảo chất lượng. Bao gồm cả bài tập lý thuyết và thực hành. | `POST /api/v1/ai/generate-practice` | Student |
| 2.4.7 | **Đánh dấu hoàn thành bài học** | Hệ thống tự động đánh dấu lesson completed chỉ khi học viên: (1) Đã xem hết nội dung bài học, (2) Đạt ≥70% điểm quiz, (3) Trả lời đúng tất cả câu điểm liệt. Khi completed, sẽ mở khóa lesson tiếp theo và cập nhật tiến độ tổng thể của module và khóa học. Ghi lại timestamp và lưu vào learning analytics. | `POST /api/v1/progress/complete-lesson` | Student (auto) |
| 2.4.8 | **Xem tiến độ khóa học và module** | Hiển thị tiến độ đa cấp: (1) Tiến độ tổng thể khóa học (%), (2) Tiến độ từng module (%), (3) Danh sách lesson đã hoàn thành/chưa hoàn thành, (4) Thời gian học ước tính còn lại, (5) Streak (số ngày học liên tiếp), (6) Điểm trung bình các quiz. Progress bar trực quan với màu sắc khác nhau cho các trạng thái. | `GET /api/v1/progress/course/{courseId}` | Student |

**Chi tiết cấu trúc Module & Learning Path:**

| **Thành phần** | **Mô tả chi tiết** |
|----------------|-------------------|
| **Module Info** | Danh sách các module, tên mô tả rõ ràng, cấp độ khó (Basic → Intermediate → Advanced), thứ tự logic trong khóa học, prerequisites (module tiên quyết cần hoàn thành trước) |
| **Learning Outcomes** | Mục tiêu học tập cụ thể và đo lường được mà người học sẽ đạt sau khi hoàn thành module (ví dụ: "Có thể viết được function Python xử lý exception", "Hiểu được các khái niệm OOP cơ bản") |
| **Kiến thức chi tiết cần đạt** | Breakdown từng concept, skill, hoặc khái niệm cụ thể cần nắm vững, có mapping rõ ràng đến các lesson và quiz tương ứng. Mỗi kiến thức có tag để dễ tracking và đánh giá |
| **Tài nguyên học tập** | **Tài nguyên lý thuyết**: Bài đọc, slide, documentation<br>**Tài nguyên thực hành**: Code examples, sandbox environment, simulators<br>**Tài nguyên tham khảo**: External links, books, video tutorials bổ sung |
| **Assessment mặc định** | Bộ câu hỏi chuẩn để kiểm tra đầu ra module: quiz kiến thức nền tảng, mini-test thực hành, project nhỏ. Có phân loại theo độ khó và trọng số điểm |
| **Thời lượng học** | Thời gian học tối thiểu và tối đa được khuyến nghị cho module, ước tính dựa trên độ phức tạp nội dung và thống kê từ học viên trước đó |
| **Ngưỡng điểm Pass** | Điểm tối thiểu cần đạt để hoàn thành module (mặc định 70%), có thể điều chỉnh tùy theo tính chất module (module nền tảng có thể yêu cầu 80%) |
| **Kiến thức bắt buộc** | Các câu hỏi hoặc concept "điểm liệt" - nếu không nắm vững sẽ không thể qua module dù tổng điểm cao. Thường là những kiến thức nền tảng quan trọng cho các module tiếp theo |

**API Endpoints cho Module Management:**
- `GET /api/v1/courses/{courseId}/modules` - Lấy danh sách tất cả modules
- `GET /api/v1/modules/{moduleId}/outcomes` - Lấy learning outcomes của module  
- `GET /api/v1/modules/{moduleId}/resources` - Lấy tài nguyên học tập
- `POST /api/v1/modules/{moduleId}/assessments/generate` - Sinh quiz đánh giá cho module
- `GET /api/v1/progress/module/{moduleId}` - Xem tiến độ hoàn thành module
---

### 2.5 NHÓM CHỨC NĂNG: KHÓA HỌC CÁ NHÂN (PERSONAL COURSE)

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 2.5.1 | **Tạo khóa học từ prompt AI** | Học viên nhập mô tả chủ đề và mục tiêu học tập (ví dụ: "Tôi muốn học lập trình Python cơ bản cho người mới bắt đầu"). AI sẽ tự động phân tích và sinh ra cấu trúc khóa học hoàn chỉnh bao gồm: danh sách modules theo thứ tự logic, các lessons trong mỗi module, learning outcomes, và nội dung cơ bản. Luồng: FE hiển thị form nhập prompt → gửi request → AI xử lý (3-5 giây) → trả về cấu trúc khóa học → FE hiển thị preview → học viên xác nhận tạo. | `POST /api/v1/courses/from-prompt` | Student |
| 2.5.2 | **Tạo khóa học thủ công** | Tạo khóa học trống với thông tin cơ bản (tên, mô tả, danh mục) do học viên tự điền. Sau khi tạo thành công, học viên có thể thêm modules và lessons thủ công qua giao diện quản lý. Luồng: FE hiển thị form tạo khóa học → nhập thông tin cơ bản → gửi request tạo → BE tạo khóa học với trạng thái "draft" → trả về course_id → chuyển đến trang quản lý khóa học để thêm nội dung. | `POST /api/v1/courses/personal` | Student |
| 2.5.3 | **Xem danh sách khóa học cá nhân** | Hiển thị tất cả khóa học do học viên tự tạo với thông tin: tên khóa học, trạng thái (draft/published), số modules/lessons đã tạo, ngày tạo, lần chỉnh sửa cuối. Hỗ trợ filter theo trạng thái và tìm kiếm theo tên. Mỗi item có các action: xem chi tiết, chỉnh sửa, xóa, publish (nếu admin cho phép). | `GET /api/v1/courses/my-personal` | Student |
| 2.5.4 | **Chỉnh sửa khóa học cá nhân** | Cho phép sửa đổi mọi thành phần của khóa học cá nhân: thay đổi tiêu đề và mô tả, thêm/xóa/sắp xếp lại modules, chỉnh sửa nội dung lessons, cập nhật learning outcomes. FE cung cấp giao diện drag-and-drop để sắp xếp modules/lessons. Mọi thay đổi được auto-save sau 2-3 giây hoặc khi người dùng blur khỏi field đang edit. | `PUT /api/v1/courses/personal/{id}` | Student (owner) |
| 2.5.5 | **Xóa khóa học cá nhân** | Xóa vĩnh viễn khóa học đã tạo (chỉ cho phép xoá khoá học cá nhân tạo bởi chính học viên). FE hiển thị dialog xác nhận với cảnh báo rõ ràng về việc xóa không thể khôi phục. BE kiểm tra điều kiện trước khi xóa (Chính học viên đó tạo thì chỉ xoá khoá học đó). | `DELETE /api/v1/courses/personal/{id}` | Student (owner) |


---

### 2.6 NHÓM CHỨC NĂNG: TƯƠNG TÁC VỚI AI CHATBOT

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 2.6.1 | **Chat về khóa học** | Học viên có thể hỏi đáp với AI về nội dung khóa học đang học. AI trả lời dựa trên context của khóa học đó (tên, mô tả modules, nội dung lessons). Luồng: FE hiển thị chat box trong trang khóa học → học viên gõ câu hỏi → gửi request kèm courseId và question → BE gửi context khóa học + câu hỏi đến AI → AI trả lời → hiển thị câu trả lời real-time.  | `POST /api/v1/chat/course/{courseId}` | Student (enrolled) |
| 2.6.2 | **Xem lịch sử chat** | Hiển thị danh sách tất cả các cuộc hội thoại đã có với AI, được nhóm theo ngày hoặc theo chủ đề. Mỗi conversation hiển thị: thời gian bắt đầu, số lượt hỏi đáp, chủ đề chính, và preview câu hỏi đầu tiên. Học viên có thể click để xem lại toàn bộ nội dung conversation và tiếp tục hỏi đáp từ đó. | `GET /api/v1/chat/history` | Student |
| 2.6.3 | **Xóa lịch sử chat** | Cho phép xóa từng conversation riêng lẻ hoặc xóa toàn bộ lịch sử chat. FE hiển thị checkbox để chọn nhiều conversation và xóa hàng loạt. Có option "Xóa tất cả" với dialog xác nhận nghiêm ngặt. Dữ liệu đã xóa không thể khôi phục được. | `DELETE /api/v1/chat/history/{id}` | Student |


### 2.7 NHÓM CHỨC NĂNG: DASHBOARD & ANALYTICS

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 2.7.1 | **Dashboard tổng quan** | Trang chính hiển thị thông tin quan trọng nhất: danh sách khóa học đang học (với progress bar cho mỗi khóa), các bài quiz gần đây cần làm hoặc đã làm, thông báo từ hệ thống, các khóa học được đề xuất, và streak học tập hiện tại. Layout responsive với các widget có thể tùy chỉnh vị trí.  | `GET /api/v1/dashboard/student` | Student |
| 2.7.2 | **Thống kê học tập chi tiết** | Hiển thị metrics học tập đầy đủ: tổng số giờ học (hôm nay, tuần này, tháng này), số bài học đã hoàn thành, số quiz đã pass, điểm trung bình tất cả quiz. FE sử dụng charts và progress rings để visualize data một cách trực quan và dễ hiểu. | `GET /api/v1/analytics/learning-stats` | Student |
| 2.7.3 | **Biểu đồ tiến độ theo thời gian** | Hiển thị biểu đồ line chart hoặc bar chart thể hiện tiến độ học tập theo thời gian (có thể chọn view theo ngày, tuần, tháng). Trục Y là số bài hoàn thành hoặc số giờ học, trục X là thời gian. Có thể filter theo từng khóa học cụ thể. FE sử dụng thư viện chart (Chart.js, D3) để render với animation mượt mà. | `GET /api/v1/analytics/progress-chart` | Student |
| 2.7.4 | **Đề xuất khóa học thông minh** | AI phân tích lịch sử học tập, sở thích đã khai báo, và performance trong các bài assessment để đề xuất khóa học phù hợp. Hiển thị danh sách khóa học được recommend kèm lý do tại sao được đề xuất (ví dụ: "Dựa trên kết quả assessment Python của bạn", "Phù hợp với sở thích AI/ML").  | `GET /api/v1/recommendations` | Student |

---


## 3. CHỨC NĂNG CHO GIẢNG VIÊN (INSTRUCTOR)

### 3.1 NHÓM CHỨC NĂNG: QUẢN LÝ LỚP HỌC

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 3.1.1 | **Tạo lớp học mới** | Giảng viên chọn một khóa học công khai có sẵn trong hệ thống làm nền tảng, sau đó tạo lớp học với thông tin: tên lớp, mô tả, thời gian bắt đầu và kết thúc, số lượng học viên tối đa. Luồng: FE hiển thị danh sách khóa học có thể chọn → chọn khóa học → điền thông tin lớp → preview cấu trúc lớp → xác nhận tạo → BE tạo lớp với trạng thái "preparing" → trả về class_id và mã mời (học viên sẽ có 1 ô nhập mã mời của giáo viên, được tạo dựa trên mỗi lớp học). | `POST /api/v1/classes` | Instructor |
| 3.1.2 | **Xem danh sách lớp học** | Hiển thị tất cả lớp học do giảng viên quản lý với thông tin: tên lớp, khóa học gốc, số học viên hiện tại/tối đa, trạng thái (preparing/active/completed), thời gian bắt đầu/kết thúc, tiến độ chung của lớp (%). Hỗ trợ filter theo trạng thái và sắp xếp theo thời gian tạo hoặc số học viên. | `GET /api/v1/classes/my-classes` | Instructor |
| 3.1.3 | **Xem chi tiết lớp học** | Hiển thị thông tin đầy đủ về lớp: thông tin cơ bản (tên ...vv), danh sách học viên với avatar và progress cá nhân, thống kê tổng quan (số bài đã hoàn thành, điểm trung bình....) | `GET /api/v1/classes/{id}` | Instructor (owner) |
| 3.1.4 | **Chỉnh sửa thông tin lớp** | Cho phép sửa đổi: tên lớp, mô tả, thời gian bắt đầu/kết thúc (chỉ khi chưa bắt đầu), số lượng học viên tối đa, trạng thái lớp (active/paused/completed). FE validate các ràng buộc (không được giảm thời gian khi đã bắt đầu, không giảm số lượng dưới số học viên hiện tại). . | `PUT /api/v1/classes/{id}` | Instructor (owner) |
| 3.1.5 | **Xóa lớp học** | Xóa vĩnh viễn lớp học (chỉ được phép khi: lớp chưa có học viên nào, hoặc lớp đã kết thúc ). FE hiển thị dialog cảnh báo với danh sách những gì sẽ bị xóa (data học viên, progress, quiz results). | `DELETE /api/v1/classes/{id}` | Instructor (owner) |


---

### 3.2 NHÓM CHỨC NĂNG: QUẢN LÝ HỌC VIÊN

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 3.2.1 | **Mời học viên vào lớp** | Tạo link mời hoặc mã code đơn giản (6-8 ký tự) để học viên có thể tự động join vào lớp.. | `POST /api/v1/classes/{id}/invite` | Instructor (owner) |
| 3.2.2 | **Xem danh sách học viên** | Hiển thị table tất cả học viên trong lớp với thông tin: avatar, tên, email, ngày join, tiến độ hoàn thành (%), điểm trung bình quiz, lần truy cập cuối, trạng thái. Hỗ trợ search theo tên, filter theo tiến độ hoặc trạng thái, và sort theo các cột khác nhau.. | `GET /api/v1/classes/{id}/students` | Instructor (owner) |
| 3.2.3 | **Xem hồ sơ học viên chi tiết** | Hiển thị thông tin đầy đủ của một học viên trong lớp: profile cơ bản, chi tiết điểm từng quiz, các bài đã hoàn thành và chưa hoàn thành,  | `GET /api/v1/classes/{id}/students/{studentId}` | Instructor (owner) |
| 3.2.4 | **Xóa học viên khỏi lớp** | Remove học viên khỏi lớp (giữ lại progress data để có thể add lại sau). Luồng: chọn học viên → xác nhận lý do remove → cập nhật trạng thái enrollment thành "removed". Học viên bị remove sẽ không thể truy cập nội dung lớp nhưng vẫn giữ progress để tham khảo. | `DELETE /api/v1/classes/{id}/students/{studentId}` | Instructor (owner) |
| 3.2.5 | **Theo dõi tiến độ tổng thể lớp** | Dashboard hiển thị tiến độ học tập của toàn lớp dưới dạng biểu đồ và bảng: phân bố điểm số, số học viên đã hoàn thành từng module, lessons được hoàn thành nhiều nhất/ít nhất, thời gian trung bình hoàn thành mỗi module.  | `GET /api/v1/classes/{id}/progress` | Instructor (owner) |

---


### 3.3 NHÓM CHỨC NĂNG: QUẢN LÝ QUIZ & ASSIGNMENTS

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 3.3.1 | **Tạo quiz tùy chỉnh** | Giảng viên tạo bài quiz riêng cho lớp học với giao diện drag-and-drop: thêm câu hỏi trắc nghiệm, điền khuyết, đúng/sai. Đặt thời gian làm bài, số lần được làm lại, điểm pass, và thời hạn nộp bài. Preview quiz trước khi publish để kiểm tra giao diện và logic. | `POST /api/v1/quizzes` | Instructor |
| 3.3.2 | **Quản lý danh sách quiz** | Hiển thị tất cả quiz đã tạo cho các lớp học với thông tin: tên quiz, lớp áp dụng, số câu hỏi, thời gian làm bài, số học viên đã làm/tổng số, tỷ lệ pass, ngày tạo. Có filter theo lớp học, trạng tháim và search theo tên quiz. | `GET /api/v1/quizzes/my-quizzes` | Instructor |
| 3.3.3 | **Chỉnh sửa quiz** | Sửa đổi mọi thành phần của quiz: thêm/xóa/sửa câu hỏi, thay đổi thời gian và điều kiện, cập nhật hướng dẫn. Nếu đã có học viên làm bài, FE sẽ cảnh báo và yêu cầu tạo phiên bản mới thay vì sửa trực tiếp.  | `PUT /api/v1/quizzes/{id}` | Instructor (owner) |
| 3.3.4 | **Xóa quiz** | Xóa quiz (chỉ được phép khi chưa có học viên nào làm bài hoặc tất cả kết quả đã được backup). FE hiển thị cảnh báo về số lượng học viên đã làm và hỏi có muốn  xóa  | `DELETE /api/v1/quizzes/{id}` | Instructor (owner) |
| 3.3.5 | **Phân tích kết quả quiz lớp** | Dashboard chi tiết với nhiều loại biểu đồ: histogram phân bổ điểm, bar chart so sánh điểm trung bình theo từng câu hỏi, table ranking học viên, timeline số lượng bài nộp theo thời gian.  | `GET /api/v1/quizzes/{id}/class-results` | Instructor (owner) |

---
---

### 3.4 NHÓM CHỨC NĂNG: DASHBOARD & ANALYTICS

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 3.4.1 | **Dashboard giảng viên tổng quan** | Hiển thị metrics tổng thể: số lớp đang quản lý, tổng số học viên across tất cả lớp, lớp có hoạt động gần đây nhất, thông báo cần xử lý . Layout gọn gàng với các widget hiển thị số liệu quan trọng và quick actions (tạo lớp mới, tạo quiz, xem báo cáo). | `GET /api/v1/dashboard/instructor` | Instructor |
---

## 4. CHỨC NĂNG CHO QUẢN TRỊ VIÊN (ADMIN)

### 4.1 NHÓM CHỨC NĂNG: QUẢN LÝ NGƯỜI DÙNG

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 4.1.1 | **Quản lý danh sách người dùng** | Hiển thị table tất cả users trong hệ thống (Students, Instructors, Admins) với thông tin: avatar, tên, email, role, ngày tạo. Advanced filters: theo role, status, ngày tạo. Search theo tên/email với autocomplete.  | `GET /api/v1/admin/users` | Admin |
| 4.1.2 | **Xem profile người dùng chi tiết** | Hiển thị thông tin đầy đủ: thông tin cá nhân, lịch sử hoạt động (đăng nhập), statistics (số khóa học đã học, điểm trung bình), các khóa học/lớp đang tham gia. | `GET /api/v1/admin/users/{id}` | Admin |
| 4.1.3 | **Tạo tài khoản người dùng** | Admin tạo trực tiếp tài khoản cho user với thông tin cơ bản (tên, email, role, password tạm thời).  | `POST /api/v1/admin/users` | Admin |
| 4.1.4 | **Cập nhật thông tin người dùng** | Chỉnh sửa thông tin: tên đầy đủ, email, role. FE validate email không trùng lặp và hiển thị preview thay đổi trước khi submit.  | `PUT /api/v1/admin/users/{id}` | Admin |
| 4.1.5 | **Xóa người dùng** |  delete vĩnh viễn tài khoản. Delete: xóa hoàn toàn (yêu cầu confirmation nghiêm ngặt). Trước khi xóa, hệ thống kiểm tra dependencies (lớp học đang dạy, khóa học đã tạo) và đưa ra cảnh báo. | `DELETE /api/v1/admin/users/{id}` | Admin |
| 4.1.6 | **Thay đổi phân quyền** | Nâng cấp hoặc hạ cấp role người dùng: Student ↔ Instructor ↔ Admin. FE hiển thị dialog xác nhận với mô tả quyền hạn mới. Khi thay đổi role, hệ thống kiểm tra impacts (ví dụ: hạ Instructor xuống Student sẽ ảnh hưởng đến lớp học nào) và yêu cầu xác nhận. | `PUT /api/v1/admin/users/{id}/role` | Admin |
| 4.1.7 | **Reset mật khẩu người dùng** | Force reset password cho user khi họ quên hoặc có vấn đề bảo mật.| `POST /api/v1/admin/users/{id}/reset-password` | Admin |

---

### 4.2 NHÓM CHỨC NĂNG: QUẢN LÝ KHÓA HỌC

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 4.2.1 | **Quản lý toàn bộ khóa học** | Hiển thị danh sách tất cả courses trong hệ thống (public, personal) với thông tin: tên khóa học, tác giả, loại (public/personal), số enrollments, ngày tạo. Filter theo tác giả, trạng thái, danh mục.. | `GET /api/v1/admin/courses` | Admin |
| 4.2.2 | **Xem chi tiết khóa học** | Hiển thị thông tin đầy đủ: metadata, cấu trúc modules/lessons chi tiết, nội dung từng phần, analytics (views, enrollments). Admin có thể preview khóa học như một student để kiểm tra chất lượng. | `GET /api/v1/admin/courses/{id}` | Admin |
| 4.2.3 | **Tạo khóa học hệ thống** | Admin tạo khóa học chính thức của hệ thống với đầy đủ quyền hạn: thiết kế cấu trúc, thêm nội dung rich text/media, cấu hình quiz, đặt prerequisites.  | `POST /api/v1/admin/courses` | Admin |
| 4.2.4 | **Chỉnh sửa mọi khóa học** | Quyền chỉnh sửa toàn bộ nội dung của bất kỳ khóa học nào (kể cả personal courses của user). Có thể: sửa nội dung, thêm/xóa modules, điều chỉnh cấu trúc, moderate reviews, update metadata. M | `PUT /api/v1/admin/courses/{id}` | Admin |
| 4.2.5 | **Xóa khóa học** | Cho phép xóa vĩnh viễn khóa học. Trước khi xóa, kiểm tra impact: số học viên đang học, lớp học đang sử dụng FE hiển thị impact analysis và yêu cầu xác nhận.  | `DELETE /api/v1/admin/courses/{id}` | Admin |

---

### 4.3 NHÓM CHỨC NĂNG: QUẢN LÝ LỚP HỌC

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 4.3.1 | **Giám sát tất cả lớp học** | Hiển thị danh sách toàn bộ classes từ mọi instructor với thông tin: tên lớp, giảng viên, khóa học , số học viên, trạng thái, thời gian bắt đầu/kết thúc,  | `GET /api/v1/admin/classes` | Admin |
| 4.3.2 | **Giám sát chi tiết lớp học** | Xem thông tin đầy đủ của bất kỳ lớp nào: thông tin giảng viên , danh sách học viên  | `GET /api/v1/admin/classes/{id}` | Admin |

---

### 4.4 NHÓM CHỨC NĂNG: DASHBOARD 

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 4.4.1 | **Dashboard quản trị tổng quan** | Hiển thị metrics quan trọng của toàn hệ thống: tổng số users (breakdown theo role), số khóa học (public/personal), số lớp đang active | `GET /api/v1/admin/dashboard` | Admin |

---

## 5. CHỨC NĂNG CHUNG (COMMON)

### 5.1 NHÓM CHỨC NĂNG: TÌM KIẾM & LỌC

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 5.1.1 | **Tìm kiếm thông minh toàn hệ thống** | Universal search với khả năng tìm kiếm courses, users (nếu có quyền), classes, modules, lessons qua một search box duy nhất. Hỗ trợ full-text search, search suggestions, typo tolerance, và search history. Results được nhóm theo category với relevant score. FE hiển thị kết quả real-time khi user typing. | `GET /api/v1/search` | All roles |
| 5.1.2 | **Bộ lọc nâng cao** | Advanced filtering system cho courses: theo category/subcategory, level (Beginner/Intermediate/Advanced), instructor.  FE sử dụng sidebar filters với count cho mỗi option và clear all functionality. | `GET /api/v1/search/filter` | All roles |

---

