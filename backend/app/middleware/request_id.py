import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds a unique X-Request-ID header to each incoming request and outgoing response.
    Ensures traceability across distributed log lines.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())
        
        # Inject request_id into state so it's readable in logging
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
