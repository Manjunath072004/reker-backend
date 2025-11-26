# 🧾 Reker Backend (Django + PostgreSQL + JWT + OTP)

Reker Backend is a fully modular, scalable backend system designed for:
- Merchant dashboard
- POS payments
- Coupon verification & redemption
- Authentication using OTP + JWT
- Real-time transactions
- Settlements
- Analytics

This project is optimized for production and follows a clean architecture.

---

# 🚀 Features Implemented (Till Now)

### ✅ **1. User Authentication**
- Signup with phone, name, email, password
- OTP verification system
- Login using phone + password
- JWT token-based authentication (`access` + `refresh`)

### ✅ **2. OTP Module**
- OTP rate limiting
- OTP stored in cache
- Optional SMS provider toggle
- OTP TTL (5 minutes)

### ✅ **3. Merchant Module**
- Merchant registration
- Merchant profile
- Merchant listing (admin-level)
- Connected with User table

### ✅ **4. Coupon Module**
- Coupon model with:
  - Flat/Percen discount
  - Min order amount
  - Max discount
  - Expiry date
  - Usage count
- Coupon Verification
- Coupon Apply (with Decimal-safe calculations)
- Coupon Listing

### 🚧 Upcoming Modules
- Payments
- Transactions
- Settlements
- Realtime WebSockets
- Analytics

---

# 🏗️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend Framework | Django 5 + Django REST Framework |
| Auth | SimpleJWT |
| Cache | Redis (or LocMemCache for development) |
| Database | PostgreSQL |
| Realtime | Django Channels |
| API Docs | Postman Collection |

---

# 📂 Project Folder Structure

```
reker-backend/
│
├── authentication/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── utils.py        # OTP Generator + Rate Limiter
│   └── urls.py
│
├── merchants/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
│
├── coupons/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
│
├── reker_project/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── .gitignore
├── manage.py
└── README.md
```

---

# ⚙️ Installation & Setup

## 1️⃣ Clone Repository

```bash
git clone https://github.com/<your-username>/reker-backend.git
cd reker-backend
```

---

## 2️⃣ Create Virtual Environment

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

If you don’t have a `requirements.txt`, generate one:

```bash
pip freeze > requirements.txt
```

---

# 🗄️ Database Setup (PostgreSQL)

Create database:

```sql
CREATE DATABASE rekerdb;
```

Update `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'rekerdb',
        'USER': 'postgres',
        'PASSWORD': '<your-password>',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

# 🔐 Authentication Setup (JWT + OTP)

### Settings Include:

```python
AUTH_USER_MODEL = "authentication.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}
```

### OTP Cache (Development, No Redis Required)

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "otp-cache"
    }
}
```

---

# 🧪 Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

# ▶️ Run Server

```bash
python manage.py runserver
```

Server will run on:

```
http://127.0.0.1:8000/
```

---

# 🧪 Testing APIs Using Postman

## 🔹 **Signup Endpoint**

`POST /api/auth/signup/`

Body:
```json
{
  "phone": "9876543210",
  "password": "password123",
  "full_name": "Manjunath",
  "email": "manju@example.com"
}
```

Response:
```
OTP Sent
```

---

## 🔹 **OTP Verify**

`POST /api/auth/verify-otp/`

```json
{
  "phone": "9876543210",
  "otp": "123456"
}
```

---

## 🔹 **Login**

`POST /api/auth/login/`

```json
{
  "phone": "9876543210",
  "password": "password123"
}
```

Returns:

```
access_token
refresh_token
user_data
```

---

# 🟦 Merchant APIs

### Create Merchant
`POST /api/merchants/create/`

```json
{
  "name": "Reker Shop",
  "address": "Bangalore",
  "business_type": "Retail",
  "gst_number": "29ABCDE1234F1Z5"
}
```

### Merchant Profile
`GET /api/merchants/profile/`

---

# 🟩 Coupon APIs

### Verify Coupon

`POST /api/coupons/verify/`

```json
{
  "code": "FIRST50"
}
```

---

### Apply Coupon

`POST /api/coupons/apply/`

```json
{
  "code": "FIRST50",
  "order_amount": 500
}
```

---

### List Coupons

`GET /api/coupons/list/`

---

# 📌 Environment Variables (Optional)

Create `.env`:

```
SECRET_KEY=your-secret-key
DB_NAME=rekerdb
DB_USER=postgres
DB_PASS=M@nju2004
DB_HOST=localhost
```

---

# 📌 .gitignore (Recommended)

```
.venv/
__pycache__/
*.pyc
.env
*.sqlite3
staticfiles/
media/
node_modules/
```

---

# 🧭 Roadmap (Next Development)

- Payments Module
- Transactions Module
- Settlements Module
- Real-Time WebSockets (Channels + Redis)
- Dashboard Analytics
- Admin Panel
- Push Notifications

