#!/usr/bin/env python
"""
Railway startup script for REJLERS Django Backend
Handles migrations, static files, and server startup with proper error handling
"""

import os
import sys
import subprocess
import django

def run_command(command, description, exit_on_error=True):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Return code: {e.returncode}")
        if e.stdout:
            print(f"   Stdout: {e.stdout.strip()}")
        if e.stderr:
            print(f"   Stderr: {e.stderr.strip()}")
        
        if exit_on_error:
            sys.exit(1)
        return False

def main():
    """Main startup sequence"""
    print("🚀 REJLERS Backend - Railway Startup")
    print("=" * 50)
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
    
    # Environment info
    print("📋 Environment Information:")
    print(f"   PORT: {os.environ.get('PORT', 'Not set')}")
    print(f"   DATABASE_URL: {os.environ.get('DATABASE_URL', 'Not set')[:30]}...")
    print(f"   DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    print(f"   Python version: {sys.version}")
    
    # Check if manage.py exists
    if not os.path.exists('manage.py'):
        print("❌ manage.py not found!")
        sys.exit(1)
    
    # Run migrations
    run_command(
        'python manage.py migrate --noinput',
        'Database migrations'
    )
    
    # Collect static files (non-critical)
    run_command(
        'python manage.py collectstatic --noinput',
        'Static files collection',
        exit_on_error=False
    )
    
    # Check Django configuration
    run_command(
        'python manage.py check --deploy',
        'Django deployment check',
        exit_on_error=False
    )
    
    # Get port from environment
    port = os.environ.get('PORT', '8000')
    
    # Start server
    print(f"🌐 Starting Django server on 0.0.0.0:{port}")
    print("=" * 50)
    
    try:
        # Use exec to replace the current process
        os.execv(sys.executable, [
            sys.executable,
            'manage.py',
            'runserver',
            f'0.0.0.0:{port}'
        ])
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()