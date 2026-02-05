--CREATE SCHEMA "100432626_DDL";
--SET search_path TO "100432626_DDL";

/*
------------------------------------------------------------------------------------

------ Part 1: DDL ------

--- DDL Statements ---

-- TABLE : Details of each examination
CREATE TABLE exam (
excode 				CHAR(4)						PRIMARY KEY,
extitle 			VARCHAR(200)				UNIQUE,
exlocation 			VARCHAR(200)				NOT NULL,
exdate 				DATE						NOT NULL, CHECK (EXTRACT(MONTH FROM exdate) = 11 AND EXTRACT(YEAR FROM exdate) = 2025),
extime 				TIME						NOT NULL, CHECK (extime >= TIME '09:00' AND extime <= TIME '18:00')
);

-- TABLE: Details of student members of the society 
CREATE TABLE student (
sno 				INTEGER						PRIMARY KEY,
sname 				VARCHAR(200)				NOT NULL,
semail 				VARCHAR(200)				UNIQUE
);

-- TABLE: Details of examination entries made by students 
CREATE TABLE entry (
eno 				INTEGER						PRIMARY KEY,
excode 				CHAR(4)						NOT NULL,
sno 				INTEGER						NOT NULL,
egrade 				DECIMAL(5,2)				CHECK (egrade >= 0 AND egrade <= 100),

-- Foreign Key Restraints: 
FOREIGN KEY (excode) REFERENCES exam(excode) ON DELETE RESTRICT,
FOREIGN KEY (sno) REFERENCES student(sno) ON DELETE CASCADE
);

-- TABLE: Records details of all entries that have been cancelled
CREATE TABLE cancel (
eno 				INTEGER						PRIMARY KEY,
excode 				CHAR(4)						NOT NULL, 
sno 				INTEGER						NOT NULL,
cdate 				TIMESTAMP					DEFAULT CURRENT_TIMESTAMP NOT NULL,
cuser 				VARCHAR(200)				NOT NULL,

 -- Foreign Key Constraints
FOREIGN KEY (eno) REFERENCES entry(eno) ON DELETE CASCADE,
FOREIGN KEY (excode) REFERENCES exam(excode) ON DELETE SET NULL,
FOREIGN KEY (sno) REFERENCES student(sno) ON DELETE SET NULL
);


------------------------------------------------------------------------------------

------ Trigger and Function Definitions ------

-- 1. Prevents duplicate entries on same day 
CREATE OR REPLACE FUNCTION prevent_duplicate_entry()
RETURNS TRIGGER AS $$
BEGIN 
	-- Checks: for duplicate entry
	IF EXISTS (
		SELECT 1 FROM entry
		WHERE sno = NEW.sno AND excode = NEW.excode
	) THEN
		RAISE EXCEPTION 'Student % has already entered exam %', NEW.sno, NEW.excode;
	END IF;

	-- Checks: if student has another exam on same day
	IF EXISTS (
		SELECT 1
		FROM entry e
		JOIN exam x ON e.excode = x.excode
		WHERE e.sno = NEW.sno AND x.exdate = (
			SELECT exdate FROM exam WHERE excode = NEW.excode 
		)
	) THEN 
		RAISE EXCEPTION 'Student % already has an exam on the same day', NEW.sno;
	END IF;

	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevent_duplicate_entry
BEFORE INSERT ON entry
FOR EACH ROW
EXECUTE FUNCTION prevent_duplicate_entry();


-- 2. Auto-Cancel entries when student is deleted

-- -- Cancel entries when entry is deleted (regardless of cause)
-- CREATE OR REPLACE FUNCTION cancel_entry()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     IF NOT EXISTS (
--         SELECT 1 FROM cancel WHERE eno = OLD.eno
--     ) THEN
--         INSERT INTO cancel (eno, excode, sno, cdate, cuser)
--         VALUES (OLD.eno, OLD.excode, OLD.sno, CURRENT_TIMESTAMP, 'admin');
--     END IF;
--     RETURN OLD;
-- END;
-- $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION cancel_entries_on_student_delete()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO cancel (eno, excode, sno, cdate, cuser)
    SELECT (eno, excode, OLD.sno, CURRENT_TIMESTAMP, 'admin'
    FROM entry
    WHERE sno = OLD.sno;

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_cancel_entries_before_student_delete
BEFORE DELETE ON student
FOR EACH ROW
EXECUTE FUNCTION cancel_entries_on_student_delete();


-- 3. Ensures Timestamp is never null
CREATE OR REPLACE FUNCTION fill_cancel_timestamp()
RETURNS TRIGGER AS $$
BEGIN 
	IF NEW.cdate IS NULL THEN 
		NEW.cdate := CURRENT_TIMESTAMP;
	END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_auto_fill_cancel_date
BEFORE INSERT ON cancel
FOR EACH ROW
EXECUTE FUNCTION fill_cancel_timestamp();


-- 4. Validate Grade Range (0 to 100)
CREATE OR REPLACE FUNCTION validate_grade_range()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.egrade IS NOT NULL AND (NEW.egrade < 0 OR NEW.egrade > 100) THEN
        RAISE EXCEPTION 'Grade % is out of range (0–100)', NEW.egrade;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_grade
BEFORE INSERT OR UPDATE ON entry
FOR EACH ROW
EXECUTE FUNCTION validate_grade_range();


-- 5. Classify Grade 
CREATE OR REPLACE FUNCTION classify_grade(g DECIMAL)
RETURNS VARCHAR AS $$
BEGIN
    IF g IS NULL THEN
        RETURN 'Not taken';
    ELSIF g >= 70 THEN
        RETURN 'Distinction';
    ELSIF g >= 50 THEN
        RETURN 'Pass';
    ELSE
        RETURN 'Fail';
    END IF;
END;
$$ LANGUAGE plpgsql;

------ VIEWS ------

-- 1. Exam timetable for students 
CREATE VIEW student_timetable AS
SELECT s.sname, e.excode, x.extitle, x.exlocation, x.exdate, x.extime
FROM entry e
JOIN student s ON s.sno = e.sno
JOIN exam x ON x.excode = e.excode
WHERE NOT EXISTS (
    SELECT 1 FROM cancel c WHERE c.eno = e.eno
);
COMMENT ON VIEW student_timetable IS 'Shows student exam timetables (non-cancelled entries)';


-- 2. Exam Results 
CREATE VIEW exam_results AS
SELECT 
    e.excode, 
    x.extitle, 
    s.sname, 
    classify_grade(e.egrade) AS result
FROM entry e
JOIN student s ON e.sno = s.sno
JOIN exam x ON x.excode = e.excode
ORDER BY e.excode, s.sname;

COMMENT ON VIEW exam_results IS 'Shows the result classification of each student per exam';

*/



