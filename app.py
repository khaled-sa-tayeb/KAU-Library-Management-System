from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn
import webbrowser

app = FastAPI(
    title="KAU Library Management System",
    description="Comprehensive University Library Management System with Modern UI.",
    version="3.8.3"
)

# ==================== 1. Pydantic Models ====================

class Employee(BaseModel):
    employee_id: int
    employee_name: str
    position: str
    starting_time: str
    leaving_time: str
    phone_no: int

class Student(BaseModel):
    student_id: int
    student_name: str
    phone_no: int
    degree: Optional[str] = None
    email: str
    age: int

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
    return_status: str

class AuthorsList(BaseModel):
    book_id: int
    author_name: str


# ==================== 2. Mock Databases ====================

fake_employees_db = [
    {"employee_id": 153692, "employee_name": "Turki Aghamdi", "position": "Director General", "starting_time": "8:00 AM", "leaving_time": "2:00 PM", "phone_no": 556784390},
    {"employee_id": 167005, "employee_name": "Hussain Ali", "position": "Department Manager", "starting_time": "8:00 AM", "leaving_time": "2:00 PM", "phone_no": 552348720},
    {"employee_id": 168112, "employee_name": "Khaled Salem", "position": "Senior Librarian", "starting_time": "9:00 AM", "leaving_time": "3:00 PM", "phone_no": 551122334},
    {"employee_id": 169223, "employee_name": "Fahad Alotaibi", "position": "Assistant Librarian", "starting_time": "8:30 AM", "leaving_time": "2:30 PM", "phone_no": 554433221},
    {"employee_id": 170334, "employee_name": "Mohammed Alghamdi", "position": "System Administrator", "starting_time": "8:00 AM", "leaving_time": "4:00 PM", "phone_no": 558899001}
]

fake_students_db = [
    {"student_id": 2245343, "student_name": "Anas Alharbi", "phone_no": 553428597, "degree": "Bachelor", "email": "Anas02@gmail.com", "age": 21},
    {"student_id": 2256578, "student_name": "Ali Alshahri", "phone_no": 552740825, "degree": "Bachelor", "email": "Ali22@gmail.com", "age": 20},
    {"student_id": 2267890, "student_name": "Salem Al-Otaibi", "phone_no": 551122334, "degree": "Master", "email": "Salem@gmail.com", "age": 24},
    {"student_id": 2278901, "student_name": "Rashed Al-Dosari", "phone_no": 554455667, "degree": "Bachelor", "email": "Rashed@yahoo.com", "age": 22},
    {"student_id": 2289012, "student_name": "Hassan Al-Ghamdi", "phone_no": 557788990, "degree": "PhD", "email": "Hassan@hotmail.com", "age": 28}
]

fake_books_db = [
    {"book_id": 12034, "book_name": "Language and Mind", "isbn": 9780521674935, "edition": 3, "genre_code": 1, "bookshelf_id": 43},
    {"book_id": 41134, "book_name": "Fundamentals of Database Systems", "isbn": 9780321415066, "edition": 5, "genre_code": 4, "bookshelf_id": 221},
    {"book_id": 50123, "book_name": "Artificial Intelligence: A Modern Approach", "isbn": 9780136042594, "edition": 4, "genre_code": 4, "bookshelf_id": 221},
    {"book_id": 50234, "book_name": "Clean Code: A Handbook of Agile Software", "isbn": 9780132350884, "edition": 1, "genre_code": 4, "bookshelf_id": 43}
]

fake_loans_db = [
    {"loan_id": 230524875, "loan_date": "2023-08-06", "due_date": "2023-08-20", "student_id": 2245343, "employee_id": 167005, "book_id": 12034},
    {"loan_id": 230463091, "loan_date": "2023-08-09", "due_date": "2023-08-23", "student_id": 2256578, "employee_id": 153692, "book_id": 41134}
]

fake_genres_db = [
    {"genre_code": 1, "genre_name": "Languages and Linguistics", "section_id": 1},
    {"genre_code": 4, "genre_name": "Technology and Computer Science", "section_id": 3}
]

fake_bookshelves_db = [
    {"bookshelf_id": 43, "bookshelf_code": "A-043", "section_id": 1},
    {"bookshelf_id": 221, "bookshelf_code": "D-022", "section_id": 3}
]

fake_sections_db = [
    {"section_id": 1, "location": "First-Floor - Wing A", "manager_id": 167005},
    {"section_id": 3, "location": "Second-Floor - Tech Lab", "manager_id": 170334}
]

fake_loan_history_db = [
    {"loan_id": 230524875, "book_id": 12034, "return_status": "Returned"},
    {"loan_id": 230463091, "book_id": 41134, "return_status": "Active"}
]

fake_authors_list_db = [
    {"book_id": 12034, "author_name": "Noam Chomsky"},
    {"book_id": 41134, "author_name": "Ramez Elmasri"},
    {"book_id": 50123, "author_name": "Stuart Russell"},
    {"book_id": 50234, "author_name": "Robert C. Martin"}
]

recent_activities = [
    {"time": "2026-08-27 01:34", "action": "Removed logo container and cleaned up interface header successfully."}
]


# ==================== 3. HTML Dashboard Interface ====================

@app.get("/", response_class=HTMLResponse)
def employee_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>KAU Advanced Library Management System</title>
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #0f172a;
                --primary-light: #1e293b;
                --accent: #0ea5e9;
                --accent-hover: #0284c7;
                --success: #10b981;
                --danger: #ef4444;
                --warning: #f59e0b;
                --bg-main: #f1f5f9;
                --card-bg: rgba(255, 255, 255, 0.92);
                --text-main: #334155;
                --text-muted: #64748b;
                --border-color: #cbd5e1;
                --radius: 14px;
                --shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
                --transition: all 0.3s ease;
            }

            body {
                font-family: 'Cairo', sans-serif;
                background: linear-gradient(rgba(15, 23, 42, 0.75), rgba(15, 23, 42, 0.85)), 
                            url('https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=1920&q=80') no-repeat center center fixed;
                background-size: cover;
                color: var(--text-main);
                margin: 0;
                padding: 40px 20px;
            }

            .container {
                max-width: 1200px;
                margin: auto;
            }

            .header-banner {
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
                color: white;
                padding: 35px 40px;
                border-radius: var(--radius);
                text-align: center;
                margin-bottom: 30px;
                box-shadow: var(--shadow);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }

            .header-banner h1 {
                margin: 0 0 10px 0;
                font-size: 30px;
                font-weight: 700;
                letter-spacing: -0.5px;
            }

            .header-banner p {
                margin: 0;
                color: #94a3b8;
                font-size: 14px;
            }

            .section-box {
                background: var(--card-bg);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.4);
                padding: 30px;
                margin-bottom: 25px;
                border-radius: var(--radius);
                box-shadow: var(--shadow);
                transition: var(--transition);
            }

            .section-box:hover {
                transform: translateY(-2px);
                box-shadow: 0 25px 30px -5px rgba(0, 0, 0, 0.15);
            }

            .section-box h3 {
                margin-top: 0;
                margin-bottom: 20px;
                color: var(--primary);
                font-size: 19px;
                font-weight: 700;
                display: flex;
                align-items: center;
                gap: 10px;
                border-bottom: 2px solid var(--border-color);
                padding-bottom: 12px;
            }

            label {
                display: block;
                margin-top: 12px;
                margin-bottom: 6px;
                font-weight: 600;
                font-size: 12px;
                color: var(--text-muted);
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            input, select {
                width: 100%;
                padding: 11px 14px;
                background-color: #ffffff;
                border: 1px solid var(--border-color);
                border-radius: 8px;
                box-sizing: border-box;
                font-family: 'Cairo', sans-serif;
                font-size: 14px;
                color: var(--text-main);
                transition: var(--transition);
            }

            input:focus, select:focus {
                outline: none;
                border-color: var(--accent);
                background-color: #ffffff;
                box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.2);
            }

            button {
                background-color: var(--accent);
                color: white;
                border: none;
                padding: 12px 20px;
                margin-top: 18px;
                cursor: pointer;
                border-radius: 8px;
                font-family: 'Cairo', sans-serif;
                font-size: 14px;
                font-weight: 600;
                width: 100%;
                transition: var(--transition);
                box-shadow: 0 4px 6px -1px rgba(14, 165, 233, 0.2);
            }

            button:hover {
                background-color: var(--accent-hover);
                transform: translateY(-1px);
            }

            .btn-success { background-color: var(--success); box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.2); }
            .btn-success:hover { background-color: #059669; }

            .btn-danger { background-color: var(--danger); box-shadow: 0 4px 6px -1px rgba(239, 68, 68, 0.2); }
            .btn-danger:hover { background-color: #dc2626; }

            .btn-warning { background-color: var(--warning); box-shadow: 0 4px 6px -1px rgba(245, 158, 11, 0.2); }
            .btn-warning:hover { background-color: #d97706; }

            .result {
                margin-top: 15px;
                padding: 12px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
                text-align: center;
            }
            .success-msg { background-color: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }
            .error-msg { background-color: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }

            .table-container {
                max-height: 280px;
                overflow-y: auto;
                margin-top: 15px;
                border: 1px solid var(--border-color);
                border-radius: 8px;
                background: white;
            }

            table {
                width: 100%;
                border-collapse: collapse;
                text-align: center;
                font-size: 13px;
            }

            th, td {
                padding: 10px 12px;
                border-bottom: 1px solid var(--border-color);
            }

            th {
                background-color: #f8fafc;
                color: var(--primary);
                font-weight: 700;
                position: sticky;
                top: 0;
                z-index: 10;
            }

            tr:hover td {
                background-color: #f1f5f9;
            }

            .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
            .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }
            .grid-4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 15px; }

            .activity-log {
                background: #ffffff;
                border: 1px solid var(--border-color);
                color: var(--text-muted);
                padding: 12px;
                border-radius: 8px;
                font-size: 13px;
                max-height: 130px;
                overflow-y: auto;
                font-family: monospace;
            }
            
            .sub-panel {
                background: rgba(241, 245, 249, 0.7);
                padding: 18px;
                border-radius: 8px;
                border: 1px solid var(--border-color);
                margin-top: 15px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Header Banner (No Logo) -->
            <div class="header-banner">
                <h1>📚 KAU Advanced Library Management System</h1>
                <p>King Abdulaziz University - Central Library Enterprise Dashboard</p>
            </div>

            <!-- Activity Log Section -->
            <div class="section-box">
                <h3>📋 System Activity Log</h3>
                <div id="activityLogBox" class="activity-log">Loading logs...</div>
                <button type="button" class="btn-warning" onclick="loadActivities()" style="width: auto; padding: 6px 14px; margin-top: 10px;">Refresh Log</button>
            </div>

            <!-- Advanced Query & Filter Hub -->
            <div class="section-box">
                <h3>⚙️ Advanced Query & Filter Hub</h3>
                
                <div class="grid-2">
                    <div>
                        <label>Target Table</label>
                        <select id="queryTarget" onchange="onTargetTableChange()">
                            <option value="students">Students</option>
                            <option value="books">Books</option>
                            <option value="employees">Employees</option>
                            <option value="loans">Loans</option>
                            <option value="genres">Genres</option>
                            <option value="bookshelves">Bookshelves</option>
                            <option value="sections">Sections</option>
                            <option value="loan_history">Loan History</option>
                            <option value="authors_list">Authors List</option>
                        </select>
                    </div>
                    <div>
                        <label>&nbsp;</label>
                        <button type="button" style="margin-top: 0;" onclick="executeAdvancedQuery()">Reset Filter & View All</button>
                    </div>
                </div>

                <div class="grid-4 sub-panel">
                    <div>
                        <label>Field</label>
                        <select id="queryField"></select>
                    </div>
                    <div>
                        <label>Operator</label>
                        <select id="queryOperator">
                            <option value="equals">Equals (=)</option>
                            <option value="not_equals">Not Equals (!=)</option>
                            <option value="greater_than">Greater Than (&gt;)</option>
                            <option value="less_than">Less Than (&lt;)</option>
                            <option value="contains">Contains</option>
                        </select>
                    </div>
                    <div>
                        <label>Value</label>
                        <input type="text" id="queryValue" placeholder="Enter value...">
                    </div>
                    <div>
                        <label>&nbsp;</label>
                        <button type="button" class="btn-success" style="margin-top: 0;" onclick="executeAdvancedQuery()">Apply Filter 🔍</button>
                    </div>
                </div>

                <div class="table-container">
                    <table id="queryTable">
                        <thead><tr id="queryHeaders"><th>Data</th></tr></thead>
                        <tbody id="queryBody"><tr><td>Table data will appear here...</td></tr></tbody>
                    </table>
                </div>
            </div>

            <!-- New Loan Registration (Auto Loan ID) -->
            <div class="section-box">
                <h3>📖 Register New Loan (Auto-Generated Loan ID)</h3>
                <div class="grid-3">
                    <div>
                        <label>Student ID</label>
                        <input type="number" id="loan_student_id" placeholder="e.g., 2245343">
                    </div>
                    <div>
                        <label>Employee ID</label>
                        <input type="number" id="loan_employee_id" placeholder="e.g., 168112">
                    </div>
                    <div>
                        <label>Book ID</label>
                        <input type="number" id="loan_book_id" placeholder="e.g., 12034">
                    </div>
                </div>
                <div class="grid-2" style="margin-top: 5px;">
                    <div>
                        <label>Loan Date</label>
                        <input type="date" id="loan_date">
                    </div>
                    <div>
                        <label>Due Date</label>
                        <input type="date" id="due_date">
                    </div>
                </div>
                <button type="button" class="btn-success" onclick="submitNewLoan()">Confirm & Create Loan Automatically</button>
                <div id="loanMessage" class="result" style="display: none;"></div>
            </div>

            <!-- Generic Insert Section -->
            <div class="section-box">
                <h3>➕ Generic Record Insertion</h3>
                <div class="grid-2">
                    <div>
                        <label>Target Section</label>
                        <select id="insertTarget" onchange="renderInsertForm()">
                            <option value="students">Add New Student</option>
                            <option value="books">Add New Book</option>
                            <option value="employees">Add New Employee</option>
                            <option value="genres">Add New Genre</option>
                            <option value="bookshelves">Add New Bookshelf</option>
                            <option value="sections">Add New Section</option>
                            <option value="loan_history">Add Loan History</option>
                            <option value="authors_list">Add Book Author</option>
                        </select>
                    </div>
                    <div>
                        <label>&nbsp;</label>
                        <button type="button" class="btn-success" style="margin-top: 0;" onclick="submitGenericInsert()">Save Record</button>
                    </div>
                </div>
                <div id="dynamicFormFields" class="grid-3 sub-panel"></div>
                <div id="insertMessage" class="result" style="display: none;"></div>
            </div>

            <!-- Deletion Panel -->
            <div class="section-box">
                <h3>🗑️ Delete Record</h3>
                <div class="grid-2">
                    <div>
                        <label>Target Table</label>
                        <select id="deleteTarget">
                            <option value="students">Student (Student ID)</option>
                            <option value="books">Book (Book ID)</option>
                            <option value="employees">Employee (Employee ID)</option>
                            <option value="loans">Loan (Loan ID)</option>
                            <option value="authors_list">Author (Book ID)</option>
                        </select>
                    </div>
                    <div>
                        <label>Enter Identifier (ID)</label>
                        <input type="number" id="deleteId" placeholder="e.g., 2245343">
                    </div>
                </div>
                <button type="button" class="btn-danger" onclick="executeDelete()">Permanently Delete Record</button>
                <div id="deleteMessage" class="result" style="display: none;"></div>
            </div>
        </div>

        <script>
            window.onload = function() {
                onTargetTableChange();
                loadActivities();
                renderInsertForm();
                document.getElementById('loan_date').valueAsDate = new Date();
                let nextWeek = new Date();
                nextWeek.setDate(nextWeek.getDate() + 14);
                document.getElementById('due_date').valueAsDate = nextWeek;
            };

            const tableFields = {
                "students": ["student_id", "student_name", "phone_no", "degree", "email", "age"],
                "books": ["book_id", "book_name", "isbn", "edition", "genre_code", "bookshelf_id"],
                "employees": ["employee_id", "employee_name", "position", "starting_time", "leaving_time", "phone_no"],
                "loans": ["loan_id", "loan_date", "due_date", "student_id", "employee_id", "book_id"],
                "genres": ["genre_code", "genre_name", "section_id"],
                "bookshelves": ["bookshelf_id", "bookshelf_code", "section_id"],
                "sections": ["section_id", "location", "manager_id"],
                "loan_history": ["loan_id", "book_id", "return_status"],
                "authors_list": ["book_id", "author_name"]
            };

            function onTargetTableChange() {
                const target = document.getElementById("queryTarget").value;
                const fieldSelect = document.getElementById("queryField");
                fieldSelect.innerHTML = "";
                
                tableFields[target].forEach(f => {
                    fieldSelect.innerHTML += `<option value="${f}">${f}</option>`;
                });
                
                executeAdvancedQuery();
            }

            function executeAdvancedQuery() {
                const target = document.getElementById("queryTarget").value;
                const field = document.getElementById("queryField").value;
                const operator = document.getElementById("queryOperator").value;
                const rawVal = document.getElementById("queryValue").value.trim();

                fetch(`/${target}`)
                .then(res => res.json())
                .then(data => {
                    let filtered = data.filter(row => {
                        if (!rawVal) return true;

                        let cellVal = row[field];
                        if (cellVal === undefined || cellVal === null) return false;

                        let targetVal = rawVal;
                        if (!isNaN(cellVal) && !isNaN(rawVal)) {
                            cellVal = Number(cellVal);
                            targetVal = Number(rawVal);
                        } else {
                            cellVal = String(cellVal).toLowerCase();
                            targetVal = String(rawVal).toLowerCase();
                        }

                        switch(operator) {
                            case "equals": return cellVal === targetVal;
                            case "not_equals": return cellVal !== targetVal;
                            case "greater_than": return cellVal > targetVal;
                            case "less_than": return cellVal < targetVal;
                            case "contains": return String(cellVal).includes(String(targetVal));
                            default: return true;
                        }
                    });

                    const thead = document.getElementById("queryHeaders");
                    const tbody = document.getElementById("queryBody");
                    thead.innerHTML = "";
                    tbody.innerHTML = "";

                    if (filtered.length === 0) {
                        tbody.innerHTML = `<tr><td colspan="6" style="color: var(--danger);">No matching records found.</td></tr>`;
                        return;
                    }

                    const keys = Object.keys(filtered[0]);
                    keys.forEach(k => thead.innerHTML += `<th>${k}</th>`);

                    filtered.forEach(row => {
                        let tr = "<tr>";
                        keys.forEach(k => tr += `<td>${row[k] !== null ? row[k] : ''}</td>`);
                        tr += "</tr>";
                        tbody.innerHTML += tr;
                    });
                });
            }

            function renderInsertForm() {
                const target = document.getElementById("insertTarget").value;
                const container = document.getElementById("dynamicFormFields");
                container.innerHTML = "";

                tableFields[target].forEach(field => {
                    container.innerHTML += `
                        <div>
                            <label>${field}</label>
                            <input type="text" id="ins_${field}" placeholder="Enter ${field}">
                        </div>
                    `;
                });
            }

            function submitGenericInsert() {
                const target = document.getElementById("insertTarget").value;
                const fields = tableFields[target];
                let payload = {};

                fields.forEach(field => {
                    let val = document.getElementById(`ins_${field}`).value.trim();
                    if (!isNaN(val) && val !== "") {
                        payload[field] = val.includes(".") ? parseFloat(val) : parseInt(val);
                    } else {
                        payload[field] = val;
                    }
                });

                const msgDiv = document.getElementById("insertMessage");

                fetch(`/${target}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                })
                .then(async res => {
                    const resJson = await res.json();
                    msgDiv.style.display = "block";
                    if (res.ok) {
                        msgDiv.className = "result success-msg";
                        msgDiv.innerText = "Record added successfully!";
                        loadActivities();
                        executeAdvancedQuery();
                    } else {
                        msgDiv.className = "result error-msg";
                        msgDiv.innerText = "Insertion failed: " + (resJson.detail || "Check inputs.");
                    }
                });
            }

            function submitNewLoan() {
                const payload = {
                    loan_date: document.getElementById("loan_date").value,
                    due_date: document.getElementById("due_date").value,
                    student_id: parseInt(document.getElementById("loan_student_id").value),
                    employee_id: parseInt(document.getElementById("loan_employee_id").value),
                    book_id: parseInt(document.getElementById("loan_book_id").value)
                };

                const msgDiv = document.getElementById("loanMessage");

                fetch("/loans", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                })
                .then(async res => {
                    const resJson = await res.json();
                    msgDiv.style.display = "block";
                    if (res.ok) {
                        msgDiv.className = "result success-msg";
                        msgDiv.innerText = "Loan registered successfully with Auto ID: " + resJson.loan_id;
                        loadActivities();
                        executeAdvancedQuery();
                    } else {
                        msgDiv.className = "result error-msg";
                        msgDiv.innerText = "Loan registration failed: " + (resJson.detail || "Verify data.");
                    }
                });
            }

            function loadActivities() {
                fetch("/activities")
                .then(res => res.json())
                .then(data => {
                    const logBox = document.getElementById("activityLogBox");
                    logBox.innerHTML = "";
                    data.reverse().forEach(act => {
                        logBox.innerHTML += `<div>⏱️ [${act.time}] - ${act.action}</div>`;
                    });
                });
            }

            function executeDelete() {
                const target = document.getElementById("deleteTarget").value;
                const id = document.getElementById("deleteId").value.trim();
                const msgDiv = document.getElementById("deleteMessage");

                if (!id) {
                    msgDiv.style.display = "block";
                    msgDiv.className = "result error-msg";
                    msgDiv.innerText = "Please enter the target identifier (ID).";
                    return;
                }

                if (!confirm("Are you sure you want to delete this record?")) return;

                fetch(`/${target}/${id}`, { method: "DELETE" })
                .then(async response => {
                    const resJson = await response.json();
                    msgDiv.style.display = "block";
                    if (response.ok) {
                        msgDiv.className = "result success-msg";
                        msgDiv.innerText = resJson.message;
                        document.getElementById("deleteId").value = "";
                        executeAdvancedQuery();
                        loadActivities();
                    } else {
                        msgDiv.className = "result error-msg";
                        msgDiv.innerText = "Deletion failed: " + (resJson.detail || "Record not found.");
                    }
                });
            }
        </script>
    </body>
    </html>
    """


# ==================== 4. API Endpoints ====================

@app.get("/activities")
def get_activities(): return recent_activities

@app.get("/employees", response_model=List[Employee])
def get_employees(): return fake_employees_db

@app.get("/students", response_model=List[Student])
def get_students(): return fake_students_db

@app.get("/books", response_model=List[Book])
def get_books(): return fake_books_db

@app.get("/loans", response_model=List[Loan])
def get_loans(): return fake_loans_db

@app.get("/genres", response_model=List[Genre])
def get_genres(): return fake_genres_db

@app.get("/bookshelves", response_model=List[Bookshelf])
def get_bookshelves(): return fake_bookshelves_db

@app.get("/sections", response_model=List[Section])
def get_sections(): return fake_sections_db

@app.get("/loan_history", response_model=List[LoanHistory])
def get_loan_history(): return fake_loan_history_db

@app.get("/authors_list", response_model=List[AuthorsList])
def get_authors_list(): return fake_authors_list_db


# --- POST Endpoints (With Auto Loan ID Generation) ---

@app.post("/students", response_model=Student)
def add_student(item: Student):
    if any(s["student_id"] == item.student_id for s in fake_students_db):
        raise HTTPException(status_code=400, detail="Student ID already exists.")
    fake_students_db.append(item.dict())
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Added student: {item.student_name}"})
    return item

@app.post("/books", response_model=Book)
def add_book(item: Book):
    if any(b["book_id"] == item.book_id for b in fake_books_db):
        raise HTTPException(status_code=400, detail="Book ID already exists.")
    fake_books_db.append(item.dict())
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Added book: {item.book_name}"})
    return item

@app.post("/employees", response_model=Employee)
def add_employee(item: Employee):
    if any(e["employee_id"] == item.employee_id for e in fake_employees_db):
        raise HTTPException(status_code=400, detail="Employee ID already exists.")
    fake_employees_db.append(item.dict())
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Added employee: {item.employee_name}"})
    return item

@app.post("/loans", response_model=Loan)
def add_loan(item: Loan):
    if not item.loan_id:
        max_id = max([l["loan_id"] for l in fake_loans_db], default=230400000)
        item.loan_id = max_id + 1

    if any(l["loan_id"] == item.loan_id for l in fake_loans_db):
        raise HTTPException(status_code=400, detail="Loan ID already exists.")
    
    fake_loans_db.append(item.dict())
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Added auto-generated loan ID: {item.loan_id}"})
    return item

@app.post("/genres", response_model=Genre)
def add_genre(item: Genre):
    if any(g["genre_code"] == item.genre_code for g in fake_genres_db):
        raise HTTPException(status_code=400, detail="Genre code already exists.")
    fake_genres_db.append(item.dict())
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Added genre ID: {item.genre_code}"})
    return item

@app.post("/bookshelves", response_model=Bookshelf)
def add_bookshelf(item: Bookshelf):
    if any(b["bookshelf_id"] == item.bookshelf_id for b in fake_bookshelves_db):
        raise HTTPException(status_code=400, detail="Bookshelf ID already exists.")
    fake_bookshelves_db.append(item.dict())
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Added bookshelf ID: {item.bookshelf_id}"})
    return item

@app.post("/sections", response_model=Section)
def add_section(item: Section):
    if any(s["section_id"] == item.section_id for s in fake_sections_db):
        raise HTTPException(status_code=400, detail="Section ID already exists.")
    fake_sections_db.append(item.dict())
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Added section ID: {item.section_id}"})
    return item

@app.post("/loan_history", response_model=LoanHistory)
def add_loan_history(item: LoanHistory):
    fake_loan_history_db.append(item.dict())
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Added loan history record for loan ID: {item.loan_id}"})
    return item

@app.post("/authors_list", response_model=AuthorsList)
def add_author(item: AuthorsList):
    fake_authors_list_db.append(item.dict())
    recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Added author for book ID: {item.book_id}"})
    return item


# --- DELETE Endpoints ---

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    for i, st in enumerate(fake_students_db):
        if st["student_id"] == student_id:
            del fake_students_db[i]
            recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Deleted student ID: {student_id}"})
            return {"message": f"Student with ID {student_id} deleted successfully."}
    raise HTTPException(status_code=404, detail="Student not found.")

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    for i, bk in enumerate(fake_books_db):
        if bk["book_id"] == book_id:
            del fake_books_db[i]
            recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Deleted book ID: {book_id}"})
            return {"message": f"Book with ID {book_id} deleted successfully."}
    raise HTTPException(status_code=404, detail="Book not found.")

@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    for i, emp in enumerate(fake_employees_db):
        if emp["employee_id"] == employee_id:
            del fake_employees_db[i]
            recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Deleted employee ID: {employee_id}"})
            return {"message": f"Employee with ID {employee_id} deleted successfully."}
    raise HTTPException(status_code=404, detail="Employee not found.")

@app.delete("/loans/{loan_id}")
def delete_loan(loan_id: int):
    for i, ln in enumerate(fake_loans_db):
        if ln["loan_id"] == loan_id:
            del fake_loans_db[i]
            recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Deleted loan ID: {loan_id}"})
            return {"message": f"Loan record {loan_id} deleted successfully."}
    raise HTTPException(status_code=404, detail="Loan record not found.")

@app.delete("/authors_list/{book_id}")
def delete_author(book_id: int):
    for i, aut in enumerate(fake_authors_list_db):
        if aut["book_id"] == book_id:
            del fake_authors_list_db[i]
            recent_activities.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": f"Deleted author for book ID: {book_id}"})
            return {"message": f"Author record for book {book_id} deleted successfully."}
    raise HTTPException(status_code=404, detail="Author record not found.")


# ==================== 5. Application Execution ====================
if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:8000/")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)