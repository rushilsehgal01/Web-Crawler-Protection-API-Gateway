# Quick Start Guide

Get the API Gateway running in 2 minutes.

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Start the Server

```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 3: Test It

Open another terminal:

### Check gateway is running
```bash
curl http://localhost:8000/
```

### Make a request
```bash
curl -X POST http://localhost:8000/forward \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "/users"}'
```

### View metrics
```bash
curl http://localhost:8000/metrics
```

### View interactive docs
Open: http://localhost:8000/docs

## Step 4: Test Rate Limiting

Run many requests to hit the limit (default: 100 requests with 10/sec refill):

```bash
for i in {1..150}; do
  curl -X POST http://localhost:8000/forward \
    -H "Content-Type: application/json" \
    -d '{"endpoint": "/users"}'
done
```

You'll see 429 errors when rate limited.

## That's It!

Explore the code:
- `main.py` - Main application
- `rate_limiter.py` - Rate limiting logic
- `metrics.py` - Metrics collection
- `mock_service.py` - Fake backend
- `models.py` - Data validation

See `README.md` for full documentation.
