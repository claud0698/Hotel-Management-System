# Database Scripts

This folder contains all database-related scripts for the KOS Database application. Scripts are organized by category below.

## Table of Contents
- [Seeding Scripts](#seeding-scripts)
- [Migration Scripts](#migration-scripts)
- [Setup & Utility Scripts](#setup--utility-scripts)
- [Schema Modification Scripts](#schema-modification-scripts)

---

## Seeding Scripts

Scripts for populating the database with initial or test data.

### `seed.py`
Original seeding script that populates the database with initial test data.
```bash
python scripts/seed.py
```

### `seed_admin_user.py`
Creates an admin user in the database.
```bash
python scripts/seed_admin_user.py
```

### `seed_real_data.py`
Seeds the database with realistic production-like data for testing.
```bash
python scripts/seed_real_data.py
```

### `seed_rooms_simple.py`
Seeds the database with a simple set of rooms for basic testing.
```bash
python scripts/seed_rooms_simple.py
```

### `seed_july_2025.py`
Seeds the database with specific data for July 2025 (historical/demo data).
```bash
python scripts/seed_july_2025.py
```

---

## Migration Scripts

Scripts for migrating data between databases or updating database schemas.

### `migrate_sqlite_to_supabase.py`
Migrates data from SQLite database to Supabase PostgreSQL.
```bash
python scripts/migrate_sqlite_to_supabase.py
```

### `migrate_users_table.py`
Migrates the users table structure or data.
```bash
python scripts/migrate_users_table.py
```

### `migrate_users_postgresql.py`
Handles user table migration specifically for PostgreSQL/Supabase.
```bash
python scripts/migrate_users_postgresql.py
```

---

## Setup & Utility Scripts

Scripts for environment setup and testing connections.

### `create_admin.py`
Interactive script to create an admin user.
```bash
python scripts/create_admin.py
```

### `setup_supabase_env.py`
Sets up environment variables and configuration for Supabase.
```bash
python scripts/setup_supabase_env.py
```

### `test_supabase_connection.py`
Tests the connection to Supabase database.
```bash
python scripts/test_supabase_connection.py
```

### `wait_for_supabase.py`
Utility script that waits for Supabase to be ready (useful in Docker/CI environments).
```bash
python scripts/wait_for_supabase.py
```

---

## Schema Modification Scripts

Scripts that modify database schema (add columns, update structures, etc.).

### `add_level_column.py`
Adds a 'level' column to the database schema.
```bash
python scripts/add_level_column.py
```

### `fix_users_table.py`
Fixes issues with the users table structure.
```bash
python scripts/fix_users_table.py
```

### `update_floor_numbers.py`
Updates floor numbers in the database.
```bash
python scripts/update_floor_numbers.py
```

---

## Usage Notes

### Prerequisites
All scripts require:
- Python 3.12+
- Dependencies installed: `pip install -r requirements.txt`
- Proper environment variables set (`.env` file configured)

### Running Scripts
Scripts should be run from the `backend` directory:
```bash
cd backend
python scripts/<script_name>.py
```

### Environment Variables
Most scripts require database connection settings. Ensure your `.env` file contains:
- SQLite: `DATABASE_URL` or default SQLite path
- Supabase: `SUPABASE_DB_URL`, `SUPABASE_DIRECT_URL`, `SUPABASE_KEY`, etc.

### Important Notes
- Always backup your database before running migration scripts
- Seeding scripts may clear existing data - review scripts before running in production
- Some scripts are executable (`chmod +x`) and can be run directly: `./scripts/script_name.py`

---

## Script Categories Summary

| Category | Count | Purpose |
|----------|-------|---------|
| Seeding | 5 | Populate database with initial/test data |
| Migration | 3 | Move data between databases or update schemas |
| Setup/Utility | 4 | Environment setup and testing |
| Schema Modification | 3 | Alter database structure |

**Total Scripts:** 15
