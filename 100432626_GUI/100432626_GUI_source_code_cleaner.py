import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import psycopg2
from datetime import datetime


#                                                        --- Database Connection Setup ---


DB_host = "cmpstudb-01.cmp.uea.ac.uk"
DB_name = "fjk23wtu"
DB_user = "fjk23wtu"
DB_password = "InsideDifficultMoon17*"


def get_connection():
    try:
        pw_file = open("pw.txt", "r")
        pw = pw_file.read().strip()
        pw_file.close()
        conn_str = f"host='{DB_host}' dbname='{DB_name}' user='{DB_user}' password='{pw}'"
        conn = psycopg2.connect(conn_str)
        return conn
    except psycopg2.Error as e:
        messagebox.showerror("Database Connection Error", f"Failed to connect to the database:\n{e}")
        return None
    
    
def execute_query(query, params=None, fetch=False):
    conn = get_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor() as cur:
            cur.execute('SET search_path TO "100432626_data_definition_statements", PUBLIC;') # Add the line here 
            cur.execute(query, params)
            if fetch:
                results = cur.fetchall()
                conn.commit()
                return results
            else:
                conn.commit()
                return None
    except psycopg2.Error as e:
        conn.rollback()
        messagebox.showerror("Query Error", f"Error executing query:\n{e}\nQuery: {query}\nParams: {params}")
        return None
    finally:
        conn.close()
        
        
class CMPSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Transactions of Interests - GUI")
        notebook = ttk.Notebook(root)
        notebook.pack(fill='both', expand=True)

        self.create_student_tab(notebook)
        self.create_exam_tab(notebook)
        self.create_entry_tab(notebook)
        self.create_result_tab(notebook)

    def create_student_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text='Students')

        # Transaction A: Insert new student
        ttk.Label(tab, text='Student No').grid(row=0, column=0)
        self.sno_entry = ttk.Entry(tab)
        self.sno_entry.grid(row=0, column=1)

        ttk.Label(tab, text='Name').grid(row=1, column=0)
        self.sname_entry = ttk.Entry(tab)
        self.sname_entry.grid(row=1, column=1)

        ttk.Label(tab, text='Email').grid(row=2, column=0)
        self.semail_entry = ttk.Entry(tab)
        self.semail_entry.grid(row=2, column=1)

        ttk.Button(tab, text="Add Student", command=self.add_student).grid(row=3, column=0, columnspan=2, pady=5)

        # Transaction C: Delete student
        ttk.Button(tab, text="Delete Student", command=self.delete_student).grid(row=4, column=0, columnspan=2, pady=5)


#                                                --- Transactions Of Interests ---


# --- A. Insert a new student ---

    def add_student(self):
        query = "INSERT INTO student (sno, sname, semail) VALUES (%s, %s, %s)"
        sno = self.sno_entry.get()
        sname = self.sname_entry.get()
        semail = self.semail_entry.get()
        execute_query(query, (sno, sname, semail))
        messagebox.showinfo("Success", "Student added successfully")


    def delete_student(self):
        sno = self.sno_entry.get()
        now = datetime.now()
        cancel_query = "INSERT INTO cancel (eno, excode, sno, cdate, cuser) SELECT eno, excode, sno, %s, %s FROM entry WHERE sno = %s"
        delete_entry_query = "DELETE FROM entry WHERE sno = %s"
        delete_student_query = "DELETE FROM student WHERE sno = %s"

        execute_query(cancel_query, (now, 'admin', sno))
        execute_query(delete_entry_query, (sno,))
        execute_query(delete_student_query, (sno,))
        messagebox.showinfo("Success", "Student and their entries deleted.")

    def create_exam_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text='Examinations')

        # Transaction B: Insert exam
        labels = ["Code", "Title", "Location", "Date (YYYY-MM-DD)", "Time (HH:MM:SS)"]
        self.exam_entries = []
        for i, label in enumerate(labels):
            ttk.Label(tab, text=label).grid(row=i, column=0)
            entry = ttk.Entry(tab)
            entry.grid(row=i, column=1)
            self.exam_entries.append(entry)

        ttk.Button(tab, text="Add Exam", command=self.add_exam).grid(row=5, column=0, columnspan=2, pady=5)

# Transaction D: Delete exam
        ttk.Button(tab, text="Delete Exam", command=self.delete_exam).grid(row=6, column=0, columnspan=2, pady=5)

    def add_exam(self):
        query = "INSERT INTO exam (excode, extitle, exlocation, exdate, extime) VALUES (%s, %s, %s, %s, %s)"
        data = [e.get() for e in self.exam_entries]
        execute_query(query, tuple(data))
        messagebox.showinfo("Success", "Exam added successfully")

    def delete_exam(self):
        excode = self.exam_entries[0].get()
        check_query = "SELECT * FROM entry WHERE excode = %s"
        entries = execute_query(check_query, (excode,), fetch=True)
        if entries:
            messagebox.showwarning("Invalid Operation", "Cannot delete exam with existing entries.")
        else:
            execute_query("DELETE FROM exam WHERE excode = %s", (excode,))
            messagebox.showinfo("Success", "Exam deleted successfully")

    def create_entry_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text='Entries')

        labels = ["Entry No", "Exam Code", "Student No", "Grade"]
        self.entry_widgets = []
        for i, label in enumerate(labels):
            ttk.Label(tab, text=label).grid(row=i, column=0)
            entry = ttk.Entry(tab)
            entry.grid(row=i, column=1)
            self.entry_widgets.append(entry)

        ttk.Button(tab, text="Add Entry", command=self.add_entry).grid(row=4, column=0, columnspan=2, pady=5)
        ttk.Button(tab, text="Update Grade", command=self.update_grade).grid(row=5, column=0, columnspan=2, pady=5)

# --- Transaction E: Insert a new exam entry ---

    def add_entry(self):
        query = "INSERT INTO entry (eno, excode, sno) VALUES (%s, %s, %s)"
        eno, excode, sno, _ = [w.get() for w in self.entry_widgets]
        check_same_day_query = '''SELECT e.excode FROM entry e JOIN exam x ON e.excode = x.excode WHERE e.sno = %s AND x.exdate = (SELECT exdate FROM exam WHERE excode = %s)'''
        same_day = execute_query(check_same_day_query, (sno, excode), fetch=True)
        if same_day:
            messagebox.showerror("Invalid", "Student already entered an exam on this day.")
        else:
            execute_query(query, (eno, excode, sno))
            messagebox.showinfo("Success", "Entry added successfully")

    def update_grade(self):
        query = "UPDATE entry SET egrade = %s WHERE eno = %s"
        eno, _, _, grade = [w.get() for w in self.entry_widgets]
        execute_query(query, (grade, eno))
        messagebox.showinfo("Success", "Grade updated")

    def create_result_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text='Reports')

        self.sno_result_entry = ttk.Entry(tab)
        self.sno_result_entry.grid(row=0, column=1)
        ttk.Label(tab, text="Student No (for Timetable)").grid(row=0, column=0)
        ttk.Button(tab, text="Show Timetable", command=self.show_timetable).grid(row=0, column=2)

        self.excode_result_entry = ttk.Entry(tab)
        self.excode_result_entry.grid(row=1, column=1)
        ttk.Label(tab, text="Exam Code (for Results)").grid(row=1, column=0)
        ttk.Button(tab, text="Show Exam Results", command=self.show_exam_results).grid(row=1, column=2)

        ttk.Button(tab, text="Show All Results", command=self.show_all_results).grid(row=2, column=0, columnspan=3)

        self.result_text = tk.Text(tab, height=20, width=100)
        self.result_text.grid(row=3, column=0, columnspan=3)

    def show_timetable(self):
        sno = self.sno_result_entry.get()
        query = '''
        SELECT s.sname, x.exlocation, x.excode, x.extitle, x.exdate, x.extime
        FROM student s
        JOIN entry e ON s.sno = e.sno
        JOIN exam x ON e.excode = x.excode
        WHERE s.sno = %s
        '''
        results = execute_query(query, (sno,), fetch=True)
        self.result_text.delete(1.0, tk.END)
        for row in results:
            self.result_text.insert(tk.END, f"Name: {row[0]}, Location: {row[1]}, Code: {row[2]}, Title: {row[3]}, Date: {row[4]}, Time: {row[5]}\n")

    def show_all_results(self):
        self.display_results()

    def show_exam_results(self):
        excode = self.excode_result_entry.get()
        self.display_results(excode)

    def display_results(self, excode=None):
        base_query = '''
        SELECT x.excode, x.extitle, s.sname, 
        CASE 
            WHEN e.egrade IS NULL THEN 'Not taken'
            WHEN e.egrade >= 70 THEN 'Distinction'
            WHEN e.egrade >= 50 THEN 'Pass'
            ELSE 'Fail'
        END as result
        FROM entry e
        JOIN student s ON e.sno = s.sno
        JOIN exam x ON e.excode = x.excode
        '''
        if excode:
            base_query += " WHERE x.excode = %s ORDER BY x.excode, s.sname"
            results = execute_query(base_query, (excode,), fetch=True)
        else:
            base_query += " ORDER BY x.excode, s.sname"
            results = execute_query(base_query, fetch=True)

        self.result_text.delete(1.0, tk.END)
        for row in results:
            self.result_text.insert(tk.END, f"Code: {row[0]}, Title: {row[1]}, Student: {row[2]}, Result: {row[3]}\n")

if __name__ == '__main__':
    root = tk.Tk()
    app = CMPSApp(root)
    root.mainloop()