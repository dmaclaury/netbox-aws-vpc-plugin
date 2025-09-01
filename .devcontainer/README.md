# NetBox AWS VPC Plugin Development Container

This development container provides a complete environment for developing the NetBox AWS VPC Plugin with all necessary dependencies and services.

## Features

- **Python 3.12** with all development tools
- **NetBox 4.0+** development environment
- **PostgreSQL 15** database
- **Redis 7** for caching and webhooks
- **AWS CLI** for AWS integration testing
- **Pre-configured VS Code extensions** for Python development
- **Automated setup** with pre-commit hooks and code formatting

## Getting Started

### Prerequisites

- Docker Desktop or Docker Engine
- VS Code with the Dev Containers extension
- Git

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/dmaclaury/netbox-aws-vpc-plugin.git
   cd netbox-aws-vpc-plugin
   ```

2. **Open in VS Code:**
   ```bash
   code .
   ```

3. **Reopen in Container:**
   - When prompted, click "Reopen in Container"
   - Or use `Ctrl+Shift+P` → "Dev Containers: Reopen in Container"

4. **Start Services:**
   ```bash
   # Start PostgreSQL and Redis
   docker-compose -f .devcontainer/docker-compose.yml up -d

   # Or start the development environment
   bash .devcontainer/start-services.sh
   ```

## Development Workflow

### Code Quality Tools

The container comes with pre-configured code quality tools:

- **Black** - Code formatting (line length: 120)
- **isort** - Import sorting (Black profile)
- **flake8** - Linting
- **pre-commit** - Git hooks for code quality

### Available Commands

```bash
# Format code
make format

# Lint code
make lint

# Run tests
make test

# Run all checks
make pre-commit

# Clean build artifacts
make clean
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=netbox_aws_vpc_plugin

# Run specific test file
pytest netbox_aws_vpc_plugin/tests/test_models.py

# Run tests with verbose output
pytest -v
```

### NetBox Development Server

```bash
# Navigate to NetBox directory
cd /opt/netbox/netbox

# Run migrations
python manage.py migrate

# Create superuser (if needed)
python manage.py createsuperuser

# Start development server
python manage.py runserver 0.0.0.0:8000
```

Access NetBox at: http://localhost:8000

## Project Structure

```
netbox-aws-vpc-plugin/
├── .devcontainer/          # Development container configuration
│   ├── devcontainer.json   # VS Code devcontainer settings
│   ├── Dockerfile         # Container image definition
│   ├── docker-compose.yml # Database services
│   ├── setup.sh          # Environment setup script
│   └── start-services.sh # Service startup script
├── netbox_aws_vpc_plugin/ # Plugin source code
│   ├── models/            # Django models
│   ├── api/               # API views and serializers
│   ├── views.py           # Web views
│   ├── forms.py           # Django forms
│   └── tests/             # Test suite
├── docs/                  # Documentation
├── pyproject.toml         # Project configuration
└── requirements_dev.txt   # Development dependencies
```

## Configuration

### Environment Variables

- `PYTHONPATH` - Set to project root
- `DJANGO_SETTINGS_MODULE` - NetBox settings module
- `NETBOX_CONFIG` - NetBox configuration file path

### Database Configuration

- **Host:** localhost
- **Port:** 5432
- **Database:** netbox
- **Username:** netbox
- **Password:** netbox

### Redis Configuration

- **Host:** localhost
- **Port:** 6379
- **Database 0:** Webhooks
- **Database 1:** Caching

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   - Ensure ports 8000, 5432, and 6379 are available
   - Stop conflicting services: `sudo systemctl stop postgresql redis`

2. **Database connection errors:**
   - Check if PostgreSQL is running: `docker-compose ps`
   - Restart services: `docker-compose restart`

3. **Permission issues:**
   - The container runs as `vscode` user
   - Use `sudo` for system-level operations

### Service Management

```bash
# Start services
docker-compose -f .devcontainer/docker-compose.yml up -d

# Stop services
docker-compose -f .devcontainer/docker-compose.yml down

# View logs
docker-compose -f .devcontainer/docker-compose.yml logs -f

# Restart services
docker-compose -f .devcontainer/docker-compose.yml restart
```

### Reset Environment

```bash
# Remove all containers and volumes
docker-compose -f .devcontainer/docker-compose.yml down -v

# Rebuild container
# In VS Code: Ctrl+Shift+P → "Dev Containers: Rebuild Container"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Format code: `make format`
6. Submit a pull request

## Support

- **Issues:** [GitHub Issues](https://github.com/dmaclaury/netbox-aws-vpc-plugin/issues)
- **Documentation:** [Project Wiki](https://github.com/dmaclaury/netbox-aws-vpc-plugin/wiki)
- **Discussions:** [GitHub Discussions](https://github.com/dmaclaury/netbox-aws-vpc-plugin/discussions)

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](../LICENSE) file for details.
