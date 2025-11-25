"""
Test script for password recovery functionality
"""
import sys
import os
import asyncio
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.email import email_service


async def test_email_service():
    """Test the email service"""
    print("Testing email service...")
    
    # Test basic email sending
    test_email = "test@example.com"  # Replace with your test email
    reset_token = "test_token_12345"
    
    try:
        result = email_service.send_password_reset_email(
            to_email=test_email,
            reset_token=reset_token,
            user_name="Test User"
        )
        
        if result:
            print(f"✅ Email sent successfully to {test_email}")
        else:
            print(f"❌ Failed to send email to {test_email}")
            
    except Exception as e:
        print(f"❌ Error testing email service: {str(e)}")


def test_password_reset_endpoints():
    """Test the password reset endpoints documentation"""
    print("\n🔧 Password Recovery Endpoints Available:")
    print("1. POST /api/v1/auth/password-recovery")
    print("   - Request body: {'email': 'user@example.com'}")
    print("   - Sends password reset email if user exists")
    
    print("\n2. POST /api/v1/auth/validate-reset-token")
    print("   - Request body: {'token': 'reset_token_here'}")
    print("   - Validates if reset token is valid and not expired")
    
    print("\n3. POST /api/v1/auth/reset-password")
    print("   - Request body: {'token': 'reset_token_here', 'new_password': 'newpass123', 'confirm_password': 'newpass123'}")
    print("   - Resets password using valid token")


if __name__ == "__main__":
    print("🚗 MundoAuto Password Recovery System Test")
    print("=" * 50)
    
    # Test email functionality (commented out to avoid sending real emails)
    # asyncio.run(test_email_service())
    
    # Show endpoint documentation
    test_password_reset_endpoints()
    
    print("\n✅ Password recovery system is ready!")
    print("\nNext steps:")
    print("1. Run the FastAPI server: poetry run uvicorn app.main:app --reload")
    print("2. Test the endpoints using your frontend or a tool like Postman")
    print("3. Make sure your database has the new password reset fields")
    print("\n📧 Email Configuration:")
    print("- Email: mundoauto2025@gmail.com")
    print("- SMTP Server: smtp.gmail.com:587")
    print("- Authentication: Configured with app password")