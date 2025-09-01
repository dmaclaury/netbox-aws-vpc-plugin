#!/bin/bash
set -e

echo "🚀 Starting development services..."

# Function to check if a service is running
check_service() {
    local service_name=$1
    local port=$2
    local max_attempts=30
    local attempt=1

    echo "⏳ Waiting for $service_name to be ready..."

    while [ $attempt -le $max_attempts ]; do
        if nc -z localhost $port 2>/dev/null; then
            echo "✅ $service_name is ready on port $port"
            return 0
        fi

        echo "   Attempt $attempt/$max_attempts: $service_name not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo "❌ $service_name failed to start after $max_attempts attempts"
    return 1
}

# Start PostgreSQL (if not already running)
if ! pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
    echo "🐘 Starting PostgreSQL..."
    # Note: In a real devcontainer, you'd typically use Docker Compose or similar
    # For now, we'll just check if it's available
    echo "⚠️  PostgreSQL not running. Please ensure PostgreSQL is available on localhost:5432"
    echo "   You can start it with: sudo systemctl start postgresql"
else
    echo "✅ PostgreSQL is already running"
fi

# Start Redis (if not already running)
if ! nc -z localhost 6379 2>/dev/null; then
    echo "🔴 Starting Redis..."
    # Note: In a real devcontainer, you'd typically use Docker Compose or similar
    # For now, we'll just check if it's available
    echo "⚠️  Redis not running. Please ensure Redis is available on localhost:6379"
    echo "   You can start it with: sudo systemctl start redis"
else
    echo "✅ Redis is already running"
fi

# Wait for services to be ready
if check_service "PostgreSQL" 5432 && check_service "Redis" 6379; then
    echo "🎉 All services are ready!"

    # Run database migrations
    echo "🗄️  Running database migrations..."
    cd /opt/netbox/netbox
    python manage.py migrate --run-syncdb

    # Create a superuser if it doesn't exist
    echo "👤 Creating superuser (if needed)..."
    python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created: admin/admin')
else:
    print('Superuser already exists')
"

    # Collect static files
    echo "📦 Collecting static files..."
    python manage.py collectstatic --noinput

    echo ""
    echo "🚀 Development environment is ready!"
    echo ""
    echo "You can now:"
    echo "1. Start the NetBox development server: cd /opt/netbox/netbox && python manage.py runserver 0.0.0.0:8000"
    echo "2. Access NetBox at: http://localhost:8000"
    echo "3. Login with: admin/admin"
    echo "4. Run tests: make test"
    echo "5. Format code: make format"
    echo "6. Lint code: make lint"
    echo ""
    echo "To start the NetBox server in the background, run:"
    echo "cd /opt/netbox/netbox && nohup python manage.py runserver 0.0.0.0:8000 > netbox.log 2>&1 &"
else
    echo "❌ Some services failed to start. Please check the logs above."
    exit 1
fi
