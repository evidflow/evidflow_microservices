from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import logging
import os
from datetime import datetime

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Service registry with ports
SERVICE_REGISTRY = {
    "auth": "http://auth-service:8001",
    "onboarding": "http://onboarding-service:8002",
    "organizations": "http://org-service:8003",
    "beneficiaries": "http://beneficiary-service:8004",
    "meal": "http://meal-service:8005",
    "analytics": "http://analytics-service:8006",
    "payments": "http://payments-service:8007",
    "files": "http://file-service:8008",
    "notifications": "http://notification-service:8009",
    "email": "http://email-service:8010",
    "reports": "http://reports-service:8011",
    "templates": "http://templates-service:8012",
    "ai": "http://ai-service:8013"
}

app = FastAPI(
    title="Evid Flow API Gateway",
    description="Main API Gateway for Evid Flow Microservices",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def gateway_middleware(request: Request, call_next):
    """Route requests to appropriate microservices"""
    path = request.url.path
    
    # Route to services
    for service_name, service_url in SERVICE_REGISTRY.items():
        if path.startswith(f"/{service_name}") or path.startswith(f"/api/{service_name}"):
            service_path = path.replace(f"/{service_name}", "").replace(f"/api/{service_name}", "")
            target_url = f"{service_url}{service_path or '/'}"
            
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    # Forward request
                    response = await client.request(
                        method=request.method,
                        url=target_url,
                        headers={k: v for k, v in request.headers.items() if k.lower() != 'host'},
                        content=await request.body(),
                        params=dict(request.query_params)
                    )
                    
                    return JSONResponse(
                        content=response.json(),
                        status_code=response.status_code,
                        headers=dict(response.headers)
                    )
                    
            except httpx.ConnectError:
                logger.error(f"Service {service_name} unavailable at {target_url}")
                return JSONResponse(
                    status_code=503,
                    content={"detail": f"Service {service_name} temporarily unavailable"}
                )
            except Exception as e:
                logger.error(f"Gateway error for {service_name}: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"detail": "Internal server error"}
                )
    
    return await call_next(request)

@app.get("/health")
async def health_check():
    """Comprehensive health check for all services"""
    service_status = {}
    
    for service_name, service_url in SERVICE_REGISTRY.items():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                start_time = datetime.now()
                response = await client.get(f"{service_url}/health")
                response_time = (datetime.now() - start_time).total_seconds()
                
                service_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": round(response_time, 3),
                    "status_code": response.status_code
                }
        except Exception as e:
            service_status[service_name] = {
                "status": "unreachable",
                "error": str(e)
            }
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "production",
        "services": service_status
    }

@app.get("/")
async def root():
    return {
        "message": "Evid Flow MEAL Automation Suite - API Gateway",
        "version": "3.0.0",
        "status": "operational",
        "services": list(SERVICE_REGISTRY.keys())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
