/* Instructor Management */

-- add_instructor(name, expertise, email):
INSERT INTO Instructors (InstructorName, Expertise, Email)
VALUES (name, expertise, email);

-- update_instructor(instructor_id, expertise, email)
UPDATE Instructors
SET
    Expertise = COALESCE(expertise, Expertise),
    Email = COALESCE(email, Email)
WHERE
    InstructorID = instructor_id;


/* Course Management */

-- create_course(course, des)
INSERT INTO Courses(CourseName, Descriptions)
VALUES (course, des)

-- update_course(course_id, des, instructor_id)
UPDATE Courses
SET 
    Descriptions = COALESCE(des, Descriptions)
    InstructorID = COALESCE(instructor_id, InstructorID)
WHERE
    CourseID = course_id;


/* Lecture content Management */

-- create_lecture(title, content, course_id)
INSERT INTO Lectures (Title, Content, CourseID)
VALUES (title, content, course_id);

-- update_lecture(lecture_id, title, content)
UPDATE Lectures
SET
    Title = COALESCE(title, Title),
    Content = COALESCE(content, Content)
WHERE
    LectureID = lecture_id;


/* Learner Management */

-- create_learner(name, email, phone)
INSERT INTO Learners (LearnerName, Email, PhoneNumber)
VALUES (name, email, phone);

-- update_learner(name, email, phone)
UPDATE Learners
SET
    LearnerName = COALESCE(name, LearnerName),
    PhoneNumber = COALESCE(phone, PhoneNumber)
WHERE
    Email = email;