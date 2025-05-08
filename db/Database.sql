USE OnlineLearning;
DROP TABLE IF EXISTS Learners;
DROP TABLE IF EXISTS Instructors;
DROP TABLE IF EXISTS Courses;
DROP TABLE IF EXISTS Lectures;
DROP TABLE IF EXISTS Enrollments;
DROP TABLE IF EXISTS LectureResults;
DROP TABLE IF EXISTS CourseStatuses;
DROP TABLE IF EXISTS Notebooks;
DROP TABLE IF EXISTS Quizzes;

-- 1. Learners
CREATE TABLE Learners (
  LearnerID     INT            AUTO_INCREMENT PRIMARY KEY,
  LearnerName   VARCHAR(50)    NOT NULL,
  Email         VARCHAR(50)    NOT NULL UNIQUE,
  AccountName   VARCHAR(50)    NOT NULL UNIQUE,
  Password      VARCHAR(200)   NOT NULL,
  PhoneNumber   VARCHAR(15),
  CreatedAt     TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UpdatedAt     TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. Instructors
CREATE TABLE Instructors (
  InstructorID   INT            AUTO_INCREMENT PRIMARY KEY,
  InstructorName VARCHAR(50)    NOT NULL,
  Expertise      VARCHAR(100),
  Email          VARCHAR(50)    NOT NULL UNIQUE,
  AccountName    VARCHAR(50)    NOT NULL UNIQUE,
  Password       VARCHAR(200)   NOT NULL,
  CreatedAt      TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UpdatedAt      TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 3. Courses
CREATE TABLE Courses (
  CourseID     INT            AUTO_INCREMENT PRIMARY KEY,
  CourseName   VARCHAR(100)   NOT NULL,
  Descriptions TEXT,
  InstructorID INT,
  CreatedAt    TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UpdatedAt    TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (InstructorID) REFERENCES Instructors(InstructorID)
);

-- 4. Lectures
CREATE TABLE Lectures (
  LectureID  INT            AUTO_INCREMENT PRIMARY KEY,
  Title      VARCHAR(50)    NOT NULL,
  Content    TEXT,
  CourseID   INT            NOT NULL,
  CreatedAt  TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UpdatedAt  TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
);

-- 5. Enrollments
CREATE TABLE Enrollments (
  EnrollmentID   INT       AUTO_INCREMENT PRIMARY KEY,
  EnrollmentDate DATE      NOT NULL,
  LearnerID      INT       NOT NULL,
  CourseID       INT       NOT NULL,
  UNIQUE KEY UX_Enrollments_Learner_Course (LearnerID, CourseID),
  FOREIGN KEY (LearnerID) REFERENCES Learners(LearnerID),
  FOREIGN KEY (CourseID)  REFERENCES Courses(CourseID)
);

-- 6. LectureResults
CREATE TABLE LectureResults (
  LearnerID  INT            NOT NULL,
  CourseID   INT            NOT NULL,
  LectureID  INT            NOT NULL,
  Score      INT,
  Date       DATE,
  State      VARCHAR(50)  NOT NULL,
  PRIMARY KEY (LearnerID, CourseID, LectureID),
  FOREIGN KEY (LearnerID)  REFERENCES Learners(LearnerID),
  FOREIGN KEY (CourseID)   REFERENCES Courses(CourseID),
  FOREIGN KEY (LectureID)  REFERENCES Lectures(LectureID)
);

-- 7. CourseStatuses
CREATE TABLE CourseStatuses (
  LearnerID  INT       NOT NULL,
  CourseID   INT       NOT NULL,
  Percentage INT,
  Rating     INT,
  PRIMARY KEY (LearnerID, CourseID),
  FOREIGN KEY (LearnerID) REFERENCES Learners(LearnerID),
  FOREIGN KEY (CourseID)  REFERENCES Courses(CourseID)
);

-- 8. Notebooks
CREATE TABLE Notebooks (
	NotebookID INT		AUTO_INCREMENT PRIMARY KEY,
    LearnerID INT		NOT NULL,
    CourseID INT,	
    LectureID INT,
    NotebookName VARCHAR(100) UNIQUE,
    Content VARCHAR(1000),
    CreatedDate DATE,
	FOREIGN KEY (LearnerID) REFERENCES Learners(LearnerID),
    FOREIGN KEY (CourseID) REFERENCES Courses(CourseID),
    FOREIGN KEY (LectureID) REFERENCES Lectures(LectureID)
);
