import logging
import sys
from typing import Any
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
import time
import json
from datetime import datetime

# Configure root logger
def setup_logging(log_level: str = "INFO"):
    """Configure logging for the application."""
    # Set the log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Set specific loggers to avoid spam
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    
    return root_logger

async def log_request(request: Request, call_next):
    """Log all incoming requests and responses."""
    logger = logging.getLogger("app.request")
    
    # Log request
    start_time = time.time()
    request_id = id(request)
    
    # Get request body if available (only for non-streaming)
    body = None
    if hasattr(request, '_body'):
        try:
            body = json.loads(request._body.decode()) if request._body else None
        except:
            body = "<binary or non-json>"
    
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} - "
        f"Query: {dict(request.query_params)} - "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    
    if body:
        logger.debug(f"[{request_id}] Request body: {json.dumps(body, default=str)}")
    
    # Process request
    try:
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        status_code = response.status_code if hasattr(response, 'status_code') else 200
        logger.info(
            f"[{request_id}] Response: {status_code} - "
            f"Duration: {duration:.3f}s"
        )
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"[{request_id}] Request failed after {duration:.3f}s: {str(e)}",
            exc_info=True
        )
        raise

def log_error(e: Exception, context: dict = None):
    """Log errors with context."""
    logger = logging.getLogger("app.error")
    context_str = ""
    if context:
        context_str = f" - Context: {json.dumps(context, default=str)}"
    logger.error(f"Error: {str(e)}{context_str}", exc_info=True)

def log_info(message: str, **kwargs):
    """Log info messages with optional kwargs."""
    logger = logging.getLogger("app.info")
    if kwargs:
        logger.info(f"{message} - {json.dumps(kwargs, default=str)}")
    else:
        logger.info(message)

def log_warning(message: str, **kwargs):
    """Log warning messages with optional kwargs."""
    logger = logging.getLogger("app.warning")
    if kwargs:
        logger.warning(f"{message} - {json.dumps(kwargs, default=str)}")
    else:
        logger.warning(message)

def log_debug(message: str, **kwargs):
    """Log debug messages with optional kwargs."""
    logger = logging.getLogger("app.debug")
    if kwargs:
        logger.debug(f"{message} - {json.dumps(kwargs, default=str)}")
    else:
        logger.debug(message)

