# CMPS Examination Management System  
*A PostgreSQL Database Application with Python GUI*

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![Python](https://img.shields.io/badge/Python-3.x-yellow)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green)
![Status](https://img.shields.io/badge/Status-Complete-success)

---

## Overview

This project is a **database-driven application** developed for the *Computing and Mathematics Professionals Society (CMPS)*.  
It demonstrates the **design, implementation, and interaction** of a relational database using **PostgreSQL**, alongside a **Python-based graphical user interface** for real-world database operations.

The system manages:
- Student members
- Professional examinations
- Examination entries and results
- Entry cancellations and audit tracking

The application was built as part of a university coursework submission, with an emphasis on **data integrity, SQL transactions, and professional presentation**.

---

## Key Features

- **Fully normalised PostgreSQL schema** with constraints and integrity rules
- **All required database transactions implemented and tested**
- **Interactive Python GUI** for database operations
- **Safe handling of edge cases** (duplicate entries, invalid deletions, invalid grades)
- **Audit trail** for cancelled examination entries
- Designed to reflect **real-world database systems**

---

## Transactions of Interest (Functionality)

The system supports the following operations:

| Code | Description |
|----|------------|
| A | Insert new student members |
| B | Insert new examinations |
| C | Delete a student and automatically cancel their entries |
| D | Delete an examination (only if no active entries exist) |
| E | Insert examination entries with validation rules |
| F | Update examination grades |
| G | Generate an examination timetable for a student |
| H | Generate results for all students across all exams |
| I | Generate results for a specific examination |

Each transaction was **individually tested in pgAdmin** and demonstrated through the GUI.

---

## Database Schema

**Tables:**
- `student(sno, sname, semail)`
- `exam(excode, extitle, exlocation, exdate, extime)`
- `entry(eno, excode, sno, egrade)`
- `cancel(eno, excode, sno, cdate, cuser)`

**Highlights:**
- Primary and foreign key constraints
- Domain validation (dates, times, grades)
- Referential integrity enforcement
- Cancellation logging via a dedicated table

---

## Graphical User Interface

The Python GUI (built using **Tkinter**) allows users to:

- Insert and delete students and examinations
- Register students for examinations
- Update grades securely
- View timetables and results
- Interact with the PostgreSQL database without writing SQL manually

This mirrors how **non-technical staff** might interact with a real production system.

---

## Tech Stack

- **PostgreSQL** – database engine
- **SQL** – DDL, DML, constraints, queries
- **Python 3**
- **Tkinter** – GUI framework
- **psycopg2** – PostgreSQL database adapter
- **pgAdmin** – testing and validation

---

## Project Structure
| Path / File | Description |
|------------|------------|
| `100432626_DDL.sql` | Database schema, constraints, triggers |
| `100432626_own_data.sql` | Test data for transactions |
| `PySQL.py` | Database connection and SQL execution |
| `Tkinter.py` | GUI components and event handling |
| `100432626_GUI_source_code.py` | Integrated GUI application |
| `pw.txt` | Local password file (not for production use) |
| `100432626_Assessment_template.docx` | Completed assessment template |
| `100432626_GUI_demo.mp4` | GUI demonstration video |
| `README.md` | Project documentation |

---

## 🚀 Setup & Usage

1. **Create the database**
```sql
   CREATE DATABASE cmps;
```
2.	**Run schema & data scripts**
```sql
psql -d cmps -f 100432626_DDL.sql
psql -d cmps -f 100432626_own_data.sql
```
3. **Install dependencies**
```sql
   pip install psycopg2
```
4. **Run the GUI**
```sql
python 100432626_GUI_source_code.py
```
Ensure PostgreSQL is running and credentials are correctly set.

⸻

## Academic Context

This project was completed as part of:

CMP-4010B / CMP-7025B – Database Systems
University coursework focusing on:
	•	SQL problem solving
	•	Database design & integrity
	•	Transaction handling
	•	Professional software presentation

While developed for assessment, the project reflects industry-relevant database design patterns and user-facing system interaction.

⸻

## Skills Demonstrated
	•	Relational database design
	•	SQL (DDL, DML, transactions)
	•	PostgreSQL constraints & integrity
	•	Python–database integration
	•	GUI development
	•	Testing & validation
	•	Professional documentation

⸻

## License

This project is shared for educational and portfolio purposes.
Please do not submit this work (or derivatives) as your own for academic assessment.

⸻

## Acknowledgements

Thanks to the CMPS coursework specification for providing a realistic and practical database problem space.
