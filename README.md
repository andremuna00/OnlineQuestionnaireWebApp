# Database Legends: Online Questionnaire Web App

![image](https://github.com/user-attachments/assets/e5410408-6b52-4cb7-a58a-b8610344cd69)

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Database Design](#database-design)
4. [Project Choices](#project-choices)

---

## Introduction

📜 **Project Name**: Online Questionnaire Web App

👨‍💻 **Developed By**:
- Giovanni Costa (880892)
- Andrea Munarin (879607)

📅 **Course**: Databases Module 2  
📆 **Date**: August 29, 2021  

🎯 **Overview**: This project involves creating an online questionnaire platform similar to Google Forms. The application allows users to create and manage questionnaires with various types of questions (e.g., single choice, multiple choice, open-ended). Users can analyze responses through detailed statistics and export data in CSV format.

---

## Features

### 🌟 Core Functionality
- **Questionnaire Management**
  - Create, edit, and delete questionnaires.
  - Add questions with different types (single choice, multiple choice, open-ended).
  - Associate tags with questions for categorization.
  - Set questions as mandatory or allow file uploads (for open-ended questions).

- **Response Analysis**
  - View collected responses.
  - Analyze data using visualizations (pie charts and histograms).
  - Export responses as CSV files.

- **User Roles**
  - Standard User: Create and respond to questionnaires.
  - Admin: Manage users and forms.
  - SuperUser: Assign and revoke admin privileges.

### 💻 Technical Overview
#### Backend
- Developed in **Python** using **Flask** framework.
- Libraries:
  - **Flask-Security**: User authentication and authorization.
  - **SQLAlchemy**: ORM for database interactions.

#### Frontend
- Technologies:
  - **HTML**, **CSS**, **JavaScript**
  - **Bootstrap** for UI components.
  - **Chart.js** for data visualizations.

---

## Database Design

### 🛠️ Conceptual Model
- **Users**:
  - Attributes: Email, Name, Age, Role.
- **Forms**:
  - Attributes: Name, Description, Date Created, Creator.
  - Linked to multiple questions and responses.
- **Questions**:
  - Types: Open-ended, Single Choice, Multiple Choice.
  - Attributes: Text, Tags, Options (if applicable).
- **Responses**:
  - Linked to users, forms, and questions.
  - Attributes: Content (text or file).

![SchemaConcettuale_DB_Legends](https://github.com/user-attachments/assets/9cefe9b2-6dbd-4526-a570-6cd78b0b731b)


### ⚙️ Logical Design
- Implemented with **PostgreSQL**.
- **ON DELETE CASCADE** ensures smooth deletion of related records.
- Efficient storage by sharing reusable questions among forms.
- Copy-on-write strategy for question updates to maintain consistency.

---

## Project Choices

### 🔐 Security Features
- **Flask-Security** handles user authentication and password encryption.
- **Roles and Permissions**:
  - SuperUser: Manage roles and permissions.
  - Admin: Moderate forms and users.
  - Standard User: Basic functionalities.

### 🧩 Optimization
- Questions stored once in the database to save space and avoid duplication.
- **Trigger Implementation**:
  - Prevents users from responding to the same form twice.

---

## How to Run

### 🛠️ Prerequisites
- **Python 3.8+**
- **PostgreSQL** database

### 📥 Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/DatabaseLegends/QuestionnaireApp.git
   ```
2. Install dependencies specified in the documentation
3. Configure `.env` file:
   ```env
   SECRET_KEY=your_secret_key
   DATABASE_URL=postgresql://username:password@localhost/db_name
   ```
4. Initialize the database:
   ```bash
   python init_db.py
   ```
5. Run the application:
   ```bash
   flask run
   ```

---

## Acknowledgements

This project was developed as part of the Databases Module 2 course at [Your University Name]. We thank our instructors and peers for their support and guidance.

