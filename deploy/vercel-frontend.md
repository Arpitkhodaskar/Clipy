# Vercel Frontend Deployment

## 🚀 Deploy to Vercel (Recommended)

### Quick Deploy
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/clipvault)

### Manual Deployment Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import from GitHub
   - Select your ClipVault repository
   - Vercel auto-detects Vite configuration

3. **Configure Environment Variables**
   In Vercel dashboard → Settings → Environment Variables:
   ```
   VITE_API_URL=https://your-backend.railway.app
   VITE_FIREBASE_API_KEY=AIzaSyCCLV16V96DKpzHL1L5ek5n2iQhveIdDRk
   VITE_FIREBASE_AUTH_DOMAIN=clipbolt-d2bf3.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=clipbolt-d2bf3
   VITE_FIREBASE_STORAGE_BUCKET=clipbolt-d2bf3.appspot.com
   VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
   VITE_FIREBASE_APP_ID=your-app-id
   ```

4. **Deploy**
   - Click "Deploy"
   - Your app will be live at `https://your-project.vercel.app`

### Build Configuration

Vercel automatically detects:
- **Framework**: Vite
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

### Custom Domain (Optional)
1. Go to Vercel dashboard → Domains
2. Add your custom domain
3. Configure DNS records as instructed

## ✅ Verification

After deployment:
1. Visit your Vercel URL
2. Test login functionality
3. Verify API calls to backend
4. Check browser console for errors

## 🔧 Troubleshooting

### CORS Issues
If you get CORS errors:
1. Update backend CORS configuration
2. Add your Vercel domain to allowed origins
3. Redeploy backend

### Environment Variables
- Make sure all `VITE_` prefixed variables are set
- Variables are applied on next deployment
- Use Vercel CLI for local testing: `vercel dev`

### Build Errors
Common fixes:
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Update dependencies
npm update

# Check TypeScript errors
npm run type-check
```
