# Smart Attendance System Backend

A real-time **face recognition--based attendance management system**
built with **FastAPI**, **SQLModel**, and **InsightFace**.\
The backend enables automated attendance tracking using facial
recognition, robust user enrollment, and complete attendance records
management.

## 🚀 Features

-   **Real-time Face Recognition**\
    WebSocket-based streaming for live facial detection and matching.

-   **User Enrollment**\
    Capture multiple face images and compute average embeddings for
    accurate recognition.

-   **Automatic Attendance Marking**\
    Creates attendance records upon successful face match---no manual
    input required.

-   **Role-Based Access Control**\
    Secure JWT authentication with admin role verification.

-   **RESTful API**\
    Complete CRUD functionality for persons, attendance records, and
    status management.

-   **Database Migrations**\
    Managed using Alembic for schema versioning.

-   **Camera Integration**\
    Built-in support for local camera capture and person enrollment
    workflows.

## 🛠 Installation

### Prerequisites

-   Python **3.12+**
-   `pip` and `virtualenv`

### Clone the repository

``` bash
git clone https://github.com/AhmadNMatar/Smart-Attendance-System-backend.git
cd Smart-Attendance-System-backend
```

### Create and activate a virtual environment

``` bash
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### Install dependencies

``` bash
pip install -r requirements.txt
```

## ⚙️ Configuration

Create a `.env` file in the project root:

``` env
# Database
DATABASE_URL=sqlite:///./attendance.db

# JWT
JWT_SECRET=your-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM="HS256"
```


## ▶️ Running the Server

Start the FastAPI server:

``` bash
uvicorn main:app --reload
```
or

```bash
fastapi run app/main.py --reload 
```
## 📄 API Documentation

-   **Swagger UI:** http://localhost:8000/docs
-   **ReDoc:** http://localhost:8000/redoc 