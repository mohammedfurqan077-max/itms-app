"""
Test password validation for registration
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.schemas.auth import RegisterRequest
from app.core.security import hash_password, verify_password, validate_password
from pydantic import ValidationError


def test_password_validation():
    """Test various password scenarios"""
    
    print("=" * 80)
    print("PASSWORD VALIDATION TESTS")
    print("=" * 80)
    
    test_cases = [
        # (password, should_pass, description)
        ("Pass123!", True, "Standard strong password"),
        ("MySecureP@ssw0rd!", True, "Strong password with special chars"),
        ("VeryLongPasswordWith123!@#", True, "Long password with mixed chars"),
        ("Simple1!", True, "Minimum length (8 chars)"),
        ("Short1", False, "Too short (7 chars)"),
        ("🔐SecurePass123!", True, "Password with emoji"),
        ("Пароль123!", True, "Password with Cyrillic"),
        ("密码123!", True, "Password with Chinese"),
        ("A" * 128, True, "Maximum length ASCII (128 chars)"),
        ("A" * 129, False, "Over maximum length (129 chars)"),
        ("🔐" * 20, False, "Too many multi-byte chars (exceeds 72 bytes)"),
    ]
    
    passed = 0
    failed = 0
    
    for password, should_pass, description in test_cases:
        print(f"\n{'─' * 80}")
        print(f"Test: {description}")
        print(f"Password: {password[:50]}{'...' if len(password) > 50 else ''}")
        print(f"Length: {len(password)} chars, {len(password.encode('utf-8'))} bytes")
        print(f"Expected: {'PASS' if should_pass else 'FAIL'}")
        
        try:
            # Test schema validation
            request = RegisterRequest(
                name="Test User",
                email="test@example.com",
                password=password,
                role="jawan"
            )
            
            # Test hashing
            hashed = hash_password(password)
            
            # Test verification
            verified = verify_password(password, hashed)
            
            if should_pass:
                if verified:
                    print(f"Result: ✅ PASSED - Password accepted and verified")
                    passed += 1
                else:
                    print(f"Result: ❌ FAILED - Password accepted but verification failed")
                    failed += 1
            else:
                print(f"Result: ❌ FAILED - Password should have been rejected")
                failed += 1
                
        except ValidationError as e:
            if not should_pass:
                print(f"Result: ✅ PASSED - Password correctly rejected")
                print(f"Error: {e.errors()[0]['msg']}")
                passed += 1
            else:
                print(f"Result: ❌ FAILED - Password should have been accepted")
                print(f"Error: {e.errors()[0]['msg']}")
                failed += 1
        except Exception as e:
            print(f"Result: ❌ FAILED - Unexpected error: {str(e)}")
            failed += 1
    
    print(f"\n{'=' * 80}")
    print(f"SUMMARY: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print(f"Success rate: {(passed/len(test_cases)*100):.1f}%")
    print("=" * 80)
    
    return failed == 0


def test_validate_password_function():
    """Test the validate_password utility function"""
    
    print("\n" + "=" * 80)
    print("VALIDATE_PASSWORD FUNCTION TESTS")
    print("=" * 80)
    
    test_cases = [
        ("Pass123!", True, None),
        ("Short1", False, "Password must be at least 8 characters long"),
        ("A" * 129, False, "Password must be at most 128 characters long"),
        ("🔐" * 20, False, "Password is too long when encoded (max 72 bytes for bcrypt)"),
    ]
    
    passed = 0
    failed = 0
    
    for password, should_pass, expected_error in test_cases:
        is_valid, error_msg = validate_password(password)
        
        print(f"\nPassword: {password[:50]}{'...' if len(password) > 50 else ''}")
        print(f"Expected: {'Valid' if should_pass else 'Invalid'}")
        print(f"Result: {'Valid' if is_valid else 'Invalid'}")
        
        if is_valid == should_pass:
            if not should_pass and expected_error:
                if expected_error in error_msg:
                    print(f"✅ PASSED - Correct error: {error_msg}")
                    passed += 1
                else:
                    print(f"❌ FAILED - Wrong error message")
                    print(f"Expected: {expected_error}")
                    print(f"Got: {error_msg}")
                    failed += 1
            else:
                print(f"✅ PASSED")
                passed += 1
        else:
            print(f"❌ FAILED")
            failed += 1
    
    print(f"\n{'=' * 80}")
    print(f"SUMMARY: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)
    
    return failed == 0


if __name__ == "__main__":
    print("\n🔐 TESTING PASSWORD VALIDATION SYSTEM\n")
    
    result1 = test_password_validation()
    result2 = test_validate_password_function()
    
    if result1 and result2:
        print("\n✅ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED!")
        sys.exit(1)
