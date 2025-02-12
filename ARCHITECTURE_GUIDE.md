# Architecture Guide - Understanding the Modular Structure

This guide explains how the project is organized and why.

## The Problem We're Solving

**Monolithic vs Modular:**

❌ MONOLITHIC (Bad):
```
main.py (250 lines)
  - Rate limiting logic (120 lines)
  - Metrics logic (70 lines)
  - Backend simulation (80 lines)
  - Everything jumbled together
```

✅ MODULAR (Good):
```
src/
  ├── rate_limiting/ (rate limiting ONLY)
  ├── metrics/ (metrics ONLY)
  ├── backend/ (backend ONLY)
  ├── models/ (data structures ONLY)
  └── gateway/ (API gateway ONLY)
```

## Single Responsibility Principle

**Rule:** Each module has ONE job. Only ONE reason to change.

### 1. Rate Limiting Module (`src/rate_limiting/`)

**Job:** Handle rate limiting for clients

**Components:**

```python
# token_bucket.py
class TokenBucket:
    """Manage tokens for ONE client"""
    - Responsibility: Refill tokens, check if allowed
    - Does NOT care about multiple clients
    - ~50 lines
```

```python
# rate_limiter.py
class RateLimiter:
    """Manage multiple clients"""
    - Responsibility: Track multiple clients, delegate to TokenBucket
    - Does NOT implement token logic
    - ~50 lines
```

**Example: Why separation?**

If you want to change token refill algorithm:
- Only edit: `token_bucket.py`
- No need to touch: `rate_limiter.py`, API, metrics, etc.

### 2. Metrics Module (`src/metrics/`)

**Job:** Collect and report metrics

**Components:**

```python
# collector.py
class MetricsCollector:
    """Store raw metrics data"""
    - Responsibility: Record requests, store response times
    - Does NOT calculate anything
    - ~40 lines
```

```python
# calculator.py
class MetricsCalculator:
    """Calculate derived metrics"""
    - Responsibility: Average, percentages, rates
    - Does NOT store data
    - ~35 lines
```

```python
# metrics_manager.py
class MetricsManager:
    """Orchestrate collector + calculator"""
    - Responsibility: Combine them, provide interface
    - Does NOT do collection or calculation
    - ~35 lines
```

**Example: Why separation?**

If you want to add a new metric like `p95_response_time`:
1. Add method to `calculator.py`
2. Add to `metrics_manager.py`
3. Done! No changes to rate limiting, backend, API

### 3. Backend Module (`src/backend/`)

**Job:** Handle backend requests

**Components:**

```python
# handlers.py
class BaseHandler:
    """Abstract base for all handlers"""

class UsersHandler(BaseHandler):
    """Handle /users endpoint"""

class DataHandler(BaseHandler):
    """Handle /data endpoint"""

class HealthHandler(BaseHandler):
    """Handle /health endpoint"""

# Each handler: ~15 lines
# Each handler has ONE job: handle ONE endpoint
```

```python
# router.py
class BackendRouter:
    """Route requests to handlers"""
    - Responsibility: Map endpoints to handlers
    - Does NOT implement endpoints
    - ~25 lines
```

```python
# service.py
class BackendService:
    """Unified backend interface"""
    - Responsibility: Provide public API
    - Uses router internally
    - ~20 lines
```

**Example: Why separation?**

Want to add `/events` endpoint?

1. Create `EventsHandler(BaseHandler)` in `handlers.py`
2. Register in `router.py`: `handlers["/events"] = EventsHandler()`
3. Done!

No changes to:
- Rate limiting
- Metrics
- API gateway
- Main app

### 4. Models Module (`src/models/`)

**Job:** Define data structures

**Components:**

```python
# request_models.py
class ForwardRequest(BaseModel):
    """Validate incoming requests"""
    - ~10 lines
```

```python
# response_models.py
class APIResponse(BaseModel):
    """Format success responses"""

class RateLimitResponse(BaseModel):
    """Format rate limit responses"""
    - ~15 lines total
```

**Responsibility:** Validate, that's it

### 5. Gateway Module (`src/gateway/`)

**Job:** Orchestrate the API gateway

**Components:**

```python
# app.py
def create_app():
    """Create FastAPI application"""
    - Responsibility: Initialize and configure app
    - Does NOT contain business logic
    - ~25 lines
```

```python
# routes.py
def create_routes(rate_limiter, metrics, backend):
    """Define API endpoints"""
    - Responsibility: Map URLs to handlers
    - Does NOT contain business logic
    - ~50 lines
```

```python
# request_handler.py
class GatewayRequestHandler:
    """Process requests through pipeline"""
    - Responsibility: Check rate limit, forward to backend
    - Does NOT know about HTTP
    - ~30 lines
```

```python
# response_formatter.py
class ResponseFormatter:
    """Format responses consistently"""
    - Responsibility: Create response objects
    - Does NOT process logic
    - ~25 lines
```

## How They Work Together

```
Request comes in
    ↓
routes.py (what endpoint is this?)
    ↓
request_handler.py (process it)
    ├─ Check: rate_limiter.is_allowed()?
    └─ Forward to: backend.handle_request()
    ↓
response_formatter.py (format response)
    ↓
metrics_manager.record_request()
    ↓
Return response
```

Each component:
- Does ONE job
- Doesn't care about other components' internals
- Can be tested independently
- Can be replaced independently

## Dependency Flow

```
HIGH LEVEL (Depends on):
  main.py
    ↓
  gateway/app.py
    ↓
  gateway/routes.py
    ↓
  - request_handler.py
  - response_formatter.py

MIDDLE LEVEL:
  request_handler.py uses:
    ├─ rate_limiting/rate_limiter.py
    └─ backend/service.py

  response_formatter.py uses:
    └─ models/ (response classes)

LOW LEVEL (No dependencies on others):
  - rate_limiting/token_bucket.py
  - rate_limiting/rate_limiter.py
  - metrics/collector.py
  - metrics/calculator.py
  - backend/handlers.py
  - models/ (just data classes)
```

## Testing Strategy

### Unit Tests (Test each module alone)

```python
# tests/unit/test_token_bucket.py
def test_token_bucket():
    bucket = TokenBucket(capacity=100, refill_rate=10)
    # Test ONLY TokenBucket logic
    # No other modules involved
```

**Why?** Each module is independent, so can test in isolation.

### Integration Tests (Test modules together)

```python
# tests/integration/test_api_endpoints.py
def test_forward_endpoint():
    client = TestClient(create_app())
    # Test full flow: request → rate limit → backend → response
    # All modules working together
```

**Why?** Ensure modules work correctly when combined.

## Adding Features

### Add new endpoint

1. Create handler in `src/backend/handlers.py`
2. Register in `src/backend/router.py`
3. Add tests in `tests/unit/test_backend_handlers.py`

That's it! No other changes needed.

### Add new metric

1. Add method to `src/metrics/calculator.py`
2. Call in `src/metrics/metrics_manager.py`
3. Add tests in `tests/unit/test_metrics_calculator.py`

That's it! No other changes needed.

### Add new rate limiting strategy

1. Create new class in `src/rate_limiting/`
2. Update `src/gateway/app.py` to use it
3. Add tests

That's it!

## Code Size

All files kept small for clarity:

```
token_bucket.py         ~50 lines
rate_limiter.py         ~50 lines
collector.py            ~40 lines
calculator.py           ~35 lines
metrics_manager.py      ~35 lines
handlers.py             ~60 lines
router.py               ~25 lines
service.py              ~20 lines
request_models.py       ~10 lines
response_models.py      ~15 lines
app.py                  ~25 lines
routes.py               ~50 lines
request_handler.py      ~30 lines
response_formatter.py   ~25 lines
```

**Average:** ~30 lines per file

**Max:** ~60 lines

This makes code:
- Easy to read
- Easy to understand
- Easy to test
- Easy to modify

## Design Patterns Used

### 1. Strategy Pattern (Handlers)

```python
class BaseHandler(ABC):
    @abstractmethod
    def handle(self, data):
        pass

class UsersHandler(BaseHandler):
    def handle(self, data):
        return {"users": [...]}
```

**Why?** Each endpoint is a different strategy. Easy to add new ones.

### 2. Facade Pattern (Manager Classes)

```python
class MetricsManager:
    def __init__(self):
        self.collector = MetricsCollector()
        self.calculator = MetricsCalculator()

    def get_metrics(self):
        raw = self.collector.get_raw_data()
        return self.calculator.calculate(raw)
```

**Why?** Hides complexity. Users just call `get_metrics()`.

### 3. Dependency Injection

```python
# Instead of:
class RateLimiter:
    def __init__(self):
        self.metrics = MetricsManager()  # Creates own dependency

# We do:
def create_routes(rate_limiter, metrics_manager):
    # Receives dependencies as parameters
    pass
```

**Why?** Easier to test, easier to swap implementations.

## Interview Talking Points

"The project follows the Single Responsibility Principle. Each module has one job:

- **token_bucket.py**: Manages tokens for one client
- **rate_limiter.py**: Manages multiple clients
- **collector.py**: Stores metrics data
- **calculator.py**: Calculates metrics
- **handlers.py**: Each implements one endpoint
- **router.py**: Routes to handlers
- **app.py**: Creates FastAPI app
- **routes.py**: Defines endpoints

This makes the code:
- Easy to test (each module independently)
- Easy to extend (add feature → add module)
- Easy to maintain (changes isolated to one module)
- Professional (shows I understand design principles)"

## Summary

| Aspect | Value |
|--------|-------|
| Modules | 18 |
| Packages | 5 |
| Classes | 15 |
| Avg lines per file | ~30 |
| SRP applied? | ✅ |
| Testable? | ✅ |
| Extensible? | ✅ |
| Professional? | ✅ |

This is how real, professional backends are structured!
