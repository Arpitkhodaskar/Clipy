# Railway Backend Deployment

## 🚀 Deploy to Railway (Recommended for Backend)

### Quick Deploy
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

### Manual Deployment Steps

1. **Prepare Backend for Deployment**
   ```bash
   cd backend
   
   # Create requirements.txt if not exists
   pip freeze > requirements.txt
   
   # Create Procfile for Railway
   echo "web: uvicorn app:app --host 0.0.0.0 --port \$PORT" > Procfile
   ```

2. **Deploy to Railway**
   - Go to [railway.app](https://railway.app)
   - Sign in with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Choose "backend" folder as root directory

3. **Configure Environment Variables**
   In Railway dashboard → Variables:
   ```
   FIREBASE_PROJECT_ID=clipbolt-d2bf3
   GOOGLE_APPLICATION_CREDENTIALS=/app/firebase-service-account-key.json
   SECRET_KEY=your-super-secret-production-key-min-32-chars
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ENVIRONMENT=production
   REDIS_URL=redis://red-xxxxx:6379
   FIREBASE_API_KEY=AIzaSyCCLV16V96DKpzHL1L5ek5n2iQhveIdDRk
   ```

4. **Upload Firebase Service Account**
   - Encode your firebase service account key:
   ```bash
   base64 firebase-service-account-key.json
   ```
   - Add as environment variable:
   ```
   FIREBASE_SERVICE_ACCOUNT_BASE64=your-base64-encoded-key
   ```

5. **Update App Startup**
   Modify `app.py` to decode the service account:
   ```python
   import base64
   import json
   import os
   
   # Decode Firebase service account in production
   if os.getenv("ENVIRONMENT") == "production":
       service_account_base64 = os.getenv("FIREBASE_SERVICE_ACCOUNT_BASE64")
       if service_account_base64:
           service_account_json = base64.b64decode(service_account_base64).decode()
           with open("/tmp/firebase-service-account-key.json", "w") as f:
               f.write(service_account_json)
           os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/firebase-service-account-key.json"
   ```

### Railway Configuration Files

Create `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

Create `nixpacks.toml`:
```toml
[phases.build]
cmds = ["pip install -r requirements.txt"]

[phases.start]
cmd = "uvicorn app:app --host 0.0.0.0 --port $PORT"
```

### Redis Setup (Optional)
1. In Railway dashboard → Add Service → Redis
2. Connect Redis to your backend service
3. Update REDIS_URL environment variable

## ✅ Verification

After deployment:
1. Visit your Railway app URL
2. Test `/` endpoint for API status
3. Test `/docs` for API documentation
4. Verify database connections
5. Test authentication endpoints

## 🔧 Troubleshooting

### Common Issues

**Port Configuration**
```python
# In app.py, ensure port binding:
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
```

**Firebase Credentials**
- Ensure service account JSON is properly encoded
- Check file path in production environment
- Verify Firebase project permissions

**Dependencies**
```bash
# Update requirements.txt
pip freeze > requirements.txt

# Pin specific versions if needed
fastapi==0.104.1
uvicorn==0.24.0
```

### Logs and Monitoring
- Use Railway dashboard → Logs for debugging
- Monitor resource usage in Metrics tab
- Set up health checks for uptime monitoring

## 🔒 Security

### Production Checklist
- [ ] Change SECRET_KEY to strong random string
- [ ] Enable HTTPS only
- [ ] Configure CORS for production domains
- [ ] Set up proper Firestore security rules
- [ ] Enable rate limiting
- [ ] Monitor for suspicious activity

### Environment Variables Security
- Never commit `.env` files
- Use Railway's secure variable storage
- Rotate keys regularly
- Use different keys for staging/production
