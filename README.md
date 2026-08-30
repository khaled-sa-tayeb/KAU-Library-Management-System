<div align="center">
  <h1>📚 KAU Library Management System</h1>
  <p><b>King Abdulaziz University - Database Course Project</b></p>
  <p>
    <img src="https://img.shields.io/badge/FastAPI-0.100%2B-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">
    <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
    <img src="https://img.shields.io/badge/Status-Live-success?style=for-the-badge" alt="Status">
    <img src="https://img.shields.io/badge/AUTHOR-KHALED%20SALEM%20TAYEB-d96b27?style=for-the-badge&logo=github&logoColor=white" alt="Author">
  </p>
</div>

<hr>

<h3>📌 Project Overview</h3>
<p>
  A comprehensive relational database design and management system developed as a <b>Database course project at King Abdulaziz University (KAU)</b>. The project covers the complete database lifecycle: requirements gathering, ER modeling, business-rule mapping, normalization (1NF → 3NF), SQL implementation, and finally a working FastAPI application enforcing the same rules the database was designed around.
</p>

<h3>📂 Quick Links & Documentation</h3>
<ul>
  <li><b><a href="https://github.com/khaled-sa-tayeb/KAU-Library-Management-System/blob/main/KAU%20Library%20Management%20System%20Report.pdf">Full Project Report (PDF):</a></b> Requirements, ER diagram, schema mapping, normalization steps, and sample queries.</li>
  <li><b><a href="https://kau-library-management-system.onrender.com/">Live Demo:</a></b> Try the working dashboard in your browser.</li>
  <li><b><a href="https://github.com/khaled-sa-tayeb/KAU-Library-Management-System/blob/main/app.py">Source Code (app.py):</a></b> Backend application, database layer, and API routes.</li>
</ul>

<hr>

<h2>🗂️ Database Design</h2>

<h3>1. Requirements & Entities</h3>
<p>
  The system was designed around <b>9 core entities</b> derived from the library's real-world data requirements:
</p>
<table>
  <tr><th>Entity</th><th>Purpose</th></tr>
  <tr><td><code>Employee</code></td><td>Library staff who manage sections and process loans.</td></tr>
  <tr><td><code>Student</code></td><td>Library members who can borrow books.</td></tr>
  <tr><td><code>Book</code></td><td>Catalog items, each linked to a genre and a bookshelf.</td></tr>
  <tr><td><code>Loan</code></td><td>An active borrowing transaction linking a student, employee, and book.</td></tr>
  <tr><td><code>Loan_History</code></td><td>Tracks the return status (Active/Returned) of every loan — resolves the M:N relationship between <code>Loan</code> and <code>Book</code>.</td></tr>
  <tr><td><code>Genre</code></td><td>Book categories, each belonging to a section.</td></tr>
  <tr><td><code>Bookshelf</code></td><td>Physical shelves, each located within a section.</td></tr>
  <tr><td><code>Section</code></td><td>Library floors/wings, each managed by exactly one employee.</td></tr>
  <tr><td><code>Authors_List</code></td><td>Resolves the multivalued "Author" attribute — a book can have multiple authors.</td></tr>
</table>

<h3>2. Entity-Relationship (ER) Design</h3>
<p>The ER diagram was built by identifying every relationship type between entities and its cardinality/participation constraints:</p>
<ul>
  <li><b>1:1</b> — Employee ⟷ Section (<i>"works in / manages"</i>): a section has exactly one manager, and a manager oversees only one section.</li>
  <li><b>1:N</b> — Student → Loan, Employee → Loan (<i>"responsible for"</i>), Section → Bookshelf, Section → Genre, Bookshelf → Book, Genre → Book.</li>
  <li><b>M:N</b> — Loan ⟷ Book (<i>"loaned in"</i>): resolved into a bridge table (<code>Loan_History</code>) since a loan transaction can reference multiple books over time and a book can be loaned multiple times.</li>
  <li><b>Multivalued attribute</b> — Book.Author was decomposed into its own <code>Authors_List</code> table (1:N from Book) instead of storing multiple authors in a single field.</li>
</ul>

<h3>3. Business Rules → Design Decisions</h3>
<p>Every business rule collected during requirements analysis was translated into a concrete schema decision:</p>
<table>
  <tr><th>Business Rule</th><th>Design Decision</th></tr>
  <tr><td>A section must have exactly one manager, and a manager cannot manage more than one section.</td><td>1:1 relationship, enforced with a <code>UNIQUE</code> constraint on <code>Section.manager_id</code>.</td></tr>
  <tr><td>A student can borrow at most 3 books at once.</td><td>Validated at the application layer against active records in <code>Loan_History</code> before inserting a new loan.</td></tr>
  <tr><td>A book can only be loaned if it's available.</td><td>M:N relationship between Loan and Book resolved via <code>Loan_History.return_status</code>; checked before every new loan.</td></tr>
  <tr><td>The maximum loan duration is two weeks.</td><td>Enforced with a <code>CHECK</code> constraint comparing <code>due_date</code> and <code>loan_date</code>, plus an application-level check for a clearer error message.</td></tr>
  <tr><td>Employee age must be between 18–60; student age must be over 15.</td><td><code>CHECK</code> constraints on the <code>Employee.age</code> and <code>Student.age</code> columns.</td></tr>
  <tr><td>A bookshelf must belong to a section; a book must belong to a bookshelf and a genre.</td><td><code>FOREIGN KEY</code> constraints with <code>ON DELETE CASCADE</code> to preserve referential integrity.</td></tr>
</table>

<h3>4. Normalization (1NF → 3NF)</h3>
<ul>
  <li><b>1NF:</b> Removed the multivalued <code>Author</code> attribute from <code>Book</code> into a separate <code>Authors_List</code> table.</li>
  <li><b>2NF:</b> No composite primary keys exist outside the bridge tables (<code>Loan_History</code>, <code>Authors_List</code>), so no partial dependency issues were found.</li>
  <li><b>3NF:</b> Removed a transitive dependency where an employee's <code>Leaving_Time</code> depended on their <code>Starting_Time</code> rather than directly on <code>Employee_ID</code>, by separating shift information out of the Employee table.</li>
</ul>

<h3>5. Final Schema Summary</h3>
<pre><code>Employee (employee_id PK, employee_name, position, starting_time, leaving_time, phone_no, age)
Section  (section_id PK, location, manager_id FK → Employee, UNIQUE)
Bookshelf(bookshelf_id PK, bookshelf_code, section_id FK → Section)
Genre    (genre_code PK, genre_name, section_id FK → Section)
Student  (student_id PK, student_name, phone_no, degree, email, age)
Book     (book_id PK, book_name, isbn, edition, genre_code FK → Genre, bookshelf_id FK → Bookshelf)
Loan     (loan_id PK, loan_date, due_date, student_id FK → Student, employee_id FK → Employee, book_id FK → Book)
Loan_History (loan_id FK, book_id FK, return_status)  -- composite PK
Authors_List (book_id FK, author_name)                -- composite PK
</code></pre>

<hr>

<h2>💻 From Design to Application</h2>
<p>
  The database design above was implemented as a real, persistent <b>SQLite</b> database (instead of the Oracle/T-SQL scripts used in the original report) and wired up to a <b>FastAPI</b> backend, so every business rule above is enforced twice: once by the database's own constraints, and once by the API before a query even reaches the database — giving clear, human-readable error messages instead of raw database errors.
</p>

<h3>🛠️ Tech Stack</h3>
<ul>
  <li><b>Database:</b> SQLite (via Python's built-in <code>sqlite3</code>) — persistent, constraint-enforced, auto-seeded on first run.</li>
  <li><b>Backend:</b> FastAPI (Python), Pydantic, Uvicorn</li>
  <li><b>Frontend:</b> HTML5, CSS3, JavaScript (Fetch API) — kept in a separate <code>templates/dashboard.html</code> file from the backend logic.</li>
  <li><b>Deployment:</b> Render (free tier)</li>
</ul>

<h3>🚀 Getting Started (Run Locally)</h3>
<ol>
  <li>
    <b>Clone the repository:</b>
    <pre><code>git clone https://github.com/khaled-sa-tayeb/KAU-Library-Management-System.git
cd KAU-Library-Management-System</code></pre>
  </li>
  <li>
    <b>Create and activate a virtual environment:</b>
    <pre><code>python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate</code></pre>
  </li>
  <li>
    <b>Install dependencies:</b>
    <pre><code>pip install -r requirements.txt</code></pre>
  </li>
  <li>
    <b>Run the application:</b>
    <pre><code>python app.py</code></pre>
    <p>The SQLite database (<code>library.db</code>) is created and seeded with sample data automatically on first run. Access the dashboard at <code>http://127.0.0.1:8000/</code>.</p>
  </li>
</ol>

<hr>

<div align="center">
  <p>Developed by <a href="https://github.com/khaled-sa-tayeb">Khaled Salem Tayeb</a> | King Abdulaziz University</p>
</div>
