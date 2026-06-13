# main.py
from fastapi import FastAPI
from middleware import RateLimitMiddleware
from redis_client import get_redis
from models import IPStatusResponse, UnblockResponse  # <-- ADD THIS

app = FastAPI(
    title="Rate Limited API",
    description="FastAPI + Redis Rate Limiter with IP Blocking",
    version="1.0.0"
)

app.add_middleware(RateLimitMiddleware)


@app.get("/")
async def root():
    return {"message": "API is running"}


@app.get("/data")
async def get_data():
    return {"data": [1, 2, 3, 4, 5]}


@app.get("/health")
async def health_check():
    try:
        get_redis().ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "redis": str(e)}


@app.get("/admin/check-ip/{ip}", response_model=IPStatusResponse)  # <-- response_model
async def check_ip_status(ip: str):
    r = get_redis()
    is_blocked = r.exists(f"blocked:{ip}") == 1
    return IPStatusResponse(   # <-- Pydantic object return karo
        ip=ip,
        is_blocked=is_blocked,
        block_ttl_seconds=r.ttl(f"blocked:{ip}") if is_blocked else 0,
        requests_in_window=r.zcard(f"rate_limit:{ip}"),
        limit=10
    )


@app.delete("/admin/unblock-ip/{ip}", response_model=UnblockResponse)  # <-- response_model
async def unblock_ip(ip: str):
    deleted = get_redis().delete(f"blocked:{ip}")
    msg = f"IP {ip} unblocked" if deleted else f"IP {ip} was not blocked"
    return UnblockResponse(message=msg)   # <-- Pydantic object return karo