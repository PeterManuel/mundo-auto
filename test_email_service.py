"""
Comprehensive test for password recovery email functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import smtplib
from app.services.email import email_service
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)


def test_smtp_connection():
    """Test basic SMTP connection to Gmail"""
    print("🔗 Testing SMTP connection...")
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        print("✅ SMTP connection successful")
        server.quit()
        return True
    except Exception as e:
        print(f"❌ SMTP connection failed: {str(e)}")
        return False


def test_gmail_auth():
    """Test Gmail authentication"""
    print("\n🔐 Testing Gmail authentication...")
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('mundoauto2025@gmail.com', 'mowu aemc gegx bfuj')
        print("✅ Gmail authentication successful")
        server.quit()
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Gmail authentication failed: {str(e)}")
        print("📝 Please make sure to:")
        print("   1. Enable 2-factor authentication on your Gmail account")
        print("   2. Generate an App Password in Google Account settings")
        print("   3. Use the App Password instead of your regular password")
        return False
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return False


def test_email_service():
    """Test the email service"""
    print("\n📧 Testing email service...")
    try:
        # Use a test email - replace with your actual email for testing
        test_email = "mundoauto2025@gmail.com"  # Send to self for testing
        reset_token = "test_token_12345_abcdef"
        
        result = email_service.send_password_reset_email(
            to_email=test_email,
            reset_token=reset_token,
            user_name="Test User"
        )
        
        if result:
            print(f"✅ Email sent successfully to {test_email}")
            print("📬 Check the inbox for the password recovery email")
            return True
        else:
            print(f"❌ Failed to send email to {test_email}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing email service: {str(e)}")
        return False


def print_instructions():
    """Print setup instructions"""
    print("\n📋 Setup Instructions for Gmail:")
    print("=" * 50)
    print("1. Go to your Google Account settings (myaccount.google.com)")
    print("2. Navigate to Security")
    print("3. Enable 2-Step Verification if not already enabled")
    print("4. Go to 'App passwords' (under 2-Step Verification)")
    print("5. Generate a new app password for 'Mail'")
    print("6. Use this 16-character password in the email service")
    print("7. Update the password in app/services/email.py")
    print("\n🔧 Current email configuration:")
    print(f"   Email: mundoauto2025@gmail.com")
    print(f"   SMTP Server: smtp.gmail.com:587")
    print(f"   App Password: {'*' * 16}")


if __name__ == "__main__":
    print("🚗 MundoAuto Password Recovery Email Test")
    print("=" * 50)
    
    # Test SMTP connection
    smtp_ok = test_smtp_connection()
    
    # Test Gmail authentication
    auth_ok = test_gmail_auth()
    
    # Test email service if authentication works
    if auth_ok:
        email_ok = test_email_service()
    else:
        email_ok = False
    
    print("\n📊 Test Results:")
    print(f"   SMTP Connection: {'✅' if smtp_ok else '❌'}")
    print(f"   Gmail Auth: {'✅' if auth_ok else '❌'}")
    print(f"   Email Service: {'✅' if email_ok else '❌'}")
    
    if not auth_ok:
        print_instructions()
    elif email_ok:
        print("\n🎉 All tests passed! Password recovery emails should work now.")
        print("\n🚀 Next steps:")
        print("   1. Start your FastAPI server: poetry run uvicorn app.main:app --reload")
        print("   2. Test the password recovery endpoints")
        print("   3. Open the test page: http://localhost:8000/static/test_password_recovery.html")
    else:
        print("\n⚠️ Email service test failed. Check the logs above for details.")