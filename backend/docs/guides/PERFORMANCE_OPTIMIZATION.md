# Performance Optimization Guide

**Purpose**: Techniques and best practices for optimizing Hotel Management System performance

**Last Updated**: November 8, 2025

---

## Table of Contents

1. [Quick Wins](#quick-wins)
2. [Database Optimization](#database-optimization)
3. [API Optimization](#api-optimization)
4. [Caching Strategies](#caching-strategies)
5. [Query Optimization](#query-optimization)
6. [Monitoring & Profiling](#monitoring--profiling)
7. [Load Testing](#load-testing)

---

## Quick Wins

### 1. Add Database Indexes (Immediate)

```python
# In models.py - Add to key fields:
class Reservation(Base):
    __tablename__ = "reservations"

    # Existing fields...

    # Add these indexes:
    __table_args__ = (
        Index('idx_reservation_dates', 'check_in_date', 'check_out_date'),
        Index('idx_reservation_guest', 'guest_id'),
        Index('idx_reservation_room', 'room_id'),
        Index('idx_reservation_status', 'status'),
        Index('idx_reservation_created', 'created_at'),
    )
```

**Impact**: 50-80% faster queries on filtered/sorted results
**Time**: 15 minutes
**Effort**: Low

### 2. Enable Query Result Caching (FastAPI)

```python
# In app.py
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend
from redis import asyncio as aioredis

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache2.init(RedisBackend(redis), prefix="fastapi-cache")

# In routes
from fastapi_cache2.decorators import cache

@router.get("/api/rooms")
@cache(expire=300)  # Cache for 5 minutes
async def list_rooms():
    return await get_all_rooms()
```

**Impact**: 90% faster repeated requests
**Time**: 30 minutes
**Effort**: Low

### 3. Lazy Load Relations (SQLAlchemy)

```python
# Before (loads all related data)
reservations = db.query(Reservation).all()  # Loads guests, rooms, payments too

# After (lazy load on demand)
reservations = db.query(Reservation).options(
    joinedload(Reservation.guest),
    joinedload(Reservation.room)
).all()

# Or use selectinload for one-to-many
reservations = db.query(Reservation).options(
    selectinload(Reservation.payments)
).all()
```

**Impact**: 40% less memory, faster initial load
**Time**: 20 minutes
**Effort**: Low

### 4. Use Pagination

```python
# In routes
@router.get("/api/reservations")
async def list_reservations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    skip = (page - 1) * page_size

    reservations = db.query(Reservation)\
        .offset(skip)\
        .limit(page_size)\
        .all()

    total = db.query(Reservation).count()

    return {
        "items": reservations,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }
```

**Impact**: 80% faster for large datasets
**Time**: 15 minutes
**Effort**: Low

---

## Database Optimization

### 1. Connection Pooling

```python
# In database.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,           # Number of connections to keep
    max_overflow=40,        # Additional connections allowed
    pool_recycle=3600,      # Recycle connections after 1 hour
    pool_pre_ping=True      # Test connection before using
)
```

**Benefit**: Better connection reuse, fewer timeouts

### 2. Query Analysis

```bash
# Enable PostgreSQL query logging (production)
# In database URL, add:
postgresql://user:pass@host/db?application_name=hotel_api

# Monitor slow queries
EXPLAIN ANALYZE SELECT * FROM reservations
WHERE check_in_date BETWEEN '2025-01-01' AND '2025-12-31';

# Look for: Sequential scans on large tables (BAD)
# Goal: Index scans or bitmap index scans (GOOD)
```

### 3. Denormalization (Strategic)

```python
# Add frequently-accessed data to Reservation
class Reservation(Base):
    __tablename__ = "reservations"

    # Original fields...
    guest_name = Column(String(200))  # Denormalized from Guest
    room_number = Column(String(50))  # Denormalized from Room
    room_type_name = Column(String(100))  # Denormalized from RoomType
    guest_email = Column(String(100))  # For quick contact

    # Still maintain foreign keys for integrity
    guest_id = Column(Integer, ForeignKey("guests.id"))
```

**Trade-off**:
- ✅ 20% faster common queries
- ❌ More complex updates (must update both places)

### 4. Batch Operations

```python
# Before: N+1 problem - 101 queries for 100 items
for reservation in reservations:
    record_payment(reservation.id)  # 100 queries

# After: 1 query
payments_data = [
    {
        'reservation_id': r.id,
        'amount': r.total_amount,
        'payment_type': 'full'
    }
    for r in reservations
]
db.bulk_insert_mappings(Payment, payments_data)
db.commit()
```

**Impact**: 100x faster for bulk operations
**Time**: 30 minutes
**Effort**: Medium

---

## API Optimization

### 1. Response Compression

```python
# In app.py
from fastapi.middleware.gzip import GZIPMiddleware

app.add_middleware(GZIPMiddleware, minimum_size=1000)
```

**Impact**: 70% smaller response size
**Automatic**: ✅ Yes

### 2. Async Endpoints

```python
# Before (blocking)
@app.get("/api/dashboard/stats")
def get_stats():
    data = db.query(Reservation).filter(...).all()
    return data

# After (non-blocking)
@app.get("/api/dashboard/stats")
async def get_stats():
    # Background task while waiting for DB
    data = await db_session.execute(select(Reservation).filter(...))
    return data.scalars().all()
```

**Impact**: Can handle 3-5x more concurrent users
**Time**: 1 hour
**Effort**: Medium

### 3. Field Selection

```python
# Before: Returns all fields
@router.get("/api/reservations/{id}")
async def get_reservation(id: int):
    return db.query(Reservation).filter(Reservation.id == id).first()

# After: Return only needed fields
@router.get("/api/reservations/{id}")
async def get_reservation(id: int):
    return db.query(
        Reservation.id,
        Reservation.confirmation_number,
        Reservation.guest_id,
        Reservation.check_in_date,
        Reservation.check_out_date,
        Reservation.total_amount,
        Reservation.status
    ).filter(Reservation.id == id).first()
```

**Impact**: 30% smaller response, faster network
**Time**: 30 minutes
**Effort**: Low

### 4. Rate Limiting

```python
# In app.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.get("/api/reservations")
@limiter.limit("100/minute")  # 100 requests per minute
async def list_reservations(request: Request):
    return await get_reservations()
```

**Benefit**: Prevents API abuse and overload

---

## Caching Strategies

### 1. In-Memory Cache (Simple)

```python
# Using functools
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=128)
def get_room_types():
    return db.query(RoomType).all()

# Cache for 1 hour
from cachetools import TTLCache

cache = TTLCache(maxsize=100, ttl=3600)

def get_dashboard_stats():
    if 'stats' in cache:
        return cache['stats']

    stats = calculate_stats()
    cache['stats'] = stats
    return stats
```

**Trade-off**: Simple, fast, but single-server only

### 2. Redis Cache (Production)

```python
# requirements.txt
redis==5.0.0
fastapi-cache2[redis]==0.2.1

# In cache_utils.py
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend

async def cache_get(key: str):
    return await FastAPICache2.get(key)

async def cache_set(key: str, value: any, ttl: int = 300):
    await FastAPICache2.set(key, value, ttl)
```

**Trade-off**: Distributed caching, but requires Redis server

### 3. Strategic Cache Keys

```python
# Good cache keys include filters
cache_key = f"reservations:guest_{guest_id}:status_{status}"

# Bad cache keys (too generic)
cache_key = "all_reservations"  # Invalidates too often

# Cache structure
{
    "reservations:guest_1:status_confirmed": [...],
    "reservations:guest_1:status_checked_in": [...],
    "reservations:guest_2:status_confirmed": [...],
}
```

### 4. Cache Invalidation

```python
# When creating/updating/deleting
@router.post("/api/reservations")
async def create_reservation(data: ReservationCreate):
    # Create reservation
    reservation = Reservation(**data.dict())
    db.add(reservation)
    db.commit()

    # Invalidate related caches
    await FastAPICache2.clear(namespace=f"guest_{data.guest_id}")
    await FastAPICache2.clear(namespace="available_rooms")

    return reservation
```

---

## Query Optimization

### 1. Use EXISTS for Checks

```python
# Before: Loads entire record
if db.query(Reservation).filter(Reservation.id == res_id).first():
    # Do something

# After: Just checks existence
if db.query(
    db.exists().where(Reservation.id == res_id)
).scalar():
    # Do something
```

**Impact**: 60% faster existence checks

### 2. Aggregate Queries

```python
# Before: Load all, then aggregate
reservations = db.query(Reservation).filter(...).all()
total = sum(r.total_amount for r in reservations)
count = len(reservations)

# After: Aggregate in database
from sqlalchemy import func

result = db.query(
    func.sum(Reservation.total_amount).label('total'),
    func.count(Reservation.id).label('count')
).filter(...).first()

total = result.total
count = result.count
```

**Impact**: 99% faster for large datasets

### 3. Avoid SELECT *

```python
# Bad
db.query(Reservation).all()  # Loads all columns

# Good
db.query(
    Reservation.id,
    Reservation.confirmation_number,
    Reservation.total_amount
).all()
```

### 4. Use EXPLAIN to Analyze

```sql
-- Show query plan
EXPLAIN ANALYZE
SELECT * FROM reservations
WHERE check_in_date = '2025-11-10'
AND status = 'confirmed';

-- Look for:
-- ✅ Index Scan (good)
-- ❌ Sequential Scan (bad - add index)
```

---

## Monitoring & Profiling

### 1. Logging Performance

```python
# In app.py
import time
from error_handlers import logger

class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start

        logger.info(f"Request completed in {duration:.2f}s", extra={
            "path": request.url.path,
            "method": request.method,
            "duration_seconds": duration,
            "status_code": response.status_code
        })

        # Slow request warning
        if duration > 1.0:
            logger.warning(f"Slow request detected: {duration:.2f}s")

        return response
```

### 2. Database Query Profiling

```python
# Add SQLAlchemy event listener
from sqlalchemy import event

queries_log = []

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total_time = time.time() - context._query_start_time

    queries_log.append({
        "statement": statement,
        "duration": total_time,
        "parameters": parameters
    })

    if total_time > 0.5:  # Log slow queries
        logger.warning(f"Slow query: {total_time:.2f}s - {statement[:100]}")
```

### 3. Memory Profiling

```bash
# Install memory profiler
pip install memory-profiler

# Profile specific function
python -m memory_profiler app.py

# In code
from memory_profiler import profile

@profile
def list_all_reservations():
    return db.query(Reservation).all()
```

### 4. APM Integration (Application Performance Monitoring)

```python
# Using New Relic (Production)
import newrelic.agent
newrelic.agent.initialize('newrelic.ini')

# Using DataDog
from ddtrace import tracer

@tracer.wrap()
def process_payment(reservation_id: int):
    # Traced automatically
    pass
```

---

## Load Testing

### 1. Basic Load Test (Locust)

```bash
pip install locust
```

Create `locustfile.py`:

```python
from locust import HttpUser, task, between

class HotelAPIUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests

    @task(3)
    def list_reservations(self):
        self.client.get("/api/reservations?page=1&page_size=20")

    @task(2)
    def get_dashboard(self):
        self.client.get("/api/dashboard/today")

    @task(1)
    def create_reservation(self):
        self.client.post("/api/reservations", json={
            "guest_id": 1,
            "room_id": 1,
            "check_in_date": "2025-11-15",
            "check_out_date": "2025-11-18",
            "total_amount": 1500000
        })

    def on_start(self):
        # Login
        response = self.client.post("/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        self.client.headers.update({
            "Authorization": f"Bearer {response.json()['access_token']}"
        })
```

Run:
```bash
locust -f locustfile.py -u 100 -r 10 -t 5m
# -u: 100 users
# -r: 10 users spawn per second
# -t: 5 minute test
```

### 2. Apache Bench

```bash
# Simple load test
ab -n 1000 -c 100 https://api.example.com/api/reservations

# -n: 1000 total requests
# -c: 100 concurrent requests
```

### 3. Check Performance Goals

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| API Response Time | <200ms | TBD | ? |
| Concurrent Users | 1,000 | TBD | ? |
| Throughput | 10,000 req/min | TBD | ? |
| Database CPU | <70% | TBD | ? |
| Memory Usage | <500MB | TBD | ? |

---

## Performance Checklist

### Before Deployment
- [ ] All indexes added (check EXPLAIN ANALYZE)
- [ ] Pagination implemented (max 100 items per request)
- [ ] Response compression enabled
- [ ] Cache configured
- [ ] Lazy loading enabled
- [ ] Rate limiting configured
- [ ] Connection pooling optimized
- [ ] Slow query logging enabled

### Monitoring Setup
- [ ] APM/monitoring tool integrated
- [ ] Slow query alerts configured
- [ ] Error rate alerts configured
- [ ] Resource usage alerts configured
- [ ] Load testing completed

### Documentation
- [ ] Performance guidelines documented
- [ ] Cache invalidation strategy documented
- [ ] Scaling strategy documented
- [ ] Disaster recovery plan documented

---

## Quick Reference

### Index Creation

```sql
-- Reservations table
CREATE INDEX idx_reservation_guest ON reservations(guest_id);
CREATE INDEX idx_reservation_room ON reservations(room_id);
CREATE INDEX idx_reservation_dates ON reservations(check_in_date, check_out_date);
CREATE INDEX idx_reservation_status ON reservations(status);

-- Payments table
CREATE INDEX idx_payment_reservation ON payments(reservation_id);
CREATE INDEX idx_payment_date ON payments(payment_date);

-- Guests table
CREATE INDEX idx_guest_email ON guests(email);
CREATE INDEX idx_guest_phone ON guests(phone_number);
```

### Query Templates

```python
# Fast list with pagination
db.query(Model).offset(skip).limit(limit).all()

# Fast single record
db.query(Model).filter(Model.id == id).first()

# Fast existence check
db.exists().where(Model.id == id)

# Fast aggregates
db.query(func.count(Model.id), func.sum(Model.amount)).first()
```

---

## Further Reading

- [SQLAlchemy Performance Tips](https://docs.sqlalchemy.org/en/20/faq/performance.html)
- [FastAPI Performance](https://fastapi.tiangolo.com/deployment/concepts/#scaling)
- [PostgreSQL Optimization](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Redis Caching Patterns](https://redis.io/docs/manual/client-side-caching/)

---

**Last Updated**: November 8, 2025
**Status**: Ready for Phase 9
**Next**: Implement optimizations based on profiling results
