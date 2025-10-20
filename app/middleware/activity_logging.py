import json
import time
import uuid
from typing import Callable, Dict, Optional, Any

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from sqlalchemy.orm import Session

from app.utils.request_logging import extract_request_metadata, extract_request_body, truncate_response
from app.db.session import SessionLocal
from app.crud.activity_log import create_activity_log
from app.api.endpoints.auth import get_current_user_optional


class ActivityLogMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all API requests and responses
    """
    def __init__(self, app: ASGIApp, exclude_paths: list = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/docs", "/redoc", "/openapi.json", "/static"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip logging for excluded paths
        path = request.url.path
        if any(path.startswith(excluded) for excluded in self.exclude_paths):
            return await call_next(request)
        
        # Record start time
        start_time = time.time()
        
        # Extract request data
        method = request.method
        endpoint = path.split("/")[-1] if "/" in path else path
        metadata = extract_request_metadata(request)
        request_body = await extract_request_body(request)
        
        # Try to get authenticated user
        user_id = None
        try:
            db = SessionLocal()
            user = await get_current_user_optional(request, db)
            if user:
                user_id = user.id
        except Exception:
            pass
        finally:
            if 'db' in locals():
                db.close()
        
        # Process the request
        response = await call_next(request)
        
        # Record end time and calculate processing time
        processing_time = round((time.time() - start_time) * 1000)
        
        # Extract response data
        status_code = str(response.status_code)
        
        # Attempt to get response body
        response_body = None
        if isinstance(response, JSONResponse):
            try:
                response_body = json.dumps(response.body.decode())
                response_body = truncate_response(response_body)
            except Exception:
                response_body = "[RESPONSE BODY EXTRACTION ERROR]"
        
        # Log the activity asynchronously
        try:
            # Create new DB session
            db = SessionLocal()
            
            # Create activity log
            log_data = {
                "user_id": user_id,
                "endpoint": endpoint,
                "method": method,
                "path": path,
                "status_code": status_code,
                "request_body": request_body,
                "response_body": response_body,
                "processing_time_ms": str(processing_time),
                **metadata
            }
            
            # Create log entry
            create_activity_log(db, log_data)
            
        except Exception as e:
            # Log error to console but don't affect request processing
            print(f"Error logging activity: {str(e)}")
        finally:
            if 'db' in locals():
                db.close()
        
        return response


def setup_activity_logging(app: FastAPI, exclude_paths: list = None) -> None:
    """
    Add activity logging middleware to FastAPI application
    """
    app.add_middleware(
        ActivityLogMiddleware,
        exclude_paths=exclude_paths
    )