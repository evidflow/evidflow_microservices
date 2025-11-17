#!/bin/bash

echo "🚀 Complete Resend.com Setup for Evid Flow"
echo "==========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to check service status
check_service() {
    if curl -s http://localhost:8010/health >/dev/null; then
        echo -e "${GREEN}✅ Email service is running${NC}"
        return 0
    else
        echo -e "${RED}❌ Email service is not responding${NC}"
        return 1
    fi
}

# Check current service status
echo ""
echo "📡 Checking current email service status..."
check_service

# Get Resend API key
echo ""
echo -e "${YELLOW}📧 Resend.com Setup${NC}"
echo "-------------------"
echo "1. Go to: https://resend.com"
echo "2. Sign up for free account"
echo "3. Verify your email address"
echo "4. Go to API Keys: https://resend.com/api-keys"
echo "5. Create a new API key"
echo ""
echo "Please enter your Resend API key:"
read -r RESEND_API_KEY

if [ -z "$RESEND_API_KEY" ]; then
    echo -e "${RED}❌ No API key provided. Setup cancelled.${NC}"
    exit 1
fi

# Validate API key format (starts with re_)
if [[ ! $RESEND_API_KEY =~ ^re_ ]]; then
    echo -e "${YELLOW}⚠️  API key should start with 're_'. Please double-check your key.${NC}"
    echo "Continue anyway? (y/n)"
    read -r confirm
    if [[ ! $confirm =~ ^[Yy] ]]; then
        exit 1
    fi
fi

# Update environment file
echo ""
echo "🔄 Updating environment configuration..."
if [ ! -f .env.production ]; then
    echo -e "${RED}❌ .env.production not found${NC}"
    exit 1
fi

# Update or add RESEND_API_KEY
if grep -q "RESEND_API_KEY" .env.production; then
    sed -i "s/RESEND_API_KEY=.*/RESEND_API_KEY=$RESEND_API_KEY/" .env.production
    echo -e "${GREEN}✅ Updated RESEND_API_KEY in .env.production${NC}"
else
    echo "RESEND_API_KEY=$RESEND_API_KEY" >> .env.production
    echo -e "${GREEN}✅ Added RESEND_API_KEY to .env.production${NC}"
fi

# Add FROM_EMAIL if not exists
if ! grep -q "FROM_EMAIL" .env.production; then
    echo "FROM_EMAIL=noreply@evidflow.com" >> .env.production
    echo -e "${GREEN}✅ Added FROM_EMAIL to .env.production${NC}"
fi

# Restart email service
echo ""
echo "🔄 Restarting email service..."
docker compose -f docker-compose.prod.yml stop email-service
docker compose -f docker-compose.prod.yml build email-service --no-cache
docker compose -f docker-compose.prod.yml up -d email-service

echo ""
echo "⏳ Waiting for service to start..."
sleep 10

# Verify service is running
echo ""
echo "🔍 Verifying service status..."
if check_service; then
    echo -e "${GREEN}🎉 Email service restarted successfully!${NC}"
else
    echo -e "${RED}❌ Service failed to start. Checking logs...${NC}"
    docker logs evid-flow-production-email-service-1 --tail 20
    exit 1
fi

# Test configuration
echo ""
echo "🧪 Testing Resend configuration..."
curl -s http://localhost:8010/health | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('📊 Service Info:')
print(f'   Status: {data.get(\"status\", \"N/A\")}')
print(f'   Provider: {data.get(\"provider\", \"N/A\")}')
print(f'   Service: {data.get(\"service\", \"N/A\")}')
"

echo ""
echo -e "${GREEN}🎉 Resend.com setup completed successfully!${NC}"
