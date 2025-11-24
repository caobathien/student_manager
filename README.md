# 🎓 Student Manager

**Student Manager** is a web application built with **Flask** that helps manage students, classes, subjects, grades, and users.  
It provides comprehensive features such as student registration, grade management, user roles and permissions, and more — streamlining academic administrative tasks.

---

## 🧭 Project Structure

- **Total folders:** 353  
- **Total files:** 2169  

### 🏁 `run.py`
The main entry point of the application.  
It initializes the Flask app from the `app` package and runs it on **port 5050** in **debug mode**.

---

## 📂 `app/` Directory Overview

The `app/` folder contains the core source code of the application, organized into modules and subfolders for clarity and maintainability.

### 🔹 Main Python Files

| File | Description |
|------|--------------|
| `auth_routes.py` | Defines authentication-related routes. |
| `decorators.py` | Contains custom decorators for access control and role-based permissions. |
| `forms.py` | Defines web forms using Flask-WTF for handling user input and validation. |
| `routes.py` | Main routing file containing core endpoints of the application. |
| `__init__.py` | Application factory responsible for initializing Flask extensions and configurations. |

---

### 🔸 Subfolders inside `app/`

| Folder | Description |
|---------|--------------|
| `controllers/` | Contains business logic and controller modules, such as `student_controller.py`, `class_controller.py`, `grade_controller.py`, etc. |
| `models/` | Defines ORM database models for students, classes, subjects, users, and grades. |
| `services/` | Business service layer that separates logic from controllers and models. |
| `static/` | Holds static assets such as CSS, JavaScript, and images. |
| `templates/` | Contains HTML templates using **Jinja2** for dynamic rendering. |

---

## 🖼️ Project Folder Structure (Example)

Below is an example screenshot of the project structure in VS Code:

![Project Structure Screenshot](/mnt/data/2107e5c8-1b52-44d1-992a-3ce80bd11ad7.png)

---

## ⚙️ Technologies Used

- **Flask** – Lightweight and powerful Python web framework  
- **Flask-WTF** – Simplifies form handling and input validation  
- **SQLAlchemy** – Robust ORM for database management  
- **Jinja2** – Templating engine for dynamic HTML rendering  
- **Bootstrap / CSS** – Provides a responsive and user-friendly interface  

---

## 👨‍💻 Author

**Cao Bá Thiên**  
📘 Student ID: `23150054`  
🏫 **Gia Định University** – 3rd-year student  

---

## 🚀 How to Run the Application

```bash
# 1️⃣ Create a virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 2️⃣ Install dependencies
pip install -r requirements.txt

# 3️⃣ Run the application
python run.py

The app will be running at:
https://caobathien.pythonanywhere.com/login?next=%2F