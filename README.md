# MeitY Audit Backend (Django Framework)

This repository contains the **backend service** for the **MeitY Audit Mobile Application**.  
It is built with the **Django framework** and is responsible for handling all **core business logic, data storage, and API communication**.  

The backend powers features such as **authentication, role-based workflows, audit request management, and secure document handling**.

---

## 🏗️ System Architecture
<div>
    <img src="flowchar_meity.png" alt="Home Screen" style="width: 30%; display: inline-block; margin-right: 1%;"/>
</div>
**The mobile app communicates with the Django backend through **RESTful APIs**, which handle **RBAC, audit workflows, and secure file storage**.

---

## 🔑 Key Features

* **User Authentication & Authorization**
  Secure **token-based authentication** for role-based access.

* **Role-Based Access Control (RBAC)**
  Roles include:
  * CSP (Cloud Service Provider)
  * STQC Auditor
  * MeitY Reviewer
  * Scientist F

* **RESTful API** for mobile-client communication

* **Data Models** for Users, Audit Requests, and Documents

* **Workflow Management** (submitted → under review → approved → rejected)

* **Secure File Handling** (upload, storage, retrieval)

---

## 📋 Prerequisites

* Python **3.8+**
* pip (Python package manager)
* PostgreSQL (recommended) or SQLite (for development)

---

## ⚙️ Installation

1. **Clone Repository**
   ```bash
   git clone https://github.com/<your-username>/<your-repo-name>.git
   cd <your-repo-name>
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Database**  
   Update your database settings in `settings.py`.  
   Default: SQLite → Recommended: PostgreSQL for production.

5. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

---

## 🔗 API Endpoints

| Endpoint                                  | Method | Description                      |
| ----------------------------------------- | ------ | -------------------------------- |
| `/api/login/`                             | POST   | Authenticate user & return token |
| `/api/register/`                          | POST   | Register new user                |
| `/api/audit-requests/`                    | GET    | List audit requests (role-based) |
| `/api/audit-requests/`                    | POST   | Submit new audit request         |
| `/api/audit-requests/<int:pk>/`           | GET    | Retrieve specific request        |
| `/api/audit-requests/<int:pk>/`           | PUT    | Update request                   |
| `/api/audit-requests/<int:pk>/`           | DELETE | Delete request                   |
| `/api/audit-requests/<int:pk>/documents/` | POST   | Upload document                  |
| `/api/audit-requests/<int:pk>/documents/` | GET    | Get documents                    |

---

## ▶️ Running the Server

```bash
python manage.py runserver
```

Server will run at:  
👉 [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🧪 Testing

Run unit and integration tests:

```bash
python manage.py test
```

---

## 🚀 Deployment

* Use **Gunicorn** or **uWSGI** with Nginx for production
* Configure **PostgreSQL** or another production-grade DB
* Set environment variables:
  ```python
  DEBUG = False
  ALLOWED_HOSTS = ['yourdomain.com']
  ```
* Collect static files:
  ```bash
  python manage.py collectstatic
  ```

---

## 📄 License

Licensed under the **MIT License**.  
See [LICENSE](LICENSE) for details.
