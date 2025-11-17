#!/bin/bash

# Evid Flow Complete Production Deployment
set -e

echo "🚀 Starting Complete Evid Flow Production Deployment..."

# Load environment
if [ -f .env.production ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded"
else
    echo "❌ .env.production file not found"
    exit 1
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p logs/nginx
mkdir -p nginx/ssl
mkdir -p services/email/templates
mkdir -p services/templates/templates
mkdir -p services/reports/templates

# Build and start all services
echo "🐳 Building and starting all Docker containers..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Wait for services
echo "⏳ Waiting for services to be healthy..."
sleep 45

# Check gateway health
echo "🔍 Checking gateway health..."
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

# Initialize email templates
echo "📧 Initializing email templates..."
docker-compose -f docker-compose.prod.yml exec email-service python -c "
import asyncio
from app.main import load_default_templates
asyncio.run(load_default_templates())
"

echo "✅ Evid Flow Complete Production Deployment Successful!"
echo ""
echo "🌐 Services Status:"
echo "   Gateway: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Health: http://localhost:8000/health"
echo ""
echo "📊 Available Services:"
echo "   ✅ Authentication & Authorization"
echo "   ✅ User Onboarding & Tier Selection"
echo "   ✅ Organization Management"
echo "   ✅ Beneficiary Database"
echo "   ✅ MEAL Service (Monitoring, Evaluation, Accountability, Learning)"
echo "   ✅ Analytics & Reporting"
echo "   ✅ Payment Processing (Stripe)"
echo "   ✅ File Upload & Management"
echo "   ✅ Email Service (SMTP)"
echo "   ✅ AI-Powered Insights (Groq)"
echo "   ✅ Report Generation (PDF, Excel, Word)"
echo "   ✅ Template Management"
echo ""
echo "💼 Business Model:"
echo "   Starter: $1,000/month - 50 users, 10K beneficiaries"
echo "   Professional: $2,500/month - 100 users, 50K beneficiaries"
echo "   Enterprise: $5,000/month - Unlimited users & beneficiaries"

# Display running services
echo ""
echo "🏃‍♂️ Running Containers:"
docker-compose -f docker-compose.prod.yml ps
