use onlinelearning;

DROP TABLE IF EXISTS Lectures;
DROP TABLE IF EXISTS Enrollments;
DROP TABLE IF EXISTS Courses;
DROP TABLE IF EXISTS Learners;
DROP TABLE IF EXISTS Instructors;

CREATE TABLE Learners
(
  LearnerID INT AUTO_INCREMENT NOT NULL,
  LearnerName VARCHAR(50) NOT NULL,
  Email VARCHAR(50) NOT NULL,
  PhoneNumber VARCHAR(15) NOT NULL,
  PRIMARY KEY (LearnerID)
);

CREATE TABLE Instructors
(
  InstructorID INT AUTO_INCREMENT NOT NULL,
  InstructorName VARCHAR(50) NOT NULL,
  Expertise VARCHAR(100) NOT NULL,
  Email VARCHAR(50) NOT NULL,
  PRIMARY KEY (InstructorID)
);

CREATE TABLE Courses
(
  CourseID INT AUTO_INCREMENT NOT NULL,
  CourseName VARCHAR(100) NOT NULL,
  Descriptions TEXT NOT NULL,
  InstructorID INT NULL,
  PRIMARY KEY (CourseID),
  FOREIGN KEY (InstructorID) REFERENCES Instructors(InstructorID)
);

CREATE TABLE Lectures
(
  LectureID INT AUTO_INCREMENT NOT NULL,
  Title VARCHAR(50) NOT NULL,
  Content TEXT NOT NULL,
  CourseID INT NOT NULL,
  PRIMARY KEY (LectureID),
  FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
);

CREATE TABLE Enrollments
(
  EnrollmentID INT AUTO_INCREMENT NOT NULL,   -- Duy trì AUTO_INCREMENT cho EnrollmentID
  EnrollmentDate DATE NOT NULL,
  LearnerID INT NOT NULL,
  CourseID INT NOT NULL,
  PRIMARY KEY (EnrollmentID),  -- EnrollmentID là khóa chính
  UNIQUE (LearnerID, CourseID),  -- Composite key như khóa phụ
  FOREIGN KEY (LearnerID) REFERENCES Learners(LearnerID),
  FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
);


INSERT INTO Learners (LearnerName, Email, PhoneNumber)
VALUES
('Lê Thị A', 'letha@edu.com', '0901234567'),
('Trần Văn B', 'tranb@edu.com', '0902345678'),
('Nguyễn Minh C', 'nguyenc@edu.com', '0903456789'),
('Phạm Thị D', 'phamd@edu.com', '0904567890'),
('Bùi Minh E', 'buie@edu.com', '0905678901'),
('Lê Thi F', 'lef@edu.com', '0906789012'),
('Trương Quang G', 'truongg@edu.com', '0907890123'),
('Nguyễn Phương H', 'nguyenh@edu.com', '0908901234'),
('Hoàng Thị I', 'hoangi@edu.com', '0909012345'),
('Vũ Minh J', 'vumj@edu.com', '0900123456');


INSERT INTO Instructors (InstructorName, Expertise, Email)
VALUES
('Nguyễn Văn A', 'Toán học', 'nguyenvana@edu.com'),
('Trần Thị B', 'Lập trình', 'tranthib@edu.com'),
('Lê Minh C', 'Vật lý', 'leminhc@edu.com'),
('Phạm Thị D', 'Hóa học', 'phamthid@edu.com'),
('Nguyễn Hoàng E', 'Kinh tế', 'nguyenhoange@edu.com'),
('Bùi Thi F', 'Ngoại ngữ', 'buithf@edu.com');


INSERT INTO Courses (CourseName, Descriptions, InstructorID)
VALUES
('Toán học cơ bản', 'Khóa học về toán học cơ bản', 1),
('Đại số 1', 'Khóa học về môn học Đại Số', 1),
('Lập trình Python', 'Khóa học về lập trình Python', 2),
('Cấu trúc dữ liệu và giải thuật', 'Đi sâu vào học cấu trúc và các thuật toán', 2),
('Vật lý đại cương', 'Khóa học về vật lý đại cương', 3),
('Sức bền vật liệu', 'Cách vật liệu hoạt động', 3),
('Hóa học hữu cơ', 'Khóa học về hóa học hữu cơ', 4),
('Hóa học vô cơ', 'Khóa học về hóa học vô cơ', 4),
('Kinh tế vĩ mô', 'Khóa học về kinh tế vĩ mô', 5),
('Kinh tế vi mô', 'Khóa học về kinh tế vi mô', 5),
('Tiếng anh thực hành tổng hợp', 'Giúp học sinh hiểu được tiếng anh cơ bản', 6),
('Tiếng anh nâng cao', 'Thực hành sơ bộ cách làm các bài luận án', 6);


INSERT INTO Lectures (Title, Content, CourseID)
VALUES
  -- Course 1: Toán học cơ bản
  ('Toán học cơ bản – Bài 1: Giới thiệu chung',    'Khái quát nội dung môn Toán học cơ bản',        1),
  ('Toán học cơ bản – Bài 2: Phép cộng và trừ',     'Cách thực hiện phép cộng và trừ cơ bản',         1),
  ('Toán học cơ bản – Bài 3: Nhân và chia',         'Phân tích phép nhân và chia trong Toán học',    1),
  ('Toán học cơ bản – Bài 4: Ứng dụng thực tế',     'Một số ứng dụng Toán học cơ bản trong đời sống',1),
  ('Toán học cơ bản – Bài 5: Ôn tập & kiểm tra',    'Bài tập tổng hợp và kiểm tra kiến thức',         1),

  -- Course 2: Đại số 1
  ('Đại số 1 – Bài 1: Tập hợp & Hàm số',            'Định nghĩa tập hợp và hàm số cơ bản',            2),
  ('Đại số 1 – Bài 2: Phương trình tuyến tính',      'Giải phương trình bậc nhất một ẩn',              2),
  ('Đại số 1 – Bài 3: Phương trình bậc hai',        'Phương pháp giải phương trình bậc hai',          2),
  ('Đại số 1 – Bài 4: Bất phương trình',            'Giải bất phương trình một ẩn',                   2),
  ('Đại số 1 – Bài 5: Ứng dụng & Ôn tập',           'Bài tập tổng hợp Đại số 1',                      2),

  -- Course 3: Lập trình Python
  ('Lập trình Python – Bài 1: Cài đặt môi trường',  'Hướng dẫn cài Python và thiết lập IDE',         3),
  ('Lập trình Python – Bài 2: Biến & Kiểu dữ liệu', 'Khai báo biến, kiểu số, chuỗi, danh sách',       3),
  ('Lập trình Python – Bài 3: Cấu trúc điều kiện', 'if, elif, else và ứng dụng',                    3),
  ('Lập trình Python – Bài 4: Vòng lặp',           'for, while và bài tập lặp',                     3),
  ('Lập trình Python – Bài 5: Hàm & Module',       'Định nghĩa hàm, import module',                 3),

  -- Course 4: Cấu trúc dữ liệu và giải thuật
  ('Cấu trúc & giải thuật – Bài 1: Giới thiệu',    'Khái niệm cấu trúc dữ liệu và giải thuật',       4),
  ('Cấu trúc & giải thuật – Bài 2: Mảng & Danh sách','Triển khai mảng, linked list',                  4),
  ('Cấu trúc & giải thuật – Bài 3: Ngăn xếp & Hàng đợi','Stack, Queue và ứng dụng',                   4),
  ('Cấu trúc & giải thuật – Bài 4: Cây & Đồ thị',   'Binary tree, graph cơ bản',                     4),
  ('Cấu trúc & giải thuật – Bài 5: Tìm kiếm & sắp xếp','Linear search, sort cơ bản',                  4),

  -- Course 5: Vật lý đại cương
  ('Vật lý đại cương – Bài 1: Giới thiệu',         'Khái quát môn Vật lý đại cương',                5),
  ('Vật lý đại cương – Bài 2: Động học chuyển động','Định nghĩa vận tốc, gia tốc',                   5),
  ('Vật lý đại cương – Bài 3: Động lực học',       'Lực, Newton và ứng dụng',                       5),
  ('Vật lý đại cương – Bài 4: Công & năng lượng',  'Công cơ học, năng lượng thế năng, động năng',   5),
  ('Vật lý đại cương – Bài 5: Bảo toàn năng lượng','Định luật bảo toàn năng lượng',                 5),

  -- Course 6: Sức bền vật liệu
  ('Sức bền vật liệu – Bài 1: Giới thiệu',         'Tổng quan về sức bền vật liệu',                 6),
  ('Sức bền vật liệu – Bài 2: Ứng suất & Biến dạng', 'Định nghĩa stress, strain',                     6),
  ('Sức bền vật liệu – Bài 3: Định luật Hooke',    'Quan hệ đàn hồi tuyến tính',                      6),
  ('Sức bền vật liệu – Bài 4: Thử nghiệm kéo nén', 'Thực hành và phân tích kết quả',                6),
  ('Sức bền vật liệu – Bài 5: Ứng dụng',           'Ứng dụng trong kết cấu và kỹ thuật',            6),

  -- Course 7: Hóa học hữu cơ
  ('Hóa học hữu cơ – Bài 1: Giới thiệu',           'Khái quát về hóa hữu cơ',                       7),
  ('Hóa học hữu cơ – Bài 2: Cấu trúc phân tử',     'Liên kết, nhóm chức cơ bản',                    7),
  ('Hóa học hữu cơ – Bài 3: Tính chất vật lý',     'Điểm nóng chảy, sôi, độ hòa tan',                7),
  ('Hóa học hữu cơ – Bài 4: Phản ứng cơ bản',      'Phản ứng thế, cộng, tách',                       7),
  ('Hóa học hữu cơ – Bài 5: Tổng hợp đơn giản',     'Các phản ứng tổng hợp thông dụng',              7),

  -- Course 8: Hóa học vô cơ
  ('Hóa học vô cơ – Bài 1: Giới thiệu',            'Khái quát về hóa vô cơ',                        8),
  ('Hóa học vô cơ – Bài 2: Kim loại',             'Tính chất và phản ứng của kim loại',             8),
  ('Hóa học vô cơ – Bài 3: Phi kim',              'Tính chất và phản ứng của phi kim',              8),
  ('Hóa học vô cơ – Bài 4: Muối',                  'Phân loại muối và phản ứng tạo muối',            8),
  ('Hóa học vô cơ – Bài 5: Axit & bazơ',          'Tính chất và độ mạnh axit, bazơ',                8),

  -- Course 9: Kinh tế vĩ mô
  ('Kinh tế vĩ mô – Bài 1: Giới thiệu',            'Các khái niệm cơ bản của kinh tế vĩ mô',         9),
  ('Kinh tế vĩ mô – Bài 2: Tổng sản phẩm quốc nội','GDP, GNP và cách tính',                        9),
  ('Kinh tế vĩ mô – Bài 3: Thất nghiệp',          'Định nghĩa, nguyên nhân và đo lường',            9),
  ('Kinh tế vĩ mô – Bài 4: Lạm phát',             'Nguyên nhân, hệ quả và đo lường lạm phát',      9),
  ('Kinh tế vĩ mô – Bài 5: Chính sách tiền tệ',    'Vai trò Ngân hàng Trung ương',                  9),

  -- Course 10: Kinh tế vi mô
  ('Kinh tế vi mô – Bài 1: Giới thiệu',            'Khái niệm cơ bản của kinh tế vi mô',            10),
  ('Kinh tế vi mô – Bài 2: Cung & cầu',            'Đường cung cầu và tương tác thị trường',         10),
  ('Kinh tế vi mô – Bài 3: Lý thuyết người tiêu dùng','Hàm hữu dụng và đỉnh hữu dụng',               10),
  ('Kinh tế vi mô – Bài 4: Thị trường cạnh tranh', 'Đặc điểm và phân tích giá cân bằng',             10),
  ('Kinh tế vi mô – Bài 5: Thị trường độc quyền',  'Tính toán lợi nhuận và chính sách giá',         10),

  -- Course 11: Tiếng anh thực hành tổng hợp
  ('Tiếng Anh tổng hợp – Bài 1: Từ vựng cơ bản',   'Nhóm từ vựng thông dụng hàng ngày',              11),
  ('Tiếng Anh tổng hợp – Bài 2: Ngữ pháp cơ bản',  'Thì, mệnh đề và cấu trúc câu đơn giản',           11),
  ('Tiếng Anh tổng hợp – Bài 3: Kỹ năng nghe',    'Chiến thuật nghe hiểu đoạn hội thoại',           11),
  ('Tiếng Anh tổng hợp – Bài 4: Kỹ năng nói',     'Thực hành phát âm và hội thoại ngắn',            11),
  ('Tiếng Anh tổng hợp – Bài 5: Kỹ năng viết',    'Viết câu, đoạn văn cơ bản',                     11),

  -- Course 12: Tiếng anh nâng cao
  ('Tiếng Anh nâng cao – Bài 1: Ngữ pháp nâng cao','Câu điều kiện, mệnh đề quan hệ',                 12),
  ('Tiếng Anh nâng cao – Bài 2: Viết luận',       'Cấu trúc bài luận và lập dàn ý',                12),
  ('Tiếng Anh nâng cao – Bài 3: Nghe hiểu nâng cao','Chiến thuật nghe hội thảo, bài giảng',          12),
  ('Tiếng Anh nâng cao – Bài 4: Đọc hiểu nâng cao','Phân tích văn bản học thuật',                   12),
  ('Tiếng Anh nâng cao – Bài 5: Giao tiếp chuyên sâu','Thực hành thuyết trình và tranh luận',         12);


INSERT INTO Enrollments (EnrollmentDate, LearnerID, CourseID)
VALUES
  ('2025-04-05',  1,  3),
  ('2025-04-05',  1,  4),
  ('2025-04-05',  1,  8),
  ('2025-04-05',  1,  10),
  ('2025-04-05',  4,  10),
  ('2025-04-10',  3, 12),
  ('2025-04-02',  6, 11),
  ('2025-04-09',  8, 10),
  ('2025-04-15',  6,  7),
  ('2025-04-15',  3,  2),
  ('2025-04-12',  4,  1),
  ('2025-04-18',  5,  6),
  ('2025-04-20',  9, 12),
  ('2025-04-11', 10,  5),
  ('2025-04-11', 4,  5),
  ('2025-04-11', 10,  9),
  ('2025-04-05',  5,  4),
  ('2025-04-02',  7,  2),
  ('2025-04-02',  7,  1),
  ('2025-04-17',  7,  8),
  ('2025-04-17',  5,  8),
  ('2025-04-05',  4,  8),
  ('2025-04-05',  3,  8),
  ('2025-04-09',  8,  3),
  ('2025-04-09',  8,  12),
  ('2025-04-07',  2, 10),
  ('2025-04-07',  2, 1),
  ('2025-04-20',  9,  6),
  ('2025-04-20',  9,  11),
  ('2025-04-10',  2,  5),
  ('2025-04-10',  2,  8),
  ('2025-04-12',  4,  9),
  ('2025-04-12',  3,  9);
