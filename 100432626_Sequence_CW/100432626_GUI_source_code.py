# CMPS Examination Database GUI
# Author: Kurt Canillas
# Date: 07/05/2025
# Description:
# This Python Tkinter GUI application interfaces with a PostgreSQL database for CMPS.
# It supports the Transactions of Interest (A–I) including student and exam insertions,
# entry handling, grade updates, and reporting functionalities.

import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2



# -------------------------- Database Configuration -------------------------- #


DB_host = "cmpstudb-01.cmp.uea.ac.uk"
DB_name = "fjk23wtu"
DB_user = "fjk23wtu"
DB_password = "InsideDifficultMoon17*"  # Password is read from file in get_connection()



# -------------------------- Connecting the GUI to my Database -------------------------- #


def get_connection():
    """Establish a connection to the PostgreSQL database."""
    try:
        with open("pw.txt", "r") as pw_file:
            pw = pw_file.read().strip()
        conn_str = f"host='{DB_host}' dbname='{DB_name}' user='{DB_user}' password='{pw}'"
        conn = psycopg2.connect(conn_str)
        return conn
    except psycopg2.Error as e:
        messagebox.showerror("Database Connection Error", f"Failed to connect to the database:\n{e}")
        return None


# -------------------------- SQL Execution Helper -------------------------- #


def execute_query(query, params=None, fetch=False):
    """Execute a given SQL query with optional parameters and optional result fetching."""
    conn = get_connection()
    if conn is None:
        return None
    try:
        with conn.cursor() as cur:
            # Set correct schema
            cur.execute('SET search_path TO "100432626_DDL", PUBLIC;')
            cur.execute(query, params)
            if fetch:
                results = cur.fetchall()
                conn.commit()
                return results
            else:
                conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        messagebox.showerror("Query Error", f"Error executing query:\n{e}\nQuery: {query}\nParams: {params}")
        raise
    finally:
        conn.close()
        

# -------------------------- GUI Initialization -------------------------- #


root = tk.Tk()
root.title("Transactions of Interest - GUI")
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')



# ----------------------- A. Insert New Student -------------------------- #


frame_a = ttk.Frame(notebook)
notebook.add(frame_a, text="A. Add Student")

# Create dictionary to store entry widgets
student_entries = {}

# Labels and entry fields
fields = [("Student No:", "sno"), ("Name:", "sname"), ("Email:", "semail")]
for idx, (label_text, field_key) in enumerate(fields):
    ttk.Label(frame_a, text=label_text).grid(row=idx, column=0, padx=10, pady=5)
    entry = tk.Entry(frame_a)
    entry.grid(row=idx, column=1, padx=10, pady=5)
    student_entries[field_key] = entry  # Save reference in dictionary

# Function to add student
def add_student():
    query = "INSERT INTO student (sno, sname, semail) VALUES (%s, %s, %s);"
    params = (
        student_entries["sno"].get(),
        student_entries["sname"].get(),
        student_entries["semail"].get(),
    )
    execute_query(query, params)
    messagebox.showinfo("Success", "Student added successfully.")

# Add button
ttk.Button(frame_a, text="Add Student", command=add_student).grid(row=3, columnspan=2, pady=10)


# -------------------------- B. Insert New Exam -------------------------- #


frame_b = ttk.Frame(notebook)
notebook.add(frame_b, text="B. Add Exam")

exam_fields = ["Exam Code", "Title", "Location", "Date (YYYY-MM-DD)", "Time (HH:MM:SS)"]
exam_vars = [tk.Entry(frame_b) for _ in exam_fields]

for idx, (label, entry) in enumerate(zip(exam_fields, exam_vars)):
    ttk.Label(frame_b, text=label).grid(row=idx, column=0, padx=10, pady=5)
    entry.grid(row=idx, column=1, padx=10, pady=5)

def add_exam():
    query = "INSERT INTO exam (excode, extitle, exlocation, exdate, extime) VALUES (%s, %s, %s, %s, %s);"
    values = [v.get() for v in exam_vars]
    execute_query(query, values)
    messagebox.showinfo("Success", "Exam added successfully.")

ttk.Button(frame_b, text="Add Exam", command=add_exam).grid(row=5, columnspan=2, pady=10)


# -------------------------- C. Delete Student -------------------------- #


frame_c = ttk.Frame(notebook)
notebook.add(frame_c, text="C. Delete Student")

student_del_entry = tk.Entry(frame_c)
student_del_entry.grid(row=0, column=1, padx=10, pady=5)

# Label
ttk.Label(frame_c, text="Student No to delete:").grid(row=0, column=0, padx=10, pady=5)

def delete_student():
    sno_val = student_del_entry.get()
    cancel_query = '''INSERT INTO cancel (eno, excode, sno, cdate, cuser)
                      SELECT eno, excode, sno, CURRENT_TIMESTAMP, 'admin' FROM entry WHERE sno = %s;'''
    delete_query = "DELETE FROM student WHERE sno = %s;"
    execute_query(cancel_query, (sno_val,))
    execute_query(delete_query, (sno_val,))
    messagebox.showinfo("Success", "Student deleted and entries cancelled.")

ttk.Button(frame_c, text="Delete Student", command=delete_student).grid(row=1, columnspan=2, pady=10)


# -------------------------- D. Delete Exam -------------------------- #


frame_d = ttk.Frame(notebook)
notebook.add(frame_d, text="D. Delete Exam")

exam_del_entry = tk.Entry(frame_d)
exam_del_entry.grid(row=0, column=1, padx=10, pady=5)

ttk.Label(frame_d, text="Exam Code to delete:").grid(row=0, column=0, padx=10, pady=5)

def delete_exam():
    excode_val = exam_del_entry.get()
    check_query = '''SELECT * FROM entry WHERE excode = %s AND eno NOT IN (SELECT eno FROM cancel);'''
    result = execute_query(check_query, (excode_val,), fetch=True)
    if result:
        messagebox.showwarning("Warning", "Cannot delete exam with active entries.")
    else:
        delete_query = "DELETE FROM exam WHERE excode = %s;"
        execute_query(delete_query, (excode_val,))
        messagebox.showinfo("Success", "Exam deleted.")

ttk.Button(frame_d, text="Delete Exam", command=delete_exam).grid(row=1, columnspan=2, pady=10)


# -------------------------- E. Insert Exam Entry -------------------------- #


frame_e = ttk.Frame(notebook)
notebook.add(frame_e, text="E. Add Entry")

entry_fields = ["Entry No", "Exam Code", "Student No"]
entry_vars = [tk.Entry(frame_e) for _ in entry_fields]

for idx, (label, entry) in enumerate(zip(entry_fields, entry_vars)):
    ttk.Label(frame_e, text=label).grid(row=idx, column=0, padx=10, pady=5)
    entry.grid(row=idx, column=1, padx=10, pady=5)

def add_entry():
    eno, excode, sno = [v.get() for v in entry_vars]
    check_query = '''SELECT 1 FROM entry e JOIN exam x ON e.excode = x.excode
                     WHERE e.sno = %s AND x.exdate = (SELECT exdate FROM exam WHERE excode = %s);'''
    existing = execute_query(check_query, (sno, excode), fetch=True)
    if existing:
        messagebox.showwarning("Invalid Entry", "Student already has exam on this date.")
    else:
        query = "INSERT INTO entry (eno, excode, sno, egrade) VALUES (%s, %s, %s, NULL);"
        execute_query(query, (eno, excode, sno))
        messagebox.showinfo("Success", "Exam entry added.")

ttk.Button(frame_e, text="Add Entry", command=add_entry).grid(row=3, columnspan=2, pady=10)


# -------------------------- F. Update Grade -------------------------- #


frame_f = ttk.Frame(notebook)
notebook.add(frame_f, text="F. Update Grade")

ttk.Label(frame_f, text="Entry No:").grid(row=0, column=0, padx=10, pady=5)
update_eno = tk.Entry(frame_f)
update_eno.grid(row=0, column=1)

ttk.Label(frame_f, text="Grade (0-100):").grid(row=1, column=0, padx=10, pady=5)
update_grade = tk.Entry(frame_f)
update_grade.grid(row=1, column=1)

def update_entry_grade():
    query = "UPDATE entry SET egrade = %s WHERE eno = %s;"
    execute_query(query, (update_grade.get(), update_eno.get()))
    messagebox.showinfo("Success", "Grade updated.")

ttk.Button(frame_f, text="Update Grade", command=update_entry_grade).grid(row=2, columnspan=2, pady=10)


# -------------------------- G. Timetable for Student -------------------------- #


frame_g = ttk.Frame(notebook)
notebook.add(frame_g, text="G. Timetable")

student_id_entry = tk.Entry(frame_g)
student_id_entry.grid(row=0, column=1)

ttk.Label(frame_g, text="Student No:").grid(row=0, column=0, padx=10, pady=5)
result_text = tk.Text(frame_g, height=10, width=80)
result_text.grid(row=1, columnspan=2, pady=5)

def show_timetable():
    sno = student_id_entry.get()
    query = '''SELECT s.sname, e.exlocation, e.excode, e.extitle, e.exdate, e.extime
               FROM student s JOIN entry en ON s.sno = en.sno
               JOIN exam e ON en.excode = e.excode WHERE s.sno = %s;'''
    result = execute_query(query, (sno,), fetch=True)
    result_text.delete(1.0, tk.END)
    for row in result:
        result_text.insert(tk.END, f"Name: {row[0]}, Location: {row[1]}, Code: {row[2]}, Title: {row[3]}, Date: {row[4]}, Time: {row[5]}\n")

ttk.Button(frame_g, text="Show Timetable", command=show_timetable).grid(row=2, columnspan=2, pady=5)


# -------------------------- H. Results for All Students -------------------------- #


frame_h = ttk.Frame(notebook)
notebook.add(frame_h, text="H. Results All")

results_text_h = tk.Text(frame_h, height=15, width=100)
results_text_h.pack()

def show_all_results():
    query = '''SELECT e.excode, e.extitle, s.sname,
               CASE 
                   WHEN en.egrade >= 70 THEN 'Distinction'
                   WHEN en.egrade >= 50 THEN 'Pass'
                   WHEN en.egrade < 50 THEN 'Fail'
                   ELSE 'Not taken'
               END AS result
               FROM exam e JOIN entry en ON e.excode = en.excode
               JOIN student s ON en.sno = s.sno
               ORDER BY e.excode, s.sname;'''
    result = execute_query(query, fetch=True)
    results_text_h.delete(1.0, tk.END)
    for row in result:
        results_text_h.insert(tk.END, f"{row[0]} | {row[1]} | {row[2]} | {row[3]}\n")

ttk.Button(frame_h, text="Show All Results", command=show_all_results).pack()


# -------------------------- I. Results for Specific Exam -------------------------- #


frame_i = ttk.Frame(notebook)
notebook.add(frame_i, text="I. Results by Exam")

exam_code_entry_i = tk.Entry(frame_i)
exam_code_entry_i.grid(row=0, column=1)

ttk.Label(frame_i, text="Exam Code:").grid(row=0, column=0, padx=10, pady=5)
results_text_i = tk.Text(frame_i, height=15, width=100)
results_text_i.grid(row=1, columnspan=2)

def show_exam_results():
    excode = exam_code_entry_i.get()
    query = '''SELECT e.excode, e.extitle, s.sname,
               CASE 
                   WHEN en.egrade >= 70 THEN 'Distinction'
                   WHEN en.egrade >= 50 THEN 'Pass'
                   WHEN en.egrade < 50 THEN 'Fail'
                   ELSE 'Not taken'
               END AS result
               FROM exam e JOIN entry en ON e.excode = en.excode
               JOIN student s ON en.sno = s.sno
               WHERE e.excode = %s
               ORDER BY s.sname;'''
    result = execute_query(query, (excode,), fetch=True)
    results_text_i.delete(1.0, tk.END)
    for row in result:
        results_text_i.insert(tk.END, f"{row[0]} | {row[1]} | {row[2]} | {row[3]}\n")

ttk.Button(frame_i, text="Show Exam Results", command=show_exam_results).grid(row=2, columnspan=2, pady=5)


# -------------------------- Main Loop -------------------------- #


root.mainloop()




