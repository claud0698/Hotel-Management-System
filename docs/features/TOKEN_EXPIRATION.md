# Token Expiration & Auto-Logout Behavior

## ✅ CONFIRMED: Auto-logout IS NOW enabled

### Current Behavior (After Update):

**When token expires or becomes invalid:**
1. ✅ Backend returns `401 Unauthorized`
2. ✅ Frontend **automatically logs out** the user
3. ✅ User is **redirected to login page**
4. ✅ Token is **cleared from localStorage**
5. ✅ User sees message: "Session expired. Please login again."

## Token Configuration

### Backend Token Settings:
- **Expiration Time**: 24 hours (1440 minutes)
- **Storage**: In-memory (resets on server restart)
- **Cleanup**: Expired tokens are automatically removed

```python
# backend/security.py
TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
```

### When Tokens Expire:

1. **After 24 hours**: Token automatically expires
2. **Backend restart**: All tokens are cleared (in-memory storage)
3. **Manual logout**: Token is revoked immediately

## Frontend Auto-Logout Implementation

### Triggers for Auto-Logout:
- ❌ Token expired (after 24 hours)
- ❌ Token invalid (backend restarted)
- ❌ Token revoked (manual logout from another session)
- ❌ Any 401 Unauthorized response from API

### What Happens:
```javascript
// frontend/src/services/api.ts
if (response.status === 401) {
  this.clearToken();              // Clear token from localStorage
  window.location.href = '/login'; // Redirect to login page
  throw new Error('Session expired. Please login again.');
}
```

## Testing Token Expiration

### Test 1: Backend Restart (Immediate)
```bash
# 1. Login to the app
# 2. Restart backend:
kill <backend-pid>
./venv/bin/python3 app.py

# 3. Try to access any page
# Result: Auto-logout + redirect to /login ✅
```

### Test 2: Token Expiration (24 hours)
```bash
# 1. Login to the app
# 2. Wait 24 hours (or modify TOKEN_EXPIRE_MINUTES to 1 minute for testing)
# 3. Try to access any page
# Result: Auto-logout + redirect to /login ✅
```

### Test 3: Invalid Token
```bash
# 1. Login to the app
# 2. Open DevTools > Application > Local Storage
# 3. Manually change the access_token value
# 4. Try to access any page
# Result: Auto-logout + redirect to /login ✅
```

## Quick Test (1 minute expiration)

To test quickly, change the expiration time:

```python
# backend/security.py
TOKEN_EXPIRE_MINUTES = 1  # Change from 24*60 to 1 minute
```

Then:
1. Restart backend
2. Login to the app
3. Wait 61 seconds
4. Click any navigation link
5. Should auto-logout and redirect to login page

## Token Lifecycle

```
┌─────────────┐
│   Login     │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Token Created       │
│ Expires: Now + 24h  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Token Active        │
│ (Valid for 24h)     │
└──────┬──────────────┘
       │
       ├─────► Backend Restart → Token Invalid
       ├─────► 24 Hours Pass → Token Expired
       └─────► Manual Logout → Token Revoked
                      │
                      ▼
              ┌───────────────┐
              │ 401 Received  │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ Auto Logout   │
              │ Clear Token   │
              │ → /login      │
              └───────────────┘
```

## Security Benefits

✅ **Expired tokens don't work** - Can't use old tokens
✅ **Auto-cleanup** - Expired tokens removed from memory
✅ **Better UX** - User automatically logged out, no confusing errors
✅ **Session management** - 24-hour sessions prevent stale authentication
✅ **No token reuse** - Backend restart invalidates all tokens

## Production Recommendations

For production, consider:
1. **Use JWT with expiration** instead of in-memory tokens
2. **Store tokens in Redis** for persistence across restarts
3. **Implement refresh tokens** for better UX (auto-renew)
4. **Add token rotation** for enhanced security
5. **Configure shorter expiration** for sensitive operations
6. **Add rate limiting** on login attempts

---

**Current Setup:**
- Backend: http://localhost:8001
- Frontend: http://localhost:8002
- Token Expiration: 24 hours
- Auto-logout: ✅ Enabled
