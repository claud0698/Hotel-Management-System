# Architecture Documentation

This directory contains system architecture, design decisions, and technical overviews.

## Available Documents

### [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
High-level overview of the entire KOS Database system.

**Topics covered:**
- Project purpose and goals
- System architecture
- Technology stack
- Key features
- Development roadmap
- Team structure

---

### [DATABASE_OPTIONS.md](DATABASE_OPTIONS.md)
Analysis and comparison of database technology choices.

**Topics covered:**
- Database options (SQLite, PostgreSQL, Supabase)
- Pros and cons comparison
- Performance considerations
- Scalability analysis
- Migration strategies
- Recommendations

---

### [FRONTEND_SUMMARY.md](FRONTEND_SUMMARY.md)
Comprehensive frontend architecture documentation.

**Topics covered:**
- React application structure
- Component architecture
- State management
- Routing strategy
- API integration
- UI/UX patterns
- Styling approach

**See also:** [frontend/COMPONENTS.md](../../frontend/COMPONENTS.md) for detailed component documentation

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────┐
│              Frontend (React)                │
│  - TypeScript                                │
│  - Vite build system                         │
│  - TailwindCSS styling                       │
│  - React Router                              │
└─────────────────┬───────────────────────────┘
                  │ HTTP/REST API
┌─────────────────▼───────────────────────────┐
│            Backend (FastAPI)                 │
│  - Python 3.12+                              │
│  - JWT Authentication                        │
│  - SQLAlchemy ORM                            │
│  - Pydantic validation                       │
└─────────────────┬───────────────────────────┘
                  │ SQL
┌─────────────────▼───────────────────────────┐
│        Database (PostgreSQL/Supabase)        │
│  - PostgreSQL 15+                            │
│  - Row Level Security                        │
│  - Real-time capabilities                    │
└─────────────────────────────────────────────┘
```

---

## Key Design Decisions

### Backend Architecture
- **Framework**: FastAPI for high performance and automatic API documentation
- **ORM**: SQLAlchemy for database abstraction
- **Authentication**: JWT tokens for stateless authentication
- **Validation**: Pydantic for request/response validation

### Frontend Architecture
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development and optimized builds
- **Styling**: TailwindCSS for utility-first styling
- **State**: Component state + Context API (no Redux/Zustand needed)

### Database Architecture
- **Primary**: PostgreSQL for ACID compliance
- **Hosting**: Supabase for managed hosting + additional features
- **Migrations**: Handled via scripts (see [backend/scripts/](../../backend/scripts/))

---

## Data Models

### Core Entities
1. **Users** - System users with role-based access
2. **Rooms** - Boarding house rooms with details
3. **Tenants** - People renting rooms
4. **Payments** - Payment records and history
5. **Expenses** - Operating expenses tracking

### Relationships
```
Users (1) ─── (*) Tenants
Rooms (1) ─── (*) Tenants
Tenants (1) ─── (*) Payments
Users (1) ─── (*) Expenses
```

---

## Security Architecture

### Authentication Flow
1. User logs in with credentials
2. Backend validates and issues JWT token
3. Frontend stores token (localStorage)
4. Token sent with each API request
5. Backend validates token for protected routes

### Authorization
- **Admin**: Full access to all features
- **Manager**: Manage tenants, payments, rooms
- **Viewer**: Read-only access

---

## API Architecture

### RESTful Endpoints
- `GET /api/rooms` - List rooms
- `POST /api/tenants` - Create tenant
- `GET /api/payments` - Payment history
- `POST /api/auth/login` - User authentication

**See**: Backend code in `backend/routes/` for complete API

---

## Frontend Structure

```
frontend/src/
├── components/        # Reusable UI components
├── pages/            # Page components (routes)
├── services/         # API service layer
├── contexts/         # React contexts
├── locales/          # i18n translations
└── types/            # TypeScript type definitions
```

---

## Performance Considerations

### Backend
- Database connection pooling
- Query optimization with indexes
- Efficient SQLAlchemy queries
- Response caching where appropriate

### Frontend
- Code splitting by route
- Lazy loading components
- Optimized bundle size
- Image optimization

### Database
- Proper indexing strategy
- Query performance monitoring
- Connection pooling
- Supabase edge functions for low latency

---

## Scalability Strategy

### Current Scale
- Supports 100+ rooms
- 1000+ tenants
- Multiple concurrent users

### Future Scaling Options
1. **Vertical**: Upgrade database resources
2. **Horizontal**: Backend API scaling with load balancer
3. **Caching**: Add Redis for session/data caching
4. **CDN**: Frontend assets via CDN

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + TypeScript | UI framework |
| **Build** | Vite | Fast development & builds |
| **Styling** | TailwindCSS | Utility-first CSS |
| **Backend** | FastAPI (Python) | REST API server |
| **ORM** | SQLAlchemy | Database abstraction |
| **Database** | PostgreSQL | Data persistence |
| **Hosting** | Supabase | Managed database |
| **Auth** | JWT | Authentication |
| **Deployment** | Vercel + GCP | Cloud hosting |

---

## Related Documentation

- **Database Scripts**: [backend/scripts/README.md](../../backend/scripts/README.md)
- **Frontend Components**: [frontend/COMPONENTS.md](../../frontend/COMPONENTS.md)
- **Setup Guides**: [../setup/](../setup/)
- **Deployment**: [../deployment/](../deployment/)

---

## Need Help?

- Return to [main documentation](../README.md)
- Check [planning docs](../planning/) for requirements
- Review [features docs](../features/) for functionality details
