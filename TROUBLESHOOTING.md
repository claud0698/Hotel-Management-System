# 🔧 Troubleshooting Guide - Rooms Not Showing

## Issue: Frontend Shows No Rooms

**Symptoms:**
- Frontend loads successfully
- Login works
- Dashboard shows "0 rooms"
- Rooms page is empty

---

## Root Causes & Solutions

### 1. **Empty Database** (Most Likely)

The production database might not have any data yet.

**Solution A: Add Data via Frontend UI**

1. Open frontend: https://kos-database-a5h0v5tot-claud0698s-projects.vercel.app
2. Login with: `admin` / `admin123`
3. Go to "Rooms" page
4. Click "Add Room" button
5. Fill in room details:
   - Room Number: A01
   - Floor: 2 (for upper/atas)
   - Room Type: single/double/suite
   - Monthly Rate: 1000000 (1 juta IDR)
   - Status: available
6. Click Save

**Solution B: Add Data via API Docs**

1. Open API docs: https://kos-backend-228057609267.asia-southeast1.run.app/api/docs
2. Click "Authorize" button (lock icon)
3. Login to get token:
   - POST `/api/auth/login`
   - Body: `{"username":"admin","password":"admin123"}`
   - Copy the `access_token` from response
4. Click "Authorize" again, paste: `Bearer YOUR_TOKEN_HERE`
5. Try POST `/api/rooms` endpoint:
   ```json
   {
     "room_number": "A01",
     "floor": 2,
     "room_type": "single",
     "monthly_rate": 1000000,
     "status": "available",
     "amenities": "AC, WiFi"
   }
   ```

**Solution C: Initialize Database with Script**

```bash
cd backend
source venv/bin/activate

# Ensure admin user exists
python init_admin.py

# Optionally, create sample data
python -c "
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Room, User
import os
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
Session = sessionmaker(bind=engine)
db = Session()

# Check if rooms exist
count = db.query(Room).count()
print(f'Current rooms: {count}')

if count == 0:
    print('Adding sample rooms...')
    rooms = [
        Room(room_number='A01', floor=2, room_type='single', monthly_rate=1000000, status='available', amenities='AC, WiFi'),
        Room(room_number='A02', floor=2, room_type='single', monthly_rate=1000000, status='available', amenities='AC, WiFi'),
        Room(room_number='B01', floor=1, room_type='double', monthly_rate=1500000, status='available', amenities='AC, WiFi, TV'),
    ]
    db.add_all(rooms)
    db.commit()
    print('✅ Added 3 sample rooms')
else:
    print('✅ Database already has rooms')

db.close()
"
```

---

### 2. **Admin User Doesn't Exist**

**Check if admin exists:**

```bash
cd backend
source venv/bin/activate
python init_admin.py
```

Expected output:
```
✅ Admin user already exists
   Username: admin
   Created: 2025-11-06...
```

Or:
```
✅ Admin user created successfully
   Username: admin
   Password: admin123
```

---

### 3. **Frontend Not Connecting to Backend**

**Test the API directly:**

```bash
# Test health
curl https://kos-backend-228057609267.asia-southeast1.run.app/health

# Should return:
# {"status":"ok","environment":"production","database":"postgresql",...}

# Test login
curl -X POST 'https://kos-backend-228057609267.asia-southeast1.run.app/api/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}'

# Should return:
# {"access_token":"...","token_type":"bearer","user":{...}}
```

**Check frontend console:**

1. Open frontend in browser
2. Open Developer Tools (F12)
3. Go to Console tab
4. Look for errors
5. Go to Network tab
6. Try to load rooms
7. Check the `/api/rooms` request:
   - Status should be 200
   - Response should have: `{"rooms": [...], "total": N}`

---

### 4. **Response Format Mismatch**

**Our backend returns:**
```json
{
  "rooms": [...],
  "total": 10,
  "skip": 0,
  "limit": 100
}
```

**Frontend expects:** `response.rooms` ✅ (This is correct!)

**Verify in code:**
```typescript
// frontend/src/stores/roomStore.ts line 35-39
const response = await apiClient.getRooms();
set({
  rooms: response.rooms || [],  // ✅ Correct!
  isLoading: false,
});
```

---

### 5. **CORS Issues**

**Symptoms:**
- Console shows CORS errors
- Network requests fail with status 0 or "CORS policy" error

**Solution:**

Backend is configured with `CORS_ORIGINS=*` which allows all origins. If you see CORS errors:

1. Check backend logs
2. Verify environment variable is set in Cloud Run
3. May need to redeploy with explicit origin:
   ```bash
   gcloud run services update kos-backend \
     --region=asia-southeast1 \
     --update-env-vars="CORS_ORIGINS=https://kos-database-a5h0v5tot-claud0698s-projects.vercel.app"
   ```

---

### 6. **Cold Start Delays**

**Symptoms:**
- First request takes 10-30 seconds
- Subsequent requests are fast
- May see timeout errors

**Cause:** Cloud Run free tier scales to zero when idle

**Solutions:**
- Wait for cold start to complete (one-time per idle period)
- Keep service warm (costs money):
  ```bash
  gcloud run services update kos-backend \
    --region=asia-southeast1 \
    --min-instances=1  # Costs $$ but eliminates cold starts
  ```

---

## Quick Diagnostic Steps

### Step 1: Verify Backend is Running
```bash
curl https://kos-backend-228057609267.asia-southeast1.run.app/health
```
**Expected:** `{"status":"ok",...}`

### Step 2: Verify You Can Login
1. Go to: https://kos-database-a5h0v5tot-claud0698s-projects.vercel.app
2. Login with: `admin` / `admin123`
3. Should redirect to dashboard

### Step 3: Check Database
```bash
cd backend
source venv/bin/activate
python check_indexes.py
```
**Expected:** Shows all tables exist

### Step 4: Count Rooms in Database
```bash
python -c "
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Room
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
Session = sessionmaker(bind=engine)
db = Session()

count = db.query(Room).count()
print(f'Total rooms in database: {count}')

if count > 0:
    rooms = db.query(Room).limit(3).all()
    for room in rooms:
        print(f'  - {room.room_number}: {room.status}')
else:
    print('⚠️  Database has NO rooms - this is why frontend is empty!')
    print('   Solution: Add rooms using the UI or API')

db.close()
"
```

### Step 5: Test API Endpoint
Open in browser (will redirect to login):
https://kos-backend-228057609267.asia-southeast1.run.app/api/docs

Then test `/api/rooms` endpoint

---

## Most Common Solution

**If frontend shows 0 rooms:**

1. The database is probably empty
2. Add rooms via the UI:
   - Login to frontend
   - Click "Rooms" in sidebar
   - Click "Add Room" button
   - Fill form and save
3. Or use API Docs to POST new rooms

**This is normal for a fresh deployment!**

The database exists, tables are created, indexes are in place - it's just waiting for you to add data! 🎉

---

## Still Having Issues?

### Check These:

1. **Browser Console** - Any JavaScript errors?
2. **Network Tab** - Are API requests successful (200)?
3. **Backend Logs**:
   ```bash
   gcloud run services logs read kos-backend --region=asia-southeast1 --limit=50
   ```
4. **Database Connection** - Can you connect to Supabase?
5. **Environment Variables** - Are they set correctly in Cloud Run?

### Get Help:

1. Check `DEPLOYMENT_COMPLETE.md` for URLs and configuration
2. Check `FRONTEND_CHECKLIST.md` for frontend integration
3. Check `backend/PERFORMANCE_OPTIMIZATION_SUMMARY.md` for backend details

---

## Success Checklist

After adding data, you should see:

- ✅ Rooms list shows on frontend
- ✅ Room details display correctly
- ✅ Can create new rooms
- ✅ Can edit rooms
- ✅ Can delete rooms
- ✅ Dashboard shows room count
- ✅ Occupancy rate displays

**Everything is deployed correctly - just needs data!** 🚀
