import re

# Read the original file
with open('main.py', 'r') as f:
    content = f.read()

# Fix the async session usage in register function
content = re.sub(
    r'async with get_session\(\) as session:',
    'async for session in get_session():',
    content
)

# Write the fixed content back
with open('main.py', 'w') as f:
    f.write(content)

print("✅ Fixed database session usage in register function")
