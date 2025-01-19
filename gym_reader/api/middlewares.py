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
from gym_reader.settings import get_settings, TOKEN_MIDDLEWARES
from gym_reader.api.cache_tools import cache
from gym_reader.clients.redis_client import redis_client

settings = get_settings()
log = get_logger(__name__)


# Middleware to verify HMAC signatures
class HMACVerificationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip HMAC verification for the /api/health endpoint
        if request.url.path == "/api/health":
            return await call_next(request)
        # Retrieve HMAC signature from headers
        hmac_signature = request.headers.get("X-Hub-Signature-256")
        if not hmac_signature:
            log.warning("Missing X-HMAC-Signature header")
            return Response("Missing HMAC signature", status_code=400)

        # Read request body
        body = await request.body()

        log.info(f"body: {body}")

        # Get the secret key from settings
        secret_key = settings.GITHUB_SECRET_KEY_FOR_WEBHOOK

        if not secret_key:
            log.error("GITHUB_SECRET_KEY_FOR_WEBHOOK is not set in settings")
            return Response("Server configuration error", status_code=500)

        # Compute HMAC using the secret key
        computed_hmac = hmac.new(
            key=secret_key.encode(), msg=body, digestmod=hashlib.sha256
        ).hexdigest()
        computed_hmac = f"sha256={computed_hmac}"
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
HMAC_VERIFICATION_MIDDLEWARE = Middleware(HMACVerificationMiddleware)

ALL_MIDDLEWARES = [
    GZIP_MIDDLEWARE,
    PROCESSING_TIME_MIDDLEWARE,
    CORS_MIDDLEWARE,
    HMAC_VERIFICATION_MIDDLEWARE,
]


class TokenLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip token limit for health and keyword search
        if request.url.path not in TOKEN_MIDDLEWARES:
            return await call_next(request)
        # Define Redis keys
        daily_key = "daily_usage"
        # ip address
        ip_address = request.headers.get("x-forwarded-for", request.client.host)
        # redis key for ip usage
        ip_key = f"ip_usage:{ip_address}"
        """
        Check if daily usage or ip usage is breached
        """
        daily_usage = int(redis_client.get(daily_key) or 0)
        ip_usage = int(redis_client.get(ip_key) or 0)
        # Check if the usage exceeds the configured limits
        if daily_usage > settings.DAILY_TOKEN_LIMIT:
            return Response("Daily token limit exceeded", status_code=429)
        if ip_usage > settings.IP_TOKEN_LIMIT:
            return Response("IP token limit exceeded", status_code=429)

        # Procced if not breached

        # Retrieve or generate a unique request ID
        request_id = request.headers.get("X-Request-ID", None)

        if not request_id:
            log.warning("X-Request-ID header is missing, generating a new one")
            request_id = str(uuid.uuid4())
            log.debug(f"request_id generated: {request_id}")
        # Store the request_id in the request state
        request.state.request_id = request_id
        # Initialize the token count in cache if not already present
        if request_id not in cache.get_available_keys():
            cache.set(request_id, 0)

        # Process the request and get the response
        response = await call_next(request)
        # Get total tokens from cache
        total_tokens = cache.get(request_id)
        log.debug(f"total_tokens: {total_tokens}")
        # Use Redis to manage daily and per-IP limits with TTL
        if total_tokens is not None:
            # Atomically increment the token counts and set TTL if the keys are new
            daily_usage = redis_client.incrby(daily_key, total_tokens)
            log.debug(f"daily_usage: {daily_usage}")
            ip_usage = redis_client.incrby(ip_key, total_tokens)
            log.debug(f"ip_usage: {ip_usage}")

            # Set TTL for the keys if they are newly created
            if daily_usage == total_tokens:
                redis_client.expire(daily_key, 86400)  # 24 hours TTL
            if ip_usage == total_tokens:
                redis_client.expire(ip_key, 86400)  # 24 hours TTL
        # Add usage information to the response headers
        response.headers[settings.TOKEN_KEY] = str(total_tokens)
        response.headers["daily_usage"] = str(daily_usage)
        response.headers["ip_usage"] = str(ip_usage)

        return response


# Add the new middleware to the ALL_MIDDLEWARES list
ALL_MIDDLEWARES.append(Middleware(TokenLimitMiddleware))

__all__ = [
    "GZIP_MIDDLEWARE",
    "PROCESSING_TIME_MIDDLEWARE",
    "CORS_MIDDLEWARE",
    "ALL_MIDDLEWARES",
    "HMAC_VERIFICATION_MIDDLEWARE",
]
