#!/bin/bash

echo "🚀 Evid Flow Production Setup"

# Check if virtual environment exists
if [ ! -d "evid_env" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv evid_env
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source evid_env/bin/activate

# Install shared requirements
echo "📚 Installing shared dependencies..."
pip install --upgrade pip
pip install fastapi==0.104.1 uvicorn==0.24.0 sqlmodel==0.0.14 sqlalchemy[asyncio]==2.0.23 asyncpg==0.29.0 python-dotenv==1.0.0 python-multipart==0.0.6 redis==5.0.1

# Create remaining service requirements
for service in meal analytics payments files notifications; do
    cp services/auth/requirements.txt services/$service/requirements.txt
    cp services/auth/Dockerfile.prod services/$service/Dockerfile.prod
    
    # Create basic main.py for remaining services
    cat > services/$service/main.py << EOL
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
import os
from datetime import datetime

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"/var/log/evidflow/{service}.log")
    ]
)

app = FastAPI(title="${service^} Service - Production", version="1.0.0")
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*.evidflow.com"])

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "$service",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=800$(( ${service:0:1} == "m" ? 5 : ${service:0:1} == "a" ? 6 : ${service:0:1} == "p" ? 7 : ${service:0:1} == "f" ? 8 : 9 )))
EOL
done

# Add specific dependencies for analytics
echo "groq==0.3.0" >> services/analytics/requirements.txt
echo "pandas==2.1.3" >> services/analytics/requirements.txt

# Add Stripe for payments
echo "stripe==7.0.0" >> services/payments/requirements.txt

echo "✅ Setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Review and update .env.production with your actual credentials"
echo "2. Run: ./scripts/deploy-prod.sh"
echo "3. Access the API at: http://localhost:8000"
echo "4. Check docs at: http://localhost:8000/docs"
