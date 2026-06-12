# middleware.py
import time
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from redis_client import get_redis
from config import (
    RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SECONDS,
    BLOCK_DURATION_SECONDS, RATE_LIMIT_KEY_PREFIX, BLOCK_KEY_PREFIX
)

def is_ip_blocked(ip: str) -> bool:
    """
    Check if an IP is currently blocked.
    Redis STRING key 'blocked:{ip}' exists = blocked.
    Redis auto-deletes it when TTL expires.
    """
    r = get_redis()
    block_key = f'{BLOCK_KEY_PREFIX}:{ip}'
    return r.exists(block_key) == 1

def block_ip(ip: str) -> None:
    """
    Block an IP for BLOCK_DURATION_SECONDS.
    setex(key, seconds, value) sets value AND expiry in one command.
    """
    r = get_redis()
    block_key = f'{BLOCK_KEY_PREFIX}:{ip}'
    r.setex(block_key, BLOCK_DURATION_SECONDS, 'blocked')
    print(f'[BLOCKED] IP {ip} blocked for {BLOCK_DURATION_SECONDS}s')

def check_rate_limit(ip: str) -> dict:
    """
    Sliding Window Counter using Redis ZSET.
    Returns: { allowed: bool, current_count: int, limit: int }
    """
    r = get_redis()
    rate_key = f'{RATE_LIMIT_KEY_PREFIX}:{ip}'
    now = time.time()                                # current Unix timestamp
    window_start = now - RATE_LIMIT_WINDOW_SECONDS  # 60 seconds ago

    # Pipeline: sends all commands at once = faster & atomic
    pipe = r.pipeline()

    # 1. Remove old timestamps (older than 60 seconds ago)
    pipe.zremrangebyscore(rate_key, '-inf', window_start)

    # 2. Count remaining timestamps = requests in current window
    pipe.zcard(rate_key)

    # 3. Add current request (score=timestamp, member=str(timestamp))
    pipe.zadd(rate_key, {str(now): now})

    # 4. Set key expiry so Redis cleans up automatically
    pipe.expire(rate_key, RATE_LIMIT_WINDOW_SECONDS + 10)

    results = pipe.execute()
    current_count = results[1]  # zcard result = count BEFORE this request

    if current_count >= RATE_LIMIT_REQUESTS:
        return {'allowed': False, 'current_count': current_count, 'limit': RATE_LIMIT_REQUESTS}

    return {'allowed': True, 'current_count': current_count + 1, 'limit': RATE_LIMIT_REQUESTS}

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Runs before every request.
    Flow: Is IP blocked? -> Rate limit exceeded? -> Allow
    """
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host

        # Check 1: Is this IP already blocked?
        if is_ip_blocked(client_ip):
            r = get_redis()
            ttl = r.ttl(f'{BLOCK_KEY_PREFIX}:{client_ip}')
            return JSONResponse(
                status_code=403,
                content={
                    'error': 'IP_BLOCKED',
                    'message': f'Your IP is blocked. Retry in {ttl} seconds.',
                    'retry_after_seconds': ttl,
                },
            )

        # Check 2: Sliding window rate limit
        rate_result = check_rate_limit(client_ip)

        if not rate_result['allowed']:
            block_ip(client_ip)  # Block IP on first violation
            return JSONResponse(
                status_code=429,
                content={
                    'error': 'RATE_LIMIT_EXCEEDED',
                    'message': f'Limit exceeded. IP blocked for 15 minutes.',
                    'limit': rate_result['limit'],
                    'retry_after_seconds': BLOCK_DURATION_SECONDS
                },
                headers={'Retry-After': str(BLOCK_DURATION_SECONDS)},
            )

        # Allow request, add rate limit headers to response
        response = await call_next(request)
        response.headers['X-RateLimit-Limit'] = str(RATE_LIMIT_REQUESTS)
        response.headers['X-RateLimit-Remaining'] = str(
            RATE_LIMIT_REQUESTS - rate_result['current_count']
        )
        return response

# Sliding Window Kaise Kaam kr rha hai? 🤔
# 1. Jab bhi request aati hai, hum pichle 60 seconds ka window nikalte hain (now - 60).
# 2. zremrangebyscore sy hum 60 seconds sy purane saare timestamps delete kr dete hain.
# 3. zcard sy bache huay timestamps ginte hain. Agar count 10 ya us se zyada hai, to block! 
# 4. r.pipeline(): Is se saari commands aik hi dfa me Redis server pr jati hain, jis se network round-trips bachti hain aur speed fast hoti hai.


# dispatch function: FastAPI me jab bhi koi request aati hai, wo pehle is function sy guzarti hai.
# Headers: Agar request allow hoti hai, to hum response me standard headers bhejte hain (X-RateLimit-Limit aur X-RateLimit-Remaining) taaky client ko pata ho uski kitni requests baqi hain