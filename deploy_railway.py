#!/usr/bin/env python3
"""
Railway Deployment Script for REJLERS Backend
Automates the deployment process with proper environment configuration
"""

import os
import sys
import json
import subprocess
from datetime import datetime

def print_header(message):
    """Print formatted header"""
    print(f"\n{'='*50}")
    print(f" {message}")
    print(f"{'='*50}")

def print_step(step, message):
    """Print formatted step"""
    print(f"\n[STEP {step}] {message}")
    print("-" * 30)

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        'requirements.txt',
        'Procfile',
        'runtime.txt',
        'railway.json',
        'manage.py',
        'config/wsgi.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files present")
    return True

def check_railway_cli():
    """Check if Railway CLI is installed"""
    try:
        result = subprocess.run(['railway', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Railway CLI installed: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Railway CLI not found. Install with: npm install -g @railway/cli")
        return False

def display_env_template():
    """Display environment variables template"""
    env_vars = {
        "DJANGO_SETTINGS_MODULE": "config.settings.production",
        "SECRET_KEY": "your-super-secret-key-change-this",
        "DEBUG": "False",
        "PYTHONUNBUFFERED": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "ALLOWED_HOSTS": ".railway.app,.vercel.app",
        "CORS_ALLOWED_ORIGINS": "https://your-frontend.vercel.app,http://localhost:3000"
    }
    
    print("\n📋 REQUIRED ENVIRONMENT VARIABLES:")
    print("Add these to your Railway project:")
    for key, value in env_vars.items():
        print(f"  {key}={value}")
    
    print("\n🔐 OPTIONAL ENVIRONMENT VARIABLES:")
    optional_vars = {
        "OPENAI_API_KEY": "your-openai-api-key",
        "EMAIL_HOST_USER": "your-email@gmail.com",
        "EMAIL_HOST_PASSWORD": "your-app-password",
        "SENTRY_DSN": "your-sentry-dsn"
    }
    
    for key, value in optional_vars.items():
        print(f"  {key}={value}")

def main():
    print_header("REJLERS Backend - Railway Deployment")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check current directory
    if not os.path.exists('manage.py'):
        print("❌ Please run this script from the Django project root directory")
        sys.exit(1)
    
    print_step(1, "Checking Requirements")
    if not check_requirements():
        sys.exit(1)
    
    print_step(2, "Checking Railway CLI")
    if not check_railway_cli():
        print("\n💡 Install Railway CLI and try again:")
        print("   npm install -g @railway/cli")
        sys.exit(1)
    
    print_step(3, "Environment Variables Template")
    display_env_template()
    
    print_step(4, "Deployment Instructions")
    print("""
📝 DEPLOYMENT STEPS:

1. Create Railway Project:
   railway new

2. Add PostgreSQL Database:
   - Go to Railway dashboard
   - Click "+ New" → "Database" → "PostgreSQL"

3. Set Environment Variables:
   - Copy variables from template above
   - Add them in Railway project settings

4. Deploy:
   railway up

5. Run Migrations:
   railway shell
   python manage.py migrate
   python manage.py setup_rbac

6. Verify Deployment:
   curl https://your-project.railway.app/health/
    """)
    
    print_step(5, "Quick Deploy (if already configured)")
    deploy = input("Deploy now? (y/N): ").lower().strip()
    
    if deploy == 'y':
        try:
            print("🚀 Deploying to Railway...")
            subprocess.run(['railway', 'up'], check=True)
            print("✅ Deployment initiated!")
            print("\n📊 Check deployment status:")
            print("   railway status")
            print("\n📋 View logs:")
            print("   railway logs")
        except subprocess.CalledProcessError as e:
            print(f"❌ Deployment failed: {e}")
            sys.exit(1)
    
    print_header("Deployment Guide Complete")
    print("📚 For detailed troubleshooting, see: RAILWAY_DEPLOYMENT_GUIDE.md")

if __name__ == "__main__":
    main()