from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import os
import logging
from typing import Optional

# Import Resend SDK
try:
    import resend
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "resend"])
    import resend

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = FastAPI(title="Email Service", version="2.1.0")

# Email models
class VerificationEmail(BaseModel):
    email: EmailStr
    code: str

class PasswordResetEmail(BaseModel):
    email: EmailStr
    code: str

class InvitationEmail(BaseModel):
    email: EmailStr
    organization_name: str
    invitation_link: str

# Resend.com configuration
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "re_XhCdy6P7_7poeNWRaBbYwQSx1xRmSHpRD")
FROM_EMAIL = os.getenv("FROM_EMAIL", "nonreply@evidflow.com")

# Initialize Resend
resend.api_key = RESEND_API_KEY

async def send_resend_email(to: str, subject: str, html: str) -> bool:
    """Send email using Resend.com Python SDK"""
    if not RESEND_API_KEY:
        logger.error("❌ Resend API key not configured")
        return False
    
    try:
        params = {
            "from": FROM_EMAIL,
            "to": [to],
            "subject": subject,
            "html": html
        }
        
        email = resend.Emails.send(params)
        logger.info(f"✅ Email sent successfully to {to}, ID: {email.get('id', 'unknown')}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Resend SDK error: {e}")
        # Fallback to test domain if domain not verified
        if "domain" in str(e).lower() or "verification" in str(e).lower():
            logger.info("🔄 Trying fallback with Resend test domain...")
            try:
                params["from"] = "onboarding@resend.dev"
                email = resend.Emails.send(params)
                logger.info(f"✅ Email sent with fallback domain to {to}, ID: {email.get('id', 'unknown')}")
                return True
            except Exception as fallback_error:
                logger.error(f"❌ Fallback also failed: {fallback_error}")
        return False

@app.post("/send-verification")
async def send_verification(email_data: VerificationEmail):
    """Send email verification code"""
    subject = "Verify Your Email - Evid Flow"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .code {{ font-size: 24px; font-weight: bold; color: #4CAF50; text-align: center; margin: 20px 0; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Welcome to Evid Flow! 👋</h2>
            <p>Thank you for signing up. Your verification code is:</p>
            <div class="code">{email_data.code}</div>
            <p>Enter this code in the application to verify your email address.</p>
            <p>If you didn't request this, please ignore this email.</p>
            <div class="footer">
                <p>Best regards,<br>The Evid Flow Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    success = await send_resend_email(email_data.email, subject, html)
    
    if success:
        return {"message": "Verification email sent successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send verification email")

@app.post("/send-password-reset")
async def send_password_reset(email_data: PasswordResetEmail):
    """Send password reset code"""
    subject = "Reset Your Password - Evid Flow"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .code {{ font-size: 24px; font-weight: bold; color: #FF6B6B; text-align: center; margin: 20px 0; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Password Reset Request 🔒</h2>
            <p>We received a request to reset your password. Your reset code is:</p>
            <div class="code">{email_data.code}</div>
            <p>Enter this code in the application to reset your password.</p>
            <p>If you didn't request a password reset, please ignore this email.</p>
            <div class="footer">
                <p>Best regards,<br>The Evid Flow Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    success = await send_resend_email(email_data.email, subject, html)
    
    if success:
        return {"message": "Password reset email sent successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send password reset email")

@app.post("/send-invitation")
async def send_invitation(email_data: InvitationEmail):
    """Send organization invitation"""
    subject = f"Invitation to join {email_data.organization_name} - Evid Flow"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .button {{ background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>You're Invited! 🎉</h2>
            <p>You've been invited to join <strong>{email_data.organization_name}</strong> on Evid Flow.</p>
            <p>Click the button below to accept the invitation:</p>
            <p><a href="{email_data.invitation_link}" class="button">Accept Invitation</a></p>
            <p>Or copy this link: <br><code>{email_data.invitation_link}</code></p>
            <div class="footer">
                <p>Best regards,<br>The Evid Flow Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    success = await send_resend_email(email_data.email, subject, html)
    
    if success:
        return {"message": "Invitation email sent successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send invitation email")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "email",
        "provider": "resend",
        "from_email": FROM_EMAIL,
        "version": "2.1.0"
    }

@app.post("/test-email")
async def test_email(email: str):
    """Test endpoint to verify Resend is working"""
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    subject = "Evid Flow Production Test ✅"
    html = f"""
    <!DOCTYPE html>
    <html>
    <body>
        <h2>Production Email Test ✅</h2>
        <p>This is a test email from your <strong>Evid Flow Production</strong> service.</p>
        <p><strong>From:</strong> {FROM_EMAIL}</p>
        <p>If you receive this, your production email service is working correctly!</p>
        <hr>
        <p><small>Sent via Resend.com from your production server</small></p>
    </body>
    </html>
    """
    
    success = await send_resend_email(email, subject, html)
    
    if success:
        return {"message": f"Production test email sent successfully to {email}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send test email")

@app.get("/")
async def root():
    return {"message": "Evid Flow Production Email Service", "from_email": FROM_EMAIL}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010, log_level="info")
