FROM mcr.microsoft.com/devcontainers/python:3.12

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    redis-tools \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN python -m pip install --upgrade pip \
    && python -m pip install \
    'flit>=3.8.0' \
    'netbox>=4.0.0' \
    'django>=4.2.0' \
    'psycopg2-binary' \
    'redis' \
    'boto3' \
    'botocore' \
    'pytest' \
    'pytest-django' \
    'pytest-cov' \
    'factory-boy' \
    'faker'

# Set environment variables
ENV FLIT_ROOT_INSTALL=1
ENV PYTHONPATH=/workspaces/netbox-aws-vpc-plugin
ENV DJANGO_SETTINGS_MODULE=netbox.settings
ENV NETBOX_CONFIG=/opt/netbox/netbox/netbox/configuration.py

# Create NetBox configuration directory
RUN mkdir -p /opt/netbox/netbox/netbox

# Copy and install project dependencies
COPY pyproject.toml requirements_dev.txt ./
RUN python -m flit install --only-deps --deps develop \
    && pip install -r requirements_dev.txt

# Install pre-commit hooks
RUN pre-commit install-hooks

# Create a development user
RUN useradd -m -s /bin/bash vscode \
    && usermod -aG sudo vscode \
    && echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Switch to vscode user
USER vscode
WORKDIR /workspaces/netbox-aws-vpc-plugin
