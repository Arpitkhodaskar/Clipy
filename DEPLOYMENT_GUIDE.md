# ClipVault Deployment Guide

## 🚀 Free Deployment Options

### Option 1: Vercel + Railway + Firebase (Recommended)
- **Frontend**: Vercel
- **Backend**: Railway
- **Database**: Firebase (already configured)
- **Cost**: Free with generous limits

### Option 2: Netlify + Render + Firebase
- **Frontend**: Netlify
- **Backend**: Render
- **Database**: Firebase
- **Cost**: Free with good limits

## 📋 Prerequisites

1. GitHub account
2. Firebase project (already set up)
3. Environment variables ready

## 🔧 Deployment Steps

### Step 1: Prepare Repository
```bash
# Push your code to GitHub if not already done
git init
git add .
git commit -m "Initial commit for deployment"
git branch -M main
git remote add origin https://github.com/yourusername/clipvault.git
git push -u origin main
```

### Step 2: Frontend Deployment (Vercel)

1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Import your repository
4. Vercel will auto-detect Vite configuration
5. Add environment variables in Vercel dashboard:
   ```
   VITE_API_URL=https://your-backend-url.railway.app
   VITE_FIREBASE_API_KEY=your-firebase-api-key
   VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=your-project-id
   ```

### Step 3: Backend Deployment (Railway)

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Create new project from GitHub repo
4. Select backend folder
5. Add environment variables:
   ```
   FIREBASE_PROJECT_ID=clipbolt-d2bf3
   GOOGLE_APPLICATION_CREDENTIALS=/app/firebase-service-account-key.json
   REDIS_URL=redis://localhost:6379
   SECRET_KEY=your-super-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

### Step 4: Alternative Backend (Render)

1. Go to [render.com](https://render.com)
2. Connect GitHub account
3. Create new Web Service
4. Point to your backend folder
5. Configure build and start commands

## 🆓 Free Tier Limits

### Vercel
- 100GB bandwidth/month
- 100 deployments/day
- Custom domains included
- Serverless functions

### Railway
- $5 credit/month (covers ~500 hours)
- 1GB RAM, 1vCPU
- 5GB storage
- Custom domains

### Render
- 750 hours/month
- Auto-sleep after 15min inactivity
- 512MB RAM
- Custom domains

### Firebase
- 1GB storage
- 10GB/month bandwidth
- 50K reads/day, 20K writes/day
- 20K deletes/day

## 🔒 Security Notes

- Use environment variables for all secrets
- Enable CORS for your frontend domain
- Set up proper Firestore security rules
- Use HTTPS only in production

## 🚀 Quick Deploy Commands

See individual deployment files for specific commands and configurations.
