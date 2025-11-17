#!/usr/bin/env python3
"""
Test script to preview email templates
"""
import os
import jinja2
from datetime import datetime

# Setup template environment
template_loader = jinja2.FileSystemLoader(searchpath="./services/email/templates")
template_env = jinja2.Environment(loader=template_loader)

# Test data for each template
test_data = {
    "welcome": {
        "user_name": "John Doe",
        "organization_name": "Humanitarian Aid International",
        "support_email": "support@evidflow.com",
        "current_year": datetime.now().year
    },
    "verify_email": {
        "verification_code": "123456",
        "expiry_hours": 24,
        "current_year": datetime.now().year
    },
    "password_reset": {
        "reset_code": "789012",
        "expiry_hours": 1,
        "current_year": datetime.now().year
    },
    "organization_invite": {
        "organization_name": "Global Development Foundation",
        "invitation_link": "https://app.evidflow.com/accept-invite?token=abc123",
        "current_year": datetime.now().year
    },
    "report_ready": {
        "report_name": "Q3 2024 Donor Report",
        "download_link": "https://app.evidflow.com/reports/download/123",
        "organization_name": "Humanitarian Aid International",
        "generated_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "current_year": datetime.now().year
    },
    "ai_insights": {
        "organization_name": "Humanitarian Aid International",
        "insights_summary": "Program participation increased by 23% in regions with mobile data collection. Beneficiary satisfaction correlates strongly with follow-up frequency.",
        "insights_link": "https://app.evidflow.com/insights/456",
        "current_year": datetime.now().year
    }
}

# Generate previews
output_dir = "./email_previews"
os.makedirs(output_dir, exist_ok=True)

for template_name, data in test_data.items():
    try:
        template = template_env.get_template(f"{template_name}.html")
        html_content = template.render(**data)
        
        # Save preview
        preview_file = os.path.join(output_dir, f"{template_name}_preview.html")
        with open(preview_file, "w") as f:
            f.write(html_content)
        
        print(f"✅ Generated preview: {preview_file}")
        
    except Exception as e:
        print(f"❌ Failed to generate {template_name}: {e}")

print(f"\n🎉 All email previews generated in {output_dir}/")
print("You can open these files in a web browser to see how the emails will look.")
