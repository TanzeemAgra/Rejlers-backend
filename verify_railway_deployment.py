#!/usr/bin/env python3
"""
Railway Deployment Verification Script
Checks all files and configurations before deployment
"""

import os
import sys
from pathlib import Path

def print_status(message, status="INFO"):
    """Print formatted status message"""
    symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
    print(f"{symbols.get(status, 'ℹ️')} {message}")

def check_file_exists(filepath, description):
    """Check if file exists and return status"""
    if os.path.exists(filepath):
        print_status(f"{description}: Found", "SUCCESS")
        return True
    else:
        print_status(f"{description}: Missing", "ERROR")
        return False

def check_requirements_content():
    """Check requirements.txt for Railway compatibility"""
    if not os.path.exists('requirements.txt'):
        return False
    
    with open('requirements.txt', 'r') as f:
        content = f.read()
    
    # Check for relative imports (problematic for Railway)
    if '-r requirements/' in content:
        print_status("requirements.txt contains relative imports", "ERROR")
        return False
    
    # Check for essential packages
    essential_packages = ['Django', 'gunicorn', 'psycopg2-binary', 'whitenoise']
    missing_packages = []
    
    for package in essential_packages:
        if package not in content:
            missing_packages.append(package)
    
    if missing_packages:
        print_status(f"Missing essential packages: {', '.join(missing_packages)}", "ERROR")
        return False
    
    print_status("requirements.txt is Railway-compatible", "SUCCESS")
    return True

def main():
    """Main verification function"""
    print("="*60)
    print("🚀 REJLERS Backend - Railway Deployment Verification")
    print("="*60)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print_status("Not in Django project root directory", "ERROR")
        sys.exit(1)
    
    print_status("Django project root detected", "SUCCESS")
    
    # Check essential files
    files_to_check = [
        ('requirements.txt', 'Requirements file'),
        ('Procfile', 'Process file'),
        ('runtime.txt', 'Python runtime specification'),
        ('railway.json', 'Railway configuration'),
        ('config/wsgi.py', 'WSGI application'),
        ('config/settings/production.py', 'Production settings'),
    ]
    
    all_files_present = True
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_files_present = False
    
    # Check requirements.txt content
    requirements_ok = check_requirements_content()
    
    # Check environment variables template
    if os.path.exists('railway.env.example'):
        print_status("Environment variables template found", "SUCCESS")
    else:
        print_status("No environment variables template", "WARNING")
    
    # Final assessment
    print("\n" + "="*60)
    if all_files_present and requirements_ok:
        print_status("✨ READY FOR RAILWAY DEPLOYMENT! ✨", "SUCCESS")
        print("\n📋 Deployment Steps:")
        print("1. Commit and push changes to your repository")
        print("2. Add environment variables to Railway:")
        print("   - SECRET_KEY")
        print("   - DATABASE_URL (auto-provided by Railway PostgreSQL)")
        print("   - DJANGO_SETTINGS_MODULE=config.settings.production")
        print("   - DEBUG=False")
        print("3. Deploy: railway up")
        print("\n🔗 Expected URL: https://your-project.railway.app")
    else:
        print_status("❌ DEPLOYMENT NOT READY", "ERROR")
        print("Fix the issues above before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main()