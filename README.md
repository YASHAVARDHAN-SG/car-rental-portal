# 🚗 DriveEase - Car Rental Management System

A full-stack **Car Rental Management System** built using **Django**, featuring user authentication, car booking, admin management, and dynamic price calculation. This project is suitable for academic submissions, portfolio showcasing, and real-world learning.

---

## 📌 Features

### 👤 Authentication
- User Registration
- User Login & Logout
- Session-based authentication
- Protected routes using `@login_required`

### 🚘 Car Management
- Add, update, and delete cars via Admin Panel
- Set car availability
- Price per day configuration

### 📅 Booking System
- Book cars by selecting start and end dates
- Automatic total price calculation
- User-specific bookings
- Secure backend validation

### 🛠 Admin Panel
- Manage users
- Manage cars
- View all bookings

---

## 🧰 Tech Stack

| Layer        | Technology |
|--------------|------------|
| Backend      | Django (Python) |
| Frontend     | HTML, CSS, JavaScript |
| Database     | SQLite |
| Auth         | Django Auth |
| ORM          | Django ORM |

---

## Continuous integration

CircleCI runs separate `build` and `test` jobs when commits are pushed, including commits on pull-request branches. Each job checks out the code and installs dependencies from `requirements.txt`. The `build` job compiles the Python files and checks the Django configuration; after it succeeds, the `test` job runs the Django test suite. Each job uploads its logs as build artifacts, including when a check fails.

---

## 📁 Project Structure

```text
Car_Rental/
│
├── bicycle/                     # Core Django application
│   ├── migrations/              # Database migration files
│   ├── __init__.py
│   ├── admin.py                 # Admin panel configuration
│   ├── models.py                # Car & Booking database models
│   ├── views.py                 # Authentication & booking logic
│   └── urls.py                  # App-level URL routing
│
├── templates/                   # HTML templates
│   ├── index.html               # Homepage – car listings
│   ├── booking.html             # Car booking page
│   ├── login.html               # User login page
│   └── register.html            # User registration page
│
├── static/                      # Static assets
│   ├── css/                     # Stylesheets
│   ├── js/                      # JavaScript files
│   └── images/                  # Images (cars, logos, UI assets)
│
├── Car_Rental/                  # Django project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py              # Project settings
│   ├── urls.py                  # Project-level URL routing
│   └── wsgi.py
│
├── db.sqlite3                   # SQLite database
├── manage.py                    # Django management script
└── README.md                    # Project documentation

```

---

## 📸 Screenshot

![GitHub Logo](https://github.com/raunakmallick18/car-rental/blob/main/DriveEase.png)
