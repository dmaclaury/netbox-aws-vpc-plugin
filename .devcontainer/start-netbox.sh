#!/bin/bash

# Check if we should run in background or foreground
BACKGROUND=false
if [ "$1" = "--background" ] || [ "$1" = "-b" ]; then
    BACKGROUND=true
fi

echo "🌐 Starting NetBox development server..."

# Set required environment variables
export SECRET_KEY="${SECRET_KEY:-dummydummydummydummydummydummydummydummydummydummydummydummy}"
export DEBUG="${DEBUG:-True}"

# Detect Codespaces and show appropriate access URL
if [ "$CODESPACES" = "true" ] && [ -n "$CODESPACE_NAME" ]; then
    GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN="${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}"
    ACCESS_URL="https://${CODESPACE_NAME}-8000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
    echo "🔗 GitHub Codespaces detected"
    echo "📍 Access NetBox at: $ACCESS_URL"
else
    ACCESS_URL="http://localhost:8000"
    echo "📍 Access NetBox at: $ACCESS_URL"
fi

# Activate NetBox virtual environment
source /opt/netbox/venv/bin/activate

# Navigate to NetBox directory
cd /opt/netbox/netbox

if [ "$BACKGROUND" = true ]; then
    echo "🚀 Starting NetBox in background"

    # Start NetBox in background with proper environment preservation
    (
        export SECRET_KEY="${SECRET_KEY:-dummydummydummydummydummydummydummydummydummydummydummydummy}"
        export DEBUG="${DEBUG:-True}"
        source /opt/netbox/venv/bin/activate
        cd /opt/netbox/netbox
        python manage.py runserver 0.0.0.0:8000 --verbosity=0
    ) > /tmp/netbox.log 2>&1 &

    # Get the PID
    NETBOX_PID=$!
    echo $NETBOX_PID > /tmp/netbox.pid

    echo "✅ NetBox started in background (PID: $NETBOX_PID)"
    echo "📄 View logs with: netbox-logs"
    echo "🛑 Stop NetBox with: netbox-stop"
else
    echo "🌐 Starting NetBox in foreground"
    python manage.py runserver 0.0.0.0:8000
fi
