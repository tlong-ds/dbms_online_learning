-- 1. Thiết lập delimiter để định nghĩa trigger
drop trigger if exists trg_after_insert_enrollment;
drop trigger if exists trg_after_update_enrollment;

select * from Enrollments;

DELIMITER $$

CREATE TRIGGER trg_after_insert_enrollment
AFTER INSERT ON Enrollments
FOR EACH ROW
BEGIN
  -- Insert các dòng tương ứng vào LectureResults
  INSERT INTO LectureResults (LearnerID, CourseID, LectureID, Score, Date, State)
  SELECT NEW.LearnerID, NEW.CourseID, LectureID, 0, NULL, 'Unpassed'
  FROM Lectures
  WHERE CourseID = NEW.CourseID;
END$$

DELIMITER ;

select * from lectureresults;
select * from enrollments;
select * from courses;
select * from lectures where CourseID = 16;

DELIMITER $$

CREATE TRIGGER trg_courses_after_update_rating
AFTER UPDATE ON Enrollments
FOR EACH ROW
BEGIN
  IF OLD.Rating <> NEW.Rating THEN
    UPDATE Courses
    SET AverageRating = (
      SELECT ROUND(AVG(Rating), 2)
      FROM Enrollments
      WHERE CourseID = NEW.CourseID
        AND Rating IS NOT NULL
    )
    WHERE CourseID = NEW.CourseID;
  END IF;
END$$

DELIMITER ;