import yaml
import sys

# Read the docker-compose file
with open('docker-compose.prod.yml', 'r') as f:
    compose_data = yaml.safe_load(f)

# Remove email-service from networks section
if 'networks' in compose_data and 'evid-network' in compose_data['networks']:
    if 'email-service' in compose_data['networks']['evid-network']:
        del compose_data['networks']['evid-network']['email-service']

# Add network_mode: host to email-service
if 'services' in compose_data and 'email-service' in compose_data['services']:
    compose_data['services']['email-service']['network_mode'] = 'host'
    # Remove networks from email-service
    if 'networks' in compose_data['services']['email-service']:
        del compose_data['services']['email-service']['networks']

# Write back
with open('docker-compose.prod.yml', 'w') as f:
    yaml.dump(compose_data, f, default_flow_style=False)

print("✅ Fixed network configuration")
