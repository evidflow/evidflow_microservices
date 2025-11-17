#!/bin/bash

# Evid Flow Fixed Docker Deployment
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
    echo "❌ .env.production not found. Creating a basic one..."
    cat > .env.production << 'ENVEOF'
# Basic Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database (using PostgreSQL from Docker Compose)
DATABASE_URL=postgresql+asyncpg://evid_user:evid_password@postgres:5432/evid_flow_prod
DB_PASSWORD=evid_password

# Security
SECRET_KEY=dev_secret_key_change_in_production_325a70a235eb0d2aad61314ff64d9be5efd57f9191da60871c921827c2c131cc

# Email (optional for testing)
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=test@example.com
SMTP_PASSWORD=test_password
FROM_EMAIL=noreply@evidflow.com

# AI (optional for testing)
GROQ_API_KEY=test_groq_key
GROQ_MODEL=llama-3.1-8b-instant
OPENAI_API_KEY=test_openai_key

# Payments (optional for testing)
STRIPE_SECRET_KEY=test_stripe_key
STRIPE_WEBHOOK_SECRET=test_webhook_secret

# Redis
REDIS_URL=redis://redis:6379
ENVEOF
    echo "✅ Created basic .env.production for testing"
fi

# Verify environment file is readable
if [ ! -r .env.production ]; then
    echo "❌ Cannot read .env.production file"
    exit 1
fi

echo "✅ Using environment file:"
cat .env.production | grep -v 'PASSWORD\|SECRET\|KEY' | head -10

# Create directories
echo "📁 Creating directories..."
mkdir -p logs/nginx
mkdir -p services/email/templates
mkdir -p services/templates/templates
mkdir -p services/reports/storage
mkdir -p services/files/storage

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose --env-file .env.production -f docker-compose.prod.yml down || true

# Validate Docker Compose configuration
echo "🔍 Validating Docker Compose configuration..."
if ! docker-compose --env-file .env.production -f docker-compose.prod.yml config > /dev/null; then
    echo "❌ Docker Compose configuration validation failed"
    exit 1
fi

# Build and start core services first
echo "🏗️ Building core services..."
docker-compose --env-file .env.production -f docker-compose.prod.yml build api-gateway auth-service redis postgres

echo "🚀 Starting core services..."
docker-compose --env-file .env.production -f docker-compose.prod.yml up -d api-gateway auth-service redis postgres

echo "⏳ Waiting for core services to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Core services are healthy!"
        break
    fi
    echo "⏳ Waiting for core services... ($i/30)"
    sleep 5
done

# Check if core services are healthy
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Core services not responding after 30 attempts"
    echo "Checking logs..."
    docker-compose --env-file .env.production -f docker-compose.prod.yml logs api-gateway
    docker-compose --env-file .env.production -f docker-compose.prod.yml logs auth-service
    exit 1
fi

# Build and start remaining services
echo "🏗️ Building remaining services..."
docker-compose --env-file .env.production -f docker-compose.prod.yml build

echo "🚀 Starting all services..."
docker-compose --env-file .env.production -f docker-compose.prod.yml up -d

echo "⏳ Waiting for all services to start..."
sleep 30

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
    docker-compose --env-file .env.production -f docker-compose.prod.yml ps
else
    echo "❌ Deployment failed - Gateway not responding"
    echo "Checking logs..."
    docker-compose --env-file .env.production -f docker-compose.prod.yml logs
    exit 1
fi
