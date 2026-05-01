#!/bin/bash

# SDIRS Deployment Script
# This script automates the deployment process

set -e

echo "====================================="
echo "  SDIRS Full-Stack Deployment"
echo "====================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Function to deploy in development mode
deploy_dev() {
    echo "🚀 Deploying in DEVELOPMENT mode..."
    echo ""

    # Check if .env files exist
    if [ ! -f "backend/.env" ]; then
        echo "⚠️  Creating backend/.env from template..."
        cp backend/.env.example backend/.env
    fi

    if [ ! -f "mobile-app/.env" ]; then
        echo "⚠️  Creating mobile-app/.env from template..."
        cp mobile-app/.env.example mobile-app/.env
        echo "⚠️  Please update mobile-app/.env with your local IP address"
    fi

    # Build and start services
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d

    echo ""
    echo "✅ Development deployment complete!"
    echo ""
    echo "Services:"
    echo "  - Backend API: http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo "  - Socket.io: ws://localhost:8000"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop: docker-compose down"
}

# Function to deploy in production mode
deploy_prod() {
    echo "🚀 Deploying in PRODUCTION mode..."
    echo ""

    # Check if production .env exists
    if [ ! -f ".env" ]; then
        echo "❌ Production .env file not found!"
        echo "Please create .env from .env.example and update the values"
        exit 1
    fi

    if [ ! -f "backend/.env.production" ]; then
        echo "❌ backend/.env.production not found!"
        echo "Please create it from .env.production.example"
        exit 1
    fi

    # Build and start services
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

    echo ""
    echo "✅ Production deployment complete!"
    echo ""
    echo "Services:"
    echo "  - Backend API: http://localhost (via Nginx)"
    echo "  - API Docs: http://localhost/docs"
    echo "  - Database: PostgreSQL (internal)"
    echo "  - Cache: Redis (internal)"
    echo ""
    echo "To view logs: docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f"
    echo "To stop: docker-compose -f docker-compose.yml -f docker-compose.prod.yml down"
}

# Function to build mobile app
build_mobile() {
    echo "📱 Building mobile app..."
    echo ""

    cd mobile-app

    # Install dependencies
    npm install

    # Build for web (if needed)
    echo "Building for web..."
    npx expo export:web

    # For mobile builds, use Expo EAS
    echo ""
    echo "For mobile builds, use:"
    echo "  npx eas build --platform android"
    echo "  npx eas build --platform ios"
    echo ""
    echo "Make sure to configure EAS with: npx eas init"

    cd ..
}

# Main menu
echo "Select deployment mode:"
echo "1) Development"
echo "2) Production"
echo "3) Build Mobile App Only"
echo ""

read -p "Enter choice (1-3): " choice

case $choice in
    1)
        deploy_dev
        ;;
    2)
        deploy_prod
        ;;
    3)
        build_mobile
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment script completed!"
echo ""