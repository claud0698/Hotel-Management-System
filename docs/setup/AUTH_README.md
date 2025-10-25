# Authentication System - KOS Database

## Overview
Simple username/password authentication system for the KOS management application.

## Features
- ✅ Username + Password authentication (no email required)
- ✅ Secure password hashing with bcrypt
- ✅ Session-based token authentication
- ✅ User management (CRUD operations)
- ✅ Protection against self-deletion
- ✅ Multi-language support (English & Indonesian)

## Default Credentials
```
Username: admin
Password: admin123
```

**⚠️ Important:** Change the default password after first login!

## Backend API Endpoints

### Authentication
- `POST /api/auth/login` - Login with username and password
- `GET /api/auth/me` - Get current user info (requires auth)

### User Management (requires authentication)
- `GET /api/users` - List all users
- `GET /api/users/{id}` - Get specific user
- `POST /api/users` - Create new user
  ```json
  {
    "username": "newuser",
    "password": "password123"
  }
  ```
- `PUT /api/users/{id}` - Update user
  ```json
  {
    "username": "updated_username",  // optional
    "password": "new_password"       // optional
  }
  ```
- `DELETE /api/users/{id}` - Delete user (cannot delete self)

## Frontend Access

### User Management Page
Navigate to: **http://localhost:5173/users**

Features:
- View all users
- Create new users (username + password)
- Edit existing users (can update username and/or password)
- Delete users (except your own account)
- Fully internationalized (English/Indonesian)

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(120) NULL,  -- optional for backwards compatibility
    created_at DATETIME
);
```

## Security Features

1. **Password Hashing**: All passwords are hashed using bcrypt
2. **Token-Based Auth**: Secure session tokens for API access
3. **Self-Protection**: Users cannot delete their own accounts
4. **Input Validation**:
   - Username: min 3 characters
   - Password: min 4 characters

## Creating Additional Users

### Via API
```bash
# 1. Login first
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 2. Create new user
curl -X POST http://localhost:8001/api/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","password":"password123"}'
```

### Via Frontend
1. Login at http://localhost:5173
2. Navigate to "Users" in the sidebar
3. Click "+ Add User"
4. Enter username and password
5. Click "Create User"

## Scripts

Located in `/backend/scripts/`:

- `seed_admin_user.py` - Creates the default admin user
- `fix_users_table.py` - Migration script for database schema

### Creating Admin User Manually
```bash
cd backend
./venv/bin/python3 scripts/seed_admin_user.py
```

## Troubleshooting

### "Invalid or expired token"
- Tokens are stored in memory and reset when backend restarts
- Solution: Log in again to get a new token

### "Cannot delete your own account"
- This is by design for security
- Create another admin user first, then delete from that account

### Password not working
- Ensure minimum 4 characters
- No special character requirements
- Case-sensitive

## Architecture

### Backend (FastAPI)
- `models.py` - User model with password hashing
- `security.py` - Token generation and validation
- `routes/auth_router.py` - Login endpoints
- `routes/users_router.py` - User management endpoints

### Frontend (React + TypeScript)
- `services/api.ts` - API client with user management methods
- `pages/UsersPage.tsx` - User management UI
- `locales/en.json` & `locales/id.json` - Translations

## Migration from Old System

The system supports the optional `email` field for backwards compatibility with existing databases. New users don't require email.

---

**Server Status:**
- Backend: http://localhost:8001
- Frontend: http://localhost:5173
- API Docs: http://localhost:8001/api/docs
