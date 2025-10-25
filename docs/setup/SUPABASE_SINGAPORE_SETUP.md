# Create Supabase Project in Singapore - Step by Step Guide

## Step 1: Go to Supabase Dashboard

1. Open your browser
2. Go to: **https://supabase.com**
3. Click **"Sign In"** (top right)
4. Sign in with GitHub, Google, or email

---

## Step 2: Create New Project

Once you're logged in:

1. You'll see the Supabase Dashboard
2. Click the **"New project"** button (green button, usually at top)
   - If you're in an organization, make sure you're in the right one
   - Or click **"All projects"** first, then **"New project"**

---

## Step 3: Fill in Project Details

You'll see a form with these fields:

### Project Name
```
kos-dashboard
```
(You can use any name you like)

### Database Password
This is VERY IMPORTANT!

1. Click the **"Generate a password"** button
2. **COPY THE PASSWORD** and save it somewhere safe (Notes app, password manager, etc.)
3. You'll need this password later!

Example password (yours will be different):
```
MySuper$ecureP@ssw0rd123!
```

### Region
**This is the important part!**

1. Click the **Region dropdown**
2. Scroll down and select:
   ```
   Southeast Asia (Singapore)
   ```

   Other options you'll see:
   - ❌ Northeast Asia (Tokyo) - Don't select this
   - ❌ Northeast Asia (Seoul) - Don't select this
   - ✅ **Southeast Asia (Singapore)** - SELECT THIS ONE!
   - ❌ South Asia (Mumbai) - Don't select this

### Pricing Plan
```
Free
```
(Should be selected by default)

---

## Step 4: Create the Project

1. Click **"Create new project"** button at the bottom
2. Wait 2-3 minutes (you'll see a loading screen)
3. ☕ Grab a coffee while it sets up!

---

## Step 5: Get Your Connection String

Once the project is created (you'll see a dashboard):

### Method A: Quick Way

1. Look for **"Project Settings"** in the left sidebar (⚙️ gear icon)
2. Click **"Database"**
3. Scroll down to find **"Connection string"** section
4. You'll see several tabs:
   - URI
   - Session mode
   - Transaction mode
5. Click the **"URI"** tab
6. You'll see something like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.abcdefghijklmnop.supabase.co:5432/postgres
   ```

### Method B: From API Settings

1. Click **"Project Settings"** (⚙️ in sidebar)
2. Click **"API"**
3. Scroll to **"Project URL"** - you'll see your project reference

---

## Step 6: Complete Your Connection String

The connection string you copied has `[YOUR-PASSWORD]` in it.

**Replace `[YOUR-PASSWORD]` with the actual password you saved in Step 3!**

Example:

**Before:**
```
postgresql://postgres:[YOUR-PASSWORD]@db.abcdefghijklmnop.supabase.co:5432/postgres
```

**After** (using the example password from Step 3):
```
postgresql://postgres:MySuper$ecureP@ssw0rd123!@db.abcdefghijklmnop.supabase.co:5432/postgres
```

---

## Step 7: Give Me the Connection String

Copy your complete connection string (with the real password) and paste it in the chat.

I will:
1. ✅ Update your `.env` file
2. ✅ Convert it to the right format for SQLAlchemy
3. ✅ Test the connection
4. ✅ Create all database tables
5. ✅ Migrate your SQLite data to Supabase
6. ✅ Verify everything works

---

## 🎯 What You Need to Copy & Paste to Me

Just the connection string that looks like this:
```
postgresql://postgres:YOUR_ACTUAL_PASSWORD@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
```

---

## 🆘 Troubleshooting

### Can't find "New Project" button?
- Make sure you're logged in
- Look at the top of the dashboard
- Or click "All projects" first

### Don't see Singapore in the region list?
- It should be there as "Southeast Asia (Singapore)"
- Make sure you're scrolling through all options
- It might be listed as "ap-southeast-1"

### Forgot to save the password?
- You can reset it later in Settings → Database → Reset database password
- But it's easier to save it now!

### Project is taking too long to create?
- It usually takes 2-3 minutes
- If it takes more than 5 minutes, refresh the page
- The project might already be created

---

## 📸 Visual Reference

Your dashboard will look something like this:

```
┌─────────────────────────────────────────────────────────────┐
│  Supabase Dashboard                                    [⚙️]  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [+ New project]                                            │
│                                                              │
│  Your Projects:                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  kos-dashboard                                       │  │
│  │  Southeast Asia (Singapore)                          │  │
│  │  Active                                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist

- [ ] Opened https://supabase.com
- [ ] Signed in
- [ ] Clicked "New project"
- [ ] Named the project: `kos-dashboard`
- [ ] Generated and SAVED the database password
- [ ] Selected Region: **Southeast Asia (Singapore)**
- [ ] Clicked "Create new project"
- [ ] Waited for project to be created
- [ ] Went to Settings → Database
- [ ] Copied the URI connection string
- [ ] Replaced [YOUR-PASSWORD] with actual password
- [ ] Ready to paste the connection string!

---

**Once you have the connection string, just paste it in the chat and I'll take care of the rest!** 🚀
