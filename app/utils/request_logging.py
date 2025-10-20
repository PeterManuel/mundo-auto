import re
import json
from typing import Dict, Optional, Any, Tuple

from fastapi import Request


class DeviceDetector:
    """
    Utility class to extract device information from requests
    """
    
    @staticmethod
    def parse_user_agent(user_agent: str) -> Dict[str, str]:
        """
        Parse user agent string to extract device information
        """
        result = {
            "device_type": "unknown",
            "browser": "unknown",
            "os": "unknown"
        }
        
        # Detect device type
        if re.search(r'Mobile|Android|iPhone|iPad|iPod', user_agent, re.I):
            if re.search(r'iPad|Tablet', user_agent, re.I):
                result["device_type"] = "tablet"
            else:
                result["device_type"] = "mobile"
        else:
            result["device_type"] = "desktop"
            
        # Detect browser
        browser_patterns = [
            (r'Edge|Edg', 'Edge'),
            (r'Chrome', 'Chrome'),
            (r'Firefox', 'Firefox'),
            (r'Safari', 'Safari'),
            (r'Opera|OPR', 'Opera'),
            (r'MSIE|Trident', 'Internet Explorer')
        ]
        
        for pattern, name in browser_patterns:
            if re.search(pattern, user_agent, re.I):
                result["browser"] = name
                break
                
        # Detect OS
        os_patterns = [
            (r'Windows NT 10', 'Windows 10'),
            (r'Windows NT 6\.3', 'Windows 8.1'),
            (r'Windows NT 6\.2', 'Windows 8'),
            (r'Windows NT 6\.1', 'Windows 7'),
            (r'Windows NT', 'Windows'),
            (r'Android', 'Android'),
            (r'iPhone|iPad|iPod', 'iOS'),
            (r'Mac OS X', 'macOS'),
            (r'Linux', 'Linux')
        ]
        
        for pattern, name in os_patterns:
            if re.search(pattern, user_agent, re.I):
                result["os"] = name
                break
        
        return result


async def extract_request_body(request: Request) -> Optional[str]:
    """
    Extract and serialize request body, handling different content types
    """
    content_type = request.headers.get("content-type", "")
    
    # Handle empty body
    if "content-length" in request.headers and request.headers["content-length"] == "0":
        return None
        
    try:
        # For JSON payloads
        if "application/json" in content_type:
            body = await request.json()
            
            # Sanitize sensitive information
            if isinstance(body, dict):
                if "password" in body:
                    body["password"] = "[REDACTED]"
                if "password_confirm" in body:
                    body["password_confirm"] = "[REDACTED]"
                    
            return json.dumps(body)
            
        # For form data
        elif "application/x-www-form-urlencoded" in content_type:
            form = await request.form()
            form_dict = {key: value for key, value in form.items()}
            
            # Sanitize sensitive information
            if "password" in form_dict:
                form_dict["password"] = "[REDACTED]"
                
            return json.dumps(form_dict)
            
        # For multipart form data (with files)
        elif "multipart/form-data" in content_type:
            return "[MULTIPART FORM DATA - CONTENT NOT LOGGED]"
            
        # For plain text
        elif "text/plain" in content_type:
            body = await request.body()
            return body.decode()
            
        # For other content types
        else:
            return "[CONTENT NOT LOGGED]"
            
    except Exception as e:
        return f"[ERROR EXTRACTING BODY: {str(e)}]"


def extract_request_metadata(request: Request) -> Dict[str, Any]:
    """
    Extract metadata from a FastAPI request
    """
    # Get client IP address
    ip_address = request.client.host if request.client else None
    
    # Get user agent
    user_agent = request.headers.get("user-agent", "")
    
    # Parse user agent for device information
    device_info = DeviceDetector.parse_user_agent(user_agent)
    
    return {
        "ip_address": ip_address,
        "user_agent": user_agent,
        "device_type": device_info["device_type"],
        "browser": device_info["browser"],
        "os": device_info["os"]
    }


def truncate_response(response_body: str, max_length: int = 1000) -> str:
    """
    Truncate response body if it's too large
    """
    if not response_body or len(response_body) <= max_length:
        return response_body
        
    return response_body[:max_length] + "... [TRUNCATED]"