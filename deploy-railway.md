# Railway Backend Deployment Guide

## Environment Variables to Set in Railway:

```bash
DATABASE_URL=postgresql://postgres:nfeAvnnoFsSJDcJDzXhsQkjKNaQQMMGP@switchyard.proxy.rlwy.net:50335/railway
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=production-testing-secret-key-change-for-real-production
DEBUG=False
ALLOWED_HOSTS=rejlers-backend-production.up.railway.app,.railway.app,localhost
FRONTEND_URL=https://rejlers-frontend.vercel.app
CORS_ALLOWED_ORIGINS=https://rejlers-frontend.vercel.app,https://rejlers.vercel.app
```

## Deployment Commands:

1. Connect to Railway CLI:
   ```bash
   railway login
   railway link
   ```

2. Set environment variables:
   ```bash
   railway variables set DATABASE_URL="postgresql://postgres:nfeAvnnoFsSJDcJDzXhsQkjKNaQQMMGP@switchyard.proxy.rlwy.net:50335/railway"
   railway variables set DJANGO_SETTINGS_MODULE="config.settings.production"
   railway variables set SECRET_KEY="production-testing-secret-key-change-for-real-production"
   railway variables set DEBUG="False"
   railway variables set ALLOWED_HOSTS="rejlers-backend-production.up.railway.app,.railway.app,localhost"
   railway variables set FRONTEND_URL="https://rejlers-frontend.vercel.app"
   ```

3. Deploy:
   ```bash
   railway up
   ```

## Manual Railway Dashboard Steps:

1. Go to https://railway.app
2. Select your project: rejlers-backend-production
3. Add environment variables in Settings > Variables
4. Redeploy the service