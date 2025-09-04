FROM mcr.microsoft.com/devcontainers/python:3.12

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    redis-tools \
    netcat-openbsd \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN python -m pip install --upgrade pip

# Set environment variables
ENV FLIT_ROOT_INSTALL=1
ENV PYTHONPATH=/workspaces/netbox-aws-vpc-plugin
ENV DJANGO_SETTINGS_MODULE=netbox.settings
ENV NETBOX_CONFIG=/opt/netbox/netbox/netbox/configuration.py

# Create NetBox configuration directory
RUN mkdir -p /opt/netbox/netbox/netbox && chown -R vscode:vscode /opt/netbox

## Project dependencies are installed during container creation (see postCreateCommand)

## Pre-commit hooks are installed during container creation (see setup.sh)

## Base image already provides the vscode user; working directory is set by devcontainer
