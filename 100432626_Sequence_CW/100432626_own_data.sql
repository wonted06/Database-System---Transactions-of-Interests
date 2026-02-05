--SET search_path TO "100432626_DDL", PUBLIC;

/*

------------------------------------------------------------------------------------

------ Test Data ------

--- Table: exam ---
INSERT INTO exam (excode, extitle, exlocation, exdate, extime) VALUES
('DB01', 'Database 1','Congregation Hall', '2025-11-05', '9:30'),
('AG01', 'Algebra','Congregation Hall', '2025-11-06', '14:00'),
('AI01', 'Artificial Intelligence Exam', 'Elizabeth Fry', '2025-11-07', '11:00'),
('EL01', 'English Literature', 'Thomas Pane', '2025-11-13', '10:30'),
('CS01', 'Computing Principles', 'Congregation Hall', '2025-11-20', '15:00'),
('EL02', 'English Language', 'Congregation Hall', '2025-11-16', '12:00'),
('WD01', 'Web Development Basics', 'Elizabeth Fry', '2025-11-08', '13:00'),
('OS01', 'Operating Systems', 'Thomas Pane', '2025-11-09', '11:30'),
('ML01', 'Machine Learning', 'Congregation Hall', '2025-11-14', '10:00'),
('NS01', 'Network Security', 'Elizabeth Fry', '2025-11-17', '16:00');

SELECT * FROM exam;

/*

exdate: All planned examinations are scheduled for November 2025

extime: No examinations start before 9:00 hours or after 18:00 hours

*/

--- Table: student ---

INSERT INTO student (sno, sname, semail) VALUES
(101, 'Alice Johnson', 'alice.johnson@gmail.com'),
(102, 'Bob Smith', 'bobsmith77@yahoo.com'),
(103, 'Charlie Brown', 'charliebrown01@yahoo.com'),
(104, 'David Lee', 'davidle_e@gmail.com'),
(105, 'Eve Harris', 'eveharris@hotmail.com'),
(106, 'Frank Miller', 'frank_miller@gmail.com'),
(107, 'Grace Kim', 'grace.kim@hotmail.com'),
(108, 'Hannah Zhang', 'hannahz@outlook.com'),
(109, 'Ian Wright', 'ian.wright@gmail.com'),
(110, 'Jackie Lee', 'jackielee@gmail.com');

SELECT * FROM student;

--- Table: entry ---

INSERT INTO entry (eno, excode, sno, egrade) VALUES
(1001, 'DB01', 101, NULL),  -- grade not yet assigned
(1002, 'CS01', 102, 85.00), 
(1003, 'AI01', 103, 90.00), 
(1004, 'AG01', 104, NULL),  -- grade not yet assigned
(1005, 'EL01', 105, NULL),  -- grade not yet assigned
(1006, 'EL02', 106, 95.00),
(1007, 'WD01', 107, 72.00),
(1008, 'OS01', 108, 55.00),
(1009, 'ML01', 109, 45.00),
(1010, 'NS01', 110, NULL); -- grade not yet assigned

SELECT * FROM entry;

/*

egrade: Range of grades is 0 to 100. If student does not attend the examination then this field remains empty

*/


--- Table: cancel ---

INSERT INTO cancel (eno, excode, sno, cdate, cuser) VALUES
(1001, 'DB01', 101, '2025-11-05 09:30:00', 'System User'), -- Alice Johnson's DB01 entry was canceled
(1002, 'CS01', 102, '2025-11-06 15:00:00', 'admin'), -- Bob Smith's CS01 entry was canceled
(1006, 'EL02', 106, '2025-11-16 12:00:00', 'admin'), -- Frank Miller's EL02 entry was canceled
(1009, 'ML01', 109, '2025-11-14 10:00:00', 'System User'); -- 
SELECT * FROM cancel;



------------------------------------------------------------------------------------

------ DML Statements ------

-- A. Insert a new student member of the society --

INSERT INTO student VALUES
(111, 'Sophie Clark', 'sophieclark06@gmail.com');


-- B.  Insert a new examination for the coming year --

INSERT INTO exam VALUES 
('FR01', 'French', 'SportsPark', '2025-11-23', '10:30');


-- C. Delete a Student (and Cancel Entries) --
-- Example for student 105 (Eve Harris)

-- 1. Insert exam entries into cancel table 
INSERT INTO cancel (eno, excode, sno, cdate, cuser)
SELECT eno, excode, sno, NOW(), 'admin'
FROM entry
WHERE sno = 105;

-- 2. Delete entries from entry table 
DELETE FROM entry
WHERE sno = 105;

-- 3. Delete student records
DELETE FROM student 
WHERE sno = 105;


-- D. Delete an examination 

-- Check if exam has any current entries
SELECT * FROM entry e
WHERE e.excode = 'FR01'
AND NOT EXISTS (
    SELECT 1 FROM cancel c
    WHERE c.eno = e.eno AND c.excode = e.excode AND c.sno = e.sno
);

-- If above returns no rows, then it's safe to delete:
DELETE FROM exam WHERE excode = 'FR01';


-- E. Insert an examination entry 

INSERT INTO entry (eno, excode, sno)
VALUES (1011, 'DB01', 111);


-- F. Update an entry 

UPDATE entry
SET egrade = 87.00
WHERE eno = 1011;


-- G. Examination timetable for a student

SELECT
    s.sname,
    e.excode,
    x.extitle,
    x.exlocation,
    x.exdate,
    x.extime
FROM student s
JOIN entry e ON s.sno = e.sno
JOIN exam x ON e.excode = x.excode
WHERE s.sno = 111;

-- H. Result table obtained by each student for each examination

SELECT
    ex.excode,
    ex.extitle,
    s.sname,
    COALESCE(d.result, p.result, f.result, 'Not taken') AS result
FROM
    exam ex
CROSS JOIN
    student s
LEFT JOIN
    entry en ON en.excode = ex.excode AND en.sno = s.sno
LEFT JOIN (
    SELECT eno, 'Distinction' AS result FROM entry WHERE egrade >= 70
) d ON d.eno = en.eno
LEFT JOIN (
    SELECT eno, 'Pass' AS result FROM entry WHERE egrade >= 50 AND egrade < 70
) p ON p.eno = en.eno
LEFT JOIN (
    SELECT eno, 'Fail' AS result FROM entry WHERE egrade < 50
) f ON f.eno = en.eno
ORDER BY
    ex.excode, s.sname;


-- I. Same as H, but for a given examination

SELECT
    ex.excode,
    ex.extitle,
    s.sname,
    COALESCE(d.result, p.result, f.result, 'Not taken') AS result
FROM
    exam ex
CROSS JOIN
    student s
LEFT JOIN
    entry en ON en.excode = ex.excode AND en.sno = s.sno
LEFT JOIN (
    SELECT eno, 'Distinction' AS result FROM entry WHERE egrade >= 70
) d ON d.eno = en.eno
LEFT JOIN (
    SELECT eno, 'Pass' AS result FROM entry WHERE egrade >= 50 AND egrade < 70
) p ON p.eno = en.eno
LEFT JOIN (
    SELECT eno, 'Fail' AS result FROM entry WHERE egrade < 50
) f ON f.eno = en.eno
WHERE ex.excode = 'DB01'
ORDER BY
    ex.excode, s.sname;

*/

-------------------------------------------------------------




/*
------ Further Test Data ------

-------------------------------------------------------
-- A. Add a new student
-------------------------------------------------------
-- Valid student
INSERT INTO student VALUES (1001, 'Alice Johnson', 'alice.johnson@example.com');

-- Duplicate email
-- Should fail due to UNIQUE constraint
INSERT INTO student VALUES (1002, 'Another Alice', 'alice.johnson@example.com');

-- Duplicate student number
-- Should fail due to PRIMARY KEY constraint
INSERT INTO student VALUES (1001, 'Duplicate ID', 'unique@example.com');

-------------------------------------------------------
-- B. Add a new exam
-------------------------------------------------------
-- Valid exam
INSERT INTO exam VALUES ('EX01', 'Maths', 'Main Hall', '2025-11-15', '14:00');

-- Invalid date (wrong month)
-- Should fail due to CHECK constraint
INSERT INTO exam VALUES ('EX02', 'Algebra', 'Room 101', '2025-10-10', '10:00');

-- Invalid time (too early)
INSERT INTO exam VALUES ('EX03', 'Calculus', 'Room 102', '2025-11-20', '07:00');

-------------------------------------------------------
-- C. Make a new entry
-------------------------------------------------------
-- Valid entry
INSERT INTO entry VALUES (2001, 'EX01', 1001, 85.00);

-- Duplicate exam on same day
-- Should trigger prevent_duplicate_entry()
INSERT INTO exam VALUES ('EX04', 'Combinatorics', 'Room 105', '2025-11-15', '16:00');
INSERT INTO entry VALUES (2002, 'EX04', 1001, 90.00);

-- Same student and exam again
-- Should trigger duplicate entry prevention
INSERT INTO entry VALUES (2003, 'EX01', 1001, 88.00);

-------------------------------------------------------
-- D. Delete a student
-- Should move entries to CANCEL via trigger
-------------------------------------------------------
DELETE FROM student WHERE sno = 1001;

-- Check cancel table
SELECT * FROM cancel WHERE sno = 1001;

-------------------------------------------------------
-- E. Cancel an entry manually
-------------------------------------------------------
-- Insert new student and exam
INSERT INTO student VALUES (1003, 'Bob Lee', 'bob.lee@example.com');
INSERT INTO exam VALUES ('EX05', 'Programming', 'Lab 1', '2025-11-18', '10:00');

-- Create entry and cancel it
INSERT INTO entry VALUES (2004, 'EX05', 1003, 75.00);

-- Manual cancel
INSERT INTO cancel (eno, excode, sno, cuser)
VALUES (2004, 'EX05', 1003, 'admin');

-- Insert without cdate (should auto-fill)
INSERT INTO cancel (eno, excode, sno, cuser)
VALUES (2004, 'EX05', 1003, 'test_user');

-------------------------------------------------------
-- F. Update grade of an entry
-------------------------------------------------------
-- Valid grade
UPDATE entry SET egrade = 65.00 WHERE eno = 2004;

-- Invalid grade (over 100)
UPDATE entry SET egrade = 150.00 WHERE eno = 2004;

-------------------------------------------------------
-- G. View timetable for a student
-------------------------------------------------------
SELECT * FROM student_timetable WHERE sname = 'Bob Lee';

-------------------------------------------------------
-- H. View result classifications
-------------------------------------------------------
SELECT * FROM exam_results;

-------------------------------------------------------
-- I. Show entries that have been cancelled
-------------------------------------------------------
SELECT * FROM cancel;

*/





--------------------------------------------------------------

------ Farhana Liza (Test Data) ------
/*

DELETE FROM entry;

DELETE FROM student;

DELETE FROM exam;

DELETE FROM cancel;

INSERT INTO exam VALUES 
    ('VB02', 'Visual Basic 2', 'London', '2025-11-02', '18:00'),
    ('SQL1', 'SQL 1', 'Norwich', '2025-11-01', '11:00'),
    ('SQL2', 'SQL 2', 'Norwich', '2025-11-02', '11:00'),
    ('XQ02', 'Xquery 2', 'Norwich', '2025-11-03', '11:00'),
    ('PMAN', 'Project Management', 'London', '2025-11-04', '11:00'),
    ('PYTH', 'Python programming', 'London', '2025-11-04', '11:00');


INSERT INTO student VALUES
    (100, 'Lewing, Y.', 'ly@myhome.com'),
    (200, 'Brown, B.', 'bb@myhome.com'),
    (300, 'Green, C.', 'cg@myhome.com'),
    (400, 'White, D.', 'dw@myhome.com'),
    (500, 'Young, E.', 'ey@myhome.com');

INSERT INTO entry(eno, excode, sno)
    VALUES (1, 'VB02', 100);   
INSERT INTO entry(eno, excode, sno)
    VALUES (2, 'XQ02', 100);
INSERT INTO entry(eno, excode, sno)
    VALUES (3, 'PMAN', 100);
INSERT INTO entry(eno, excode, sno)
    VALUES (4, 'SQL1', 200);
INSERT INTO entry(eno, excode, sno)
    VALUES (5, 'VB02', 200);
INSERT INTO entry(eno, excode, sno)
    VALUES (6, 'XQ02', 200);
INSERT INTO entry(eno, excode, sno)
    VALUES (7, 'PMAN', 200);
INSERT INTO entry(eno, excode, sno)
    VALUES (8, 'PYTH', 300);
INSERT INTO entry(eno, excode, sno)
    VALUES (9, 'SQL2', 500);	



SELECT 'Students', count(*) FROM student
UNION 
SELECT 'Exams', count(*) FROM exam
UNION 
SELECT 'Entries', count(*)FROM entry
UNION 
SELECT 'Cancelled', count(*)FROM cancel;

-- This should show you 9 entries, 6 exams, 5 students and 0 cancelled.

UPDATE entry SET

    egrade = 50

    WHERE eno = 1;

UPDATE entry SET

    egrade = 55

    WHERE eno = 2;

UPDATE entry SET

    egrade = 45

    WHERE eno = 3;

UPDATE entry SET

    egrade = 50

    WHERE eno = 4;

UPDATE entry SET

    egrade = 90

    WHERE eno = 5;

UPDATE entry SET

    egrade = 20

    WHERE eno = 6;



SELECT * FROM entry order by eno;

-- This should show entries 1-6 with egrades and entries 7 TO 9 with null values.

*/

------ Evaluation of transactions of Interest ------

-- A. Insert a new student member of the society --
-- 1)	Insert a student with student number 600; Student name: “Liza, F.”; Student email ffl@myhome.com

-- INSERT INTO student VALUES
-- (600, 'Liza, F.', 'ffl@myhome.com');


-- 2)	Insert a student with student number 100; Student name: “Perez, B.”; Student email pb@myhome.com

-- INSERT INTO student VALUES
-- (100, 'Perez,B.', 'pb@myhome.com');


-- B. Insert a new examination for the coming year
-- 1)	Insert the values ‘VB01’ as exam code, ‘Visual Basic 1’ as exam title, ‘Norwich’ as location and date ‘02-11-2025’ with time ’09:00’.  

-- INSERT INTO exam VALUES 
-- ('VB01', 'Visual Basic 1', 'Norwich', '02-11-2025', '09:00');


-- 2)	Insert the values ‘VB03 as exam code, ‘Visual Basic 3’ as exam title, ‘London’ as location and date ‘03-11-2024’ with time ’19:00’.  

-- INSERT INTO exam VALUES 
-- ('VB03', 'Visual Basic 3', 'London', '03-11-2025', '19:00');


-- C. Delete a student.  This happens if a student withdraws from the society.  
--	  All the examination entries for the student must be cancelled.  
--    The cancelled entries must retain their student reference number even though there is no longer a matching row in the student table.

-- 1)	Delete student with student number 200;

--Check if exam has any current entries
-- 1. Insert exam entries into cancel table 

-- INSERT INTO cancel (eno, excode, sno, cdate, cuser)
-- SELECT eno, excode, sno, NOW(), 'System User'
-- FROM entry
-- WHERE sno = 200;

-- -- 2. Delete entries from entry table 
-- DELETE FROM entry
-- WHERE sno = 200;

-- -- 3. Delete student records
-- DELETE FROM student 
-- WHERE sno = 200;

-- SELECT * FROM cancel


-- D. Delete an examination. Examinations that have no entries may be deleted from the database.  
--    The examination must not have any current (not cancelled) entries.
-- 1)	Delete examination with code ‘VB01’;

-- -- Check if exam has any current entries
-- SELECT * FROM entry e
-- WHERE e.excode = 'VB01'
-- AND NOT EXISTS (
--     SELECT 1 FROM cancel c
--     WHERE c.eno = e.eno AND c.excode = e.excode AND c.sno = e.sno
-- );

-- -- If above returns no rows, then it's safe to delete:
-- DELETE FROM exam WHERE excode = 'VB01';

-- 2)	Delete examination with code ‘PYTH’;

-- -- Check if exam has any current entries
-- SELECT * FROM entry e
-- WHERE e.excode = 'PYTH'
-- AND NOT EXISTS (
--     SELECT 1 FROM cancel c
--     WHERE c.eno = e.eno AND c.excode = e.excode AND c.sno = e.sno
-- );

-- -- If above returns no rows, then it's safe to delete:
-- DELETE FROM exam WHERE excode = 'PYTH';

-- SELECT * FROM exam;


-- E. Insert an examination entry. A student can only enter a specific examination once in a year.  
--	  The student cannot take more than one examination on the same day.

-- 1)	 Insert a new entry with examination code  ‘VB02’ and student number 400. The examination entry number should be 10.

-- INSERT INTO entry (eno, excode, sno)
-- VALUES (10, 'VB02', 400);

-- 2)	Insert a new entry with examination code  ‘VB02’ and student number 100. The examination entry number should be 11.

-- INSERT INTO entry (eno, excode, sno)
-- VALUES (11, 'VB02', 100);

-- 3)	Insert a new entry with examination code  ‘VB02’ and student number 500. The examination entry number should be 12.

-- INSERT INTO entry (eno, excode, sno)
-- VALUES (12, 'VB02', 500);

-- F. Update an entry.  This records the grade awarded by the examiners to an entry made by a student for an examination.  
-- 	  The entry is specified by entry reference number.

-- -- 1)	Update entry for exam ‘XQ02’ and student 200 with the mark of 60.

-- UPDATE entry
-- SET egrade = 60
-- WHERE sno = 200 AND excode = 'XQ02';
 
-- -- 2)	Update entry for exam entry number 99 with the mark of 60.

-- UPDATE entry
-- SET egrade = 60
-- WHERE eno= 99;

-- -- 3) Update entry for exam entry number 9  with a mark of  110.

-- UPDATE entry
-- SET egrade = 110
-- WHERE eno= 9;

-- SELECT * FROM entry;

-------------------------------------------------------------------------
--							Testing task G
-------------------------------------------------------------------------
-- P. Produce a table showing the examination timetable for a given student.  
--    The student is specified by his/her student membership number.  
--    The timetable should contain the student's name and the location, code, title, day and time of each examination for which the student has entered. 
--    There should be one row for each exam code.

-- 1)	Show timetable for student number 100.

-- SELECT
--     s.sname,
--     e.excode,
--     x.extitle,
--     x.exlocation,
--     x.exdate,
--     x.extime
-- FROM student s
-- JOIN entry e ON s.sno = e.sno
-- JOIN exam x ON e.excode = x.excode
-- WHERE s.sno = 100;


-------------------------------------------------------------------------
--							Testing task H
-------------------------------------------------------------------------
-- Q.  Produce a table showing the result obtained by each student for each examination. 
-- The table should be sorted by examination code and then by student name. 
-- If the student is awarded a grade of 70% or more then the result is to be shown as 'Distinction', a grade of at least 50% but less than 70% is to be shown as 'Pass' and grades below 50% are to be shown as 'Fail'. 
-- If the student has not taken the examination then the result is shown as 'Not taken'. 
-- The table should display the exam code, exam title, student name and exam result (e.g., 'Distinction', ‘Pass’, ‘Fail’, ‘Not taken’). 

-- SELECT
--     ex.excode,
--     ex.extitle,
--     s.sname,
--     COALESCE(d.result, p.result, f.result, 'Not taken') AS result
-- FROM
--     exam ex
-- CROSS JOIN
--     student s
-- LEFT JOIN
--     entry en ON en.excode = ex.excode AND en.sno = s.sno
-- LEFT JOIN (
--     SELECT eno, 'Distinction' AS result FROM entry WHERE egrade >= 70
-- ) d ON d.eno = en.eno
-- LEFT JOIN (
--     SELECT eno, 'Pass' AS result FROM entry WHERE egrade >= 50 AND egrade < 70
-- ) p ON p.eno = en.eno
-- LEFT JOIN (
--     SELECT eno, 'Fail' AS result FROM entry WHERE egrade < 50
-- ) f ON f.eno = en.eno
-- ORDER BY
--     ex.excode, s.sname;


-------------------------------------------------------------------------
--							Testing task I
-------------------------------------------------------------------------
-- R.  As H above but for a given examination.  The examination is specified by examination code.

-- 1)	Use examination code ‘VB02’.

-- SELECT
--     ex.excode,
--     ex.extitle,
--     s.sname,
--     COALESCE(d.result, p.result, f.result, 'Not taken') AS result
-- FROM
--     exam ex
-- CROSS JOIN
--     student s
-- LEFT JOIN
--     entry en ON en.excode = ex.excode AND en.sno = s.sno
-- LEFT JOIN (
--     SELECT eno, 'Distinction' AS result FROM entry WHERE egrade >= 70
-- ) d ON d.eno = en.eno
-- LEFT JOIN (
--     SELECT eno, 'Pass' AS result FROM entry WHERE egrade >= 50 AND egrade < 70
-- ) p ON p.eno = en.eno
-- LEFT JOIN (
--     SELECT eno, 'Fail' AS result FROM entry WHERE egrade < 50
-- ) f ON f.eno = en.eno
-- WHERE ex.excode = 'VB02'
-- ORDER BY
--     ex.excode, s.sname;


------ End of Evaluation ------