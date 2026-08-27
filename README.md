ر<div align="center">
  <h1>📚 KAU Library Management System</h1>
  <p><b>King Abdulaziz University - Database Course Project</b></p>
  <p>
    <img src="https://img.shields.io/badge/FastAPI-0.100%2B-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">
    <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/SQL%20Server-Database-CC2927?style=for-the-badge&logo=microsoft-sql-server&logoColor=white" alt="SQL Server">
    <img src="https://img.shields.io/badge/Status-Completed-success?style=for-the-badge" alt="Status">
    <img src="https://img.shields.io/badge/AUTHOR-KHALED%20SALEM%20TAYEB-d96b27?style=for-the-badge&logo=github&logoColor=white" alt="Author">

  </p>
  <p>
  </p>
</div>

<hr>

<h3>📌 Project Overview</h3>
<p>
  A comprehensive relational database design and enterprise management system developed as a <b>Database course project at King Abdulaziz University (KAU)</b>. The project covers the complete database lifecycle from requirements analysis and ER modeling to normalization, transactional SQL implementation, and application integration.
</p>

<h3>📂 Quick Links & Documentation</h3>
<ul>
  <li><b><a href="https://github.com/khaled-sa-tayeb/KAU-Advanced-Library-Management-System/blob/main/KAU%20Advanced%20Library%20Management%20System%20Report.pdf">Project Report (PDF):</a></b> Comprehensive documentation including requirements, ERD, and schema mapping.</li>
  <li><b><a href="[https://github.com/khaled-sa-tayeb/KAU-Advanced-Library-Management-System/blob/main/UI%20Preview.pdf](https://github.com/khaled-sa-tayeb/KAU-Library-Management-System/blob/main/UI%20Preview.pdf)">UI Preview (PDF):</a></b> Screenshots and interface design of the dashboard.</li>
  <li><b><a href="https://github.com/khaled-sa-tayeb/KAU-Advanced-Library-Management-System/blob/main/app.py">Source Code (app.py):</a></b> Main backend application and routing logic.</li>
</ul>

<h3>🏛️ System Entities</h3>
<p>
  The database architecture manages a robust network of interconnected entities:
</p>
<ul>
  <li><b>Core Entities:</b> EMPLOYEE, STUDENT, BOOK, LOAN, GENRE, BOOKSHELF, SECTION, LOAN_HISTORY, AUTHORS_LIST, and SHIFT.</li>
</ul>

<h3>⚙️ Key Design Decisions & Normalization</h3>
<ul>
  <li><b>Relational Mappings:</b> Established 1:N relationships between Student and Loan, M:N between Loan and Book (resolved via <code>LOAN_HISTORY</code>), and 1:1 between Employee and Section (manager role).</li>
  <li><b>Normalization (1NF → 2NF → 3NF):</b> Rigorously applied normalization rules, including decomposing the <code>SHIFT</code> table to eliminate transitive dependencies and ensure data integrity.</li>
  <li><b>Advanced Querying & Transactions:</b> Developed complex SQL queries, views, and secure database transactions supporting multi-criteria filtering and reporting.</li>
</ul>

<h3>🛠️ Tech Stack & Tools</h3>
<ul>
  <li><b>Database Management:</b> Microsoft SQL Server (T-SQL)</li>
  <li><b>Backend Framework:</b> FastAPI (Python)</li>
  <li><b>Data Validation & Server:</b> Pydantic, Uvicorn</li>
  <li><b>Frontend & Design:</b> HTML5, CSS3, JavaScript (Fetch API), ERD Design Tools</li>
</ul>

<h3>🚀 Getting Started</h3>
<p>Follow these steps to run the project locally on your machine:</p>

<ol>
  <li>
    <b>Clone the repository:</b>
    <pre><code>git clone https://github.com/khaled-sa-tayeb/KAU-Advanced-Library-Management-System.git
cd KAU-Advanced-Library-Management-System</code></pre>
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
    <pre><code>pip install fastapi uvicorn pydantic pyodbc</code></pre>
  </li>
  <li>
    <b>Database Setup:</b>
    <p>Execute the provided <code>schema.sql</code> script in your Microsoft SQL Server instance to construct the normalized schema and load sample data.</p>
  </li>
  <li>
    <b>Run the application:</b>
    <pre><code>python app.py</code></pre>
    <p>Access the web interface at <code>http://127.0.0.1:8000/</code>.</p>
  </li>
</ol>

<hr>

<div align="center">
  <p>Developed by <a href="https://github.com/khaled-sa-tayeb">Khaled Salem Tayeb</a> | King Abdulaziz University</p>
</div>
