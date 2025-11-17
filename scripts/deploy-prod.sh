#!/bin/bash

# Evid Flow Production Deployment Script
set -e

echo "🚀 Starting Evid Flow Production Deployment..."

# Load environment variables
if [ -f .env.production ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded"
else
    echo "❌ .env.production file not found"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs/nginx
mkdir -p nginx/ssl

# Build and start services
echo "🐳 Building and starting Docker containers..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
curl -f http://localhost:8000/health || {
    echo "❌ Gateway health check failed"
    docker-compose -f docker-compose.prod.yml logs api-gateway
    exit 1
}

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose -f docker-compose.prod.yml exec api-gateway python -c "
import asyncio
from app.database import create_db_and_tables
asyncio.run(create_db_and_tables())
"

echo "✅ Evid Flow Production Deployment Completed Successfully!"
echo "🌐 Gateway: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"
echo "🔍 Health: http://localhost:8000/health"

# Display running services
echo ""
echo "🏃‍♂️ Running Services:"
docker-compose -f docker-compose.prod.yml ps
