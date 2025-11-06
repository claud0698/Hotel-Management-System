# Kos Management System - Frontend

Modern React + TypeScript frontend for the Kos Management System, built with Vite and deployed on Vercel.

## Production Deployment

**Frontend URL:** *(Deploy to Vercel and add URL here)*
**Backend API:** https://kos-backend-228057609267.asia-southeast1.run.app/api
**Status:** Ready for deployment

## Tech Stack

- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios
- **State Management:** React Context API
- **Routing:** React Router v6
- **Deployment:** Vercel

## Quick Start

### Prerequisites
- Node.js 18+
- npm or yarn
- Backend API running (see [backend README](../backend/README.md))

### Local Development

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env`:
```env
VITE_API_URL=http://localhost:8001/api
VITE_APP_ENV=development
```

3. Start development server:
```bash
npm run dev
```

The app will be available at http://localhost:5173

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Deploy to Vercel

### Option 1: Deploy via Vercel CLI

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel --prod
```

### Option 2: Deploy via Vercel Dashboard

1. Push your code to GitHub/GitLab/Bitbucket

2. Go to [vercel.com](https://vercel.com)

3. Click "Add New Project"

4. Import your repository

5. Configure project:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`

6. Add Environment Variables:
   ```
   VITE_API_URL=https://kos-backend-228057609267.asia-southeast1.run.app/api
   ```

7. Click "Deploy"

### Environment Variables on Vercel

Go to your project settings on Vercel → Environment Variables:

| Variable | Value | Environment |
|----------|-------|-------------|
| `VITE_API_URL` | `https://kos-backend-228057609267.asia-southeast1.run.app/api` | Production |

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── auth/        # Authentication components
│   │   ├── dashboard/   # Dashboard components
│   │   ├── rooms/       # Room management
│   │   ├── tenants/     # Tenant management
│   │   └── payments/    # Payment management
│   ├── contexts/        # React Context providers
│   ├── hooks/           # Custom React hooks
│   ├── services/        # API service layer
│   │   └── api.ts      # Axios instance & API calls
│   ├── types/           # TypeScript type definitions
│   ├── utils/           # Utility functions
│   ├── App.tsx          # Main App component
│   └── main.tsx         # Entry point
├── public/              # Static assets
├── dist/                # Build output (generated)
├── .env                 # Local environment variables
├── .env.production      # Production environment variables
├── package.json         # Dependencies
├── tsconfig.json        # TypeScript config
├── vite.config.ts       # Vite config
└── vercel.json          # Vercel config
```

## API Integration

### API Service Configuration

The frontend uses Axios for API calls. Configuration is in `src/services/api.ts`:

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add authentication token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### Example API Calls

```typescript
// Login
const response = await api.post('/auth/login', {
  username: 'admin',
  password: 'admin'
});
localStorage.setItem('token', response.data.access_token);

// Get rooms
const rooms = await api.get('/rooms');

// Create room
const newRoom = await api.post('/rooms', {
  room_number: 'A1',
  floor: 1,
  room_type: 'single',
  monthly_rate: 700000,
  status: 'available',
  amenities: 'WiFi, AC, Bed'
});

// Update room
await api.put(`/rooms/${roomId}`, updateData);

// Delete room
await api.delete(`/rooms/${roomId}`);
```

## Features

### Authentication
- ✅ User login/logout
- ✅ JWT token management
- ✅ Protected routes
- ✅ Auto-refresh token

### Dashboard
- ✅ Statistics overview
- ✅ Occupancy rate
- ✅ Revenue tracking
- ✅ Recent activities

### Room Management
- ✅ List all rooms
- ✅ Create new room
- ✅ Update room details
- ✅ Delete room
- ✅ Filter by status/floor
- ✅ Room availability tracking

### Tenant Management
- ✅ List all tenants
- ✅ Add new tenant
- ✅ Update tenant info
- ✅ Move tenant in/out
- ✅ View tenant history
- ✅ Search tenants

### Payment Management
- ✅ Record payments
- ✅ View payment history
- ✅ Filter by date/status
- ✅ Payment reminders
- ✅ Overdue tracking

## Configuration Files

### vercel.json
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "env": {
    "VITE_API_URL": "https://kos-backend-228057609267.asia-southeast1.run.app/api"
  }
}
```

### vite.config.ts
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      }
    }
  }
})
```

## Styling

### Tailwind CSS

The project uses Tailwind CSS for styling:

```typescript
// Example component
export default function RoomCard({ room }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <h3 className="text-xl font-semibold text-gray-800">
        Room {room.room_number}
      </h3>
      <p className="text-gray-600 mt-2">
        Rp {room.monthly_rate.toLocaleString()}
      </p>
      <span className={`inline-block px-3 py-1 rounded-full text-sm ${
        room.status === 'available'
          ? 'bg-green-100 text-green-800'
          : 'bg-red-100 text-red-800'
      }`}>
        {room.status}
      </span>
    </div>
  );
}
```

## Development

### Running Tests
```bash
npm run test
```

### Linting
```bash
npm run lint
```

### Type Checking
```bash
npm run type-check
```

### Format Code
```bash
npm run format
```

## Environment Variables

### Development (.env)
```env
VITE_API_URL=http://localhost:8001/api
VITE_APP_ENV=development
```

### Production (.env.production)
```env
VITE_API_URL=https://kos-backend-228057609267.asia-southeast1.run.app/api
VITE_APP_ENV=production
```

## Backend Connection

The frontend connects to the GCP Cloud Run backend:

- **Backend URL:** https://kos-backend-228057609267.asia-southeast1.run.app
- **API Base:** https://kos-backend-228057609267.asia-southeast1.run.app/api
- **Health Check:** https://kos-backend-228057609267.asia-southeast1.run.app/health

### CORS Configuration

The backend is configured to accept requests from your Vercel frontend. If you encounter CORS errors:

1. Update backend CORS_ORIGINS in GCP Cloud Run:
```bash
gcloud run services update kos-backend \
  --region asia-southeast1 \
  --update-env-vars="CORS_ORIGINS=https://your-vercel-app.vercel.app"
```

2. Or allow all origins for testing (not recommended for production):
```bash
--update-env-vars="CORS_ORIGINS=*"
```

## Performance Optimization

### Build Optimization
- ✅ Code splitting
- ✅ Tree shaking
- ✅ Asset optimization
- ✅ Lazy loading
- ✅ Gzip compression (Vercel)
- ✅ CDN delivery (Vercel)

### Runtime Optimization
- ✅ React.memo for expensive components
- ✅ useMemo/useCallback hooks
- ✅ Virtualized lists for large data
- ✅ Debounced search
- ✅ Optimistic UI updates

## Troubleshooting

### Issue: API calls fail with CORS error
**Solution:** Update backend CORS_ORIGINS to include your Vercel domain

### Issue: Authentication not working
**Solution:** Check that token is stored in localStorage and added to request headers

### Issue: Build fails on Vercel
**Solution:**
1. Check Node.js version matches local (18+)
2. Verify all dependencies in package.json
3. Check build logs for specific errors

### Issue: Environment variables not working
**Solution:**
1. Ensure variables start with `VITE_`
2. Redeploy after adding env vars in Vercel
3. Access with `import.meta.env.VITE_VAR_NAME`

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Create feature branch
2. Make changes
3. Test locally
4. Submit pull request

## Documentation

- [Component Documentation](./COMPONENTS.md)
- [Setup Guide](./SETUP.md)
- [Backend API Documentation](../backend/README.md)

## Deployment Checklist

Before deploying to production:

- [ ] Update API URL in .env.production
- [ ] Test all features locally
- [ ] Run build and check for errors
- [ ] Configure Vercel environment variables
- [ ] Update backend CORS settings
- [ ] Test authentication flow
- [ ] Verify API connectivity
- [ ] Check responsive design
- [ ] Test on multiple browsers
- [ ] Set up error tracking (optional)

## Support

For issues and questions:
- Backend issues: See [backend README](../backend/README.md)
- Frontend issues: Open issue in repository

## License

MIT License

---

**Last Updated:** 2025-11-06
**Version:** 1.0.0
**Deployment Platform:** Vercel
**Backend API:** GCP Cloud Run
