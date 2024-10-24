from fastapi.middleware.gzip import GZipMiddleware
from gym_reader.logger import get_logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import Response
import uuid
import time
import hmac
import hashlib
from gym_reader.settings import get_settings
from gym_reader.api.cache_tools import cache

settings = get_settings()
log = get_logger(__name__)


# Middleware to track tokens
class TokenTrackingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get the request_id from headers
        request_id = request.headers.get("X-Request-ID", None)

        if not request_id:
            log.warning("X-Request-ID header is missing, generating a new one")
            request_id = str(uuid.uuid4())

        # Store the request_id in the request state
        request.state.request_id = request_id

        TOKEN_KEY = request_id
        # Initialize the token count in cache if not already present
        if TOKEN_KEY not in cache.get_available_keys():
            cache.set(TOKEN_KEY, 0)

        # Process the request and get the response
        response = await call_next(request)

        # Get total tokens from cache
        total_tokens = cache.get(TOKEN_KEY)

        # Add total_tokens to the response headers
        response.headers[settings.TOKEN_KEY] = str(total_tokens)

        # Optionally, clean up the cache entry
        cache.pop(TOKEN_KEY)

        return response


# Middleware to verify HMAC signatures
class HMACVerificationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Retrieve HMAC signature from headers
        hmac_signature = request.headers.get("X-Hub-Signature-256")
        if not hmac_signature:
            log.warning("Missing X-HMAC-Signature header")
            return Response("Missing HMAC signature", status_code=400)

        # Read request body
        body = await request.body()

        # Get the secret key from settings
        secret_key = settings.GITHUB_SECRET_KEY_FOR_WEBHOOK

        if not secret_key:
            log.error("GITHUB_SECRET_KEY_FOR_WEBHOOK is not set in settings")
            return Response("Server configuration error", status_code=500)

        # Compute HMAC using the secret key
        computed_hmac = hmac.new(
            key=secret_key.encode(), msg=body, digestmod=hashlib.sha256
        ).hexdigest()

        # Compare the provided HMAC with the computed HMAC
        if not hmac.compare_digest(computed_hmac, hmac_signature):
            log.warning(
                f"Invalid HMAC signature , received: {hmac_signature}, computed: {computed_hmac}"
            )
            return Response("Invalid HMAC signature", status_code=400)

        # Proceed to the next middleware or request handler
        response = await call_next(request)
        return response


# Middleware to add processing time
class ProcessingTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response


# Configure CORS middleware as per need
CORS_MIDDLEWARE = Middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create instances of Middleware
GZIP_MIDDLEWARE = Middleware(GZipMiddleware)
PROCESSING_TIME_MIDDLEWARE = Middleware(ProcessingTimeMiddleware)
TOKEN_TRACKING_MIDDLEWARE = Middleware(TokenTrackingMiddleware)
HMAC_VERIFICATION_MIDDLEWARE = Middleware(HMACVerificationMiddleware)

ALL_MIDDLEWARES = [
    GZIP_MIDDLEWARE,
    PROCESSING_TIME_MIDDLEWARE,
    CORS_MIDDLEWARE,
    TOKEN_TRACKING_MIDDLEWARE,
    HMAC_VERIFICATION_MIDDLEWARE,
]

__all__ = [
    "GZIP_MIDDLEWARE",
    "PROCESSING_TIME_MIDDLEWARE",
    "CORS_MIDDLEWARE",
    "ALL_MIDDLEWARES",
    "TokenTrackingMiddleware",
    "HMAC_VERIFICATION_MIDDLEWARE",
]
