# Quick Start: Deploy to Vercel

This is a simplified guide for deploying the frontend to Vercel.

## Prerequisites

- GitHub account
- Vercel account (sign up at [vercel.com](https://vercel.com))
- This repository pushed to GitHub

## Step 1: Push to GitHub

If you haven't already:

```bash
# Initialize git (if not done)
git init
git add .
git commit -m "Initial commit"

# Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/kos-database.git
git push -u origin main
```

## Step 2: Deploy to Vercel

### Option A: Vercel Dashboard (Recommended)

1. Go to [vercel.com/new](https://vercel.com/new)
2. Click **"Import Project"**
3. Select your GitHub repository
4. Configure settings:
   - **Project Name**: `kos-management` (or your choice)
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

5. Add Environment Variable:
   - **Name**: `VITE_API_URL`
   - **Value**: `http://localhost:8001/api` (temporary, update after backend deployment)

6. Click **"Deploy"**

### Option B: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Navigate to frontend
cd frontend

# Deploy
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name: kos-management
# - Directory: ./ (already in frontend/)
# - Override settings? No
```

## Step 3: Get Your URL

After deployment, you'll receive a URL like:
```
https://kos-management-xyz123.vercel.app
```

## Step 4: Test the Frontend

1. Visit your Vercel URL
2. You should see the login page
3. **Note**: API calls will fail until you deploy the backend

## Step 5: Update Backend URL (After GCP Deployment)

Once you deploy the backend to GCP:

1. Go to Vercel Dashboard
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Edit `VITE_API_URL`
5. Set value to your GCP backend URL (e.g., `https://kos-backend-xyz.run.app/api`)
6. Click **Save**
7. Go to **Deployments** → **Redeploy** latest deployment

## Automatic Deployments

Every push to your `main` branch will trigger a new deployment automatically!

## Custom Domain (Optional)

1. Go to Project **Settings** → **Domains**
2. Click **"Add Domain"**
3. Enter your domain name
4. Follow DNS configuration instructions

## Environment Variables Reference

| Variable | Value | When to Set |
|----------|-------|-------------|
| `VITE_API_URL` | `http://localhost:8001/api` | Initial deployment |
| `VITE_API_URL` | `https://your-backend.run.app/api` | After backend deployed |

## Troubleshooting

**Build Fails:**
```bash
# Clear Vercel cache
vercel --force

# Or in dashboard: Deployments → Options → Clear Cache and Deploy
```

**API Not Working:**
- Check `VITE_API_URL` is set correctly
- Verify backend CORS allows your Vercel domain
- Check browser console for errors

**White Screen:**
- Check build logs in Vercel dashboard
- Verify all dependencies are in `package.json`
- Try local build: `npm run build && npm run preview`

## Next Steps

After frontend is deployed:
1. Deploy backend to GCP (see `DEPLOYMENT.md`)
2. Update `VITE_API_URL` in Vercel
3. Test the full application
4. (Optional) Set up custom domain

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [Vite Documentation](https://vitejs.dev/)
- Check `DEPLOYMENT.md` for full deployment guide
