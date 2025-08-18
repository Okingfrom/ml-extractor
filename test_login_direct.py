#!/usr/bin/env python3
"""
TEST FINAL - Prueba directa del sistema de autenticación
"""
import sys
sys.path.append('/home/keller/ml-extractor')

from auth_system import UserManager

def test_authentication():
    print("=== PRUEBA FINAL AUTENTICACIÓN ===")
    
    # Initialize user manager
    user_manager = UserManager()
    
    # Test credentials
    test_email = "premium@test.com"
    test_password = "Premium123!"
    test_ip = "127.0.0.1"
    
    print(f"Testing login for: {test_email}")
    
    try:
        # Attempt login
        success, result = user_manager.login_user(test_email, test_password, test_ip)
        
        print(f"Login attempt - Success: {success}")
        
        if success:
            print("✅ LOGIN SUCCESSFUL!")
            print(f"User data: {result}")
            print(f"Account type: {result.get('account_type', 'N/A')}")
            print(f"User ID: {result.get('id', 'N/A')}")
            print(f"Email: {result.get('email', 'N/A')}")
            print(f"Verified: {result.get('is_verified', 'N/A')}")
            print(f"Active: {result.get('is_active', 'N/A')}")
        else:
            print("❌ LOGIN FAILED!")
            print(f"Error: {result}")
            
        return success, result
        
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)

if __name__ == "__main__":
    test_authentication()
