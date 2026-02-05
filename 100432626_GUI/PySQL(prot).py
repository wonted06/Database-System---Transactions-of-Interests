import psycopg2

def connect_db():
    pwFile = open("pw.txt", "r")
    pw = pwFile.read();
    pwFile.close()
    return psycopg2.connect(
        DB_name="100432626_data_definition_statements",
        DB_user="fjk23wtu",
        DB_password= pw,
        DB_host="cmpstudb-01.cmp.uea.ac.uk",
        DB_port="5432"
    )


## DML Statements 

# A. Insert a new student member of the society 
def insert_student(sno, name, email):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO student VALUES (%s, %s, %s)", (sno, name, email))
    conn.commit()
    cur.close()
    conn.close()
    
# B. Insert a new examination for the coming year  
def insert_exam(excode, title, location, date, time):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO exam VALUES (%s, %s, %s, %s, %s)", (excode, title, location, date, time))
    conn.commit()
    cur.close()
    conn.close()

# C. Delete a Student and Cancel entries
def delete_student(sno):
    conn = connect_db()
    cur = conn.cursor()

    # Insert into cancel
    cur.execute("""
        INSERT INTO cancel (eno, excode, sno, cdate, cuser)
        SELECT eno, excode, sno, CURRENT_TIMESTAMP, 'admin'
        FROM entry WHERE sno = %s
    """, (sno,))
    
    # Delete from entry
    cur.execute("DELETE FROM entry WHERE sno = %s", (sno,))
    
    # Delete from student
    cur.execute("DELETE FROM student WHERE sno = %s", (sno,))
    
    conn.commit()
    cur.close()
    conn.close()
    
# D. Delete an examination
def delete_exam_if_safe(excode):
    conn = connect_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM entry e
        WHERE e.excode = %s
        AND NOT EXISTS (
            SELECT 1 FROM cancel c
            WHERE c.eno = e.eno AND c.excode = e.excode AND c.sno = e.sno
        )
    """, (excode,))
    
    rows = cur.fetchall()
    if not rows:
        cur.execute("DELETE FROM exam WHERE excode = %s", (excode,))
    
    conn.commit()
    cur.close()
    conn.close()
    
# E. Insert an examination entry
def insert_entry(eno, excode, sno):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO entry (eno, excode, sno) VALUES (%s, %s, %s)", (eno, excode, sno))
    conn.commit()
    cur.close()
    conn.close()
    
# F. Update an entry
def update_entry_grade(conn, eno, grade):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE entry
            SET egrade = %s
            WHERE eno = %s
        """, (grade, eno))
        conn.commit()
        print(f"Grade {grade} set for entry {eno}.")
        
# G. Examination timetable for student 
def get_timetable_for_student(conn, sno):
    with conn.cursor() as cur:
        cur.execute("""
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
            WHERE s.sno = %s
        """, (sno,))
        return cur.fetchall()
    
# H. Result table obtained by each student for each examination
def get_all_results(conn):
    with conn.cursor() as cur:
        cur.execute("""
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
            ORDER BY ex.excode, s.sname
        """)
        return cur.fetchall()
    
# I. Same as H, but for a given examination 
def get_results_by_exam(conn, excode):
    with conn.cursor() as cur:
        cur.execute("""
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
            WHERE ex.excode = %s
            ORDER BY ex.excode, s.sname
        """, (excode,))
        return cur.fetchall()
    
    
    
    
    
    
    