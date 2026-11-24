import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger("app.middleware.logging")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that records HTTP request context and latency metrics.
    Output formats adapt based on Environment settings (Production JSON or Local Dev Text).
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        
        request_id = getattr(request.state, "request_id", "unknown")
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        
        logger.debug(
            f"Incoming Request: {method} {path} | Client IP: {client_ip} | ID: {request_id}"
        )
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            logger.info(
                f"HTTP {response.status_code} {method} {path} | "
                f"Duration: {process_time:.4f}s | Client IP: {client_ip} | ID: {request_id}"
            )
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.exception(
                f"HTTP 500 Failure | {method} {path} | "
                f"Duration: {process_time:.4f}s | Error: {str(e)} | ID: {request_id}"
            )
            raise
