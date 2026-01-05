# Smart Attendance System Backend

A real-time **face recognition-based attendance management system** built with **FastAPI**, **SQLModel**, and **InsightFace**. The backend enables automated attendance tracking using facial recognition, robust user enrollment, and complete attendance records management.

![FastAPI](https://img.shields.io/badge/FastAPI-0.120-green)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![InsightFace](https://img.shields.io/badge/InsightFace-0.7.3-orange)

---

## 🚀 Features

- **Real-time Face Recognition** - WebSocket-based streaming for live facial detection and matching
- **Multiple Enrollment Methods** - Enroll users via single image, multiple images, or direct camera capture
- **Automatic Attendance Marking** - Creates attendance records upon successful face match with no manual input
- **Role-Based Access Control** - Secure JWT authentication with admin role verification
- **RESTful API** - Complete CRUD functionality for persons, attendance records, and status management
- **Cosine Similarity Matching** - Accurate face matching with configurable threshold (0.65 default)
- **Absent User Tracking** - Mark users absent who didn't mark attendance on a given day

---

## 📁 Project Structure

```
Smart-Attendance-System-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config/
│   │   ├── __init__.py
│   │   └── dbsetup.py             # Database configuration and setup
│   ├── models/
│   │   ├── __init__.py
│   │   ├── administrator.py       # Admin user model
│   │   ├── attendance.py          # Attendance records model
│   │   ├── embedding.py           # Face embedding vectors model
│   │   ├── person.py              # Person model
│   │   └── status.py              # Attendance status (Present/Absent)
│   ├── cruds/
│   │   ├── __init__.py
│   │   ├── admin_crud.py          # Admin CRUD operations
│   │   ├── attendance_crud.py     # Attendance CRUD operations
│   │   ├── embedding_crud.py      # Embedding CRUD operations
│   │   ├── person_crud.py         # Person CRUD operations
│   │   └── status_crud.py         # Status CRUD operations
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── admin_router.py        # Admin authentication endpoints
│   │   ├── attendance_router.py   # Attendance & recognition endpoints
│   │   ├── person_router.py       # Person management endpoints
│   │   └── status_router.py       # Status management endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py                # JWT authentication service
│   │   ├── enrollment_service.py  # Camera-based enrollment helper
│   │   ├── face_service.py        # InsightFace embedding & matching
│   │   └── password_utils.py      # Password hashing utilities
│   └── enroll_images/             # Temporary storage for enrollment captures
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## 🛠 Installation

### Prerequisites

- Python **3.12+**
- pip and virtualenv
- Git

### Clone the repository

```bash
git clone https://github.com/AhmadNMatar/Smart-Attendance-System-backend.git
cd Smart-Attendance-System-backend
```

### Create and activate a virtual environment

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Create a `.env` file in the project root with the following variables:

```env
# Database
DATABASE_URL=sqlite:///./attendance.db

# JWT Authentication
JWT_SECRET=your-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM=HS256
```

---

## ▶️ Running the Server

Start the FastAPI server using Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or using the FastAPI CLI:

```bash
fastapi run app/main.py
```

---

## 📄 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🔐 Authentication

All attendance and person management endpoints require JWT authentication. Use the `/admin/login` endpoint to obtain a token.

### Login Flow

```bash
# Login to get JWT token
curl -X POST "http://localhost:8000/admin/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=your-password"
```

Include the token in subsequent requests:

```bash
curl -X GET "http://localhost:8000/attendance/records" \
  -H "Authorization: Bearer <your-jwt-token>"
```

---

## 📚 API Endpoints

### Admin Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/admin/signup` | Register a new admin user |
| POST | `/admin/login` | Login and get JWT token |

### Person Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/person/` | Create a new person |
| GET | `/person/` | Get person by ID |

### Attendance & Recognition

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/attendance/records` | Get all attendance records |
| POST | `/attendance/enroll` | Enroll a person from an image |
| POST | `/attendance/enroll_images` | Enroll using multiple images |
| POST | `/attendance/enroll_camera` | Enroll using camera capture |
| POST | `/attendance/recognize_user` | Recognize a user from an image |
| POST | `/attendance/take_attendance` | Mark attendance from image |
| GET | `/attendance/absent` | Mark all absent users |

---

## 🎯 Usage Examples

### 1. Enroll a New Person

```python
import requests

url = "http://localhost:8000/attendance/enroll"
headers = {"Authorization": "Bearer <your-token>"}
data = {
    "first_name": "John",
    "last_name": "Doe",
    "image_path": "/path/to/photo.jpg"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### 2. Take Attendance

```python
import requests

url = "http://localhost:8000/attendance/take_attendance"
headers = {
    "Authorization": "Bearer <your-token>",
    "Content-Type": "image/jpeg"
}

with open("/path/to/capture.jpg", "rb") as f:
    response = requests.post(url, data=f.read(), headers=headers)

print(response.json())
```

### 3. Get Attendance Records

```python
import requests

url = "http://localhost:8000/attendance/records"
headers = {"Authorization": "Bearer <your-token>"}

response = requests.get(url, headers=headers)
print(response.json())
```

---

## 🛡️ Security Features

- **JWT Token Authentication** - Secure stateless authentication
- **Password Hashing** - Using bcrypt for secure password storage
- **Admin-Only Access** - All sensitive endpoints require admin privileges
- **CORS Configuration** - Configured for frontend integration

---

## 📦 Dependencies

Key packages used in this project:

- **FastAPI** - Modern web framework for building APIs
- **SQLModel** - ORM for database operations
- **InsightFace** - Face analysis and recognition
- **ONNX Runtime** - Cross-platform ML inference
- **OpenCV** - Image processing
- **PyJWT** - JWT token handling
- **Uvicorn** - ASGI server

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📝 License

This project is licensed under the MIT License.

---

## 👤 Author

**Ahmad Matar**

- GitHub: [@AhmadNMatar](https://github.com/AhmadNMatar)

---

## 🙏 Acknowledgments

- [InsightFace](https://github.com/deepinsight/insightface) - Face analysis library
- [FastAPI](https://fastapi.tiangolo.com/) - Excellent Python API framework
- [SQLModel](https://sqlmodel.tiangolo.com/) - Great ORM library

