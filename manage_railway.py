#!/usr/bin/env python
"""
Smart Railway Startup Manager - Python Version
Handles Railway deployment phases with intelligent environment detection
"""
import os
import sys
import subprocess
import time

def detect_environment():
    """Detect the current deployment environment with advanced intelligence"""
    is_railway = bool(os.getenv('RAILWAY_PROJECT_ID'))
    is_nixpacks_build = bool(os.getenv('NIXPACKS_PLAN_PATH'))
    is_docker_build = bool(os.getenv('DOCKER_BUILDKIT'))
    
    return {
        'is_railway_build': is_nixpacks_build,
        'is_railway_runtime': is_railway and not is_nixpacks_build,
        'is_docker_build': is_docker_build,
        'is_local': not is_railway and not is_docker_build,
        'railway_env': os.getenv('RAILWAY_ENVIRONMENT_NAME', 'production'),
        'railway_project': os.getenv('RAILWAY_PROJECT_ID', ''),
        'port': os.getenv('PORT', '8000'),
        'python_path': os.getenv('PYTHON', 'python'),
        'virtual_env': os.getenv('VIRTUAL_ENV', ''),
        'nixpacks_venv': '/opt/venv' if os.path.exists('/opt/venv') else None
    }

def run_command(command, description, ignore_errors=False):
    """Run a command with proper error handling"""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        if not ignore_errors:
            return False
        return True

def main():
    env = detect_environment()
    
    print("🚀 REJLERS Backend - Advanced Railway Startup")
    print(f"   Build Phase: {env['is_railway_build']}")
    print(f"   Runtime Phase: {env['is_railway_runtime']}")
    print(f"   Docker Build: {env['is_docker_build']}")
    print(f"   Local Dev: {env['is_local']}")
    print(f"   Environment: {env['railway_env']}")
    print(f"   Project ID: {env['railway_project'][:8]}..." if env['railway_project'] else "   Project ID: None")
    print(f"   Virtual ENV: {env['nixpacks_venv'] or env['virtual_env'] or 'None'}")
    
    # Set Python executable path for Railway
    if env['nixpacks_venv'] and os.path.exists(f"{env['nixpacks_venv']}/bin/python"):
        python_path = f"{env['nixpacks_venv']}/bin/python"
        pip_path = f"{env['nixpacks_venv']}/bin/pip"
        print(f"   Using Nixpacks Python: {python_path}")
    else:
        python_path = env['python_path']
        pip_path = 'pip'
        print(f"   Using System Python: {python_path}")
    
    # Set Django settings based on environment
    if env['is_railway_build'] or env['is_docker_build']:
        print("🔧 Build Phase: Using railway settings")
        os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.railway'
    elif env['is_railway_runtime']:
        print("🏃 Runtime Phase: Using production settings") 
        os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.production'
    else:
        print("🏠 Local Development")
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    
    # Build phase - minimal operations
    if env['is_railway_build']:
        print("📦 Build Phase Complete - No database operations")
        return 0
    
    # Runtime phase - full deployment
    if env['is_railway_runtime']:
        print("🚀 Runtime Phase - Starting deployment sequence")
        
        # Wait for database to be ready
        print("⏳ Waiting for database connection...")
        max_retries = 30
        for i in range(max_retries):
            if run_command('python manage.py check --database default', f"Database check attempt {i+1}/{max_retries}", ignore_errors=True):
                print("✅ Database connection established")
                break
            time.sleep(2)
        else:
            print("❌ Database connection failed after 30 attempts")
            return 1
        
        # Run migrations
        if not run_command('python manage.py migrate --noinput', "Running database migrations"):
            print("❌ Migration failed")
            return 1
        
        # Collect static files
        if not run_command('python manage.py collectstatic --noinput --clear', "Collecting static files", ignore_errors=True):
            print("⚠️ Static file collection had issues, but continuing")
        
        # Final health check
        if not run_command('python manage.py check --deploy', "Final deployment health check", ignore_errors=True):
            print("⚠️ Health check had warnings, but continuing")
    
    # Start web server with correct Python path
    if len(sys.argv) > 1 and sys.argv[1] == 'web' or env['is_railway_runtime']:
        print(f"🌐 Starting Gunicorn web server on port {env['port']}")
        
        # Use Gunicorn for production
        if env['nixpacks_venv'] and os.path.exists(f"{env['nixpacks_venv']}/bin/gunicorn"):
            os.execv(f"{env['nixpacks_venv']}/bin/gunicorn", [f"{env['nixpacks_venv']}/bin/gunicorn", 'config.wsgi:application', '--bind', f"0.0.0.0:{env['port']}"])
        else:
            os.execvp('gunicorn', ['gunicorn', 'config.wsgi:application', '--bind', f"0.0.0.0:{env['port']}"])
    
    print("✅ Startup sequence complete")
    return 0

if __name__ == '__main__':
    sys.exit(main())