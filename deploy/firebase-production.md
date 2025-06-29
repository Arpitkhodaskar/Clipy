# Firebase Production Setup

## 🔥 Firebase Configuration for Production

Your Firebase is already set up, but here are production optimization steps:

### 1. Firestore Security Rules (IMPORTANT)

Update your Firestore rules for production security:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only access their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Devices - users can only access their own devices
    match /devices/{deviceId} {
      allow read, write: if request.auth != null && 
        request.auth.uid == resource.data.user_id;
    }
    
    // Clipboard items - users can only access their own clipboard
    match /clipboard/{clipId} {
      allow read, write: if request.auth != null && 
        request.auth.uid == resource.data.user_id;
    }
    
    // Audit logs - users can only read their own logs
    match /audit_logs/{logId} {
      allow read: if request.auth != null && 
        request.auth.uid == resource.data.user_id;
      allow create: if request.auth != null;
      allow update, delete: if false; // Logs are immutable
    }
    
    // Shared clipboard - read/write access for authenticated users
    match /shared_clipboard/{shareId} {
      allow read, write: if request.auth != null;
    }
  }
}
```

### 2. Firebase Authentication Setup

Configure authentication providers:

```bash
# Enable Email/Password authentication
# Go to Firebase Console → Authentication → Sign-in method
# Enable "Email/Password"
```

### 3. Environment Variables for Production

Frontend (Vercel):
```env
VITE_FIREBASE_API_KEY=AIzaSyCCLV16V96DKpzHL1L5ek5n2iQhveIdDRk
VITE_FIREBASE_AUTH_DOMAIN=clipbolt-d2bf3.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=clipbolt-d2bf3
VITE_FIREBASE_STORAGE_BUCKET=clipbolt-d2bf3.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id
```

Backend (Railway):
```env
FIREBASE_PROJECT_ID=clipbolt-d2bf3
FIREBASE_API_KEY=AIzaSyCCLV16V96DKpzHL1L5ek5n2iQhveIdDRk
```

### 4. Service Account Key for Backend

Your service account key (`firebase-service-account-key.json`) needs to be securely uploaded:

**Option 1: Base64 Encoding (Recommended)**
```bash
# Encode the service account key
base64 -w 0 backend/firebase-service-account-key.json

# Add to Railway as environment variable:
FIREBASE_SERVICE_ACCOUNT_BASE64=your-base64-encoded-key
```

**Option 2: Railway Volume (Alternative)**
Upload the file directly to Railway persistent storage.

### 5. Production Optimizations

**Firestore Indexes**
Create composite indexes for common queries:
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Create indexes
firebase deploy --only firestore:indexes
```

**Firestore Backup**
Set up automated backups:
1. Go to Firebase Console → Firestore → Backups
2. Enable automatic daily backups
3. Set retention period

### 6. Monitoring and Analytics

**Firebase Performance Monitoring**
```javascript
// Add to frontend
import { getPerformance } from 'firebase/performance';

const perf = getPerformance(app);
```

**Firebase Analytics**
```javascript
// Add to frontend
import { getAnalytics } from 'firebase/analytics';

const analytics = getAnalytics(app);
```

### 7. Cost Optimization

**Current Firebase Free Tier Limits:**
- 1 GiB storage
- 10 GiB/month bandwidth
- 50,000 reads/day
- 20,000 writes/day
- 20,000 deletes/day

**Optimization Tips:**
- Use pagination for large data sets
- Cache frequently accessed data
- Optimize query efficiency
- Clean up old audit logs periodically

### 8. Security Checklist

- [ ] Firestore security rules implemented
- [ ] Service account key securely stored
- [ ] API keys restricted to specific domains
- [ ] HTTPS enforced everywhere
- [ ] Regular security rule testing
- [ ] Monitor for unusual activity

### 9. Production URLs

After deployment:
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-backend.railway.app`
- **Firebase Console**: `https://console.firebase.google.com/project/clipbolt-d2bf3`

### 10. Scaling Considerations

**When you exceed free tier:**
- Upgrade to Firebase Blaze plan (pay-as-you-go)
- Consider implementing data archiving
- Optimize queries and indexes
- Monitor usage in Firebase Console
