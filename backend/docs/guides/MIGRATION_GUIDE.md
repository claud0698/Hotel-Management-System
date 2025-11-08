# Database Migration Guide

**Purpose**: Complete guide for setting up and managing database migrations with Alembic

**Last Updated**: November 8, 2025

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Setup & Installation](#setup--installation)
3. [Creating Migrations](#creating-migrations)
4. [Running Migrations](#running-migrations)
5. [Migration Best Practices](#migration-best-practices)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Topics](#advanced-topics)

---

## Quick Start

### One-Time Setup
```bash
# 1. Install Alembic (already in requirements.txt)
pip install alembic

# 2. Initialize Alembic in project
alembic init migrations

# 3. Configure database connection in migrations/env.py
# Edit alembic.ini and set: sqlalchemy.url = postgresql://user:password@localhost/hotel_db

# 4. Create initial migration from current models
alembic revision --autogenerate -m "Initial schema"

# 5. Apply migration to database
alembic upgrade head
```

### Regular Development
```bash
# When you modify models.py:
alembic revision --autogenerate -m "descriptive message"
alembic upgrade head

# To check migration status:
alembic current
alembic branches
alembic history
```

---

## Setup & Installation

### 1. Prerequisites

Ensure you have:
- Python 3.8+
- PostgreSQL (or SQLite for development)
- SQLAlchemy installed (`pip install sqlalchemy`)
- Alembic installed (`pip install alembic`)

All are in `requirements.txt`:
```
sqlalchemy==2.0.x
alembic==1.12.x
psycopg2-binary==2.9.x  # For PostgreSQL
```

### 2. Initialize Alembic

```bash
cd backend
alembic init migrations
```

This creates:
```
migrations/
├── alembic.ini              # Configuration file
├── env.py                   # Migration environment setup
├── script.py.mako           # Migration template
├── versions/                # Actual migration files
└── README
```

### 3. Configure Connection

Edit `alembic.ini`:
```ini
# Development (SQLite)
sqlalchemy.url = sqlite:///./test.db

# Production (PostgreSQL)
sqlalchemy.url = postgresql://user:password@localhost:5432/hotel_db
```

Or set via environment variable:
```bash
# In your .env file
DATABASE_URL=postgresql://user:password@localhost:5432/hotel_db

# In migrations/env.py
database_url = os.getenv('DATABASE_URL', 'sqlite:///./test.db')
configuration.set_main_option('sqlalchemy.url', database_url)
```

### 4. Configure env.py

Edit `migrations/env.py` to use your SQLAlchemy models:

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import your models
from models import Base

config = context.config
fileConfig(config.config_file_name)

# Set target_metadata for autogenerate
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost/hotel_db'
    )

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

## Creating Migrations

### Automatic Migration (Recommended)

When you modify `models.py`, Alembic can auto-generate the migration:

```bash
alembic revision --autogenerate -m "Add deposit_amount to reservations"
```

Alembic compares your models with the current database schema and creates SQL to match.

**Supported Operations:**
- ✅ Add columns
- ✅ Remove columns
- ✅ Change column types
- ✅ Add/remove constraints
- ✅ Add/remove indexes
- ✅ Add/remove foreign keys
- ✅ Rename columns/tables

**Not Supported (Manual):**
- ❌ Column renames (autogenerate detects as add + drop)
- ❌ Complex data transformations
- ❌ Custom SQL logic

### Manual Migration

For complex changes, create manual migrations:

```bash
alembic revision -m "Complex data transformation"
```

Edit `migrations/versions/xxxxx_complex_data_transformation.py`:

```python
"""Complex data transformation

Revision ID: xxxxx
Revises: yyyyy
Create Date: 2025-11-08 12:00:00

"""
from alembic import op
import sqlalchemy as sa

revision = 'xxxxx'
down_revision = 'yyyyy'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Apply migration"""
    # Add new column
    op.add_column('reservations', sa.Column('new_field', sa.String(100)))

    # Populate data
    op.execute("""
        UPDATE reservations
        SET new_field = 'default_value'
    """)

    # Make not nullable
    op.alter_column('reservations', 'new_field', nullable=False)

def downgrade() -> None:
    """Revert migration"""
    op.drop_column('reservations', 'new_field')
```

### Examples for Hotel Management System

#### Example 1: Add Deposit System

```bash
alembic revision --autogenerate -m "Add deposit system to reservations"
```

Auto-generated migration:
```python
def upgrade() -> None:
    op.add_column('reservations',
        sa.Column('deposit_amount', sa.Numeric(12, 2), nullable=False, server_default='0'))
    op.add_column('reservations',
        sa.Column('deposit_returned_at', sa.DateTime(), nullable=True))

def downgrade() -> None:
    op.drop_column('reservations', 'deposit_returned_at')
    op.drop_column('reservations', 'deposit_amount')
```

#### Example 2: Add Payment Type Field

```bash
alembic revision --autogenerate -m "Add payment_type to payments"
```

Auto-generated:
```python
def upgrade() -> None:
    op.add_column('payments',
        sa.Column('payment_type', sa.String(20), nullable=False, server_default='full'))

def downgrade() -> None:
    op.drop_column('payments', 'payment_type')
```

#### Example 3: Rename Column

For renames, create manual migration:

```bash
alembic revision -m "Rename checked_in_by_name to receptionist_name"
```

```python
def upgrade() -> None:
    op.alter_column('reservations',
        existing_column_name='checked_in_by_name',
        new_column_name='receptionist_name')

def downgrade() -> None:
    op.alter_column('reservations',
        existing_column_name='receptionist_name',
        new_column_name='checked_in_by_name')
```

---

## Running Migrations

### Apply Latest Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific number of migrations
alembic upgrade +1      # Apply next 1 migration
alembic upgrade +2      # Apply next 2 migrations
```

### Check Migration Status

```bash
# Show current revision
alembic current
# Output: 1a2b3c4d5e6f (head)

# Show migration history
alembic history
# Output:
# <base> -> 1a2b3c4d, Initial schema
# 1a2b3c4d -> 2b3c4d5e, Add deposit system
# 2b3c4d5e -> 3c4d5e6f, Add payment type
# 3c4d5e6f -> <head>

# Show branches
alembic branches
```

### Rollback Migrations

```bash
# Rollback to specific revision
alembic downgrade 1a2b3c4d

# Rollback one step
alembic downgrade -1

# Rollback all migrations
alembic downgrade base
```

### Offline Mode (Generate SQL without executing)

```bash
# Generate migration SQL without applying
alembic upgrade head --sql

# Generate rollback SQL
alembic downgrade -1 --sql
```

---

## Migration Best Practices

### 1. Commit Migrations with Code Changes

When you modify `models.py`, always create and commit the migration:

```bash
# Modify models.py
nano models.py

# Create migration
alembic revision --autogenerate -m "Add field to model"

# Review generated migration
cat migrations/versions/xxxxx_add_field_to_model.py

# Commit both
git add models.py migrations/versions/xxxxx_add_field_to_model.py
git commit -m "feat: Add new field with migration"
```

### 2. Review Auto-Generated Migrations

Always review auto-generated migrations before running:

```bash
# View migration without applying
alembic upgrade head --sql

# Check what will change
cat migrations/versions/xxxxx_xxxxx.py

# Only apply if correct
alembic upgrade head
```

### 3. Use Meaningful Messages

```bash
# Good ✅
alembic revision --autogenerate -m "Add deposit system with settlement tracking"
alembic revision --autogenerate -m "Add payment type field for transaction categorization"
alembic revision --autogenerate -m "Add receptionist tracking to check-in"

# Bad ❌
alembic revision --autogenerate -m "Update"
alembic revision --autogenerate -m "Changes"
```

### 4. Handle Data Migrations

When modifying existing data, use manual migrations:

```python
def upgrade() -> None:
    # Add new column with default
    op.add_column('reservations',
        sa.Column('new_status', sa.String(20), nullable=False, server_default='pending'))

    # Migrate existing data
    op.execute("""
        UPDATE reservations
        SET new_status = CASE
            WHEN status = 'old_confirmed' THEN 'confirmed'
            WHEN status = 'old_checked_in' THEN 'checked_in'
            ELSE 'pending'
        END
    """)

    # Remove default after data migration
    op.alter_column('reservations', 'new_status', server_default=None)

    # Drop old column
    op.drop_column('reservations', 'status')
```

### 5. Test Migrations

```bash
# Development: Test on SQLite
DATABASE_URL=sqlite:///test_migrations.db alembic upgrade head

# Staging: Test on PostgreSQL
DATABASE_URL=postgresql://user:password@staging-db/hotel_db alembic upgrade head

# Verify rollback works
alembic downgrade -1
alembic upgrade head
```

### 6. Dependencies Between Migrations

Create explicit dependencies:

```python
# If migration B depends on A
revision = 'xxxxx'
down_revision = 'yyyyy'  # Explicitly set parent migration
depends_on = None

# If migration needs another branch first
depends_on = ('other_branch_migration_id',)
```

---

## Troubleshooting

### Problem: "Target database is not up to date"

```bash
# Cause: Alembic head doesn't match database
# Solution 1: Check current database revision
alembic current

# Solution 2: View pending migrations
alembic upgrade head --sql

# Solution 3: Apply pending migrations
alembic upgrade head
```

### Problem: "Can't locate revision"

```bash
# Cause: Migration file missing or corrupted
# Solution: Check migration directory
ls -la migrations/versions/

# Check alembic history
alembic history

# If file is missing, recreate from version control
git checkout migrations/versions/xxxxx.py
```

### Problem: "UNIQUE constraint failed"

```bash
# Cause: Adding NOT NULL column without default to non-empty table
# Solution: Add default value during migration

def upgrade() -> None:
    # Add with server default
    op.add_column('table_name',
        sa.Column('new_column', sa.String(100),
                 nullable=False, server_default='default_value'))

    # Populate existing rows
    op.execute("UPDATE table_name SET new_column = 'default_value' WHERE new_column IS NULL")

    # Remove server default
    op.alter_column('table_name', 'new_column', server_default=None)
```

### Problem: "Foreign key constraint failed"

```bash
# Cause: Migration violates foreign key constraints
# Solution: Disable constraints during migration (PostgreSQL)

def upgrade() -> None:
    # Disable constraints
    op.execute('SET CONSTRAINTS ALL DEFERRED')

    # Your migration steps
    op.add_column('reservations', sa.Column('guest_id', sa.Integer))

    # Re-enable constraints
    op.execute('SET CONSTRAINTS ALL IMMEDIATE')

def downgrade() -> None:
    # Similar pattern for downgrade
    op.execute('SET CONSTRAINTS ALL DEFERRED')
    op.drop_column('reservations', 'guest_id')
    op.execute('SET CONSTRAINTS ALL IMMEDIATE')
```

### Problem: "Circular dependency in migrations"

```bash
# Cause: Migration A depends on B, and B depends on A
# Solution: Check migration structure
alembic branches

# Identify the cycle and adjust down_revision values
# Ensure: Migration 1 <- 2 <- 3 (linear chain, no cycles)
```

---

## Advanced Topics

### 1. Branching (Multiple Development Paths)

```bash
# Create migration in feature branch
git checkout -b feature/new-feature
alembic revision --autogenerate -m "Add feature X"

# Later, merge and resolve if conflicts
git checkout main
git merge feature/new-feature

# If migrations conflict:
alembic branches  # See the branch point
# Edit the newer migration's down_revision to point to the older one's revision
```

### 2. Zero-Downtime Migrations

For production with running services:

```python
def upgrade() -> None:
    # Step 1: Add column as nullable (no locks)
    op.add_column('large_table',
        sa.Column('new_column', sa.String(100), nullable=True))

    # Step 2: In separate migration, backfill data
    # (Can run in background job)

    # Step 3: In another migration, make NOT NULL
    # op.alter_column('large_table', 'new_column', nullable=False)

def downgrade() -> None:
    op.drop_column('large_table', 'new_column')
```

### 3. Environment-Specific Migrations

```bash
# Create separate migration configs
cp migrations/env.py migrations/env_production.py
cp alembic.ini alembic_production.ini

# Use specific config
alembic -c alembic_production.ini upgrade head
alembic -c alembic.ini upgrade head
```

### 4. Automated Migrations in CI/CD

```bash
# In your GitHub Actions / GitLab CI workflow
- name: Run database migrations
  run: |
    alembic upgrade head

- name: Verify migration success
  run: |
    alembic current
```

### 5. Migration Statistics

```bash
# Count total migrations
ls migrations/versions | wc -l

# Show size of migrations directory
du -sh migrations/

# List largest migrations
ls -lSh migrations/versions | head -5
```

---

## Integration with Hotel Management System

### Current System Models

The system currently has these main models (no migrations yet):
- User
- RoomType
- Room
- Guest
- Reservation (with deposit_amount, payment_type)
- Payment
- Dashboard metrics

### Initial Migration Setup

```bash
# 1. Initialize Alembic
alembic init migrations

# 2. Configure env.py to import models
# (See "Configure env.py" section above)

# 3. Create initial migration
alembic revision --autogenerate -m "Initial schema - all models"

# 4. Review generated migration
cat migrations/versions/xxxx_initial_schema.py

# 5. Apply to database
alembic upgrade head

# 6. Verify
alembic current
```

### Ongoing Development

When modifying models:

```bash
# 1. Edit models.py
# 2. Create migration
alembic revision --autogenerate -m "Descriptive message"

# 3. Review
cat migrations/versions/xxxx_descriptive_message.py

# 4. Apply
alembic upgrade head

# 5. Commit
git add models.py migrations/versions/xxxx_*.py
git commit -m "feat: Meaningful change with migration"
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `alembic init migrations` | Initialize Alembic |
| `alembic revision --autogenerate -m "msg"` | Create auto migration |
| `alembic revision -m "msg"` | Create manual migration |
| `alembic upgrade head` | Apply all pending migrations |
| `alembic downgrade -1` | Rollback one migration |
| `alembic current` | Show current database revision |
| `alembic history` | Show all migrations |
| `alembic branches` | Show migration branches |
| `alembic upgrade head --sql` | Show SQL without applying |

---

## Related Documentation

- [ERROR_HANDLING_GUIDE.md](ERROR_HANDLING_GUIDE.md) - Handle migration errors
- [VALIDATION_GUIDE.md](VALIDATION_GUIDE.md) - Validate schema changes
- [QUICK_REFERENCE.md](../references/QUICK_REFERENCE.md) - Quick lookup for database

---

**Last Updated**: November 8, 2025
**Status**: Ready for Phase 9
**Next**: Deploy migrations to production
