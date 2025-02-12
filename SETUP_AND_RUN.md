# Setup and Run Guide

Real talk: setting up Python projects can be annoying. This guide makes it as painless as possible.

---

## Step 1: Setup (Do This Once)

### Option A: The Lazy Way (Recommended for Learning)

```bash
# Just install requirements and go
pip install -r requirements.txt
python main.py
```

That's it. Go to http://localhost:8000/docs and start playing.

### Option B: The Right Way (Using Virtual Environment)

Virtual environments keep your Python project isolated. Good practice.

**On Mac/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see (venv) at the start of your terminal line
# Install requirements
pip install -r requirements.txt

# Run the app
python main.py
```

**On Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Run the app
python main.py
```

To exit the virtual environment later:
```bash
deactivate
```

### Option C: Using Docker (If You Have It)

```bash
# Build the image
docker build -t api-gateway .

# Run it
docker run -p 8000:8000 api-gateway

# Gateway is now at http://localhost:8000
```

---

## Step 2: Verify It's Running

Open a new terminal and run:

```bash
curl http://localhost:8000/
```

You should get back JSON with the gateway info. If you do, you're good!

---

## Step 3: Run the Tests

Want to make sure everything actually works? Run the test suite.

### Install Test Dependencies (if not done already)

```bash
pip install pytest httpx
```

Or they're already in requirements.txt if you installed that.

### Run All Tests

```bash
pytest test_gateway.py -v
```

You should see something like:

```
test_gateway.py::TestTokenBucket::test_bucket_initialization PASSED
test_gateway.py::TestTokenBucket::test_single_request_allowed PASSED
test_gateway.py::TestRateLimiter::test_rate_limiter_initialization PASSED
...
```

All passing? Great!

### Run Specific Tests

```bash
# Just token bucket tests
pytest test_gateway.py::TestTokenBucket -v

# Just rate limiting tests
pytest test_gateway.py::TestRateLimiter -v

# Just API endpoint tests
pytest test_gateway.py::TestAPIEndpoints -v

# Stop on first failure
pytest test_gateway.py -x

# Show print statements
pytest test_gateway.py -s

# Run with detailed output
pytest test_gateway.py -vv
```

### What the Tests Do

There are 7 test classes:

1. **TestTokenBucket** - Tests the rate limiting algorithm
2. **TestRateLimiter** - Tests multi-client rate limiting
3. **TestMetrics** - Tests metrics collection
4. **TestMockBackendService** - Tests the fake backend
5. **TestAPIEndpoints** - Tests FastAPI endpoints
6. **TestRateLimitingIntegration** - Tests rate limiting with API
7. **TestEndToEnd** - Full workflow tests

Each test is independent and tests one thing. Easy to understand.

---

## Step 4: Actually Use the Thing

### Scenario 1: "I want to see if it works"

```bash
# Terminal 1: Start the gateway
python main.py

# Terminal 2: Make a request
curl -X POST http://localhost:8000/forward \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "/users"}'

# You should get user data back
```

Done. It works.

### Scenario 2: "I want to understand rate limiting"

```bash
# Terminal 1: Start gateway
python main.py

# Terminal 2: Reset metrics and test
curl -X POST http://localhost:8000/reset-metrics

# Send 150 requests fast (watch some get blocked)
for i in {1..150}; do
  curl -s -X POST http://localhost:8000/forward \
    -H "Content-Type: application/json" \
    -d '{"endpoint": "/users"}' > /dev/null
  if [ $((i % 50)) -eq 0 ]; then echo "Sent $i"; fi
done

# Check what happened
curl http://localhost:8000/metrics | jq .
```

You'll see metrics showing ~100 succeeded and ~50 blocked. That's rate limiting!

### Scenario 3: "I want to test everything"

```bash
# Terminal 1: Start gateway
python main.py

# Terminal 2: Run the full test script

# 1. Reset metrics
curl -X POST http://localhost:8000/reset-metrics

# 2. Test each endpoint
echo "Testing /users:"
curl -s -X POST http://localhost:8000/forward \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "/users"}' | jq '.success'

echo "Testing /data:"
curl -s -X POST http://localhost:8000/forward \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "/data"}' | jq '.success'

echo "Testing /health:"
curl -s -X POST http://localhost:8000/forward \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "/health"}' | jq '.success'

# 3. Check metrics
echo "Metrics:"
curl -s http://localhost:8000/metrics | jq '.'

# 4. Check client status
echo "Client status:"
curl -s http://localhost:8000/client-status/127.0.0.1 | jq '.rate_limit_status'

# 5. Test rate limiting
echo "Testing rate limit (sending 150 requests)..."
blocked=0
for i in {1..150}; do
  status=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/forward \
    -H "Content-Type: application/json" \
    -d '{"endpoint": "/users"}')
  if [ "$status" = "429" ]; then
    ((blocked++))
  fi
done
echo "Blocked requests: $blocked"

# 6. Final metrics
echo "Final metrics:"
curl -s http://localhost:8000/metrics | jq '.'
```

This hits all the main functionality.

---

## Common Commands Reference

| What I Want | Command |
|---|---|
| Start the gateway | `python main.py` |
| Test in browser | `http://localhost:8000/docs` |
| Make a request | `curl -X POST http://localhost:8000/forward -H "Content-Type: application/json" -d '{"endpoint": "/users"}'` |
| See metrics | `curl http://localhost:8000/metrics \| jq .` |
| Run tests | `pytest test_gateway.py -v` |
| Reset metrics | `curl -X POST http://localhost:8000/reset-metrics` |
| Check rate limit | `curl http://localhost:8000/client-status/127.0.0.1` |
| Stop the server | `Ctrl + C` (in the terminal where it's running) |

---

## Troubleshooting

### "Command not found: python"
Use `python3` instead. On some systems, `python` is Python 2 (ancient).
```bash
python3 main.py
pip3 install -r requirements.txt
```

### "Port 8000 already in use"
Something else is using port 8000. Either:
- Kill the other process
- Or run on a different port:
```bash
uvicorn main:app --port 8001
```

### "ModuleNotFoundError: No module named 'fastapi'"
You didn't install requirements.
```bash
pip install -r requirements.txt
```

### "All my test requests get rate limited immediately"
The metrics aren't reset. Run:
```bash
curl -X POST http://localhost:8000/reset-metrics
```
Or restart the gateway.

### "Curl commands aren't working"
1. Make sure curl is installed (usually is on Mac/Linux)
2. On Windows, use the Python test client instead:
   ```bash
   python test_gateway.py
   ```
3. Or just use the browser docs at http://localhost:8000/docs

### "Tests are failing"
1. Make sure the gateway isn't running (it would interfere)
2. Make sure you have pytest installed:
   ```bash
   pip install pytest httpx
   ```
3. Run tests with verbose output:
   ```bash
   pytest test_gateway.py -v -s
   ```

### "I want to modify the rate limiting settings"
Edit `main.py` line 28-31:
```python
rate_limiter = RateLimiter(capacity=100, refill_rate=10.0)
```
Change `capacity` (max tokens) or `refill_rate` (tokens per second).

---

## Project Files Quick Reference

```
api-gateway-learning/
├── main.py                 # ← The app itself. Start here.
├── rate_limiter.py         # Rate limiting logic
├── metrics.py              # Metrics tracking
├── mock_service.py         # Fake backend
├── models.py               # Data validation
├── test_gateway.py         # ← Tests. Run these!
├── requirements.txt        # Install with: pip install -r requirements.txt
├── README.md               # Full documentation
├── QUICK_START.md          # 2-minute guide
├── TESTING_GUIDE.md        # Human-friendly testing
├── SETUP_AND_RUN.md        # This file
└── EXAMPLES.md             # Copy-paste examples
```

---

## The Workflow

Here's what you probably want to do:

**Day 1:**
```bash
# Setup
pip install -r requirements.txt

# Run
python main.py

# Explore in browser
open http://localhost:8000/docs

# Run tests
pytest test_gateway.py -v
```

**Day 2:**
```bash
# Read the code
cat main.py
cat rate_limiter.py
# etc.

# Run specific tests to understand
pytest test_gateway.py::TestTokenBucket -v

# Experiment with changes
# (edit the files, run again)
```

**Day 3:**
```bash
# Use it as a project to talk about
# Explain rate limiting
# Talk about metrics
# Defend design choices

# Or extend it:
# - Add authentication
# - Add different rate limiting strategies
# - Add persistence
```

---

## Next Steps

1. **Get it running** - Follow step 1-2 above
2. **Run the tests** - `pytest test_gateway.py -v`
3. **Understand it** - Read main.py, then rate_limiter.py
4. **Play with it** - Use TESTING_GUIDE.md
5. **Extend it** - Add features (see README.md for ideas)
6. **Interview it** - Prepare to explain it to someone

---

## Need Help?

- **Understanding the code?** → Read README.md
- **Testing it?** → Read TESTING_GUIDE.md
- **Copy-paste commands?** → See EXAMPLES.md
- **Understanding architecture?** → Read PROJECT_STRUCTURE.md
- **Quick start?** → Read QUICK_START.md

---

That's it! You're ready to go. Stop reading and start running.

```bash
python main.py
```

Go!
