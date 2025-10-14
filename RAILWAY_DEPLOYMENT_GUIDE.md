# Railway Deployment Guide - REJLERS Backend

## Prerequisites
- Railway account at railway.app
- Railway CLI installed (optional but recommended)
- GitHub repository with your Django backend

## Step 1: Create Railway Project

1. Go to railway.app and create a new project
2. Connect your GitHub repository
3. Select the Django backend directory (`backend/`)

## Step 2: Add PostgreSQL Database

1. In your Railway project dashboard, click "New Service"
2. Select "PostgreSQL" from the database options
3. Railway will automatically create a `DATABASE_URL` environment variable

## Step 3: Configure Environment Variables

In your Railway project settings, add these environment variables:

```
SECRET_KEY=your-generated-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.railway.app,127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
CORS_ALLOW_CREDENTIALS=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Generate a Secret Key
Run this Python command to generate a secure key:
```python
import secrets
print(secrets.token_urlsafe(50))
```

## Step 4: Deployment Configuration

Your backend is already configured with:

✅ **Procfile** - Defines the web process with Gunicorn
✅ **nixpacks.toml** - Optimizes the build process
✅ **requirements.txt** - All necessary dependencies
✅ **Production settings** - Railway-compatible configuration

## Step 5: Deploy

1. Push your changes to GitHub
2. Railway will automatically detect and deploy your Django app
3. Wait for the build to complete (usually 2-3 minutes)

## Step 6: Run Database Migrations

After successful deployment, you may need to run migrations:

1. In Railway dashboard, go to your Django service
2. Open the "Deployments" tab
3. Click on the latest deployment
4. Open "View Logs" and look for any migration errors
5. If needed, you can run migrations manually using Railway CLI:

```bash
railway run python manage.py migrate
railway run python manage.py collectstatic --noinput
```

## Step 7: Verify Deployment

1. Your API will be available at: `https://your-app-name.railway.app`
2. Test the health endpoint: `https://your-app-name.railway.app/api/health/`
3. Check CORS by testing from your frontend domain

## Common Issues & Solutions

### Build Failures
- Check logs in Railway dashboard
- Ensure `requirements.txt` is in the root backend directory
- Verify Python version in `runtime.txt` (Python 3.11.6)

### Database Connection Issues
- Verify `DATABASE_URL` is automatically set by Railway PostgreSQL service
- Check that the PostgreSQL service is running in your project

### CORS Issues
- Ensure `CORS_ALLOWED_ORIGINS` includes your exact frontend domain
- Make sure protocol (https://) is included in the origin
- Verify `CORS_ALLOW_CREDENTIALS=True` if using authentication

### Static Files Issues
- `collectstatic` runs automatically via Procfile
- Static files are served by WhiteNoise (already configured)

## Environment Variables Checklist

Required:
- [ ] `SECRET_KEY` - Django secret key
- [ ] `DEBUG=False` - Production mode
- [ ] `ALLOWED_HOSTS` - Include Railway domain
- [ ] `CORS_ALLOWED_ORIGINS` - Frontend domain

Optional but recommended:
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] `CSRF_COOKIE_SECURE=True`
- [ ] `CORS_ALLOW_CREDENTIALS=True`

## Support

If deployment fails, check:
1. Railway build logs for specific errors
2. Django logs in Railway dashboard
3. Database connection status
4. Environment variables are correctly set

Your backend is now fully prepared for Railway deployment with optimized configuration!