import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test the password hashing function directly
from core.security import get_password_hash, verify_password

print("Testing password hashing...")

try:
    password = "TestPass123"
    hashed = get_password_hash(password)
    print(f"Password '{password}' hashed successfully")
    
    is_valid = verify_password(password, hashed)
    print(f"Password verification: {is_valid}")
    
    print("Password hashing test passed!")
except Exception as e:
    print(f"Password hashing test failed: {e}")
    import traceback
    traceback.print_exc()