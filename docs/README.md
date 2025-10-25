# KOS Database Documentation

Complete documentation for the KOS (Kost) Database Management System - a comprehensive solution for managing boarding house operations including room management, tenant tracking, payments, and expenses.

## Table of Contents

- [Quick Links](#quick-links)
- [Documentation Structure](#documentation-structure)
- [Getting Started](#getting-started)
- [Documentation Categories](#documentation-categories)

---

## Quick Links

- **Main README**: [../README.md](../README.md)
- **Quick Start Guide**: [setup/QUICK_START.md](setup/QUICK_START.md)
- **Backend Setup**: [setup/BACKEND_SETUP.md](setup/BACKEND_SETUP.md)
- **Frontend Setup**: [../frontend/README.md](../frontend/README.md)

---

## Documentation Structure

```
docs/
├── README.md                 # This file - Documentation index
├── setup/                    # Installation and setup guides
├── deployment/               # Deployment guides for various platforms
├── architecture/             # System design and architecture
├── features/                 # Feature documentation and enhancements
└── planning/                 # Project planning and requirements
```

---

## Getting Started

### For New Users
1. Start with [setup/QUICK_START.md](setup/QUICK_START.md)
2. Review the [Project Overview](architecture/PROJECT_OVERVIEW.md)
3. Follow [Backend Setup](setup/BACKEND_SETUP.md) or [Frontend Setup](../frontend/README.md)

### For Developers
1. Read the [Product Requirements Document](planning/PRD.md)
2. Check the [Frontend Components Guide](../frontend/COMPONENTS.md)
3. Review [Database Scripts Documentation](../backend/scripts/README.md)

### For Deployment
1. Choose your platform from [Deployment](#deployment)
2. Follow the relevant deployment guide
3. Configure environment variables as needed

---

## Documentation Categories

### 📚 Setup & Installation

Complete guides for setting up the development environment.

| Document | Description |
|----------|-------------|
| [QUICK_START.md](setup/QUICK_START.md) | Fast-track guide to get started quickly |
| [BACKEND_SETUP.md](setup/BACKEND_SETUP.md) | Detailed backend setup instructions |
| [SUPABASE_SETUP.md](setup/SUPABASE_SETUP.md) | Supabase database configuration guide |
| [SUPABASE_SINGAPORE_SETUP.md](setup/SUPABASE_SINGAPORE_SETUP.md) | Singapore region-specific setup |
| [AUTH_README.md](setup/AUTH_README.md) | Authentication system documentation |

**Frontend Setup:** See [frontend/README.md](../frontend/README.md)

---

### 🚀 Deployment

Step-by-step guides for deploying to various platforms.

| Document | Description |
|----------|-------------|
| [DEPLOYMENT.md](deployment/DEPLOYMENT.md) | General deployment overview |
| [DEPLOYMENT_STACK.md](deployment/DEPLOYMENT_STACK.md) | Technology stack and deployment options |
| [GCP_DEPLOYMENT.md](deployment/GCP_DEPLOYMENT.md) | Google Cloud Platform deployment guide |
| [GCP_CLOUD_RUN_DEPLOY.md](deployment/GCP_CLOUD_RUN_DEPLOY.md) | Specific Cloud Run deployment steps |
| [VERCEL_DEPLOY.md](deployment/VERCEL_DEPLOY.md) | Vercel frontend deployment guide |
| [FRONTEND_HOSTING.md](deployment/FRONTEND_HOSTING.md) | Frontend hosting options and setup |

---

### 🏗️ Architecture & Design

System architecture, design decisions, and technical overviews.

| Document | Description |
|----------|-------------|
| [PROJECT_OVERVIEW.md](architecture/PROJECT_OVERVIEW.md) | High-level project overview |
| [DATABASE_OPTIONS.md](architecture/DATABASE_OPTIONS.md) | Database technology comparisons |
| [FRONTEND_SUMMARY.md](architecture/FRONTEND_SUMMARY.md) | Frontend architecture and structure |

**Component Documentation:** See [frontend/COMPONENTS.md](../frontend/COMPONENTS.md)

---

### ✨ Features & Enhancements

Documentation for features, improvements, and known issues.

| Document | Description |
|----------|-------------|
| [FUTURE_FEATURES.md](features/FUTURE_FEATURES.md) | Planned features and roadmap |
| [MANUAL_PAYMENT_SYSTEM.md](features/MANUAL_PAYMENT_SYSTEM.md) | Payment system documentation |
| [BACKEND_ENHANCEMENTS.md](features/BACKEND_ENHANCEMENTS.md) | Backend improvements and updates |
| [IMPLEMENTATION_COMPLETE.md](features/IMPLEMENTATION_COMPLETE.md) | Completed implementation notes |
| [TOKEN_EXPIRATION.md](features/TOKEN_EXPIRATION.md) | Token management and expiration handling |

---

### 📋 Planning & Requirements

Project planning documents, requirements, and task breakdowns.

| Document | Description |
|----------|-------------|
| [PRD.md](planning/PRD.md) | Product Requirements Document |
| [TASKS_BREAKDOWN.md](planning/TASKS_BREAKDOWN.md) | Detailed task breakdown and tracking |

---

## Additional Resources

### Backend Resources
- **Database Scripts**: [backend/scripts/README.md](../backend/scripts/README.md)
- **API Routes**: See backend route files in `backend/routes/`

### Frontend Resources
- **Setup Guide**: [frontend/SETUP.md](../frontend/SETUP.md)
- **Components**: [frontend/COMPONENTS.md](../frontend/COMPONENTS.md)
- **Main README**: [frontend/README.md](../frontend/README.md)

### Development Tools
- **Claude Agents**: `.claude/agents/` - AI agent configurations
- **Git Workflows**: See `.github/` for CI/CD configurations

---

## Documentation Categories at a Glance

| Category | Files | Purpose |
|----------|-------|---------|
| **Setup** | 5 docs | Get the system running locally |
| **Deployment** | 6 docs | Deploy to production platforms |
| **Architecture** | 3 docs | Understand system design |
| **Features** | 5 docs | Feature documentation |
| **Planning** | 2 docs | Requirements and roadmap |

**Total Documentation Files:** 21+ markdown files

---

## Contributing to Documentation

When adding new documentation:
1. Place it in the appropriate category folder
2. Update this README.md with a link
3. Use clear, descriptive filenames
4. Include a table of contents for longer documents
5. Cross-reference related documentation

---

## Need Help?

- **Project Issues**: Check the main [README.md](../README.md)
- **Quick Start Problems**: See [setup/QUICK_START.md](setup/QUICK_START.md)
- **Deployment Issues**: Review the relevant deployment guide
- **Feature Requests**: See [features/FUTURE_FEATURES.md](features/FUTURE_FEATURES.md)

---

**Last Updated:** October 26, 2025
**Documentation Version:** 1.0
