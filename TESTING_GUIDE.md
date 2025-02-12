# Testing Guide - How to Actually Use This Thing

Alright, so you built an API Gateway. Now you want to make sure it doesn't break. Here's how to actually test it.

## Getting Started

First, make sure the gateway is running:

```bash
python main.py
```

You should see something like this in your terminal:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

Great! It's alive. Now let's test it.

## 1. Basic Sanity Check

**Just make sure it's working:**

```bash
curl http://localhost:8000/
```

You should get back a nice greeting. If you do, congrats, it's working.

---

## 2. Test Rate Limiting (The Fun Part)

This is what the project is actually about. Let's make sure it works.

### Single request - should work fine
```bash
curl -X POST http://localhost:8000/forward \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "/users"}'
```

You'll get a 200 and some user data. Good.

### Hammer it with requests - should hit the limit

Open a new terminal and run this script. It'll send 150 requests as fast as possible:

```bash
#!/bin/bash
for i in {1..150}; do
  curl -s -X POST http://localhost:8000/forward \
    -H "Content-Type: application/json" \
    -d '{"endpoint": "/users"}' \
    -w "Request %{http_code}\n" > /dev/null
  if [ $((i % 50)) -eq 0 ]; then
    echo "Sent $i requests..."
  fi
done
```

Save this as `stress_test.sh`, then:
```bash
chmod +x stress_test.sh
./stress_test.sh
```

What you'll see:
- First ~100 requests: `200` (allowed)
- After that: `429` (rate limited)

That's it working! The rate limiter is doing its job.

### Check how many tokens are left

```bash
curl http://localhost:8000/client-status/127.0.0.1
```

You'll see something like:
```json
{
  "client_ip": "127.0.0.1",
  "rate_limit_status": {
    "tokens_remaining": 0,
    "capacity": 100,
    "refill_rate": 10.0
  }
}
```

After about 10 seconds, check again and you'll see tokens coming back (10 per second). Pretty cool.

---

## 3. Check the Metrics

See what the gateway has recorded:

```bash
curl http://localhost:8000/metrics | jq .
```

You'll see something like this after running tests:

```json
{
  "total_requests": 150,
  "successful_requests": 100,
  "blocked_requests": 50,
  "average_response_time_seconds": 0.0521,
  "success_rate_percent": 66.67
}
```

This tells you:
- Total requests: 150 came in
- Successful: 100 actually made it through
- Blocked: 50 hit the rate limit
- Average response time: About 52ms
- Success rate: 66.67% got through

### Reset metrics to start fresh

```bash
curl -X POST http://localhost:8000/reset-metrics
```

Now if you check metrics again, everything's at 0. Useful for running multiple tests.

---

## 4. Test Different Endpoints

The mock backend has three endpoints. Test them all:

### Get users
```bash
curl -X POST http://localhost:8000/forward \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "/users"}'
```

### Get data
```bash
curl -X POST http://localhost:8000/forward \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "/data"}'
```

### Check backend health
```bash
curl -X POST http://localhost:8000/forward \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "/health"}'
```

---

## 5. Test Error Handling

### Invalid endpoint - backend returns error

```bash
curl -X POST http://localhost:8000/forward \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "/doesntexist"}'
```

The gateway forwards it, the backend says "I dunno what that is", gateway sends back the response. Smart routing.

### Bad JSON - gateway catches it

```bash
curl -X POST http://localhost:8000/forward \
  -H "Content-Type: application/json" \
  -d '{this is not valid json}'
```

Gateway rejects it immediately before even hitting the backend. Returns 422 validation error.

### Missing required field

```bash
curl -X POST http://localhost:8000/forward \
  -H "Content-Type: application/json" \
  -d '{}'
```

The "endpoint" field is required. Gateway tells you exactly what's wrong.

---

## 6. Test With More Realistic Load

If you want to simulate real-ish traffic patterns:

### Python script for controlled testing

Create a file called `test_gateway.py`:

```python
import requests
import time

BASE_URL = "http://localhost:8000"

print("Starting gateway tests...\n")

# Test 1: Single request
print("Test 1: Single request")
r = requests.post(f"{BASE_URL}/forward", json={"endpoint": "/users"})
print(f"Status: {r.status_code}")
print(f"Success: {r.json()['success']}\n")

# Test 2: Check metrics
print("Test 2: Check metrics")
metrics = requests.get(f"{BASE_URL}/metrics").json()
print(f"Total requests: {metrics['total_requests']}")
print(f"Average response time: {metrics['average_response_time_seconds']}s\n")

# Test 3: Burst and watch rate limiting
print("Test 3: Sending 150 requests (watch for 429s)...")
blocked = 0
allowed = 0
for i in range(150):
    r = requests.post(f"{BASE_URL}/forward", json={"endpoint": "/users"})
    if r.status_code == 429:
        blocked += 1
    else:
        allowed += 1

print(f"Allowed: {allowed}, Blocked: {blocked}\n")

# Test 4: Final metrics
print("Test 4: Final metrics")
metrics = requests.get(f"{BASE_URL}/metrics").json()
print(f"Total requests: {metrics['total_requests']}")
print(f"Blocked: {metrics['blocked_requests']}")
print(f"Success rate: {metrics['success_rate_percent']}%")
```

Run it:
```bash
pip install requests  # if you don't have it
python test_gateway.py
```

---

## 7. Visual Testing - Use the Docs

Forget curl. Just open your browser:

**Go to:** `http://localhost:8000/docs`

You'll get an interactive playground where you can:
- See all endpoints
- Click "Try it out"
- Send requests
- See responses in real-time

It's built in automatically by FastAPI. Pretty slick.

---

## 8. Monitor Performance Over Time

Keep metrics in a terminal window and watch them live:

```bash
while true; do
  clear
  echo "=== Gateway Metrics (Updated every 1s) ==="
  date
  curl -s http://localhost:8000/metrics | jq '.'
  sleep 1
done
```

Now in another terminal, hit it with requests. Watch the metrics update in real-time. It's weirdly satisfying.

---

## 9. Full Test Workflow

Here's the whole thing in one go:

```bash
# Terminal 1: Start the gateway
python main.py

# Terminal 2: Run these in order
# 1. Reset metrics
curl -X POST http://localhost:8000/reset-metrics

# 2. Send some normal requests
for i in {1..5}; do
  curl -X POST http://localhost:8000/forward \
    -H "Content-Type: application/json" \
    -d '{"endpoint": "/users"}'
  sleep 0.5
done

# 3. Check metrics
curl http://localhost:8000/metrics | jq .

# 4. Send a burst (will hit rate limit)
for i in {1..150}; do
  curl -s -X POST http://localhost:8000/forward \
    -H "Content-Type: application/json" \
    -d '{"endpoint": "/users"}' > /dev/null
done

# 5. Check metrics again (lots blocked!)
curl http://localhost:8000/metrics | jq .

# 6. Wait 10 seconds and try again (tokens refilled)
sleep 10
curl -X POST http://localhost:8000/forward \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "/users"}'
```

---

## 10. What to Look For

### Rate limiting is working if:
- ✅ First 100 requests get 200 status
- ✅ Requests 101+ get 429 status
- ✅ After waiting 10 seconds, you can make more requests
- ✅ Metrics show "blocked_requests" > 0

### Metrics are working if:
- ✅ total_requests increases with each request
- ✅ successful_requests = total - blocked
- ✅ average_response_time is between 0.01 and 0.1 seconds
- ✅ success_rate drops when you hit the limit

### Gateway is working if:
- ✅ All endpoints return data
- ✅ Invalid requests get validation errors
- ✅ Backend errors are passed through correctly
- ✅ Response times are reasonable

---

## Common Gotchas

### "I hit rate limit but it never refills"
The tokens refill automatically over time. After 10 seconds of no requests, you get 10 tokens back. Just wait.

### "Metrics show different numbers than I sent"
Metrics include ALL requests - even ones before you started testing. Run `curl -X POST http://localhost:8000/reset-metrics` first.

### "Everything is returning 500 errors"
Check that the gateway is actually running. If it is, check the terminal where it's running - there might be error messages.

### "Rate limiting seems too strict/lenient"
The settings are: 100 tokens max, 10 per second. Change them in `rate_limiter.py` line 87:
```python
rate_limiter = RateLimiter(capacity=100, refill_rate=10.0)
```

---

## Tips for Testing

- **Always test in order:** Start simple, then get complex
- **Use jq:** Makes JSON output readable. Install it: `brew install jq` on Mac
- **Watch metrics:** They tell you what's actually happening
- **Reset between tests:** Fresh metrics = less confusion
- **Read the errors:** They're usually pretty specific about what went wrong
- **Try the docs:** http://localhost:8000/docs is genuinely useful

---

## Next Steps After Basic Testing

1. Read the code. Seriously. It's not that long.
2. Try to break it. If you can't, great!
3. Add some of your own endpoints to the mock backend
4. Change rate limit settings and see what happens
5. Write some actual unit tests (pytest is great for this)

---

That's it. Go test it out!
