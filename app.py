from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from io import BytesIO
import sqlite3
import os
import uvicorn
import webbrowser
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "library.db")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

with open(os.path.join(TEMPLATES_DIR, "dashboard.html"), "r", encoding="utf-8") as f:
    DASHBOARD_HTML = f.read()

app = FastAPI(
    title="KAU Library Management System",
    description="Comprehensive University Library Management System with Modern UI, backed by a real SQLite database.",
    version="5.0.0"
)

STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ==================== 1. Pydantic Models (with business-rule validation) ====================

class Employee(BaseModel):
    employee_id: int
    employee_name: str
    position: str
    starting_time: Optional[str] = None
    leaving_time: Optional[str] = None
    phone_no: int
    age: int = Field(..., ge=18, le=60, description="Employee age must be between 18 and 60")

class Student(BaseModel):
    student_id: int
    student_name: str
    phone_no: int
    degree: Optional[str] = None
    email: str
    age: int = Field(..., gt=15, description="Student age must be over 15")

class Book(BaseModel):
    book_id: int
    book_name: str
    isbn: int
    edition: int
    genre_code: int
    bookshelf_id: int

class Loan(BaseModel):
    loan_id: Optional[int] = None
    loan_date: str
    due_date: str
    student_id: int
    employee_id: int
    book_id: int

class Genre(BaseModel):
    genre_code: int
    genre_name: str
    section_id: int

class Bookshelf(BaseModel):
    bookshelf_id: int
    bookshelf_code: str
    section_id: int

class Section(BaseModel):
    section_id: int
    location: str
    manager_id: int

class LoanHistory(BaseModel):
    loan_id: int
    book_id: int
    return_status: str = "Active"

class AuthorsList(BaseModel):
    book_id: int
    author_name: str


# ==================== 2. Real SQLite Database Layer ====================
# Replaces the old in-memory Python lists with a persistent SQLite database.
# Foreign keys + CHECK constraints enforce the same business rules described
# in the project's design report (Sections 2.2 and 7).

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def friendly_integrity_error(e: sqlite3.IntegrityError) -> str:
    msg = str(e)
    if "UNIQUE constraint failed: Section.manager_id" in msg:
        return "This employee already manages another section. A manager can only manage one section."
    if "UNIQUE constraint failed" in msg:
        return "A record with this ID already exists."
    if "FOREIGN KEY constraint failed" in msg:
        return "This record references an ID that doesn't exist yet (check related IDs such as Section, Genre, Bookshelf, Employee, Student or Book)."
    if "CHECK constraint failed" in msg:
        return "This violates a business rule (e.g. age range 18-60/15+, or loan duration over 14 days)."
    return f"Database error: {msg}"


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS Employee (
        employee_id     INTEGER PRIMARY KEY,
        employee_name   TEXT NOT NULL,
        position        TEXT NOT NULL,
        starting_time   TEXT,
        leaving_time    TEXT,
        phone_no        INTEGER NOT NULL,
        age             INTEGER NOT NULL CHECK (age BETWEEN 18 AND 60)
    );

    CREATE TABLE IF NOT EXISTS Section (
        section_id      INTEGER PRIMARY KEY,
        location        TEXT,
        manager_id      INTEGER NOT NULL UNIQUE,
        FOREIGN KEY (manager_id) REFERENCES Employee(employee_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Bookshelf (
        bookshelf_id    INTEGER PRIMARY KEY,
        bookshelf_code  TEXT,
        section_id      INTEGER NOT NULL,
        FOREIGN KEY (section_id) REFERENCES Section(section_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Genre (
        genre_code      INTEGER PRIMARY KEY,
        genre_name      TEXT NOT NULL,
        section_id      INTEGER NOT NULL,
        FOREIGN KEY (section_id) REFERENCES Section(section_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Student (
        student_id      INTEGER PRIMARY KEY,
        student_name    TEXT NOT NULL,
        phone_no        INTEGER NOT NULL,
        degree          TEXT,
        email           TEXT NOT NULL,
        age             INTEGER NOT NULL CHECK (age > 15)
    );

    CREATE TABLE IF NOT EXISTS Book (
        book_id         INTEGER PRIMARY KEY,
        book_name       TEXT NOT NULL,
        isbn            INTEGER NOT NULL,
        edition         INTEGER,
        genre_code      INTEGER NOT NULL,
        bookshelf_id    INTEGER NOT NULL,
        FOREIGN KEY (genre_code) REFERENCES Genre(genre_code) ON DELETE CASCADE,
        FOREIGN KEY (bookshelf_id) REFERENCES Bookshelf(bookshelf_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Loan (
        loan_id         INTEGER PRIMARY KEY,
        loan_date       TEXT NOT NULL,
        due_date        TEXT NOT NULL,
        student_id      INTEGER NOT NULL,
        employee_id     INTEGER NOT NULL,
        book_id         INTEGER NOT NULL,
        FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE,
        FOREIGN KEY (employee_id) REFERENCES Employee(employee_id) ON DELETE CASCADE,
        FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE,
        CHECK (julianday(due_date) - julianday(loan_date) <= 14)
    );

    CREATE TABLE IF NOT EXISTS Loan_History (
        loan_id         INTEGER NOT NULL,
        book_id         INTEGER NOT NULL,
        return_status   TEXT NOT NULL DEFAULT 'Active',
        PRIMARY KEY (loan_id, book_id),
        FOREIGN KEY (loan_id) REFERENCES Loan(loan_id) ON DELETE CASCADE,
        FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Authors_List (
        book_id         INTEGER NOT NULL,
        author_name     TEXT NOT NULL,
        PRIMARY KEY (book_id, author_name),
        FOREIGN KEY (book_id) REFERENCES Book(book_id) ON DELETE CASCADE
    );
    """)
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM Employee")
    if cur.fetchone()[0] == 0:
        seed_data(conn)

    conn.close()


def seed_data(conn):
 
    cur = conn.cursor()

    cur.executemany(
        "INSERT INTO Employee (employee_id, employee_name, position, starting_time, leaving_time, phone_no, age) VALUES (?,?,?,?,?,?,?)",
        [
            (153692, "Turki Aghamdi", "Director General", "8:00 AM", "2:00 PM", 556784390, 45),
            (167005, "Hussain Ali", "Department Manager", "8:00 AM", "2:00 PM", 552348720, 38),
            (168112, "Khaled Salem", "Senior Librarian", "9:00 AM", "3:00 PM", 551122334, 33),
            (169223, "Fahad Alotaibi", "Assistant Librarian", "8:30 AM", "2:30 PM", 554433221, 27),
            (170334, "Mohammed Alghamdi", "System Administrator", "8:00 AM", "4:00 PM", 558899001, 41),
        ],
    )

    cur.executemany(
        "INSERT INTO Section (section_id, location, manager_id) VALUES (?,?,?)",
        [
            (1, "First-Floor - Wing A", 167005),
            (3, "Second-Floor - Tech Lab", 170334),
        ],
    )

    cur.executemany(
        "INSERT INTO Bookshelf (bookshelf_id, bookshelf_code, section_id) VALUES (?,?,?)",
        [
            (43, "A-043", 1),
            (221, "D-022", 3),
        ],
    )

    cur.executemany(
        "INSERT INTO Genre (genre_code, genre_name, section_id) VALUES (?,?,?)",
        [
            (1, "Languages and Linguistics", 1),
            (4, "Technology and Computer Science", 3),
        ],
    )

    cur.executemany(
        "INSERT INTO Student (student_id, student_name, phone_no, degree, email, age) VALUES (?,?,?,?,?,?)",
        [
            (2245343, "Anas Alharbi", 553428597, "Bachelor", "Anas02@gmail.com", 21),
            (2256578, "Ali Alshahri", 552740825, "Bachelor", "Ali22@gmail.com", 20),
            (2267890, "Salem Al-Otaibi", 551122334, "Master", "Salem@gmail.com", 24),
            (2278901, "Rashed Al-Dosari", 554455667, "Bachelor", "Rashed@yahoo.com", 22),
            (2289012, "Hassan Al-Ghamdi", 557788990, "PhD", "Hassan@hotmail.com", 28),
        ],
    )

    cur.executemany(
        "INSERT INTO Book (book_id, book_name, isbn, edition, genre_code, bookshelf_id) VALUES (?,?,?,?,?,?)",
        [
            (12034, "Language and Mind", 9780521674935, 3, 1, 43),
            (41134, "Fundamentals of Database Systems", 9780321415066, 5, 4, 221),
            (50123, "Artificial Intelligence: A Modern Approach", 9780136042594, 4, 4, 221),
            (50234, "Clean Code: A Handbook of Agile Software", 9780132350884, 1, 4, 43),
        ],
    )

    cur.executemany(
        "INSERT INTO Loan (loan_id, loan_date, due_date, student_id, employee_id, book_id) VALUES (?,?,?,?,?,?)",
        [
            (230524875, "2023-08-06", "2023-08-20", 2245343, 167005, 12034),
            (230463091, "2023-08-09", "2023-08-23", 2256578, 153692, 41134),
        ],
    )

    cur.executemany(
        "INSERT INTO Loan_History (loan_id, book_id, return_status) VALUES (?,?,?)",
        [
            (230524875, 12034, "Returned"),
            (230463091, 41134, "Active"),
        ],
    )

    cur.executemany(
        "INSERT INTO Authors_List (book_id, author_name) VALUES (?,?)",
        [
            (12034, "Noam Chomsky"),
            (41134, "Ramez Elmasri"),
            (50123, "Stuart Russell"),
            (50234, "Robert C. Martin"),
        ],
    )

    conn.commit()


init_db()

recent_activities = [
    {"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": "System started - connected to persistent SQLite database (library.db)."}
]


# ==================== 3. HTML Dashboard Interface ====================

@app.get("/", response_class=HTMLResponse)
def employee_dashboard():
    return DASHBOARD_HTML


# ==================== 4. API Endpoints (SQLite-backed) ====================

@app.get("/activities")
def get_activities():
    return recent_activities


@app.get("/employees", response_model=List[Employee])
def get_employees():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM Employee").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/students", response_model=List[Student])
def get_students():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM Student").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/books", response_model=List[Book])
def get_books():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM Book").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/loans", response_model=List[Loan])
def get_loans():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM Loan").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/genres", response_model=List[Genre])
def get_genres():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM Genre").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/bookshelves", response_model=List[Bookshelf])
def get_bookshelves():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM Bookshelf").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/sections", response_model=List[Section])
def get_sections():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM Section").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/loan_history", response_model=List[LoanHistory])
def get_loan_history():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM Loan_History").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/authors_list", response_model=List[AuthorsList])
def get_authors_list():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM Authors_List").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- POST Endpoints ---

@app.post("/students", response_model=Student)
def add_student(item: Student):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO Student (student_id, student_name, phone_no, degree, email, age) VALUES (?,?,?,?,?,?)",
            (item.student_id, item.student_name, item.phone_no, item.degree, item.email, item.age),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        raise HTTPException(status_code=400, detail=friendly_integrity_error(e))
    conn.close()
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Added student: {item.student_name}"})
    return item


@app.post("/books", response_model=Book)
def add_book(item: Book):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO Book (book_id, book_name, isbn, edition, genre_code, bookshelf_id) VALUES (?,?,?,?,?,?)",
            (item.book_id, item.book_name, item.isbn, item.edition, item.genre_code, item.bookshelf_id),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        raise HTTPException(status_code=400, detail=friendly_integrity_error(e))
    conn.close()
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Added book: {item.book_name}"})
    return item


@app.post("/employees", response_model=Employee)
def add_employee(item: Employee):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO Employee (employee_id, employee_name, position, starting_time, leaving_time, phone_no, age) VALUES (?,?,?,?,?,?,?)",
            (item.employee_id, item.employee_name, item.position, item.starting_time, item.leaving_time, item.phone_no, item.age),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        raise HTTPException(status_code=400, detail=friendly_integrity_error(e))
    conn.close()
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Added employee: {item.employee_name}"})
    return item


@app.post("/loans", response_model=Loan)
def add_loan(item: Loan):
    conn = get_connection()
    cur = conn.cursor()

    # --- Business Rule: loan duration cannot exceed 2 weeks ---
    try:
        d_loan = datetime.strptime(item.loan_date, "%Y-%m-%d")
        d_due = datetime.strptime(item.due_date, "%Y-%m-%d")
    except ValueError:
        conn.close()
        raise HTTPException(status_code=400, detail="Dates must be in YYYY-MM-DD format.")

    if d_due < d_loan:
        conn.close()
        raise HTTPException(status_code=400, detail="Due date cannot be before the loan date.")
    if (d_due - d_loan).days > 14:
        conn.close()
        raise HTTPException(status_code=400, detail="Loan duration cannot exceed 14 days (2 weeks).")

    # --- Business Rule: a student can have at most 3 active loans at the same time ---
    active_count = cur.execute(
        """
        SELECT COUNT(*) FROM Loan L
        JOIN Loan_History H ON L.loan_id = H.loan_id
        WHERE L.student_id = ? AND H.return_status = 'Active'
        """,
        (item.student_id,),
    ).fetchone()[0]
    if active_count >= 3:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"Student {item.student_id} already has {active_count} active loans. Max allowed is 3.",
        )

    # --- Business Rule: a book that is currently on loan cannot be loaned again ---
    book_active = cur.execute(
        """
        SELECT COUNT(*) FROM Loan L
        JOIN Loan_History H ON L.loan_id = H.loan_id
        WHERE L.book_id = ? AND H.return_status = 'Active'
        """,
        (item.book_id,),
    ).fetchone()[0]
    if book_active > 0:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Book {item.book_id} is currently on loan and not available.")

    if not item.loan_id:
        max_id = cur.execute("SELECT MAX(loan_id) FROM Loan").fetchone()[0] or 230400000
        item.loan_id = max_id + 1

    try:
        cur.execute(
            "INSERT INTO Loan (loan_id, loan_date, due_date, student_id, employee_id, book_id) VALUES (?,?,?,?,?,?)",
            (item.loan_id, item.loan_date, item.due_date, item.student_id, item.employee_id, item.book_id),
        )
        cur.execute(
            "INSERT INTO Loan_History (loan_id, book_id, return_status) VALUES (?,?,?)",
            (item.loan_id, item.book_id, "Active"),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=400, detail=friendly_integrity_error(e))

    conn.close()
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Added auto-generated loan ID: {item.loan_id}"})
    return item


@app.post("/genres", response_model=Genre)
def add_genre(item: Genre):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO Genre (genre_code, genre_name, section_id) VALUES (?,?,?)",
            (item.genre_code, item.genre_name, item.section_id),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        raise HTTPException(status_code=400, detail=friendly_integrity_error(e))
    conn.close()
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Added genre ID: {item.genre_code}"})
    return item


@app.post("/bookshelves", response_model=Bookshelf)
def add_bookshelf(item: Bookshelf):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO Bookshelf (bookshelf_id, bookshelf_code, section_id) VALUES (?,?,?)",
            (item.bookshelf_id, item.bookshelf_code, item.section_id),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        raise HTTPException(status_code=400, detail=friendly_integrity_error(e))
    conn.close()
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Added bookshelf ID: {item.bookshelf_id}"})
    return item


@app.post("/sections", response_model=Section)
def add_section(item: Section):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO Section (section_id, location, manager_id) VALUES (?,?,?)",
            (item.section_id, item.location, item.manager_id),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        raise HTTPException(status_code=400, detail=friendly_integrity_error(e))
    conn.close()
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Added section ID: {item.section_id}"})
    return item


@app.post("/loan_history", response_model=LoanHistory)
def add_loan_history(item: LoanHistory):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO Loan_History (loan_id, book_id, return_status) VALUES (?,?,?)",
            (item.loan_id, item.book_id, item.return_status),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        raise HTTPException(status_code=400, detail=friendly_integrity_error(e))
    conn.close()
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Added loan history record for loan ID: {item.loan_id}"})
    return item


@app.post("/authors_list", response_model=AuthorsList)
def add_author(item: AuthorsList):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO Authors_List (book_id, author_name) VALUES (?,?)",
            (item.book_id, item.author_name),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        raise HTTPException(status_code=400, detail=friendly_integrity_error(e))
    conn.close()
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Added author for book ID: {item.book_id}"})
    return item


# --- Excel Export & Import ---

TABLE_SQL_NAME = {
    "students": "Student",
    "books": "Book",
    "employees": "Employee",
    "loans": "Loan",
    "genres": "Genre",
    "bookshelves": "Bookshelf",
    "sections": "Section",
    "loan_history": "Loan_History",
    "authors_list": "Authors_List",
}

TABLE_CONFIG = {
    "students": (Student, add_student),
    "books": (Book, add_book),
    "employees": (Employee, add_employee),
    "loans": (Loan, add_loan),
    "genres": (Genre, add_genre),
    "bookshelves": (Bookshelf, add_bookshelf),
    "sections": (Section, add_section),
    "loan_history": (LoanHistory, add_loan_history),
    "authors_list": (AuthorsList, add_author),
}


@app.get("/export/excel")
def export_excel():

    conn = get_connection()
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for table_key, sql_name in TABLE_SQL_NAME.items():
            df = pd.read_sql_query(f"SELECT * FROM {sql_name}", conn)
            df.to_excel(writer, sheet_name=table_key[:31], index=False)

    conn.close()
    output.seek(0)

    filename = f"KAU_Library_Export_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": "Exported full database to Excel."})

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _clean_excel_value(v):
    """يحوّل أرقام الأعمدة اللي تطلع Float من الإكسل (مثلاً 2245343.0) لأرقام صحيحة، ويحول NaN لـ None."""
    if isinstance(v, float):
        if pd.isna(v):
            return None
        if v.is_integer():
            return int(v)
    return v


@app.post("/import/{table}")
async def import_excel(table: str, file: UploadFile = File(...)):

    if table not in TABLE_CONFIG:
        raise HTTPException(status_code=400, detail=f"Unknown table: {table}")

    model_cls, add_func = TABLE_CONFIG[table]

    try:
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read the Excel file: {e}")

    inserted = 0
    failures = []

    for i, row in df.iterrows():
        row_dict = {k: _clean_excel_value(v) for k, v in row.to_dict().items()}
        excel_row_number = i + 2  # +2: نعوض صف العناوين ونبدأ العد من 1 مثل إكسل

        try:
            item = model_cls(**row_dict)
            add_func(item)
            inserted += 1
        except HTTPException as e:
            failures.append({"row": excel_row_number, "error": e.detail})
        except Exception as e:
            msg = str(e).split("\n")[0] if "\n" not in str(e) else " | ".join(
                line.strip() for line in str(e).split("\n") if line.strip() and "https://" not in line
            )
            failures.append({"row": excel_row_number, "error": msg})

    recent_activities.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "action": f"Imported {inserted} record(s) into '{table}' from Excel ({len(failures)} failed)."
    })

    return {"inserted": inserted, "failed_count": len(failures), "failures": failures[:20]}


# --- DELETE Endpoints ---

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    conn = get_connection()
    cur = conn.execute("DELETE FROM Student WHERE student_id = ?", (student_id,))
    conn.commit()
    found = cur.rowcount > 0
    conn.close()
    if not found:
        raise HTTPException(status_code=404, detail="Student not found.")
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Deleted student ID: {student_id}"})
    return {"message": f"Student with ID {student_id} deleted successfully."}


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    conn = get_connection()
    cur = conn.execute("DELETE FROM Book WHERE book_id = ?", (book_id,))
    conn.commit()
    found = cur.rowcount > 0
    conn.close()
    if not found:
        raise HTTPException(status_code=404, detail="Book not found.")
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Deleted book ID: {book_id}"})
    return {"message": f"Book with ID {book_id} deleted successfully."}


@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    conn = get_connection()
    cur = conn.execute("DELETE FROM Employee WHERE employee_id = ?", (employee_id,))
    conn.commit()
    found = cur.rowcount > 0
    conn.close()
    if not found:
        raise HTTPException(status_code=404, detail="Employee not found.")
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Deleted employee ID: {employee_id}"})
    return {"message": f"Employee with ID {employee_id} deleted successfully."}


@app.delete("/loans/{loan_id}")
def delete_loan(loan_id: int):
    conn = get_connection()
    cur = conn.execute("DELETE FROM Loan WHERE loan_id = ?", (loan_id,))
    conn.commit()
    found = cur.rowcount > 0
    conn.close()
    if not found:
        raise HTTPException(status_code=404, detail="Loan record not found.")
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Deleted loan ID: {loan_id}"})
    return {"message": f"Loan record {loan_id} deleted successfully."}


@app.put("/loans/{loan_id}/return")
def return_loan(loan_id: int):

    conn = get_connection()
    row = conn.execute("SELECT * FROM Loan_History WHERE loan_id = ?", (loan_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Loan history record not found.")
    if row["return_status"] == "Returned":
        conn.close()
        raise HTTPException(status_code=400, detail="This loan is already marked as returned.")

    conn.execute("UPDATE Loan_History SET return_status = 'Returned' WHERE loan_id = ?", (loan_id,))
    conn.commit()
    conn.close()
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Book returned for loan ID: {loan_id}"})
    return {"message": f"Loan {loan_id} marked as returned successfully.", "loan_id": loan_id, "return_status": "Returned"}


@app.delete("/authors_list/{book_id}")
def delete_author(book_id: int):
    conn = get_connection()
    cur = conn.execute("DELETE FROM Authors_List WHERE book_id = ?", (book_id,))
    conn.commit()
    found = cur.rowcount > 0
    conn.close()
    if not found:
        raise HTTPException(status_code=404, detail="Author record not found.")
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Deleted author for book ID: {book_id}"})
    return {"message": f"Author record for book {book_id} deleted successfully."}


@app.delete("/genres/{genre_code}")
def delete_genre(genre_code: int):
    conn = get_connection()
    cur = conn.execute("DELETE FROM Genre WHERE genre_code = ?", (genre_code,))
    conn.commit()
    found = cur.rowcount > 0
    conn.close()
    if not found:
        raise HTTPException(status_code=404, detail="Genre not found.")
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Deleted genre code: {genre_code}"})
    return {"message": f"Genre {genre_code} deleted successfully."}


@app.delete("/bookshelves/{bookshelf_id}")
def delete_bookshelf(bookshelf_id: int):
    conn = get_connection()
    cur = conn.execute("DELETE FROM Bookshelf WHERE bookshelf_id = ?", (bookshelf_id,))
    conn.commit()
    found = cur.rowcount > 0
    conn.close()
    if not found:
        raise HTTPException(status_code=404, detail="Bookshelf not found.")
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Deleted bookshelf ID: {bookshelf_id}"})
    return {"message": f"Bookshelf {bookshelf_id} deleted successfully."}


@app.delete("/sections/{section_id}")
def delete_section(section_id: int):
    conn = get_connection()
    cur = conn.execute("DELETE FROM Section WHERE section_id = ?", (section_id,))
    conn.commit()
    found = cur.rowcount > 0
    conn.close()
    if not found:
        raise HTTPException(status_code=404, detail="Section not found.")
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Deleted section ID: {section_id}"})
    return {"message": f"Section {section_id} deleted successfully."}


@app.delete("/loan_history/{loan_id}")
def delete_loan_history(loan_id: int):
    conn = get_connection()
    cur = conn.execute("DELETE FROM Loan_History WHERE loan_id = ?", (loan_id,))
    conn.commit()
    found = cur.rowcount > 0
    conn.close()
    if not found:
        raise HTTPException(status_code=404, detail="Loan history record not found.")
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Deleted loan history for loan ID: {loan_id}"})
    return {"message": f"Loan history record for loan {loan_id} deleted successfully."}



UPDATABLE_TABLES = {
    "students": ("Student", "student_id", Student),
    "books": ("Book", "book_id", Book),
    "employees": ("Employee", "employee_id", Employee),
    "loans": ("Loan", "loan_id", Loan),
    "genres": ("Genre", "genre_code", Genre),
    "bookshelves": ("Bookshelf", "bookshelf_id", Bookshelf),
    "sections": ("Section", "section_id", Section),
}


@app.put("/{table}/{record_id}")
def update_record(table: str, record_id: int, payload: dict):
    if table not in UPDATABLE_TABLES:
        raise HTTPException(status_code=400, detail=f"Table '{table}' does not support editing here.")

    sql_name, pk_col, model_cls = UPDATABLE_TABLES[table]
    allowed_fields = model_cls.model_fields.keys()
    clean_payload = {k: v for k, v in payload.items() if k in allowed_fields and k != pk_col}

    if not clean_payload:
        raise HTTPException(status_code=400, detail="No valid fields provided to update.")

    conn = get_connection()

    # نجيب الصف الحالي كامل، وندمجه مع التعديلات المطلوبة، عشان نتحقق من سجل كامل
    # صحيح (مو بس الحقول اللي تغيّرت) — وإلا أي تعديل جزئي بيفشل بخطأ "حقل مفقود" بالغلط.
    existing = conn.execute(f"SELECT * FROM {sql_name} WHERE {pk_col} = ?", (record_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Record with {pk_col}={record_id} not found.")

    merged = {**dict(existing), **clean_payload, pk_col: record_id}

    try:
        model_cls(**merged)
    except Exception as e:
        conn.close()
        msg = str(e).split("\n")[0] if "\n" not in str(e) else " | ".join(
            line.strip() for line in str(e).split("\n") if line.strip() and "https://" not in line
        )
        raise HTTPException(status_code=400, detail=msg)

    set_clause = ", ".join(f"{k} = ?" for k in clean_payload.keys())
    values = list(clean_payload.values()) + [record_id]

    try:
        conn.execute(f"UPDATE {sql_name} SET {set_clause} WHERE {pk_col} = ?", values)
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=400, detail=friendly_integrity_error(e))
    conn.close()

    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Updated {table} record ID: {record_id}"})
    return {"message": "Record updated successfully.", pk_col: record_id, **clean_payload}


# ==================== 5. Application Execution ====================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    if not os.environ.get("RENDER") and not os.environ.get("PORT"):
        try:
            webbrowser.open(f"http://127.0.0.1:{port}/")
        except Exception:
            pass
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
