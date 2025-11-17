#!/bin/bash

# Evid Flow Simple Docker Deployment
set -e

echo "🚀 Starting Evid Flow Docker Deployment..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

# Check environment file
if [ ! -f .env.production ]; then
    echo "❌ .env.production not found. Please create it first."
    exit 1
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p logs/nginx
mkdir -p services/email/templates
mkdir -p services/templates/templates
mkdir -p services/reports/storage
mkdir -p services/files/storage

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose -f docker-compose.prod.yml down || true

# Build and start core services first
echo "🏗️ Building core services..."
docker-compose -f docker-compose.prod.yml build api-gateway auth-service redis postgres

echo "🚀 Starting core services..."
docker-compose -f docker-compose.prod.yml up -d api-gateway auth-service redis postgres

echo "⏳ Waiting for core services to start..."
sleep 30

# Check if core services are healthy
echo "🔍 Checking core services..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Core services are healthy!"
else
    echo "❌ Core services not responding"
    docker-compose -f docker-compose.prod.yml logs api-gateway
    exit 1
fi

# Build and start remaining services
echo "🏗️ Building remaining services..."
docker-compose -f docker-compose.prod.yml build

echo "🚀 Starting all services..."
docker-compose -f docker-compose.prod.yml up -d

echo "⏳ Waiting for all services to start..."
sleep 45

# Final health check
echo "🔍 Final health check..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo ""
    echo "🎉 Evid Flow Deployment Successful!"
    echo ""
    echo "🌐 Access URLs:"
    echo "   API Gateway: http://localhost:8000"
    echo "   API Documentation: http://localhost:8000/docs"
    echo "   Health Check: http://localhost:8000/health"
    echo ""
    echo "📊 Running Services:"
    docker-compose -f docker-compose.prod.yml ps
else
    echo "❌ Deployment failed - Gateway not responding"
    echo "Checking logs..."
    docker-compose -f docker-compose.prod.yml logs
    exit 1
fi
