-- Create Database
CREATE DATABASE KAU_Library_DB;
GO

USE KAU_Library_DB;
GO

-- 1. Students Table
CREATE TABLE Students (
    StudentID INT PRIMARY KEY IDENTITY(1,1),
    FullName NVARCHAR(100) NOT NULL,
    Email NVARCHAR(100) UNIQUE NOT NULL,
    Major NVARCHAR(50) NOT NULL,
    EnrollmentDate DATE DEFAULT GETDATE()
);
GO

-- 2. Employees Table
CREATE TABLE Employees (
    EmployeeID INT PRIMARY KEY IDENTITY(1,1),
    FullName NVARCHAR(100) NOT NULL,
    Email NVARCHAR(100) UNIQUE NOT NULL,
    Role NVARCHAR(50) NOT NULL,
    HireDate DATE DEFAULT GETDATE()
);
GO

-- 3. Books Table
CREATE TABLE Books (
    BookID INT PRIMARY KEY IDENTITY(1,1),
    Title NVARCHAR(150) NOT NULL,
    Author NVARCHAR(100) NOT NULL,
    ISBN NVARCHAR(20) UNIQUE NOT NULL,
    PublishedYear INT,
    CopiesAvailable INT DEFAULT 1
);
GO

-- 4. Loans Table (Relational Entity linking Students, Books, and Employees)
CREATE TABLE Loans (
    LoanID INT PRIMARY KEY IDENTITY(1,1),
    BookID INT FOREIGN KEY REFERENCES Books(BookID),
    StudentID INT FOREIGN KEY REFERENCES Students(StudentID),
    EmployeeID INT FOREIGN KEY REFERENCES Employees(EmployeeID),
    LoanDate DATE DEFAULT GETDATE(),
    DueDate DATE NOT NULL,
    Status NVARCHAR(20) DEFAULT 'Active'
);
GO
