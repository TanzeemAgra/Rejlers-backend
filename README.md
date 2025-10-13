# REJLERS Django Backend

## Overview
This is the Django REST Framework backend for the REJLERS industrial consulting platform. It provides APIs for authentication, contact management, service requests, and business logic.

## 🏗️ Technology Stack

- **Framework**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **Authentication**: JWT (Simple JWT)
- **Cache**: Redis
- **Documentation**: drf-spectacular (OpenAPI/Swagger)
- **Deployment**: Railway

## 📁 Project Structure

```
backend/
├── manage.py                   # Django management script
├── requirements/               # Dependencies for different environments
│   ├── base.txt               # Base dependencies
│   ├── development.txt        # Development dependencies
│   └── production.txt         # Production dependencies
├── config/                    # Django configuration
│   ├── __init__.py
│   ├── urls.py               # Main URL configuration
│   ├── wsgi.py               # WSGI application
│   ├── asgi.py               # ASGI application
│   └── settings/             # Environment-specific settings
│       ├── __init__.py
│       ├── base.py           # Base settings
│       ├── development.py    # Development settings
│       └── production.py     # Production settings
└── apps/                     # Django applications
    ├── __init__.py
    ├── core/                 # Core utilities and base classes
    ├── authentication/       # User authentication and management
    ├── contacts/            # Contact forms and inquiries
    └── services/            # Service management
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL (or SQLite for development)
- Redis (optional, for caching)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rejlers/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/development.txt
   ```

4. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at: http://localhost:8000/

## 🔧 Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure:

#### Required Variables:
- `SECRET_KEY`: Django secret key
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Database credentials
- `REDIS_URL`: Redis connection string

#### Optional Variables:
- `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`: Email configuration
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`: AWS S3 storage
- `SENTRY_DSN`: Error monitoring

### Settings Files:
- **Development**: `config.settings.development`
- **Production**: `config.settings.production`

## 📚 API Documentation

### API Endpoints
- **Base API**: `/api/v1/`
- **Authentication**: `/api/v1/auth/`
- **Contacts**: `/api/v1/contacts/`
- **Services**: `/api/v1/services/`
- **Admin**: `/admin/`

### API Documentation:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### Health Check:
- **Health Status**: http://localhost:8000/health/

## 🔐 Authentication

The API uses JWT authentication:

1. **Register**: `POST /api/v1/auth/register/`
2. **Login**: `POST /api/v1/auth/login/`
3. **Refresh Token**: `POST /api/v1/auth/refresh/`
4. **Logout**: `POST /api/v1/auth/logout/`

### Usage:
```javascript
// Login
const response = await fetch('/api/v1/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com', password: 'password' })
});

// Use token
const { access_token } = await response.json();
fetch('/api/v1/protected-endpoint/', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

## 🧪 Testing

### Run Tests
```bash
python manage.py test
```

### Test with Coverage
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### API Testing
Use the test suite in the `Test/` folder:
```bash
cd ../Test/api-tests
npm install axios
node test-runner.js
```

## 🚀 Deployment to Railway

### Prerequisites for Railway Deployment
1. **GitHub Repository**: Push your code to GitHub
2. **Railway Account**: Sign up at [railway.app](https://railway.app)
3. **PostgreSQL Add-on**: Railway will provision this automatically

### Step-by-Step Railway Deployment

#### 1. Prepare Your Repository
```bash
# Make sure all files are committed
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

#### 2. Deploy to Railway
1. **Connect to Railway**:
   - Go to [railway.app](https://railway.app) and login with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your REJLERS backend repository

2. **Add PostgreSQL Database**:
   - In your Railway project dashboard
   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway will automatically provide `DATABASE_URL`

3. **Configure Environment Variables**:
   - Go to your service settings → "Variables"
   - Add all variables from `railway.env.example`:

```bash
# Required Environment Variables for Railway
SECRET_KEY=your-super-secret-django-key-here
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.production
FRONTEND_URL=https://your-frontend-domain.vercel.app
ALLOWED_HOSTS=your-domain.up.railway.app,localhost
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app

# Email Configuration (Gmail example)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=REJLERS <noreply@rejlers.com>

# Business Settings
COMPANY_NAME=REJLERS
COMPANY_EMAIL=contact@rejlers.com
```

#### 3. Railway Automatic Configuration
Railway automatically:
- Detects your Django app
- Installs dependencies from `requirements/production.txt`
- Runs database migrations
- Serves your application on a public URL

#### 4. Custom Start Command (if needed)
If Railway doesn't detect your setup correctly, add this start command:
```bash
python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application
```

### Post-Deployment Steps

1. **Create Superuser** (via Railway CLI):
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and connect to your project
railway login
railway link

# Create superuser
railway run python manage.py createsuperuser
```

2. **Test Your API**:
   - Visit: `https://your-domain.up.railway.app/admin/`
   - Check API docs: `https://your-domain.up.railway.app/api/v1/docs/`
   - Health check: `https://your-domain.up.railway.app/health/`

### Railway Benefits for Django
- ✅ Automatic PostgreSQL database provisioning
- ✅ Automatic SSL certificates
- ✅ Built-in monitoring and logs
- ✅ Easy scaling and environment management
- ✅ Git-based deployments (auto-deploy on push)
- ✅ Free tier available for development

## 📊 Database

### Models:
- **User**: Custom user model with company information
- **ContactInquiry**: Contact form submissions
- **ServiceRequest**: Service request submissions
- **NewsletterSubscription**: Newsletter subscriptions

### Migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Database Backup:
```bash
python manage.py dumpdata > backup.json
python manage.py loaddata backup.json
```

## 🛠️ Development

### Code Style:
```bash
black .              # Format code
isort .              # Sort imports
flake8 .             # Lint code
```

### Django Extensions:
```bash
python manage.py shell_plus      # Enhanced shell
python manage.py show_urls       # List all URLs
python manage.py graph_models    # Generate model diagrams
```

## 🔍 Monitoring

### Logging:
Logs are configured for different environments:
- Development: Console + File
- Production: File + Sentry

### Health Checks:
- `/health/`: Basic health status
- Django admin: Database connectivity

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes and test
3. Run code quality checks: `black .`, `isort .`, `flake8 .`
4. Commit changes: `git commit -m "Add new feature"`
5. Push branch: `git push origin feature/new-feature`
6. Create Pull Request

## 📝 License

This project is proprietary to REJLERS AB.

## 📞 Support

For technical support:
- **Documentation**: `/api/docs/`
- **Health Check**: `/health/`
- **Admin Interface**: `/admin/`

---

**REJLERS AB - Engineering Excellence Since 1942**