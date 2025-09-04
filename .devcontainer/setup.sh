#!/bin/bash
set -e

echo "🚀 Setting up NetBox AWS VPC Plugin development environment..."

# Ensure dev Python tools are installed (includes pre-commit)
echo "📦 Installing development requirements..."
cd /workspaces/netbox-aws-vpc-plugin || cd "$HOME/workspaces/netbox-aws-vpc-plugin" || true
python -m pip install --upgrade pip
if [ -f requirements_dev.txt ]; then
    pip install -r requirements_dev.txt
else
    pip install pre-commit
fi

# Create NetBox configuration
mkdir -p /opt/netbox/netbox/netbox

cat > /opt/netbox/netbox/netbox/configuration.py << 'EOF'
import os
import sys

# Add the project directory to Python path
sys.path.insert(0, '/workspaces/netbox-aws-vpc-plugin')

# NetBox configuration
PLUGINS = [
    'netbox_aws_vpc_plugin'
]

PLUGINS_CONFIG = {
    "netbox_aws_vpc_plugin": {},
}

# Database configuration
DATABASE = {
    'NAME': 'netbox',
    'USER': 'netbox',
    'PASSWORD': 'netbox',
    'HOST': 'postgres',
    'PORT': '5432',
}

# Redis configuration
REDIS = {
    'webhooks': {
        'HOST': 'redis',
        'PORT': 6379,
        'PASSWORD': '',
        'DATABASE': '0',
        'SSL': False,
    },
    'caching': {
        'HOST': 'redis',
        'PORT': 6379,
        'PASSWORD': '',
        'DATABASE': '1',
        'SSL': False,
    },
}

# Secret key for development
SECRET_KEY = 'django-insecure-development-key-change-in-production'

# Debug mode for development
DEBUG = True

# Allowed hosts
ALLOWED_HOSTS = ['*']

# Static files
STATIC_ROOT = '/opt/netbox/netbox/static'
MEDIA_ROOT = '/opt/netbox/netbox/media'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
EOF

# Create a basic NetBox settings file
cat > /opt/netbox/netbox/netbox/settings.py << 'EOF'
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-development-key-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'netbox_aws_vpc_plugin',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'netbox.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'netbox.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'netbox',
        'USER': 'netbox',
        'PASSWORD': 'netbox',
        'HOST': 'postgres',
        'PORT': '5432',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Plugin configuration
PLUGINS = [
    'netbox_aws_vpc_plugin'
]

PLUGINS_CONFIG = {
    "netbox_aws_vpc_plugin": {},
}
EOF

# Create a basic NetBox URLs file
cat > /opt/netbox/netbox/netbox/urls.py << 'EOF'
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('netbox_aws_vpc_plugin.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
EOF

# Create a basic NetBox WSGI file
cat > /opt/netbox/netbox/netbox/wsgi.py << 'EOF'
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netbox.settings')
application = get_wsgi_application()
EOF

# Create __init__.py files
touch /opt/netbox/netbox/netbox/__init__.py

echo "✅ NetBox configuration created successfully!"

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
pre-commit install-hooks

echo "🎉 Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Start the development services with: bash .devcontainer/start-services.sh"
echo "2. Run tests with: make test"
echo "3. Format code with: make format"
echo "4. Lint code with: make lint"
