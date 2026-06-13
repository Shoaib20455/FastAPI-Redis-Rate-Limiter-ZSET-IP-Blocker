# FastAPI Redis Rate Limiter & IP Blocker

A production-grade API rate limiting and automated IP blocking system built using FastAPI middleware and Redis. By utilizing Redis Sorted Sets (`ZSET`), the system implements a highly accurate Sliding Window Counter algorithm to mitigate burst attacks at window boundaries. If a client exceeds the defined request threshold, their IP is dynamically blocked via a TTL-backed Redis key, protecting downstream resources from API abuse and DDoS attempts.

## Features

- **Sliding Window Counter:** Prevents edge-case traffic bursts common in Fixed Window algorithms using Redis Sorted Sets (`ZSET`).
- **Automated IP Blocking:** Automatically blocks malicious IPs with temporary, TTL-based expiration (`SETEX`).
- **Centralized FastAPI Middleware:** Protects all endpoints seamlessly without modifying individual route handlers.
- **Atomic Redis Pipelines:** Batches commands into a single network round-trip to reduce latency and prevent race conditions.
- **Standard Compliance Headers:** Automatically appends industry-standard rate-limiting headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`) to responses.

## Tech Stack & Tools

| Layer | Technology |
|---|---|
| Backend Framework | FastAPI (Python 3.9+) |
| In-Memory Data Store | Redis (using `redis-py` client) |
| ASGI Server | Uvicorn |
| Testing HTTP Client | HTTPX |

## Steps to Run the Project

### 1. Prerequisites & Environment Setup

Ensure you have Python 3.9+, pip, and Redis installed on your machine.

**Install Redis:**

- **Ubuntu/WSL:** `sudo apt install redis-server && sudo service redis start`
- **macOS:** `brew install redis && brew services start redis`

### 2. Clone and Initialize Project

Clone your repository, navigate into the project directory, and create a virtual environment:

```bash
# Create directory and navigate into it
mkdir rate_limiter_project
cd rate_limiter_project

# Setup virtual environment
python -m venv venv

# Activate virtual environment
# On Mac/Linux/WSL:
source venv/bin/activate

# On Windows CMD:
venv\Scripts\activate
```

### 3. Install Dependencies

Create a `requirements.txt` file with the necessary packages and install them:

```bash
pip install -r requirements.txt
```

### 4. Run the Application

Start the Uvicorn server to host your FastAPI application locally:

```bash
sudo service redis start
uvicorn main:app --reload
```

The API will now be running at `http://127.0.0.1:8000`. You can explore the interactive documentation via Swagger UI at `http://127.0.0.1:8000/docs`.

### 5. Verify and Test

```bash
for i in {1..15}; do echo -n "Request $i: "; curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/data; echo; sleep 0.1; done
```