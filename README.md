# Rate-Limited API Gateway

A clean, educational backend project that demonstrates core concepts for software engineering internships: request handling, rate limiting, and performance metrics collection.

**Project Level:** Strong final-year undergraduate student project
**Built For:** Learning and interview preparation

## What This Project Does

This is a **Rate-Limited API Gateway** that acts as a proxy between clients and a backend service. It's designed to:

1. **Accept HTTP requests** from clients
2. **Enforce rate limits** using the Token Bucket algorithm
3. **Forward valid requests** to a mock backend service
4. **Track metrics** about gateway performance
5. **Return clear responses** with errors when rate limits are exceeded

Think of it as a "traffic controller" that protects a backend service from being overwhelmed by too many requests.

## Tech Stack

- **Language:** Python 3.9+
- **Framework:** FastAPI (modern, fast, excellent for learning)
- **Storage:** In-memory dictionaries (simple, no external dependencies)
- **Containerization:** Docker (optional, included)

## Project Structure

```
api-gateway-learning/
├── main.py              # FastAPI application & endpoints
├── rate_limiter.py      # Token bucket rate limiting logic
├── metrics.py           # Metrics collection and reporting
├── mock_service.py      # Simulated backend service
├── models.py            # Request/response schemas (Pydantic)
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container configuration
└── README.md           # This file
```

Each module is **self-contained** and clearly documented. The code is written to be **easy to understand and defend in an interview**.

## How Rate Limiting Works

### The Token Bucket Algorithm

Imagine each client has a bucket of tokens:

1. **Bucket capacity:** 100 tokens (max burst)
2. **Refill rate:** 10 tokens per second
3. **Request cost:** 1 token per request

**What happens:**
- Client makes request → Check if bucket has ≥1 token
- **If yes:** Remove 1 token, allow request
- **If no:** Reject request with 429 status code

**Why this is good:**
- Allows bursts (useful for real traffic patterns)
- Maintains average rate limit (prevents abuse)
- Simple to understand and implement
- Scales well per-client

**Example timeline:**
```
Time=0s:   Bucket=100 tokens, request comes in → Bucket=99, request allowed
Time=0.1s: Bucket=99+1=100 tokens, request comes in → Bucket=99, request allowed
Time=1s:   Bucket=99+10=109→capped at 100, request comes in → Bucket=99
Time=5s:   Bucket has filled up again, client gets full burst capacity
```

See `rate_limiter.py:TokenBucket` for implementation details.

## How Metrics Are Collected

The gateway tracks **four key metrics:**

1. **Total Requests** - Every request (blocked or allowed)
2. **Successful Requests** - Requests that weren't rate limited
3. **Blocked Requests** - Requests rejected due to rate limiting
4. **Average Response Time** - Mean time to process successful requests
5. **Success Rate %** - Percentage of requests that weren't blocked

Each request records:
- Whether it was blocked
- How long it took to process

Metrics are calculated on-demand and returned as JSON. See `metrics.py:Metrics` for implementation.

## How to Run Locally

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. **Navigate to the project directory:**
   ```bash
   cd api-gateway-learning
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Server

```bash
python main.py
```

Or with auto-reload for development:
```bash
uvicorn main:app --reload
```

The gateway will start on `http://localhost:8000`

### Testing the Gateway

#### 1. Check if gateway is running
```bash
curl http://localhost:8000/
```

#### 2. Make a forward request
```bash
curl -X POST http://localhost:8000/forward \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "/users"}'
```

Response:
```json
{
  "success": true,
  "message": "Request forwarded successfully",
  "data": {
    "status": "success",
    "data": [
      {"id": 1, "name": "Alice", ...}
    ]
  }
}
```

#### 3. View metrics
```bash
curl http://localhost:8000/metrics
```

Response:
```json
{
  "total_requests": 5,
  "successful_requests": 5,
  "blocked_requests": 0,
  "average_response_time_seconds": 0.0523,
  "success_rate_percent": 100.0
}
```

#### 4. Test rate limiting (trigger 429)
```bash
# Run this in a loop to exceed rate limit
for i in {1..150}; do
  curl -X POST http://localhost:8000/forward \
    -H "Content-Type: application/json" \
    -d '{"endpoint": "/users"}'
  echo "Request $i"
done
```

You'll see responses with HTTP 429 status when rate limited:
```json
{
  "success": false,
  "message": "Rate limit exceeded",
  "error": "Too many requests",
  "retry_after_seconds": 1
}
```

#### 5. Check client-specific rate limit status
```bash
curl http://localhost:8000/client-status/127.0.0.1
```

Response:
```json
{
  "client_ip": "127.0.0.1",
  "rate_limit_status": {
    "tokens_remaining": 95,
    "capacity": 100,
    "refill_rate": 10.0
  }
}
```

### Interactive API Documentation

FastAPI automatically generates interactive documentation:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

You can test all endpoints directly in the browser!

## Running with Docker

```bash
# Build image
docker build -t api-gateway .

# Run container
docker run -p 8000:8000 api-gateway
```

Gateway will be available at `http://localhost:8000`

## What I Learned From This Project

### Backend Fundamentals
- How HTTP request/response cycles work
- Request validation using schemas (Pydantic)
- Status codes and error handling

### Rate Limiting
- **Token Bucket algorithm** - elegant, practical approach
- Per-client rate limiting strategy
- Balancing burst capacity with average rate limits
- Why rate limiting matters for service protection

### Metrics & Observability
- Importance of tracking what happens in production
- Simple in-memory metrics collection
- Calculating derived metrics (averages, percentages)
- Making metrics accessible via APIs

### API Design
- Clear endpoint naming conventions
- Consistent response formats
- Meaningful error messages
- Status code semantics

### Code Organization
- Separating concerns (rate limiting, metrics, service logic)
- Using type hints for clarity
- Writing self-documenting code
- Keeping modules focused and reusable

### Testing Strategies
- How to test rate limiting behavior
- Verifying metrics accuracy
- Testing error paths

## Design Decisions & Trade-offs

### Why Token Bucket?
- **Simple to understand** - easier to explain in interviews
- **Fair to clients** - everyone gets equal capacity
- **Handles bursts** - realistic traffic patterns
- **Per-client tracking** - protects service from single bad actor

### Why In-Memory Storage?
- **Simplicity** - easier to reason about
- **Educational** - teaches core concepts without infrastructure
- **Learning focus** - emphasis on algorithm, not infrastructure
- **Limitation acknowledged** - wouldn't work for distributed systems

### Why Mock Backend?
- **Focus on gateway** - rate limiting is the main point
- **Deterministic** - testing is reproducible
- **No external dependencies** - just Python
- **Fast development** - no setup needed

## Limitations (Intentional for Learning)

This project **intentionally avoids** complexity that would appear in production systems:

- ❌ No Redis or external storage (wouldn't scale to multiple gateway instances)
- ❌ No authentication/authorization (focuses on rate limiting, not security)
- ❌ No distributed tracing (single instance only)
- ❌ No load balancing logic (single backend only)
- ❌ No persistent metrics (lost on restart)

These are **features, not bugs**. Adding them would obscure the core learning objectives.

## Interview Talking Points

If asked about this project in an interview:

**Q: Walk me through how rate limiting works**
- "We use a Token Bucket algorithm. Each client gets a bucket with 100 tokens that refill at 10/second. Each request costs 1 token. If the bucket is empty, we reject the request."

**Q: Why Token Bucket over fixed window?**
- "Fixed window has edge case problems (two requests at boundary). Token Bucket smooths traffic and allows bursts while maintaining average limits."

**Q: How do you track metrics?**
- "Each request records its status (blocked/allowed) and response time. We store these in memory and calculate aggregates on-demand. In production, you'd stream to a monitoring system."

**Q: What would you change for production?**
- "I'd add: Redis for distributed rate limiting, persistent metrics (Prometheus), authentication, better error handling, and distributed tracing for performance debugging."

**Q: How does it scale?**
- "Currently single-instance only. To scale: use Redis for shared rate limit state, multiple gateway instances with load balancing, and centralized metrics storage."

## Extending This Project

Some ideas if you want to learn more:

1. **Add different rate limiting strategies** - Fixed window, sliding window log
2. **Add request authentication** - Simple API keys
3. **Add request validation** - Schema validation for different endpoints
4. **Add monitoring integration** - Export metrics to Prometheus
5. **Add persistence** - SQLite for metrics history
6. **Add testing** - Unit tests with pytest
7. **Add load testing** - locust for stress testing
8. **Add caching** - Cache backend responses

## Files Explained

### `main.py` (main.py:1-150)
Core FastAPI application. Handles request flow:
1. Extract client IP
2. Check rate limit
3. Forward if allowed
4. Record metrics
5. Return response

### `rate_limiter.py` (rate_limiter.py:1-120)
Token Bucket implementation. Key classes:
- `TokenBucket` - Single client's bucket with refill logic
- `RateLimiter` - Manages multiple clients

### `metrics.py` (metrics.py:1-70)
Metrics collection. Tracks and calculates:
- Request counts
- Response times
- Derived metrics (success rate, averages)

### `mock_service.py` (mock_service.py:1-80)
Simulated backend with endpoints:
- `/users` - Returns user list
- `/data` - Returns sample data
- `/health` - Returns service health

### `models.py` (models.py:1-40)
Pydantic schemas for validation and documentation.

## Questions?

This project is designed to be explained and discussed. Every design choice is intentional and defensible. Good luck with your interviews!

---

**Built as:** Educational backend project
**Intended for:** Learning, interviews, portfolio
**Not intended for:** Production use
**Level:** Strong undergraduate final-year project
