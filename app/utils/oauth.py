import json
from typing import Dict, Optional, Any

import requests
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.core.config.settings import settings


class GoogleOAuth:
    """Utility class for Google OAuth operations"""
    
    @staticmethod
    def get_authorization_url() -> str:
        """Generate the Google authorization URL"""
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "scope": "email profile",
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
        }
        
        query_params = "&".join([f"{key}={value}" for key, value in params.items()])
        return f"https://accounts.google.com/o/oauth2/auth?{query_params}"
    
    @staticmethod
    def exchange_code_for_token(code: str) -> Dict[str, Any]:
        """Exchange authorization code for tokens"""
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        
        response = requests.post("https://oauth2.googleapis.com/token", data=data)
        if response.status_code != 200:
            raise ValueError(f"Failed to exchange code for token: {response.text}")
        
        return response.json()
    
    @staticmethod
    def validate_token(token: str) -> Dict[str, Any]:
        """Validate Google ID token and extract user info"""
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            
            # Check issuer
            if idinfo.get('iss') not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
                
            return idinfo
            
        except Exception as e:
            raise ValueError(f"Invalid token: {str(e)}")
    
    @staticmethod
    def get_user_info(access_token: str) -> Dict[str, Any]:
        """Get user information from Google API using access token"""
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers=headers)
        
        if response.status_code != 200:
            raise ValueError(f"Failed to get user info: {response.text}")
        
        return response.json()