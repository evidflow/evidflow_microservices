#!/bin/bash

echo "🧪 Email Service Test Suite"
echo "============================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test health endpoint
echo ""
echo "1. Testing Health Endpoint:"
response=$(curl -s -w "%{http_code}" http://localhost:8010/health)
http_code=${response: -3}
body=${response%???}

if [ "$http_code" -eq 200 ]; then
    echo -e "${GREEN}✅ Health check passed (HTTP $http_code)${NC}"
    echo "   Response: $body"
else
    echo -e "${RED}❌ Health check failed (HTTP $http_code)${NC}"
    exit 1
fi

# Test root endpoint
echo ""
echo "2. Testing Root Endpoint:"
curl -s http://localhost:8010/ | python3 -m json.tool

# Prompt for test email
echo ""
echo -e "${YELLOW}3. Send Test Email${NC}"
echo "-----------------"
echo "Enter an email address to send test verification email:"
read -r TEST_EMAIL

if [ -n "$TEST_EMAIL" ]; then
    echo "Sending test email to: $TEST_EMAIL"
    
    response=$(curl -s -w "%{http_code}" -X POST "http://localhost:8010/send-verification" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$TEST_EMAIL\",
            \"code\": \"TEST123\"
        }")
    
    http_code=${response: -3}
    body=${response%???}
    
    if [ "$http_code" -eq 200 ]; then
        echo -e "${GREEN}✅ Test email sent successfully!${NC}"
        echo "   Response: $body"
        echo ""
        echo "📧 Please check your inbox (and spam folder) for the test email."
    else
        echo -e "${RED}❌ Failed to send test email (HTTP $http_code)${NC}"
        echo "   Error: $body"
    fi
else
    echo "Skipping test email send."
fi

echo ""
echo "📋 Service Status:"
docker ps --filter "name=email-service" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
