"""
Soft Coding Configuration for User Management System
Environment-driven configuration for REJLERS backend
"""

import os
from django.conf import settings

# USER CREATION CONFIGURATION - Soft Coded
USER_CREATION_CONFIG = {
    'auto_approve': os.getenv('AUTO_APPROVE_USERS', 'false').lower() == 'true',
    'auto_verify': os.getenv('AUTO_VERIFY_USERS', 'false').lower() == 'true',
    'default_role_id': os.getenv('DEFAULT_ROLE_ID', None),
    'send_welcome_email': os.getenv('SEND_WELCOME_EMAIL', 'true').lower() == 'true',
    'require_email_verification': os.getenv('REQUIRE_EMAIL_VERIFICATION', 'true').lower() == 'true',
    'password_policy': {
        'min_length': int(os.getenv('PASSWORD_MIN_LENGTH', '8')),
        'require_uppercase': os.getenv('PASSWORD_REQUIRE_UPPERCASE', 'true').lower() == 'true',
        'require_lowercase': os.getenv('PASSWORD_REQUIRE_LOWERCASE', 'true').lower() == 'true',
        'require_numbers': os.getenv('PASSWORD_REQUIRE_NUMBERS', 'true').lower() == 'true',
        'require_special_chars': os.getenv('PASSWORD_REQUIRE_SPECIAL', 'false').lower() == 'true'
    },
    'notification_settings': {
        'notify_admin_on_creation': os.getenv('NOTIFY_ADMIN_ON_USER_CREATION', 'true').lower() == 'true',
        'notification_email': os.getenv('ADMIN_NOTIFICATION_EMAIL', 'admin@rejlers.com'),
        'slack_webhook': os.getenv('SLACK_WEBHOOK_URL', None)
    }
}

# BULK IMPORT CONFIGURATION - Soft Coded  
BULK_IMPORT_CONFIG = {
    'max_users_per_batch': int(os.getenv('BULK_MAX_USERS_PER_BATCH', '100')),
    'auto_generate_passwords': os.getenv('BULK_AUTO_GENERATE_PASSWORDS', 'true').lower() == 'true',
    'password_length': int(os.getenv('BULK_PASSWORD_LENGTH', '12')),
    'auto_approve_all': os.getenv('BULK_AUTO_APPROVE_ALL', 'false').lower() == 'true',
    'auto_verify_all': os.getenv('BULK_AUTO_VERIFY_ALL', 'false').lower() == 'true',
    'skip_invalid_records': os.getenv('BULK_SKIP_INVALID_RECORDS', 'true').lower() == 'true',
    'send_bulk_notifications': os.getenv('BULK_SEND_NOTIFICATIONS', 'false').lower() == 'true',
    'default_department': os.getenv('BULK_DEFAULT_DEPARTMENT', 'General'),
    'ai_role_matching': os.getenv('BULK_AI_ROLE_MATCHING', 'true').lower() == 'true',
    'parallel_processing': os.getenv('BULK_PARALLEL_PROCESSING', 'false').lower() == 'true',
    'batch_size': int(os.getenv('BULK_BATCH_SIZE', '10')),
    'error_threshold': float(os.getenv('BULK_ERROR_THRESHOLD', '0.1'))  # 10% error threshold
}

# RBAC CONFIGURATION - Soft Coded
RBAC_CONFIG = {
    'enable_role_hierarchy': os.getenv('RBAC_ENABLE_ROLE_HIERARCHY', 'true').lower() == 'true',
    'auto_role_assignment': os.getenv('RBAC_AUTO_ROLE_ASSIGNMENT', 'true').lower() == 'true',
    'role_inheritance': os.getenv('RBAC_ROLE_INHERITANCE', 'false').lower() == 'true',
    'permission_caching': os.getenv('RBAC_PERMISSION_CACHING', 'true').lower() == 'true',
    'cache_timeout': int(os.getenv('RBAC_CACHE_TIMEOUT', '3600')),  # 1 hour
    'default_permissions': {
        'new_user_permissions': ['view_profile', 'change_password'],
        'guest_permissions': ['view_public'],
        'employee_permissions': ['view_profile', 'change_password', 'view_dashboard']
    }
}

# AI CONFIGURATION - Soft Coded
AI_ROLE_MATCHING_CONFIG = {
    'enable_ai_matching': os.getenv('AI_ROLE_MATCHING_ENABLED', 'true').lower() == 'true',
    'confidence_threshold': float(os.getenv('AI_CONFIDENCE_THRESHOLD', '0.7')),
    'learning_mode': os.getenv('AI_LEARNING_MODE', 'active').lower(),  # active, passive, disabled
    'feedback_collection': os.getenv('AI_FEEDBACK_COLLECTION', 'true').lower() == 'true',
    'model_version': os.getenv('AI_MODEL_VERSION', 'v1.0'),
    'fallback_role': os.getenv('AI_FALLBACK_ROLE', 'Employee'),
    'department_weights': {
        'engineering': float(os.getenv('AI_WEIGHT_ENGINEERING', '0.8')),
        'hr': float(os.getenv('AI_WEIGHT_HR', '0.9')),
        'finance': float(os.getenv('AI_WEIGHT_FINANCE', '0.85')),
        'operations': float(os.getenv('AI_WEIGHT_OPERATIONS', '0.75')),
        'it': float(os.getenv('AI_WEIGHT_IT', '0.8')),
        'sales': float(os.getenv('AI_WEIGHT_SALES', '0.7')),
        'marketing': float(os.getenv('AI_WEIGHT_MARKETING', '0.7'))
    }
}

# AUDIT CONFIGURATION - Soft Coded
AUDIT_CONFIG = {
    'enable_audit_logging': os.getenv('AUDIT_LOGGING_ENABLED', 'true').lower() == 'true',
    'log_level': os.getenv('AUDIT_LOG_LEVEL', 'INFO').upper(),
    'retention_days': int(os.getenv('AUDIT_RETENTION_DAYS', '365')),
    'log_sensitive_data': os.getenv('AUDIT_LOG_SENSITIVE_DATA', 'false').lower() == 'true',
    'compress_old_logs': os.getenv('AUDIT_COMPRESS_OLD_LOGS', 'true').lower() == 'true',
    'export_format': os.getenv('AUDIT_EXPORT_FORMAT', 'json').lower(),
    'real_time_monitoring': os.getenv('AUDIT_REAL_TIME_MONITORING', 'false').lower() == 'true',
    'alert_on_suspicious_activity': os.getenv('AUDIT_ALERT_SUSPICIOUS', 'true').lower() == 'true'
}

# SECURITY CONFIGURATION - Soft Coded
SECURITY_CONFIG = {
    'password_expiry_days': int(os.getenv('PASSWORD_EXPIRY_DAYS', '90')),
    'max_login_attempts': int(os.getenv('MAX_LOGIN_ATTEMPTS', '5')),
    'account_lockout_duration': int(os.getenv('ACCOUNT_LOCKOUT_DURATION', '1800')),  # 30 minutes
    'session_timeout': int(os.getenv('SESSION_TIMEOUT', '28800')),  # 8 hours
    'require_2fa': os.getenv('REQUIRE_2FA', 'false').lower() == 'true',
    'ip_whitelist_enabled': os.getenv('IP_WHITELIST_ENABLED', 'false').lower() == 'true',
    'allowed_ips': os.getenv('ALLOWED_IPS', '').split(',') if os.getenv('ALLOWED_IPS') else [],
    'data_encryption': {
        'encrypt_sensitive_fields': os.getenv('ENCRYPT_SENSITIVE_FIELDS', 'true').lower() == 'true',
        'encryption_algorithm': os.getenv('ENCRYPTION_ALGORITHM', 'AES256'),
        'key_rotation_days': int(os.getenv('KEY_ROTATION_DAYS', '90'))
    }
}

# NOTIFICATION CONFIGURATION - Soft Coded
NOTIFICATION_CONFIG = {
    'email_backend': os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend'),
    'email_host': os.getenv('EMAIL_HOST', 'smtp.gmail.com'),
    'email_port': int(os.getenv('EMAIL_PORT', '587')),
    'email_use_tls': os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true',
    'email_host_user': os.getenv('EMAIL_HOST_USER', ''),
    'email_host_password': os.getenv('EMAIL_HOST_PASSWORD', ''),
    'default_from_email': os.getenv('DEFAULT_FROM_EMAIL', 'noreply@rejlers.com'),
    'admin_email': os.getenv('ADMIN_EMAIL', 'admin@rejlers.com'),
    'notification_templates': {
        'welcome_email': os.getenv('WELCOME_EMAIL_TEMPLATE', 'emails/welcome.html'),
        'password_reset': os.getenv('PASSWORD_RESET_TEMPLATE', 'emails/password_reset.html'),
        'account_activation': os.getenv('ACCOUNT_ACTIVATION_TEMPLATE', 'emails/activation.html'),
        'bulk_import_complete': os.getenv('BULK_IMPORT_TEMPLATE', 'emails/bulk_import.html')
    }
}

# INTEGRATION CONFIGURATION - Soft Coded
INTEGRATION_CONFIG = {
    'ldap_integration': {
        'enabled': os.getenv('LDAP_INTEGRATION_ENABLED', 'false').lower() == 'true',
        'server': os.getenv('LDAP_SERVER', ''),
        'bind_dn': os.getenv('LDAP_BIND_DN', ''),
        'bind_password': os.getenv('LDAP_BIND_PASSWORD', ''),
        'user_search': os.getenv('LDAP_USER_SEARCH', ''),
        'group_search': os.getenv('LDAP_GROUP_SEARCH', ''),
        'sync_interval': int(os.getenv('LDAP_SYNC_INTERVAL', '3600'))  # 1 hour
    },
    'active_directory': {
        'enabled': os.getenv('AD_INTEGRATION_ENABLED', 'false').lower() == 'true',
        'domain': os.getenv('AD_DOMAIN', ''),
        'server': os.getenv('AD_SERVER', ''),
        'use_ssl': os.getenv('AD_USE_SSL', 'true').lower() == 'true'
    },
    'sso_providers': {
        'google': {
            'enabled': os.getenv('GOOGLE_SSO_ENABLED', 'false').lower() == 'true',
            'client_id': os.getenv('GOOGLE_CLIENT_ID', ''),
            'client_secret': os.getenv('GOOGLE_CLIENT_SECRET', '')
        },
        'microsoft': {
            'enabled': os.getenv('MICROSOFT_SSO_ENABLED', 'false').lower() == 'true',
            'client_id': os.getenv('MICROSOFT_CLIENT_ID', ''),
            'client_secret': os.getenv('MICROSOFT_CLIENT_SECRET', '')
        }
    }
}

# PERFORMANCE CONFIGURATION - Soft Coded
PERFORMANCE_CONFIG = {
    'database_connection_pooling': os.getenv('DB_CONNECTION_POOLING', 'true').lower() == 'true',
    'query_optimization': os.getenv('QUERY_OPTIMIZATION', 'true').lower() == 'true',
    'caching_backend': os.getenv('CACHING_BACKEND', 'redis'),
    'cache_timeout': int(os.getenv('CACHE_TIMEOUT', '300')),  # 5 minutes
    'paginate_users_by': int(os.getenv('PAGINATE_USERS_BY', '50')),
    'bulk_operation_chunk_size': int(os.getenv('BULK_OPERATION_CHUNK_SIZE', '100')),
    'async_processing': os.getenv('ASYNC_PROCESSING', 'false').lower() == 'true',
    'celery_enabled': os.getenv('CELERY_ENABLED', 'false').lower() == 'true'
}

# MONITORING CONFIGURATION - Soft Coded
MONITORING_CONFIG = {
    'health_check_interval': int(os.getenv('HEALTH_CHECK_INTERVAL', '60')),  # seconds
    'metrics_collection': os.getenv('METRICS_COLLECTION', 'true').lower() == 'true',
    'performance_monitoring': os.getenv('PERFORMANCE_MONITORING', 'true').lower() == 'true',
    'error_tracking': os.getenv('ERROR_TRACKING', 'true').lower() == 'true',
    'sentry_dsn': os.getenv('SENTRY_DSN', ''),
    'prometheus_enabled': os.getenv('PROMETHEUS_ENABLED', 'false').lower() == 'true',
    'log_level': os.getenv('LOG_LEVEL', 'INFO').upper(),
    'log_format': os.getenv('LOG_FORMAT', 'json').lower()
}


def get_user_management_config():
    """
    Get complete user management configuration with environment overrides
    """
    return {
        'user_creation': USER_CREATION_CONFIG,
        'bulk_import': BULK_IMPORT_CONFIG,
        'rbac': RBAC_CONFIG,
        'ai_matching': AI_ROLE_MATCHING_CONFIG,
        'audit': AUDIT_CONFIG,
        'security': SECURITY_CONFIG,
        'notifications': NOTIFICATION_CONFIG,
        'integrations': INTEGRATION_CONFIG,
        'performance': PERFORMANCE_CONFIG,
        'monitoring': MONITORING_CONFIG
    }


def apply_config_to_django_settings():
    """
    Apply soft coded configuration to Django settings
    """
    if hasattr(settings, '_wrapped') and settings._wrapped is not None:
        # Apply configurations to Django settings
        settings.USER_CREATION_CONFIG = USER_CREATION_CONFIG
        settings.BULK_IMPORT_CONFIG = BULK_IMPORT_CONFIG
        settings.RBAC_CONFIG = RBAC_CONFIG
        settings.AI_ROLE_MATCHING_CONFIG = AI_ROLE_MATCHING_CONFIG
        settings.AUDIT_CONFIG = AUDIT_CONFIG
        settings.SECURITY_CONFIG = SECURITY_CONFIG
        settings.NOTIFICATION_CONFIG = NOTIFICATION_CONFIG
        settings.INTEGRATION_CONFIG = INTEGRATION_CONFIG
        settings.PERFORMANCE_CONFIG = PERFORMANCE_CONFIG
        settings.MONITORING_CONFIG = MONITORING_CONFIG


# Auto-apply configuration when module is imported
apply_config_to_django_settings()