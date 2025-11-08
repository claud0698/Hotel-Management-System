# 🏨 Hotel Management System - Quick Start Guide

## Local Development Setup (Docker PostgreSQL)

### Prerequisites
- ✅ Docker installed and running
- ✅ Python 3.12
- ✅ Terminal/Command Line access

---

## Step 1: Start PostgreSQL Docker Container

```bash
docker run --name hotel-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=hotel_db \
  -p 5432:5432 \
  -d postgres:15-alpine
```

**Verify it's running:**
```bash
docker ps | grep hotel-postgres
```

Expected: A running container on port 5432

---

## Step 2: Setup Backend Environment

```bash
cd backend

# Use local PostgreSQL connection
cp .env.local .env

# Verify connection in .env
cat .env | grep DATABASE_URL
# Should show: DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hotel_db
```

---

## Step 3: Run Database Migrations

The backend will automatically create tables on startup via SQLAlchemy. Manual migrations are optional:

```bash
# Optional: Apply SQL migrations manually
docker exec -i hotel-postgres psql -U postgres -d hotel_db < migrations/001_v1_0_initial_schema.sql
docker exec -i hotel-postgres psql -U postgres -d hotel_db < migrations/003_create_missing_tables.sql
docker exec -i hotel-postgres psql -U postgres -d hotel_db < migrations/004_insert_mock_data.sql
```

---

## Step 4: Start the Backend

```bash
python app.py
```

**Expected output:**
```
INFO:     Will watch for changes in these directories: ['...']
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Application startup complete.
Database: postgresql://postgres:postgres@localhost:5432/hotel_db
Environment: development
```

Backend is ready at: **http://localhost:8001**

---

## 🧪 Test the API

### Login (Get Auth Token)
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "test123"
  }'
```

**Test Credentials:**
| Username      | Password | Role    |
|---------------|----------|---------|
| admin         | test123  | Admin   |
| manager       | test123  | User    |
| receptionist  | test123  | User    |

### Get Dashboard Metrics
```bash
curl -X GET "http://localhost:8001/api/dashboard/metrics?start_date=2025-06-01T00:00:00Z&end_date=2025-12-31T23:59:59Z" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Get Guests
```bash
curl -X GET "http://localhost:8001/api/guests?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Get Expenses
```bash
curl -X GET "http://localhost:8001/api/expenses?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Create Expense
```bash
curl -X POST http://localhost:8001/api/expenses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "date": "2025-11-08",
    "category": "maintenance",
    "amount": 1500000,
    "description": "AC unit repair"
  }'
```

---

## 📊 Mock Data Available

Your local database includes:

| Entity       | Count |
|-------------|-------|
| Users       | 3     |
| Room Types  | 4     |
| Rooms       | 9     |
| Guests      | 7     |
| Reservations| 3     |
| Payments    | 4     |
| Expenses    | 5     |

**Sample Data:**
- **Rooms**: 101-303 with various statuses (available, occupied, out_of_order)
- **Guests**: John Doe, Jane Smith, Robert Johnson, Maria Garcia, Chen Wei
- **Reservations**: CONF-001, CONF-002, CONF-003 with various dates and guests
- **Payments**: Multiple payment methods (bank_transfer, credit_card)
- **Expenses**: utilities, maintenance, cleaning, supplies, insurance

---

## 🛠️ API Endpoints

### Authentication
```
POST   /api/auth/login           - Login and get token
POST   /api/auth/register        - Register new user
```

### Users
```
GET    /api/users                - List all users
GET    /api/users/{id}           - Get user details
POST   /api/users                - Create user
PUT    /api/users/{id}           - Update user
DELETE /api/users/{id}           - Delete user
```

### Guests
```
GET    /api/guests               - List guests with pagination
GET    /api/guests/{id}          - Get guest details
POST   /api/guests               - Create new guest
PUT    /api/guests/{id}          - Update guest
DELETE /api/guests/{id}          - Delete guest
```

### Reservations
```
GET    /api/reservations         - List reservations
GET    /api/reservations/{id}    - Get reservation details
POST   /api/reservations         - Create reservation
PUT    /api/reservations/{id}    - Update reservation
DELETE /api/reservations/{id}    - Cancel reservation
```

### Payments
```
GET    /api/payments             - List payments
GET    /api/payments/{id}        - Get payment details
POST   /api/payments             - Record payment
PUT    /api/payments/{id}        - Update payment
```

### Expenses
```
GET    /api/expenses             - List expenses with filters
GET    /api/expenses/{id}        - Get expense details
POST   /api/expenses             - Create expense
PUT    /api/expenses/{id}        - Update expense
DELETE /api/expenses/{id}        - Delete expense
```

### Dashboard
```
GET    /api/dashboard/metrics    - Get dashboard metrics
GET    /api/dashboard/summary    - Get dashboard summary
```

---

## 🔄 Docker Management

### Check Container Status
```bash
docker ps | grep hotel-postgres
docker logs hotel-postgres
```

### Connect Directly to PostgreSQL
```bash
docker exec -it hotel-postgres psql -U postgres -d hotel_db
```

**Example queries:**
```sql
-- List all tables
\dt

-- Count records
SELECT COUNT(*) FROM guests;
SELECT COUNT(*) FROM reservations;
SELECT COUNT(*) FROM payments;

-- View sample data
SELECT * FROM guests LIMIT 5;
SELECT * FROM expenses ORDER BY date DESC;
```

### Stop Container
```bash
docker stop hotel-postgres
```

### Restart Container
```bash
docker start hotel-postgres
```

### Remove Container (Deletes Data)
```bash
docker stop hotel-postgres
docker rm hotel-postgres
# Then re-run: docker run --name hotel-postgres ...
```

---

## 🔄 Switch Between Environments

### Use Local Database
```bash
cp .env.local .env
python app.py
```

### Use Supabase (Production)
```bash
# Restore your .env with Supabase credentials
# Make sure to keep the original .env backup
python app.py
```

---

## ⚡ Performance Notes

- **Local PostgreSQL**: ~50-100ms query latency (excellent)
- **Supabase**: ~150-300ms (includes network latency)
- **SQLite**: ~5-10ms (but limited features)

For development, local PostgreSQL Docker is ideal because it matches production exactly.

---

## 🐛 Troubleshooting

### Port 5432 Already in Use
```bash
# Find and kill process using port 5432
lsof -ti:5432 | xargs kill -9

# Or use different port
docker run -p 5433:5432 ...  # Maps to 5433 on host
# Update .env: DB_PORT=5433
```

### Cannot Connect to Database
```bash
# Verify container is running
docker ps | grep hotel-postgres

# Check container logs
docker logs hotel-postgres

# Wait a few seconds after starting
sleep 5
```

### SQLAlchemy Errors
```bash
# Check if all tables exist
docker exec -i hotel-postgres psql -U postgres -d hotel_db -c "\dt"

# Recreate container and migrations
docker stop hotel-postgres
docker rm hotel-postgres
docker run --name hotel-postgres ...  # (re-run the original docker run command)
```

### Authentication Failing
- Verify token in Authorization header: `Bearer YOUR_TOKEN`
- Check user exists: `SELECT * FROM users WHERE username='admin';`
- Token expires after 24 hours by default

---

## 📝 Notes

- All `.env.local` variables are for development only
- Never commit actual database passwords to Git
- `.env.local` is in `.gitignore` for security
- Mock data resets when you delete the Docker container
- For production, use actual Supabase with `.env` (not `.env.local`)

---

## 📚 Additional Resources

- [LOCAL_SETUP.md](backend/LOCAL_SETUP.md) - Detailed local setup guide
- [models.py](backend/models.py) - Database schema definitions
- [app.py](backend/app.py) - FastAPI application entry point
- [migrations/](backend/migrations/) - Database migration files

---

**Happy Coding! 🚀**

For questions or issues, check the logs:
```bash
# Backend logs
python app.py  # See output in terminal

# Database logs
docker logs -f hotel-postgres
```
