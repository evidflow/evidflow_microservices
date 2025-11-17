#!/usr/bin/env python3
import resend

# Use your actual API key
resend.api_key = "re_XhCdy6P7_7poeNWRaBbYwQSx1xRmSHpRD"

print("🔑 Using your Resend API key")
print("📧 Testing email delivery...")

try:
    params = {
        "from": "nonreply@evidflow.com",  # Use Resend test domain
        "to": ["evidflow0@gmail.com"],   # REPLACE WITH YOUR ACTUAL EMAIL
        "subject": "Evid Flow Test - Resend is Working!",
        "html": """
        <!DOCTYPE html>
        <html>
        <body>
            <h2>🎉 Success! Resend.com is Working</h2>
            <p>This is a test email from your Evid Flow application.</p>
            <p>If you receive this, your email service is correctly configured!</p>
            <p><strong>Next steps:</strong></p>
            <ul>
                <li>Verify your domain in Resend dashboard</li>
                <li>Update FROM_EMAIL to your domain</li>
                <li>Test verification emails in your app</li>
            </ul>
        </body>
        </html>
        """
    }
    
    print("Sending test email...")
    email = resend.Emails.send(params)
    print(f"✅ Email sent successfully!")
    print(f"📨 Email ID: {email.get('id')}")
    print("📧 Check your inbox (and spam folder) for the test email!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("This indicates the issue with your Resend configuration")
