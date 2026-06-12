# main.py
from fastapi import FastAPI
from middleware import RateLimitMiddleware
from redis_client import get_redis

app = FastAPI(
    title='Rate Limited API',
    description='FastAPI + Redis Rate Limiter with IP Blocking',
    version='1.0.0',
)

# Yeh aik line hamari saari middleware logic ko FastAPI ke sath connect kr deti hai.
# Har incoming request sab se pehle RateLimitMiddleware.dispatch() se guzre gi.
app.add_middleware(RateLimitMiddleware)

@app.get('/')
async def root():
    return {'message': 'API is running'}

@app.get('/data')
async def get_data():
    """Protected endpoint. Rate limiting yahan automatically apply hogi."""
    return {'data': [1, 2, 3, 4, 5]}

@app.get('/health')
async def health_check():
    try:
        get_redis().ping()
        return {'status': 'healthy', 'redis': 'connected'}
    except Exception as e:
        return {'status': 'unhealthy', 'redis': str(e)}

@app.get('/admin/check-ip/{ip}')
async def check_ip_status(ip: str):
    r = get_redis()
    is_blocked = r.exists(f'blocked:{ip}') == 1
    return {
        'ip': ip,
        'is_blocked': is_blocked,
        'block_ttl_seconds': r.ttl(f'blocked:{ip}') if is_blocked else 0,
        'requests_in_window': r.zcard(f'rate_limit:{ip}'),
        'limit': 10,
    }

@app.delete('/admin/unblock-ip/{ip}')
async def unblock_ip(ip: str):
    deleted = get_redis().delete(f'blocked:{ip}')
    msg = f'IP {ip} unblocked' if deleted else f'IP {ip} was not blocked'
    return {'message': msg}