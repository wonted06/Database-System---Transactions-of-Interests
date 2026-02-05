import tkinter as tk
from tkinter import messagebox
import psycopg2

#                                                        --- Database Connection Setup ---

# Securely read the database password from a local text file
with open("pw.txt") as f:
    pw = f.read().strip()

# Establish a connection to the PostgreSQL database
conn = psycopg2.connect(
    dbname="fjk23wtu",
    user="fjk23wtu",
    password=pw,
    host="cmpstudb-01.cmp.uea.ac.uk",
)
cursor = conn.cursor()
#                                                           --- GUI Initialization ---

# Set up the main application window
root = tk.Tk()
root.title("Transactions of Interest GUI")
root.geometry("900x600")

# Create layout frames
left_frame = tk.Frame(root, width=200, bg="lightgrey")
left_frame.pack(side="left", fill="y")

right_frame = tk.Frame(root)
right_frame.pack(side="right", expand=True, fill="both")


def view_all_students():
    query = "SELECT sno,sname,semail FROM student ORDER BY sno"
    conn = psycopg2
    cursor = conn.cursor()
    cursor.execute('SET search_path TO "100432626_data_definition_statements", PUBLIC;')
    cursor.execute(query)
    students = cursor.fetchfall()
    conn.close()


# Utility function to clear right frame content before loading new UI
def clear_right_frame():
    for widget in right_frame.winfo_children():
        widget.destroy()


#                                                       --- Transactions of Interest ---



# --- Transaction A: Insert a New Student ---
def insert_student():
    clear_right_frame()
    tk.Label(right_frame, text="Insert New Student").pack()

    # Input fields for student details
    sno_entry = tk.Entry(right_frame)
    sname_entry = tk.Entry(right_frame)
    semail_entry = tk.Entry(right_frame)

    tk.Label(right_frame, text="Student Number").pack()
    sno_entry.pack()
    tk.Label(right_frame, text="Student Name").pack()
    sname_entry.pack()
    tk.Label(right_frame, text="Student Email").pack()
    semail_entry.pack()

    # Submit action
    def submit():
        try:
            cursor.execute("INSERT INTO student VALUES (%s, %s, %s)",
                           (sno_entry.get(), sname_entry.get(), semail_entry.get()))
            conn.commit()
            messagebox.showinfo("Success", "Student inserted successfully")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", str(e))

    tk.Button(right_frame, text="Submit", command=submit).pack()

# --- Transaction B: Insert a New Exam ---
def insert_exam():
    clear_right_frame()
    tk.Label(right_frame, text="Insert New Exam").pack()

    # Input fields for exam details
    excode = tk.Entry(right_frame)
    extitle = tk.Entry(right_frame)
    exlocation = tk.Entry(right_frame)
    exdate = tk.Entry(right_frame)
    extime = tk.Entry(right_frame)

    tk.Label(right_frame, text="Exam Code").pack()
    excode.pack()
    tk.Label(right_frame, text="Title").pack()
    extitle.pack()
    tk.Label(right_frame, text="Location").pack()
    exlocation.pack()
    tk.Label(right_frame, text="Date (YYYY-MM-DD)").pack()
    exdate.pack()
    tk.Label(right_frame, text="Time (HH:MM)").pack()
    extime.pack()

    # Submit action
    def submit():
        try:
            cursor.execute("INSERT INTO exam VALUES (%s, %s, %s, %s, %s)",
                           (excode.get(), extitle.get(), exlocation.get(), exdate.get(), extime.get()))
            conn.commit()
            messagebox.showinfo("Success", "Exam inserted successfully")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", str(e))

    tk.Button(right_frame, text="Submit", command=submit).pack()

# --- Transaction C: Delete a Student and Cancel Entries ---
def delete_student():
    clear_right_frame()
    tk.Label(right_frame, text="Delete Student").pack()

    sno_entry = tk.Entry(right_frame)
    tk.Label(right_frame, text="Student Number").pack()
    sno_entry.pack()

    # Submit action
    def submit():
        try:
            sno = sno_entry.get()
            # Archive entries in cancel table before deletion
            cursor.execute("INSERT INTO cancel (eno, excode, sno, cdate, cuser) "
                           "SELECT eno, excode, sno, NOW(), 'admin' FROM entry WHERE sno = %s", (sno,))
            # Remove entries and the student
            cursor.execute("DELETE FROM entry WHERE sno = %s", (sno,))
            cursor.execute("DELETE FROM student WHERE sno = %s", (sno,))
            conn.commit()
            messagebox.showinfo("Success", "Student and their entries deleted")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", str(e))

    tk.Button(right_frame, text="Submit", command=submit).pack()

# --- Transaction D: Delete an Exam Only If No Active Entries Exist ---
def delete_exam():
    clear_right_frame()
    tk.Label(right_frame, text="Delete Exam").pack()

    excode_entry = tk.Entry(right_frame)
    tk.Label(right_frame, text="Exam Code").pack()
    excode_entry.pack()

    # Submit action
    def submit():
        try:
            excode = excode_entry.get()
            # Check if active entries exist for the exam
            cursor.execute("SELECT * FROM entry e WHERE e.excode = %s AND NOT EXISTS (" 
                           "SELECT 1 FROM cancel c WHERE c.eno = e.eno AND c.excode = e.excode AND c.sno = e.sno)", (excode,))
            if cursor.fetchone() is None:
                cursor.execute("DELETE FROM exam WHERE excode = %s", (excode,))
                conn.commit()
                messagebox.showinfo("Success", "Exam deleted")
            else:
                messagebox.showwarning("Blocked", "Exam has active entries and cannot be deleted.")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", str(e))

    tk.Button(right_frame, text="Submit", command=submit).pack()

# --- Transaction E: Insert a New Exam Entry ---
def insert_entry():
    clear_right_frame()
    tk.Label(right_frame, text="Insert Exam Entry").pack()

    # Input fields
    eno = tk.Entry(right_frame)
    excode = tk.Entry(right_frame)
    sno = tk.Entry(right_frame)

    tk.Label(right_frame, text="Entry Number").pack()
    eno.pack()
    tk.Label(right_frame, text="Exam Code").pack()
    excode.pack()
    tk.Label(right_frame, text="Student Number").pack()
    sno.pack()

    # Submit action
    def submit():
        try:
            cursor.execute("INSERT INTO entry (eno, excode, sno) VALUES (%s, %s, %s)",
                           (eno.get(), excode.get(), sno.get()))
            conn.commit()
            messagebox.showinfo("Success", "Entry inserted")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", str(e))

    tk.Button(right_frame, text="Submit", command=submit).pack()

# --- Transaction F: Update the Grade of an Entry ---
def update_grade():
    clear_right_frame()
    tk.Label(right_frame, text="Update Entry Grade").pack()

    eno = tk.Entry(right_frame)
    grade = tk.Entry(right_frame)

    tk.Label(right_frame, text="Entry Number").pack()
    eno.pack()
    tk.Label(right_frame, text="Grade").pack()
    grade.pack()

    # Submit action
    def submit():
        try:
            cursor.execute("UPDATE entry SET egrade = %s WHERE eno = %s",
                           (grade.get(), eno.get()))
            conn.commit()
            messagebox.showinfo("Success", "Grade updated")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", str(e))

    tk.Button(right_frame, text="Submit", command=submit).pack()

# --- Transaction G: View Student Timetable ---
def view_timetable():
    clear_right_frame()
    tk.Label(right_frame, text="View Student Timetable").pack()

    sno = tk.Entry(right_frame)
    tk.Label(right_frame, text="Student Number").pack()
    sno.pack()

    # Submit action
    def submit():
        try:
            cursor.execute("SELECT s.sname, e.excode, x.extitle, x.exlocation, x.exdate, x.extime "
                           "FROM student s JOIN entry e ON s.sno = e.sno JOIN exam x ON e.excode = x.excode "
                           "WHERE s.sno = %s", (sno.get(),))
            rows = cursor.fetchall()
            for row in rows:
                tk.Label(right_frame, text=str(row)).pack()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(right_frame, text="Show", command=submit).pack()

# --- Transaction H: Show All Students’ Results ---
def all_results():
    clear_right_frame()
    tk.Label(right_frame, text="All Student Exam Results").pack()

    try:
        cursor.execute("""
        SELECT ex.excode, ex.extitle, s.sname,
        COALESCE(d.result, p.result, f.result, 'Not taken') AS result
        FROM exam ex
        CROSS JOIN student s
        LEFT JOIN entry en ON en.excode = ex.excode AND en.sno = s.sno
        LEFT JOIN (SELECT eno, 'Distinction' AS result FROM entry WHERE egrade >= 70) d ON d.eno = en.eno
        LEFT JOIN (SELECT eno, 'Pass' AS result FROM entry WHERE egrade >= 50 AND egrade < 70) p ON p.eno = en.eno
        LEFT JOIN (SELECT eno, 'Fail' AS result FROM entry WHERE egrade < 50) f ON f.eno = en.eno
        ORDER BY ex.excode, s.sname
        """)
        for row in cursor.fetchall():
            tk.Label(right_frame, text=str(row)).pack()
    except Exception as e:
        messagebox.showerror("Error", str(e))

# --- Transaction I: Show Results for a Specific Exam ---
def exam_results():
    clear_right_frame()
    tk.Label(right_frame, text="Exam Results by Exam Code").pack()

    excode = tk.Entry(right_frame)
    tk.Label(right_frame, text="Exam Code").pack()
    excode.pack()

    # Submit action
    def submit():
        try:
            cursor.execute("""
            SELECT ex.excode, ex.extitle, s.sname,
            COALESCE(d.result, p.result, f.result, 'Not taken') AS result
            FROM exam ex
            CROSS JOIN student s
            LEFT JOIN entry en ON en.excode = ex.excode AND en.sno = s.sno
            LEFT JOIN (SELECT eno, 'Distinction' AS result FROM entry WHERE egrade >= 70) d ON d.eno = en.eno
            LEFT JOIN (SELECT eno, 'Pass' AS result FROM entry WHERE egrade >= 50 AND egrade < 70) p ON p.eno = en.eno
            LEFT JOIN (SELECT eno, 'Fail' AS result FROM entry WHERE egrade < 50) f ON f.eno = en.eno
            WHERE ex.excode = %s
            ORDER BY ex.excode, s.sname
            """, (excode.get(),))
            for row in cursor.fetchall():
                tk.Label(right_frame, text=str(row)).pack()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(right_frame, text="Show", command=submit).pack()

# --- Sidebar Navigation Buttons ---
# Map button labels to their corresponding functions
buttons = [
    ("Insert Student", insert_student),
    ("Insert Exam", insert_exam),
    ("Delete Student", delete_student),
    ("Delete Exam", delete_exam),
    ("Insert Entry", insert_entry),
    ("Update Grade", update_grade),
    ("Student Timetable", view_timetable),
    ("All Results", all_results),
    ("Results by Exam", exam_results)
]

# Create buttons in sidebar
for text, command in buttons:
    tk.Button(left_frame, text=text, width=20, command=command).pack(pady=5)

# Start the Tkinter event loop
root.mainloop()

# --- Cleanup: Close DB Connection on Exit ---
cursor.close()
conn.close()


