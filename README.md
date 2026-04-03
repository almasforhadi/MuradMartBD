# 🛒 MuradMartBD — Django E-commerce Platform

A modern, scalable **Django-based E-commerce web application** with full production-ready architecture.

This project supports complete shopping flow including product browsing, cart management, order processing, and secure payments via SSLCommerz.

The application is containerized using Docker, served via Gunicorn + Nginx, and designed with AWS cloud deployment architecture.

---

# 🚀 Features

## 🛍️ Shopping Experience
- Product listing with categories  
- Product detail page  
- Product rating and reviews  
- Product search and filtering  

## 🛒 Cart System
- Add to cart  
- Update cart quantity  
- Remove items  
- Session-based cart for guests  
- Persistent cart for authenticated users  

## 💳 Checkout & Orders
- Cash on Delivery (COD)  
- Secure online payment via SSLCommerz  
- Order confirmation system  
- Order tracking  

## 👤 User Accounts
- Registration & Login  
- Google Social Login (Django Allauth)  
- Profile management  
- Password change  

## ⭐ Product Ratings
- Verified purchase rating system  
- 1–5 star rating  
- Review comments  

## 📧 Email Notifications
- Order confirmation emails  

---

# 🏗️ Tech Stack

| Technology       | Purpose                       |
|----------------|------------------------------|
| Django          | Backend framework            |
| PostgreSQL      | Database (AWS RDS)           |
| Gunicorn        | WSGI server                  |
| Nginx           | Reverse proxy                |
| Docker          | Containerization             |
| AWS EC2         | Application hosting          |
| AWS RDS         | Managed database             |
| AWS S3          | Media storage                |
| Cloudinary      | Image CDN (fallback)         |
| GitHub Actions  | CI/CD pipeline               |
| SSLCommerz      | Payment gateway              |
| Bootstrap       | Frontend                     |

---

# ☁️ AWS Deployment Architecture


User Request </br>
↓</br>
Nginx (Reverse Proxy)</br>
↓</br>
Gunicorn</br>
↓</br>
Django Application (Docker Container)</br>
↓</br>
PostgreSQL (AWS RDS)</br>
↓</br>
Media Files → AWS S3 Bucket


---

# 📂 Project Structure


eshop/</br>
│</br>
├── eshop/     # Django project settings</br>
├── shop/      # Main app</br>
│</br>
├── templates/    </br>
├── static/       </br>
├── staticfiles/  </br>
│</br>
├── nginx/         </br>
│ └── default.conf </br>
│</br>
├── .github/</br>
│ └── workflows/</br>
│ └── deploy.yml     # CI/CD pipeline</br>
│</br>
├── Dockerfile</br>
├── docker-compose.yml</br>
├── .env</br>
├── requirements.txt</br>
├── manage.py</br>
└── README.md</br>


---

# ⚙️ Environment Variables

## Create a `.env` file in root:

SECRET_KEY=your_secret_key</br>
DEBUG=False</br>
ALLOWED_HOSTS=your-domain.com</br>
DATABASE_URL=your_rds_database_url</br>

AWS_ACCESS_KEY_ID=your_key</br>
AWS_SECRET_ACCESS_KEY=your_secret</br>
AWS_STORAGE_BUCKET_NAME=your_bucket</br>
AWS_S3_REGION_NAME=your_region</br>

SSLCOMMERZ_STORE_ID=your_store_id</br>
SSLCOMMERZ_STORE_PASSWORD=your_store_password</br>
SSLCOMMERZ_PAYMENT_URL=https://sandbox.sslcommerz.com/gwprocess/v4/api.php</br>
SSLCOMMERZ_VALIDATION_URL=https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php</br>

EMAIL_HOST=smtp.gmail.com</br>
EMAIL_HOST_USER=your_email@gmail.com</br>
EMAIL_HOST_PASSWORD=your_password</br>
EMAIL_PORT=587</br>
EMAIL_USE_TLS=True</br>

---

# 🐳 Docker Setup

## Run locally using Docker:
```bash
docker-compose up --build
```

## 🔄 CI/CD Pipeline
Configured using GitHub Actions.
Workflow:
```bash
Push Code → GitHub
        ↓
Docker Build
        ↓
CI Pipeline Run
        ↓
Deployment Ready
```

# 📦 Deployment (AWS)

This project is designed for AWS deployment using the following services:

## 🔹 EC2 (Elastic Compute Cloud)
Hosts the Django application</br>
Dockerized environment</br>
Gunicorn server</br>
Nginx reverse proxy</br>

## 🔹 RDS (PostgreSQL)
Managed database service</br>
Secure and scalable storage</br>

## 🔹 S3 Bucket
Stores uploaded media files</br>
Integrated with Django storage backend</br>

## 🚀 Deployment Steps
Launch EC2 instance (Ubuntu)</br>
Install Docker & Docker Compose</br>
Clone project from GitHub</br>
Configure .env file</br>

## Run:
docker-compose up -d</br>
Configure Nginx</br>
Connect domain to EC2 public IP</br>
(Optional) Setup HTTPS using SSL</br>

## 🔐 Security Features
CSRF protection</br>
Secure cookies</br>
XSS protection</br>
Content-type protection</br>
Payment validation with SSLCommerz</br>
Environment-based secret management</br>

# 🧪 Admin Panel

Access admin panel:
```bash
/admin
```

# 🌐 Live Demo
```bash
https://muradmartbd.com
```

# 👨‍💻 Author
Md Almas Forhadi | 2026

# 📄 License

This project is not open-source. It is intended for production use only. Unauthorized copying, modification, or distribution is strictly prohibited.