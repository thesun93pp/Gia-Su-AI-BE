# TÀI LIỆU CHI TIẾT CHỨC NĂNG HỆ THỐNG AI LEARNING PLATFORM
> Người tạo: NGUYỄN NGỌC TUẤN ANH  
> Phân tích chi tiết chức năng theo vai trò và nhóm chức năng  
> Ngày cập nhật: 2/11/2025

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
| 2.1.1 | **Đăng ký tài khoản** | Tạo tài khoản mới với email, mật khẩu, tên đầy đủ, vai trò (mặc định là student).  Thông tin bắt buộc: full_name (tối thiểu 2 từ), email (định dạng hợp lệ), password (tối thiểu 8 ký tự). | `POST /api/v1/auth/register` | Public |
| 2.1.2 | **Đăng nhập** | Xác thực người dùng với email và password. Trả về JWT access token (thời hạn 15 phút) và refresh token (thời hạn 7 ngày) để duy trì phiên đăng nhập. Hỗ trợ "Ghi nhớ đăng nhập" để gia hạn refresh token. | `POST /api/v1/auth/login` | Public |
| 2.1.3 | **Đăng xuất** | Vô hiệu hóa token hiện tại và xóa session trên client. Đồng thời hủy bỏ tất cả refresh token liên quan để đảm bảo bảo mật. | `POST /api/v1/auth/logout` | Student |
| 2.1.4 | **Xem hồ sơ cá nhân** | Hiển thị thông tin chi tiết người dùng: tên đầy đủ, email, avatar, bio cá nhân, sở thích học tập. ( có thể null ko bắt buộc )| `GET /api/v1/users/me` | Student |
| 2.1.5 | **Cập nhật hồ sơ** | Chỉnh sửa thông tin cá nhân: tên đầy đủ, avatar, bio mô tả bản thân, thông tin liên hệ, sở thích học tập, | `PATCH /api/v1/users/me` | Student |

---

### 2.2 NHÓM CHỨC NĂNG: ĐÁNH GIÁ NĂNG LỰC (AI Dynamic Assessment)

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 2.2.1 | **Chọn phạm vi đánh giá năng lực** | Học viên chọn lĩnh vực và chủ đề cụ thể muốn đánh giá năng lực (ví dụ: Programming → Python → Web Development, Math → Đại số → Linear Algebra). **Lưu ý quan trọng:** Lĩnh vực và chủ đề phải tuân theo các khóa học đã được tạo sẵn trong hệ thống để đảm bảo câu hỏi AI sinh ra luôn bám sát nội dung khóa học. Hệ thống hiển thị danh sách các danh mục có sẵn dưới dạng cây phân cấp (lĩnh vực → chủ đề → chủ đề con) và cho phép chọn mức độ mong muốn: **Beginner** (Sơ cấp), **Intermediate** (Trung cấp), **Advanced** (Nâng cao). Thông tin này được gửi đến AI để tạo bộ câu hỏi phù hợp với năng lực và mục tiêu của học viên. | `POST /api/v1/assessments/generate` | Student |
| 2.2.2 | **Làm bài đánh giá năng lực** | AI tự động sinh ra bài quiz đánh giá với nhiều dạng câu hỏi: **(1) Trắc nghiệm nhiều lựa chọn**, **(2) Tự luận điền khuyết**, **(3) Kéo thả (drag-and-drop)**. Các câu hỏi được sắp xếp từ dễ đến khó để đánh giá chính xác trình độ. **Số lượng câu hỏi theo từng mức độ:** Beginner = 15 câu, Intermediate = 25 câu, Advanced = 35 câu. **Thời gian làm bài:** 15-30 phút tùy theo độ phức tạp của chủ đề. Học viên làm bài theo `session_id` được tạo tự động và gửi kết quả lên hệ thống khi hoàn thành. | `POST /api/v1/assessments/{session_id}/submit` | Student |
| 2.2.3 | **Chấm điểm và phân tích năng lực** | AI tự động chấm điểm dựa trên thuật toán có trọng số (câu khó có điểm cao hơn câu dễ). Sau đó thực hiện phân tích sâu về năng lực học viên theo 4 khía cạnh: **(1) Điểm tổng thể** (trên thang 100), **(2) Phân loại trình độ chính xác** (Beginner/Intermediate/Advanced) dựa trên kết quả thực tế, **(3) Xác định điểm mạnh và điểm yếu cụ thể** theo từng skill tag (ví dụ: giỏi về "python-syntax" nhưng yếu về "algorithm-complexity"), **(4) Phát hiện các "lỗ hổng kiến thức"** - những khái niệm quan trọng mà học viên chưa nắm vững và cần ưu tiên học lại. | `GET /api/v1/assessments/{session_id}/results` | Student |
| 2.2.4 | **Đề xuất lộ trình học tập cá nhân hóa** | Dựa trên kết quả phân tích chi tiết ở bước 2.2.3, AI sinh ra lộ trình học tập được cá nhân hóa hoàn toàn cho từng học viên bao gồm: **(1) Danh sách khóa học được đề xuất** theo thứ tự ưu tiên (ưu tiên trước những khóa giải quyết lỗ hổng kiến thức nghiêm trọng nhất), **(2) Các module cần tập trung học** đầu tiên trong mỗi khóa, **(3) Thứ tự học tối ưu** để xây dựng kiến thức từ cơ bản đến nâng cao một cách logic, **(4) Các bài tập ôn luyện** để củng cố những kiến thức còn yếu trước khi tiếp tục. | `GET /api/v1/recommendations/from-assessment` | Student |

---

**📋 GHI CHÚ CHI TIẾT VỀ CƠ CHẾ SINH CÂU HỎI ĐÁNH GIÁ**

#### **1. NGUỒN SINH CÂU HỎI**

- **AI Engine:** Sử dụng Google Gemini API để sinh câu hỏi tự động
- **Cơ chế hoạt động:** 
  - AI đọc và phân tích nội dung miêu tả ngắn của các khóa học có sẵn trong hệ thống
  - Dựa trên chủ đề mà học viên chọn để đánh giá, AI trích xuất các khái niệm cốt lõi và sinh câu hỏi bám sát nội dung đó
  - **KHÔNG** sử dụng ngân hàng câu hỏi có sẵn → mỗi lần làm bài sẽ có bộ câu hỏi khác nhau để đảm bảo tính đa dạng và tránh học thuộc lòng
- **Yêu cầu bắt buộc:** Câu hỏi phải bám sát nội dung các khóa học đã tạo sẵn theo chủ đề học viên chọn

#### **2. PHÂN BỔ SỐ LƯỢNG VÀ ĐỘ KHÓ CỦA CÂU HỎI**

Mỗi bài test có số lượng câu hỏi và cơ cấu độ khó khác nhau tùy theo mức độ học viên chọn:

| Mức độ | Tổng số câu | Câu Dễ (Easy) | Câu Trung bình (Medium) | Câu Khó (Hard) | Thời gian |
|--------|-------------|---------------|------------------------|----------------|-----------|
| **Beginner (Sơ cấp)** | 15 câu | 3 câu (20%) | 8 câu (53%) | 4 câu (27%) | 15 phút |
| **Intermediate (Trung cấp)** | 25 câu | 5 câu (20%) | 13 câu (52%) | 7 câu (28%) | 22 phút |
| **Advanced (Nâng cao)** | 35 câu | 7 câu (20%) | 18 câu (51%) | 10 câu (29%) | 30 phút |

**Giải thích tỷ lệ phân bổ:**
- **Câu dễ (20%):** Kiểm tra kiến thức nền tảng cơ bản nhất
- **Câu trung bình (50-53%):** Chiếm tỷ trọng lớn nhất, đánh giá khả năng áp dụng kiến thức
- **Câu khó (27-30%):** Kiểm tra tư duy phản biện và khả năng giải quyết vấn đề phức tạp

**Cách sắp xếp:** Các câu hỏi được sắp xếp theo thứ tự **từ dễ đến khó** trong bài test để:
- Giúp học viên khởi động tốt với các câu dễ
- Tăng dần độ khó để đánh giá chính xác giới hạn năng lực
- Tránh gây áp lực ngay từ đầu bài

#### **3. CẤU TRÚC CHI TIẾT MỖI CÂU HỎI**

Mỗi câu hỏi được sinh ra bởi AI sẽ có đầy đủ các thành phần sau:

| Thành phần | Mô tả chi tiết |
|------------|----------------|
| **Đề bài** | Câu hỏi rõ ràng, súc tích, có ngữ cảnh thực tế để học viên dễ hình dung |
| **Dạng câu hỏi** | **Trắc nghiệm:** 4 đáp án (A, B, C, D) với 1 đáp án đúng<br>**Điền khuyết:** Điền từ/cụm từ vào chỗ trống<br>**Kéo thả:** Kéo các phần tử vào vị trí đúng |
| **Độ khó** | Easy / Medium / Hard (được phân loại tự động bởi AI) |
| **Skill Tag** | Gắn nhãn kỹ năng cụ thể mà câu hỏi kiểm tra (ví dụ: "python-syntax", "algorithm-complexity", "data-structures-array") |
| **Điểm số** | Easy = 1 điểm, Medium = 2 điểm, Hard = 3 điểm (có thể điều chỉnh theo trọng số) |
| **Giải thích** | Giải thích chi tiết tại sao đáp án đúng và tại sao các đáp án khác sai (hiển thị sau khi nộp bài) |

**Ví dụ câu hỏi:**
```
Câu 1 (Easy - python-syntax):
Cú pháp nào sau đây dùng để khai báo list trong Python?
A. list = ()
B. list = []  ✓ (Đúng)
C. list = {}
D. list = <>

Giải thích: 
- B đúng vì [] là cú pháp khai báo list trong Python
- A sai vì () dùng cho tuple
- C sai vì {} dùng cho dictionary hoặc set
- D sai vì <> không phải cú pháp hợp lệ trong Python
```

#### **4. QUY TẮC TÍNH ĐIỂM VÀ ĐÁNH GIÁ**

- **Hệ thống tính điểm có trọng số:**
  - Câu dễ (Easy): 1 điểm
  - Câu trung bình (Medium): 2 điểm
  - Câu khó (Hard): 3 điểm

- **Công thức tính điểm tổng:**
  ```
  Điểm tổng = (Số câu Easy đúng × 1 + Số câu Medium đúng × 2 + Số câu Hard đúng × 3) / Tổng điểm tối đa × 100
  ```

- **Phân tích năng lực chi tiết:**
  - Nhóm câu hỏi theo **Skill Tag** để xác định điểm mạnh/yếu cụ thể
  - Ví dụ: Nếu học viên làm đúng 80% câu hỏi tag "python-syntax" nhưng chỉ 40% câu tag "algorithm-complexity" → AI sẽ xác định "lỗ hổng kiến thức" ở phần thuật toán

- **Ngưỡng đánh giá trình độ:**
  - **Beginner:** < 60 điểm
  - **Intermediate:** 60-80 điểm
  - **Advanced:** > 80 điểm

- **Báo cáo kết quả bao gồm:**
  1. Điểm tổng và xếp loại trình độ
  2. Biểu đồ radar thể hiện điểm số theo từng skill tag
  3. Danh sách cụ thể các lỗ hổng kiến thức cần khắc phục
  4. Đề xuất lộ trình học tập cá nhân hóa dựa trên kết quả


---


### 2.3 NHÓM CHỨC NĂNG: KHÁM PHÁ & ĐĂNG KÝ KHÓA HỌC

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 2.3.1 | **Tìm kiếm khóa học** | Tìm kiếm khóa học theo nhiều tiêu chí: **(1) Từ khóa** (tên khóa học, mô tả), **(2) Danh mục** (Programming, Math, Business...), **(3) Cấp độ** (Beginner/Intermediate/Advanced),. **Hỗ trợ filter nâng cao:** lọc theo thời lượng, ngày tạo, số học viên đã đăng ký.(FE tự thêm hoặc xem xét bỏ ở filter nâng cao) **Hỗ trợ sắp xếp:**  mới nhất, cũ nhất. Kết quả tìm kiếm hiển thị real-time khi người dùng nhập.(FE tự thêm hoặc xem xét bỏ) | `GET /api/v1/courses/search` | Student |
| 2.3.2 | **Xem danh sách khóa học công khai** | Hiển thị tất cả khóa học đã được Admin publish công khai. **Mỗi khóa học hiển thị:** **(1) Tiêu đề và hình ảnh đại diện**, **(2) Mô tả ngắn gọn (2-3 câu)**, **(3) Thời lượng học tập ước tính**, **(4) Số lượng modules và lessons**, **(5) Cấp độ khóa học**. Layout dạng grid card với pagination để dễ duyệt.(FE) | `GET /api/v1/courses/public` | Student |
| 2.3.3 | **Xem chi tiết khóa học** | Hiển thị thông tin đầy đủ và toàn diện về khóa học: **(1) Thông tin tổng quan:** tiêu đề, mô tả chi tiết, hình ảnh/video giới thiệu, **(2) Cấu trúc khóa học:** danh sách modules và lessons (có thể expand/collapse), **(3) Mục tiêu học tập** (Learning Outcomes) - những gì học viên sẽ đạt được sau khóa học, **(4) Yêu cầu đầu vào** (Prerequisites) - kiến thức cần có trước khi học(FE thể hiện ở dạng text cứng cho mỗi khóa học, có thể bỏ ) **(5) Thông tin giảng viên:** (nếu giảng viên sử dụng khóa học tạo lớp có thể bỏ tùy FE) tên giảng viên, avatar, tên, bio, kinh nghiệm **(7) Video preview** (có thể null) để xem trước nội dung. **Nếu đã đăng ký:** hiển thị thêm tiến độ học tập hiện tại và nút "Tiếp tục học". | `GET /api/v1/courses/{id}` | Student |
| 2.3.4 | **Đăng ký khóa học** | Học viên đăng ký tham gia khóa học bằng `course_id`. **Luồng xử lý:** **(1)** Học viên xem chi tiết khóa học và click nút "Đăng ký", **(2)** Hệ thống kiểm tra điều kiện:  đã đăng ký khóa này chưa **(3)** Nếu hợp lệ, tạo bản ghi `enrollment` mới với trạng thái "active", **(4)** Trả về thông báo thành công và chuyển hướng đến trang học tập. Ghi nhận thời gian đăng ký để tracking. | `POST /api/v1/enrollments` | Student |
| 2.3.5 | **Xem khóa học đã đăng ký** | Hiển thị danh sách tất cả khóa học mà học viên đã đăng ký. **Phân loại theo trạng thái:** **(1) Đang học** (in-progress): khóa học chưa hoàn thành, đang trong quá trình học, **(2) Đã hoàn thành** (completed): đã học xong 100%, **(3) Đã hủy** (cancelled): đã rút khỏi khóa học. **Mỗi khóa hiển thị:** tên khóa học, hình ảnh, tiến độ hoàn thành (%), ngày đăng ký, điểm trung bình các quiz, nút "Tiếp tục học" hoặc "Xem lại". Có filter và sort để dễ quản lý. | `GET /api/v1/enrollments/my-courses` | Student |
| 2.3.6 | **Hủy đăng ký khóa học** | Cho phép học viên rút khỏi khóa học chưa hoàn thành. **Cơ chế xử lý:** Cập nhật trạng thái `enrollment` từ "active" thành "cancelled", nhưng **không xóa dữ liệu học tập** (progress, quiz results) đã có để học viên có thể tham khảo sau này. Hiển thị dialog xác nhận trước khi hủy. Học viên có thể đăng ký lại khóa học này sau nếu muốn. | `DELETE /api/v1/enrollments/{id}` | Student |

---

### 2.4 NHÓM CHỨC NĂNG: HỌC TẬP & THEO DÕI TIẾN ĐỘ

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 2.4.1 | **Xem thông tin module** | Hiển thị thông tin chi tiết về một module trong khóa học: **(1) Tiêu đề và mô tả module**, **(2) Cấp độ khó** (Basic/Intermediate/Advanced), **(3) Danh sách tất cả lessons** trong module theo thứ tự, **(4) Mục tiêu học tập** (Learning Outcomes) của module, **(5) Thời lượng học ước tính**, **(6) Tài nguyên đính kèm** (PDF, slides, code samples... theo mỗi khóa học), **(7) Trạng thái hoàn thành** của từng lesson. Giao diện trực quan giúp học viên nắm được tổng quan kiến thức sẽ học. | `GET /api/v1/courses/{id}/modules/{moduleId}` | Student (enrolled) |
| 2.4.2 | **Xem nội dung bài học** | Truy cập và học nội dung của một lesson cụ thể. **Các loại nội dung:** **(1) Nội dung text/HTML** (bài giảng, giải thích lý thuyết), **(2) Video bài giảng** với player hỗ trợ tua, tốc độ phát (FE tùy biến), **(3) Tài liệu đính kèm** (PDF, Word, code files) (theo từng khóa học). **Tracking tự động:** Hệ thống ghi nhận thời gian học, phần nào đã xem, video . Tự động đánh dấu phần đã hoàn thành khi học viên xem hết. | `GET /api/v1/courses/{id}/lessons/{lessonId}` | Student (enrolled) |
| 2.4.3 | **Làm bài quiz kèm theo bài học** | Sau khi hoàn thành nội dung lý thuyết của bài học, học viên **bắt buộc phải làm bài quiz** để kiểm tra kiến thức. **Dạng câu hỏi đa dạng:** **(1) Trắc nghiệm nhiều lựa chọn** (multiple choice), **(2) Điền khuyết** (fill in the blank), **(3) Kéo thả** (drag-and-drop) để sắp xếp hoặc ghép cặp. **Câu hỏi "điểm liệt"** (mandatory questions): là những kiến thức nền tảng quan trọng nhất, **bắt buộc phải trả lời đúng** mới pass. **Điều kiện pass:** **(1)** Đạt tối thiểu 70% tổng điểm, **(2)** Trả lời đúng **tất cả** các câu điểm liệt. | `POST /api/v1/quizzes/{id}/attempt` | Student |
| 2.4.4 | **Xem kết quả và giải thích chi tiết** | Sau khi nộp bài quiz, hiển thị kết quả toàn diện: **(1) Tổng điểm đạt được** (X/100), **(2) Trạng thái** (Pass/Fail), **(3) Kết quả từng câu hỏi:** điểm số, đáp án học viên chọn, đáp án đúng, trạng thái (đúng/sai/điểm liệt). **Giải thích chi tiết cho mỗi câu:** **(a)** Tại sao đáp án này đúng, **(b)** Tại sao các đáp án khác sai. **Đặc biệt chú trọng** giải thích các câu điểm liệt để học viên hiểu rõ kiến thức cốt lõi. Có **link trực tiếp** đến các phần trong bài học để ôn lại. | `GET /api/v1/quizzes/{id}/results` | Student |
| 2.4.5 | **Làm lại quiz khi chưa đạt** | Nếu không đạt yêu cầu (dưới 70% hoặc sai câu điểm liệt), học viên **bắt buộc phải làm lại** quiz. **Cơ chế tạo bài mới:** Hệ thống AI sinh ra bộ câu hỏi **tương tự về nội dung** nhưng **khác về chi tiết** (số liệu, ví dụ, ngữ cảnh) để tránh học viên học thuộc lòng đáp án. **Số lần làm lại:** Không giới hạn, cho phép học viên cố gắng cho đến khi hiểu bài. **Tracking tiến bộ:** Mỗi lần làm lại đều ghi nhận thời gian và điểm số để phân tích sự tiến bộ của học viên(lịch sử quizz). **Điều kiện tiếp tục:** Chỉ khi **pass quiz** mới được phép học lesson tiếp theo (unlock mechanism). | `POST /api/v1/quizzes/{id}/retake` | Student |
| 2.4.6 | **Nhận bài tập luyện tập cá nhân hóa** | AI phân tích chi tiết các câu trả lời sai của học viên và tự động sinh ra **bài tập luyện tập cá nhân hóa** phù hợp. **Bài tập được tạo dựa trên:** **(1) Loại kiến thức bị thiếu** - xác định chính xác concept nào học viên chưa hiểu, **(2) Mức độ khó phù hợp** - không quá khó hoặc quá dễ so với trình độ hiện tại, **(3) Dạng bài tương tự** trong module - để củng cố kiến thức. **Nguồn câu hỏi:** AI không tạo hoàn toàn mới mà **kết hợp và chọn lọc** từ ngân hàng câu hỏi có sẵn để đảm bảo chất lượng. **Loại bài tập:** Cả lý thuyết và thực hành để học viên vừa hiểu vừa biết vận dụng. | `POST /api/v1/ai/generate-practice` | Student |
| 2.4.7 | **Đánh dấu hoàn thành bài học tự động** | Hệ thống **tự động** đánh dấu lesson là "completed" chỉ khi học viên đáp ứng **đủ 3 điều kiện** sau: **(1)** Đã xem hết nội dung bài học (100% content), **(2)** Đạt ≥70% điểm quiz, **(3)** Trả lời đúng tất cả câu hỏi điểm liệt. **Khi hoàn thành:** **(a)** Tự động mở khóa lesson tiếp theo trong module, **(b)** Cập nhật tiến độ tổng thể của module (%), **(c)** Cập nhật tiến độ tổng thể của khóa học (%), **(d)** Ghi lại timestamp (thời gian hoàn thành), **(e)** Lưu vào learning analytics để phân tích sau. **Không** cho phép đánh dấu thủ công để đảm bảo học viên thực sự hoàn thành. | `POST /api/v1/progress/complete-lesson` | Student (auto) |
| 2.4.8 | **Xem tiến độ học tập đa cấp** | Hiển thị tiến độ học tập ở nhiều cấp độ một cách trực quan và chi tiết: **(1) Tiến độ tổng thể khóa học** (X% hoàn thành) với progress bar màu sắc, **(2) Tiến độ từng module** (% hoàn thành cho mỗi module) để biết phần nào còn thiếu, **(3) Danh sách lessons:** phân loại rõ ràng đã hoàn thành (màu xanh ✓) và chưa hoàn thành (màu xám), **(4) Thời gian học ước tính còn lại** dựa trên tốc độ học hiện tại, **(5) Streak học tập** - số ngày học liên tiếp để động viên, **(6) Điểm trung bình tất cả quiz** đã làm (trên thang 100). **Giao diện:** Progress bar trực quan với màu sắc khác nhau (xanh = hoàn thành, vàng = đang học, xám = chưa bắt đầu) để dễ theo dõi. | `GET /api/v1/progress/course/{courseId}` | Student |

---

**📚 GHI CHÚ CHI TIẾT VỀ CẤU TRÚC MODULE & LEARNING PATH**

Mỗi Module trong khóa học được thiết kế với cấu trúc hoàn chỉnh và logic để đảm bảo học viên có lộ trình học tập rõ ràng:

| **Thành phần** | **Mô tả chi tiết** |
|----------------|-------------------|
| **Thông tin Module** | **(1) Tiêu đề và mô tả** rõ ràng về nội dung module<br>**(2) Cấp độ khó:** Basic (cơ bản) → Intermediate (trung cấp) → Advanced (nâng cao)<br>**(3) Thứ tự logic** trong khóa học (Module 1, 2, 3...)<br>**(4) Prerequisites:** Các module tiên quyết cần hoàn thành trước (nếu có) |
| **Mục tiêu học tập** (Learning Outcomes) | Liệt kê cụ thể và **đo lường được** những gì học viên sẽ đạt được sau khi hoàn thành module.<br>**Ví dụ:**<br>- "Có thể viết được function Python xử lý exception"<br>- "Hiểu được các khái niệm OOP cơ bản: class, object, inheritance"<br>- "Biết cách debug code Python hiệu quả" |
| **Kiến thức chi tiết cần đạt** | **Breakdown** (phân tích chi tiết) từng concept, skill, hoặc khái niệm cụ thể cần nắm vững:<br>- Có **mapping rõ ràng** đến các lesson và quiz tương ứng<br>- Mỗi kiến thức có **skill tag** để dễ tracking và đánh giá (ví dụ: "python-functions", "error-handling")<br>- Phân loại theo độ quan trọng: bắt buộc (mandatory) hoặc tùy chọn (optional) |
| **Tài nguyên học tập** | **(1) Tài nguyên lý thuyết:** Bài đọc, slide PowerPoint, documentation chính thức<br>**(2) Tài nguyên thực hành:** Code examples mẫu, sandbox environment để code trực tiếp, simulators/tools tương tác<br>**(3) Tài nguyên tham khảo:** External links (StackOverflow, GitHub), sách giáo khoa, video tutorials bổ sung từ YouTube, blog posts liên quan |
| **Bài kiểm tra mặc định** (Assessment) | Bộ câu hỏi chuẩn để kiểm tra đầu ra của module:<br>- **Quiz kiến thức nền tảng:** trắc nghiệm về lý thuyết cốt lõi<br>- **Mini-test thực hành:** bài tập viết code, debug, hoặc giải quyết vấn đề<br>- **Project nhỏ:** bài tập tổng hợp (nếu có)<br>Có phân loại theo độ khó (Easy/Medium/Hard) và trọng số điểm |
| **Thời lượng học** | **(1) Thời gian tối thiểu:** ước tính thời gian ngắn nhất cần thiết để hoàn thành module<br>**(2) Thời gian tối đa khuyến nghị:** để tránh kéo dài quá lâu<br>**(3) Cơ sở ước tính:** dựa trên độ phức tạp nội dung và thống kê thời gian học thực tế của học viên trước đó |
| **Ngưỡng điểm Pass** | Điểm tối thiểu cần đạt để được coi là hoàn thành module:<br>- **Mặc định:** 70% tổng điểm<br>- **Có thể điều chỉnh:** Ví dụ module nền tảng quan trọng có thể yêu cầu 80%<br>- **Điều kiện bổ sung:** Phải trả lời đúng tất cả câu hỏi điểm liệt |
| **Kiến thức bắt buộc** ("Điểm liệt") | Các câu hỏi hoặc concept **"điểm liệt"** - những kiến thức nền tảng **bắt buộc phải nắm vững**:<br>- Nếu không nắm vững sẽ **không thể pass module** dù tổng điểm cao<br>- Thường là những kiến thức nền tảng quan trọng cho các module tiếp theo<br>- Được đánh dấu rõ ràng trong quiz để học viên biết |

**🔗 API Endpoints cho quản lý Module:**

- `GET /api/v1/courses/{courseId}/modules` - Lấy danh sách tất cả modules trong khóa học
- `GET /api/v1/modules/{moduleId}/outcomes` - Lấy chi tiết learning outcomes của module
- `GET /api/v1/modules/{moduleId}/resources` - Lấy tất cả tài nguyên học tập của module
- `POST /api/v1/modules/{moduleId}/assessments/generate` - Sinh quiz đánh giá tự động cho module
- `GET /api/v1/progress/module/{moduleId}` - Xem tiến độ hoàn thành module của học viên

---

### 2.5 NHÓM CHỨC NĂNG: KHÓA HỌC CÁ NHÂN (PERSONAL COURSE)

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 2.5.1 | **Tạo khóa học từ AI Prompt** | Học viên chỉ cần nhập **mô tả bằng ngôn ngữ tự nhiên** về chủ đề và mục tiêu học tập, AI sẽ tự động tạo khóa học hoàn chỉnh. **Ví dụ prompt:** "Tôi muốn học lập trình Python cơ bản cho người mới bắt đầu, tập trung vào xử lý dữ liệu". **AI sẽ sinh ra:** **(1) Danh sách modules** (ở đây AI sẽ trả về json, FE tự tạo khung mẫu để hiển thị ra )được sắp xếp theo thứ tự logic từ cơ bản đến nâng cao, **(2) Các lessons** trong mỗi module với nội dung cụ thể, **(3) Learning outcomes** cho từng module, **(4) Nội dung cơ bản** cho mỗi lesson. **Luồng xử lý:** Hiển thị form nhập prompt → Gửi request → AI xử lý (3-5 giây) → Trả về cấu trúc khóa học đầy đủ → Hiển thị preview để học viên xem trước → Học viên xác nhận tạo hoặc yêu cầu AI điều chỉnh lại. | `POST /api/v1/courses/from-prompt` | Student |
| 2.5.2 | **Tạo khóa học thủ công** | Tạo khóa học **từ đầu** với thông tin cơ bản do học viên tự nhập và tổ chức nội dung. **Bước 1:** Nhập thông tin cơ bản: tên khóa học, mô tả ngắn, danh mục (Programming, Math...), cấp độ. **Bước 2:** Hệ thống tạo khóa học trống với trạng thái "draft". **Bước 3:** Trả về `course_id` và chuyển đến trang quản lý để học viên tự thêm modules, lessons, và nội dung. **Lợi ích:** Kiểm soát hoàn toàn nội dung và cấu trúc khóa học theo ý muốn. Phù hợp cho người có kinh nghiệm hoặc muốn tạo khóa học độc đáo. | `POST /api/v1/courses/personal` | Student |
| 2.5.3 | **Xem danh sách khóa học cá nhân** | Hiển thị tất cả khóa học do chính học viên tạo (từ AI hoặc thủ công). **Thông tin hiển thị:** **(1) Tên khóa học và hình ảnh**, **(2) Trạng thái:**"published" (đã hoàn thành), **(3) Thống kê:** số modules/lessons đã tạo, **(4) Ngày tạo** **Tính năng:** **(a)** Filter theo trạng thái (draft/published), **(b)** Tìm kiếm theo tên, **(c)** Mỗi item có các action: Xem chi tiết, Xóa. | `GET /api/v1/courses/my-personal` | Student |
| 2.5.4 | **Chỉnh sửa khóa học cá nhân** | Cho phép sửa đổi **mọi thành phần** của khóa học cá nhân: **(1) Thay đổi tiêu đề, mô tả, hình ảnh khóa học**, **(2) Thêm/xóa/sắp xếp lại modules**, **(3) Thêm/xóa/chỉnh sửa nội dung lessons**, **(4) Cập nhật learning outcomes**, **(5) Thêm/xóa tài nguyên đính kèm**. **Giao diện:** Cung cấp **drag-and-drop** để sắp xếp modules/lessons dễ dàng. **Auto-save:** Mọi thay đổi được tự động lưu sau 2-3 giây hoặc khi người dùng rời khỏi trường đang chỉnh sửa để tránh mất dữ liệu. | `PUT /api/v1/courses/personal/{id}` | Student (owner) |
| 2.5.5 | **Xóa khóa học cá nhân** | Xóa vĩnh viễn khóa học đã tạo. **Điều kiện:** Chỉ cho phép xóa khóa học **do chính học viên đó tạo** (owner). **Cảnh báo:** Hiển thị dialog xác nhận rõ ràng về việc: **(1)** Xóa không thể khôi phục, **(2)** Tất cả nội dung, modules, lessons sẽ bị xóa, **Kiểm tra:** Backend kiểm tra ownership (quyền sở hữu) trước khi cho phép xóa. | `DELETE /api/v1/courses/personal/{id}` | Student (owner) |

---

### 2.6 NHÓM CHỨC NĂNG: TƯƠNG TÁC VỚI AI CHATBOT

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 2.6.1 | **Chat hỏi đáp về khóa học** | Học viên có thể **hỏi bất cứ điều gì** liên quan đến nội dung khóa học đang học, AI sẽ trả lời dựa trên context (ngữ cảnh) của khóa học đó. **AI có context của:** **(1) Tên và mô tả khóa học**, **(2) Nội dung tất cả modules và lessons**, **(3) Learning outcomes**, **(4) Tài nguyên đính kèm**. **Ví dụ câu hỏi:** "Exception trong Python là gì?", "Cho ví dụ về list comprehension", "Bài tập lesson 3 làm thế nào?". **Luồng xử lý:** Hiển thị chat box trong trang khóa học → Học viên gõ câu hỏi → Gửi request kèm `courseId` và `question` → Backend lấy context khóa học + câu hỏi gửi đến AI (Google Gemini) → AI phân tích và trả lời → Hiển thị câu trả lời real-time với format đẹp (markdown, code highlight). | `POST /api/v1/chat/course/{courseId}` | Student (enrolled) |
| 2.6.2 | **Xem lịch sử hội thoại** | Hiển thị danh sách tất cả các cuộc hội thoại (conversations) đã có với AI. **Nhóm theo:** **(1) Ngày** (hôm nay, hôm qua, tuần này...), **(2) Chủ đề/khóa học** đã chat. **Mỗi conversation hiển thị:** **(a) Thời gian bắt đầu** **(b) Chủ đề chính** (được AI tóm tắt) **Tính năng:** Học viên có thể click vào để **xem lại toàn bộ nội dung** conversation và **tiếp tục hỏi đáp** từ đó (giữ nguyên context). Hữu ích để ôn lại kiến thức đã hỏi trước đó. | `GET /api/v1/chat/history` | Student |
| 2.6.3 | **Xóa lịch sử chat** | Cho phép xóa lịch sử hội thoại để giữ gọn gàng hoặc bảo mật thông tin. **Xóa từng conversation:** Click icon xóa trên mỗi conversation riêng lẻ. **Xóa hàng loạt:** Hiển thị checkbox để chọn nhiều conversations và xóa cùng lúc. **Xóa tất cả:** Option "Xóa tất cả lịch sử" với dialog xác nhận nghiêm ngặt (yêu cầu nhập mật khẩu hoặc confirmation text). **Cảnh báo:** Dữ liệu đã xóa **không thể khôi phục** được. | `DELETE /api/v1/chat/history/{id}` | Student |

---

### 2.7 NHÓM CHỨC NĂNG: DASHBOARD & PHÂN TÍCH HỌC TẬP

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 2.7.1 | **Dashboard tổng quan học viên** | Trang chủ (home) hiển thị thông tin quan trọng nhất để học viên nắm bắt nhanh tình hình học tập. **Các widget hiển thị:** **(1) Khóa học đang học:** danh sách 3-5 khóa đang học gần đây nhất với progress bar (%) cho mỗi khóa, **(2) Quiz cần làm:** các bài quiz đến hạn hoặc chưa hoàn thành **Giao diện:** Layout responsive với các widget có thể **tùy chỉnh vị trí** (drag-and-drop) theo sở thích. | `GET /api/v1/dashboard/student` | Student |
| 2.7.2 | **Thống kê học tập chi tiết** | Hiển thị metrics (chỉ số) học tập đầy đủ để học viên theo dõi tiến bộ. **Các chỉ số hiển thị:** **(2) Số bài học đã hoàn thành:** breakdown theo khóa học, **(3) Số quiz đã pass:** tỷ lệ pass/fail, **(4) Điểm trung bình tất cả quiz:** trên thang 100, có thể filter theo khóa học hoặc thời gian, **(5) Số khóa học đã hoàn thành** vs đang học vs đã hủy. **Visualization:** Sử dụng **charts** (biểu đồ) và **progress rings** (vòng tròn tiến độ) để visualize data một cách trực quan, dễ hiểu và đẹp mắt. | `GET /api/v1/analytics/learning-stats` | Student |
| 2.7.3 | **Biểu đồ tiến độ theo thời gian** | Hiển thị biểu đồ (chart) thể hiện tiến độ học tập qua các mốc thời gian. **Loại biểu đồ:** **(1) Line chart** (đường) để thấy xu hướng, **(2) Bar chart** (cột) để so sánh theo ngày/tuần. **Trục Y:** Số bài hoàn thành hoặc số giờ học. **Trục X:** Thời gian (ngày, tuần, tháng). **Tính năng:** **(a) Chọn view:** theo ngày (7 ngày gần nhất), tuần (4 tuần), tháng (6 tháng), **(b) Filter:** theo từng khóa học cụ thể hoặc tất cả khóa học. **Thư viện:** Sử dụng Chart.js hoặc D3.js để render với animation mượt mà và interactive (hover để xem chi tiết). **Ý nghĩa:** Giúp học viên thấy được sự tiến bộ và duy trì động lực. | `GET /api/v1/analytics/progress-chart` | Student |
| 2.7.4 | **Đề xuất khóa học thông minh bằng AI** | AI phân tích toàn bộ dữ liệu học tập để đề xuất khóa học phù hợp nhất. **AI phân tích:** **(1) Lịch sử học tập:** các khóa đã học, đang học, đã hoàn thành, **(2) Sở thích:** danh mục/chủ đề đã khai báo hoặc học nhiều, **(3) Performance:** kết quả các bài assessment, điểm quiz, **(4) Skill gaps:** lỗ hổng kiến thức cần bổ sung **Kết quả:** Hiển thị danh sách 5-10 khóa học được recommend theo thứ tự ưu tiên. **Mỗi khóa kèm lý do:** ví dụ "Dựa trên kết quả assessment Python của bạn, khóa này sẽ giúp bạn nâng cao kỹ năng", "Phù hợp với sở thích AI/ML bạn đã chọn", "Nhiều học viên tương tự đã học khóa này". **Cập nhật:** Recommendation được cập nhật định kỳ dựa trên tiến độ mới. | `GET /api/v1/recommendations` | Student |

---


## 3. CHỨC NĂNG CHO GIẢNG VIÊN (INSTRUCTOR)

### 3.1 NHÓM CHỨC NĂNG: QUẢN LÝ LỚP HỌC

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 3.1.1 | **Tạo lớp học mới** | Giảng viên chọn một khóa học công khai có sẵn trong hệ thống làm nền tảng, sau đó tạo lớp học. **Thông tin cần nhập:** **(1) Tên lớp học**, **(2) Mô tả lớp học**, **(3) Thời gian bắt đầu và kết thúc**, **(4) Số lượng học viên tối đa**. **Luồng xử lý:** Hiển thị danh sách khóa học có thể chọn → Giảng viên chọn khóa học → Điền thông tin lớp → Preview cấu trúc lớp → Xác nhận tạo → Hệ thống tạo lớp với trạng thái "preparing" → Trả về `class_id` và **mã mời** (6-8 ký tự) để học viên có thể join vào lớp. **Ghi chú:** Mỗi lớp học có một mã mời duy nhất, học viên nhập mã này vào ô "Tham gia lớp học" để đăng ký. | `POST /api/v1/classes` | Instructor |
| 3.1.2 | **Xem danh sách lớp học** | Hiển thị tất cả lớp học do giảng viên đang quản lý. **Thông tin hiển thị:** **(1) Tên lớp học**, **(2) Khóa học gốc** (khóa học được sử dụng làm nền tảng), **(3) Số học viên:** hiện tại/tối đa (ví dụ: 25/30), **(4) Trạng thái:** preparing (đang chuẩn bị), active (đang hoạt động), completed (đã kết thúc), **(5) Thời gian:** ngày bắt đầu và kết thúc, **(6) Tiến độ chung** của lớp (%). **Tính năng:** Hỗ trợ filter theo trạng thái và sắp xếp theo thời gian tạo hoặc số học viên. | `GET /api/v1/classes/my-classes` | Instructor |
| 3.1.3 | **Xem chi tiết lớp học** | Hiển thị thông tin đầy đủ của một lớp học cụ thể. **Bao gồm:** **(1) Thông tin cơ bản:** tên lớp, mô tả, mã mời, thời gian, số học viên, **(2) Danh sách học viên:** hiển thị avatar, tên, email, tiến độ cá nhân (%) của từng học viên, **(3) Thống kê tổng quan:** số bài học đã hoàn thành, điểm trung bình lớp, tỷ lệ hoàn thành các module. Giúp giảng viên nắm được tình hình học tập của cả lớp. | `GET /api/v1/classes/{id}` | Instructor (owner) |
| 3.1.4 | **Chỉnh sửa thông tin lớp** | Cho phép giảng viên sửa đổi thông tin lớp học. **Có thể chỉnh sửa:** **(1) Tên lớp**, **(2) Mô tả**, **(3) Thời gian bắt đầu/kết thúc** (chỉ khi lớp chưa bắt đầu), **(4) Số lượng học viên tối đa**, **(5) Trạng thái lớp:** active, paused (tạm dừng), completed. **Ràng buộc validation:** Không được giảm thời gian khi lớp đã bắt đầu, không được giảm số lượng học viên tối đa xuống dưới số học viên hiện tại. Frontend cần validate trước khi submit. | `PUT /api/v1/classes/{id}` | Instructor (owner) |
| 3.1.5 | **Xóa lớp học** | Xóa vĩnh viễn lớp học khỏi hệ thống. **Điều kiện xóa:** Chỉ được phép xóa khi **(1)** Lớp chưa có học viên nào, HOẶC **(2)** Lớp đã kết thúc (completed). **Cảnh báo:** Hiển thị dialog xác nhận với danh sách những gì sẽ bị xóa vĩnh viễn: dữ liệu học viên, tiến độ học tập, kết quả quiz. **Ghi chú:** Không thể khôi phục sau khi xóa. | `DELETE /api/v1/classes/{id}` | Instructor (owner) |

---

### 3.2 NHÓM CHỨC NĂNG: QUẢN LÝ HỌC VIÊN TRONG LỚP

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 3.2.1 | **Tạo mã mời học viên** | Tạo mã mời để học viên tham gia lớp học. **Hệ thống tạo:** **(1) Mã code đơn giản** 6-8 ký tự (ví dụ: ABC123XY). Học viên sử dụng mã mời tham gia lớp. **Ghi chú:** Mỗi lớp có 1 mã mời, không thể tạo thêm mã khác. | `POST /api/v1/classes/{id}/invite` | Instructor (owner) |
| 3.2.2 | **Xem danh sách học viên** | Hiển thị tất cả học viên đang tham gia lớp học dạng bảng (table). **Thông tin hiển thị:** **(1) Avatar và tên học viên**, **(2) Email**, **(3) Ngày tham gia lớp**, **(4) Tiến độ hoàn thành** (%), **(5) Điểm trung bình quiz**. **Tính năng:** Hỗ trợ search theo tên, filter theo tiến độ hoặc trạng thái, sort (sắp xếp) theo các cột khác nhau. | `GET /api/v1/classes/{id}/students` | Instructor (owner) |
| 3.2.3 | **Xem hồ sơ học viên chi tiết** | Xem thông tin chi tiết của một học viên cụ thể trong lớp. **Hiển thị:** **(1) Thông tin cá nhân:** profile cơ bản (tên, email, avatar), **(2) Chi tiết điểm số:** kết quả từng bài quiz đã làm với điểm số và thời gian, **(3) Tiến độ học tập:** danh sách bài học đã hoàn thành và chưa hoàn thành, **(4) Thống kê:**  số bài đã pass/fail. Giúp giảng viên hiểu rõ tình hình của từng học viên để hỗ trợ kịp thời. | `GET /api/v1/classes/{id}/students/{studentId}` | Instructor (owner) |
| 3.2.4 | **Xóa học viên khỏi lớp** | Loại bỏ học viên ra khỏi lớp học. **Cơ chế:** **(1)** Giảng viên chọn học viên cần xóa, **(2)** Xác nhận , **(3)** Hệ thống cập nhật trạng thái enrollment thành "removed". **Ghi chú quan trọng:** Dữ liệu tiến độ học tập (progress) của học viên **vẫn được giữ lại** để có thể tham khảo sau hoặc add lại vào lớp. Học viên bị xóa sẽ không thể truy cập nội dung lớp nhưng vẫn có thể xem lại tiến độ cũ. | `DELETE /api/v1/classes/{id}/students/{studentId}` | Instructor (owner) |
| 3.2.5 | **Xem tiến độ tổng thể của lớp** | Dashboard hiển thị tiến độ học tập của toàn bộ lớp học một cách trực quan. **Hiển thị dưới dạng:** **(1) Biểu đồ phân bố điểm số** của lớp (histogram), **(2) Số học viên đã hoàn thành từng module** (bar chart), **(3) Lessons được hoàn thành nhiều nhất/ít nhất** | `GET /api/v1/classes/{id}/progress` | Instructor (owner) |

---

### 3.3 NHÓM CHỨC NĂNG: QUẢN LÝ QUIZ & BÀI TẬP

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 3.3.1 | **Tạo quiz tùy chỉnh** | Giảng viên tự tạo bài quiz riêng cho lớp học của mình. **Giao diện:** Sử dụng drag-and-drop để thêm câu hỏi. **Các dạng câu hỏi:** **(1) Trắc nghiệm nhiều lựa chọn**, **(2) Điền khuyết**, **(3) Đúng/Sai**. **Cấu hình:** **(a) Thời gian làm bài** (phút), **(b) Số lần được làm lại**, **(c) Điểm pass tối thiểu** (%), **(d) Thời hạn nộp bài**. **Tính năng:** Preview quiz trước khi publish để kiểm tra giao diện và logic câu hỏi. | `POST /api/v1/quizzes` | Instructor |
| 3.3.2 | **Xem danh sách quiz đã tạo** | Hiển thị tất cả quiz mà giảng viên đã tạo cho các lớp học. **Thông tin hiển thị:** **(1) Tên quiz**, **(2) Lớp học áp dụng**, **(3) Số câu hỏi**, **(4) Thời gian làm bài**, **(5) Số học viên đã làm/tổng số**, **(6) Tỷ lệ pass** (%), **(7) Ngày tạo**. **Tính năng:** Filter theo lớp học, trạng thái (draft/published) và search theo tên quiz. | `GET /api/v1/quizzes/my-quizzes` | Instructor |
| 3.3.3 | **Chỉnh sửa quiz** | Sửa đổi mọi thành phần của quiz đã tạo. **Có thể chỉnh sửa:** **(1) Thêm/xóa/sửa câu hỏi**, **(2) Thay đổi thời gian và điều kiện**, **(3) Cập nhật hướng dẫn**. **Cảnh báo quan trọng:** Nếu đã có học viên làm bài, frontend sẽ hiển thị cảnh báo và đề xuất **tạo phiên bản mới** thay vì sửa trực tiếp quiz cũ để tránh ảnh hưởng đến kết quả đã có. | `PUT /api/v1/quizzes/{id}` | Instructor (owner) |
| 3.3.4 | **Xóa quiz** | Xóa vĩnh viễn quiz khỏi hệ thống. **Điều kiện xóa:** Chỉ được phép xóa khi **(1)** Chưa có học viên nào làm bài,  **Cảnh báo:** Frontend hiển thị số lượng học viên đã làm bài và xác nhận có chắc chắn muốn xóa. Dữ liệu không thể khôi phục sau khi xóa. | `DELETE /api/v1/quizzes/{id}` | Instructor (owner) |
| 3.3.5 | **Phân tích kết quả quiz của lớp** | Dashboard chi tiết phân tích kết quả quiz của toàn lớp học. **Hiển thị:** **(1) Histogram phân bổ điểm** (xem phân bố điểm của học viên), **(2) Bảng ranking học viên** (xếp hạng theo điểm), Giúp giảng viên đánh giá độ khó của quiz và hiệu quả học tập của lớp. | `GET /api/v1/quizzes/{id}/class-results` | Instructor (owner) |

---

### 3.4 NHÓM CHỨC NĂNG: DASHBOARD GIẢNG VIÊN

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 3.4.1 | **Dashboard tổng quan** | Trang chủ dành cho giảng viên hiển thị các thông tin quan trọng nhất. **Các widget hiển thị:** **(1) Số lớp đang quản lý** (active classes), **(2) Tổng số học viên** across (trên tất cả) các lớp, **(3) Thống kê nhanh:** quiz đã tạo, tỷ lệ hoàn thành trung bình, **(4) Quick actions:** nút tạo lớp mới, tạo quiz, xem báo cáo chi tiết. **Layout:** Giao diện gọn gàng, responsive, dễ nhìn và thao tác nhanh. | `GET /api/v1/dashboard/instructor` | Instructor |

---

## 4. CHỨC NĂNG CHO QUẢN TRỊ VIÊN (ADMIN)

### 4.1 NHÓM CHỨC NĂNG: QUẢN LÝ NGƯỜI DÙNG

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 4.1.1 | **Xem danh sách người dùng** | Hiển thị tất cả người dùng trong hệ thống dạng bảng (table). **Thông tin hiển thị:** **(1) Avatar**, **(2) Tên đầy đủ**, **(3) Email**, **(4) Vai trò** (Student/Instructor/Admin), **(5) Trạng thái** tài khoản (active/inactive), **(6) Ngày tạo**. **Tính năng nâng cao:** **(a) Filter:** theo vai trò, trạng thái, ngày tạo, **(b) Search:** theo tên hoặc email với autocomplete (gợi ý tự động), **(c) Sort:** sắp xếp theo các cột. | `GET /api/v1/admin/users` | Admin |
| 4.1.2 | **Xem hồ sơ người dùng chi tiết** | Xem thông tin đầy đủ của một người dùng cụ thể. **Hiển thị:** **(1) Thông tin cá nhân:** tên, email, avatar, bio **() Thống kê:** số khóa học đã học (Student), số lớp đang dạy (Instructor), điểm trung bình, **(4) Khóa học/lớp đang tham gia**. Admin có cái nhìn tổng quan để quản lý và hỗ trợ người dùng. | `GET /api/v1/admin/users/{id}` | Admin |
| 4.1.3 | **Tạo tài khoản người dùng** | Admin tạo trực tiếp tài khoản cho người dùng mới. **Thông tin cần nhập:** **(1) Tên đầy đủ**, **(2) Email**, **(3) Vai trò** (chọn Student/Instructor/Admin), | `POST /api/v1/admin/users` | Admin |
| 4.1.4 | **Cập nhật thông tin người dùng** | Chỉnh sửa thông tin của bất kỳ người dùng nào. **Có thể chỉnh sửa:** **(1) Tên đầy đủ**, **(2) Email**, **(3) Vai trò** (nâng cấp/hạ cấp). **Validation:** Frontend validate email không trùng lặp trong hệ thống và hiển thị preview (xem trước) thay đổi trước khi submit để tránh nhầm lẫn. | `PUT /api/v1/admin/users/{id}` | Admin |
| 4.1.5 | **Xóa người dùng** | Xóa vĩnh viễn tài khoản người dùng khỏi hệ thống. **Yêu cầu xác nhận nghiêm ngặt:** Hiển thị dialog cảnh báo rõ ràng. **Kiểm tra trước khi xóa:** Hệ thống kiểm tra dependencies (phụ thuộc): **(1)** Instructor: có đang dạy lớp nào không, **(2)** Student: có đang học khóa nào không, **(3)** Có khóa học cá nhân nào đã tạo không. Đưa ra cảnh báo chi tiết về những gì sẽ bị ảnh hưởng. **Ghi chú:** Xóa không thể khôi phục. | `DELETE /api/v1/admin/users/{id}` | Admin |
| 4.1.6 | **Thay đổi vai trò người dùng** | Nâng cấp hoặc hạ cấp vai trò của người dùng. **Các thay đổi có thể:** Student ↔ Instructor ↔ Admin. **Luồng xử lý:** **(1)** Admin chọn vai trò mới, **(2)** Frontend hiển thị dialog xác nhận với mô tả chi tiết quyền hạn của vai trò mới, **(3)** Hệ thống kiểm tra impact (ảnh hưởng) - ví dụ: hạ Instructor xuống Student sẽ ảnh hưởng đến những lớp học nào, **(4)** Yêu cầu xác nhận cuối cùng. | `PUT /api/v1/admin/users/{id}/role` | Admin |
| 4.1.7 | **Reset mật khẩu người dùng** | Force reset (đặt lại bắt buộc) mật khẩu cho người dùng. **Trường hợp sử dụng:** **(1)** Người dùng quên mật khẩu| `POST /api/v1/admin/users/{id}/reset-password` | Admin |

---

### 4.2 NHÓM CHỨC NĂNG: QUẢN LÝ KHÓA HỌC

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 4.2.1 | **Xem tất cả khóa học** | Hiển thị danh sách toàn bộ khóa học trong hệ thống (cả public và personal). **Thông tin hiển thị:** **(1) Tên khóa học**, **(2) Tác giả** (người tạo), **(3) Loại:** public (công khai) hoặc personal (cá nhân), **(4) Số lượt đăng ký** (enrollments), **(5) Trạng thái:** draft/published, **(6) Ngày tạo**. **Tính năng:** Filter theo tác giả, trạng thái, danh mục và search theo tên khóa học. | `GET /api/v1/admin/courses` | Admin |
| 4.2.2 | **Xem chi tiết khóa học** | Xem thông tin đầy đủ của một khóa học cụ thể. **Hiển thị:** **(1) Metadata:** tên, mô tả, ảnh đại diện, cấp độ, **(2) Cấu trúc chi tiết:** tất cả modules và lessons, nội dung từng phần, **(3) Analytics:**  số lượt đăng ký (enrollments), tỷ lệ hoàn thành. **Tính năng đặc biệt:** Admin có thể **preview khóa học** như một student để kiểm tra chất lượng nội dung và giao diện học tập. | `GET /api/v1/admin/courses/{id}` | Admin |
| 4.2.3 | **Tạo khóa học chính thức** | Admin tạo khóa học chính thức của hệ thống (khóa học public). **Quyền hạn đầy đủ:** **(1) Thiết kế cấu trúc** modules và lessons, **(2) Thêm nội dung:** rich text (text định dạng), hình ảnh, video, media khác, **(3) Cấu hình quiz:** tạo bài kiểm tra cho từng lesson, **(4) Đặt prerequisites:** yêu cầu kiến thức đầu vào, **(5) Publish:** công khai để mọi người đăng ký. | `POST /api/v1/admin/courses` | Admin |
| 4.2.4 | **Chỉnh sửa bất kỳ khóa học nào** | Admin có quyền chỉnh sửa toàn bộ nội dung của **bất kỳ khóa học nào**, kể cả personal courses (khóa học cá nhân) của user. **Có thể thực hiện:** **(1) Sửa nội dung** bài học, **(2) Thêm/xóa modules**, **(3) Điều chỉnh cấu trúc** khóa học, **(4) Update metadata** (tên, mô tả, ảnh), **(5) Kiểm duyệt** và đảm bảo chất lượng nội dung. | `PUT /api/v1/admin/courses/{id}` | Admin |
| 4.2.5 | **Xóa khóa học** | Xóa vĩnh viễn khóa học khỏi hệ thống. **Kiểm tra trước khi xóa:** **(1) Số học viên đang học** khóa này, **(2) Số lớp học đang sử dụng** khóa học này làm nền tảng. **Cảnh báo:** Frontend hiển thị **impact analysis** (phân tích ảnh hưởng) chi tiết về những gì sẽ bị ảnh hưởng và yêu cầu xác nhận nghiêm ngặt. Xóa không thể khôi phục. | `DELETE /api/v1/admin/courses/{id}` | Admin |

---

### 4.3 NHÓM CHỨC NĂNG: GIÁM SÁT LỚP HỌC

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 4.3.1 | **Xem tất cả lớp học** | Hiển thị danh sách toàn bộ lớp học từ mọi giảng viên trong hệ thống. **Thông tin hiển thị:** **(1) Tên lớp học**, **(2) Giảng viên** (người tạo/quản lý lớp), **(3) Khóa học gốc** (khóa học được sử dụng làm nền tảng), **(4) Số học viên** hiện tại, **(5) Trạng thái:** preparing/active/completed, **(6) Thời gian:** bắt đầu và kết thúc. **Mục đích:** Giám sát hoạt động của tất cả lớp học trong hệ thống. | `GET /api/v1/admin/classes` | Admin |
| 4.3.2 | **Xem chi tiết lớp học** | Xem thông tin đầy đủ của bất kỳ lớp học nào (kể cả lớp của instructor khác). **Hiển thị:** **(1) Thông tin giảng viên:** tên, email **(2) Danh sách học viên:** tất cả học viên trong lớp với tiến độ của từng người, **(3) Thống kê:** tiến độ chung, điểm trung bình, tỷ lệ hoàn thành. **Mục đích:** Giám sát chất lượng giảng dạy và hỗ trợ khi cần thiết. | `GET /api/v1/admin/classes/{id}` | Admin |

---

### 4.4 NHÓM CHỨC NĂNG: DASHBOARD QUẢN TRỊ

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 4.4.1 | **Dashboard tổng quan hệ thống** | Trang chủ admin hiển thị các chỉ số quan trọng nhất của toàn hệ thống. **Các metrics hiển thị:** **(1) Tổng số người dùng:** breakdown (phân tách) theo vai trò (X Students, Y Instructors, Z Admins), **(2) Số khóa học:** public vs personal, tỷ lệ published vs draft, **(3) Số lớp học:** đang active (hoạt động) vs completed (đã kết thúc), **(4) Thống kê hoạt động:** ,**(5) Biểu đồ trực quan:** line chart hoặc bar chart thể hiện xu hướng. **Mục đích:** Giúp admin nắm bắt tình hình tổng thể và đưa ra quyết định quản lý. | `GET /api/v1/admin/dashboard` | Admin |

---

## 5. CHỨC NĂNG CHUNG (COMMON)

### 5.1 NHÓM CHỨC NĂNG: TÌM KIẾM & LỌC

| STT | Chức năng | Mô tả chi tiết | API Endpoint | Quyền truy cập |
|-----|-----------|----------------|--------------|----------------|
| 5.1.1 | **Tìm kiếm thông minh** | Universal search box (ô tìm kiếm toàn hệ thống) cho phép tìm kiếm nhiều loại đối tượng qua một ô duy nhất. **Có thể tìm:** **(1) Khóa học** (courses), **(2) Người dùng** (users - nếu có quyền), **(3) Lớp học** (classes), **(4) Modules**, **(5) Lessons**. **Tính năng nâng cao:** **(a) Full-text search:** tìm theo nội dung đầy đủ, **(b) Search suggestions:** gợi ý khi đang gõ, **(c) Typo tolerance:** cho phép sai chính tả, **(d) Search history:** lưu lịch sử tìm kiếm. **Kết quả:** Được nhóm theo category (danh mục) với điểm relevant score (độ liên quan). Frontend hiển thị kết quả **real-time** khi user đang typing. | `GET /api/v1/search` | All roles |
| 5.1.2 | **Bộ lọc nâng cao** | Advanced filtering system (hệ thống lọc nâng cao) dành cho khóa học. **Có thể lọc theo:** **(1) Category/Subcategory:** danh mục và danh mục con (Programming → Python → Web Development), **(2) Level:** Beginner/Intermediate/Advanced, **(3) Instructor:** theo giảng viên cụ thể. **Giao diện:** Frontend sử dụng **sidebar filters** với count (số lượng) cho mỗi option và nút **"Clear all"** để xóa tất cả filter. **Mục đích:** Giúp người dùng tìm khóa học phù hợp nhanh chóng. | `GET /api/v1/search/filter` | All roles |

---
