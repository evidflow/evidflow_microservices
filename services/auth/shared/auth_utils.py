from passlib.context import CryptContext
import hashlib
import secrets

# Password hashing context with fallback
pwd_context = CryptContext(
    schemes=["bcrypt", "sha256_crypt"], 
    deprecated="auto",
    bcrypt__rounds=12
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash with fallback"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"⚠️  Password verification error: {e}")
        # Fallback to SHA256 for legacy users
        if hashed_password.startswith("sha256$"):
            return verify_sha256_password(plain_password, hashed_password)
        return False

def get_password_hash(password: str) -> str:
    """Generate password hash with bcrypt fallback to sha256"""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        print(f"⚠️  Bcrypt hashing failed, using SHA256 fallback: {e}")
        return get_sha256_password_hash(password)

def verify_sha256_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using SHA256 (fallback)"""
    try:
        if hashed_password.startswith("sha256$"):
            parts = hashed_password.split("$")
            if len(parts) == 3:
                salt = parts[1]
                stored_hash = parts[2]
                new_hash = hashlib.pbkdf2_hmac(
                    'sha256', 
                    plain_password.encode('utf-8'), 
                    salt.encode('utf-8'), 
                    100000
                ).hex()
                return stored_hash == new_hash
    except Exception as e:
        print(f"⚠️  SHA256 verification failed: {e}")
    return False

def get_sha256_password_hash(password: str) -> str:
    """Generate SHA256 password hash with salt (fallback)"""
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        salt.encode('utf-8'), 
        100000
    ).hex()
    return f"sha256${salt}${hashed}"
