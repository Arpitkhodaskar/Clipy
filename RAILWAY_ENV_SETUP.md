# Railway Backend Environment Variables Setup

## 🚀 Railway Deployment Environment Variables

### Required Environment Variables for Railway

When deploying your ClipVault backend to Railway, you need to set these environment variables in your Railway project dashboard:

#### 1. **FIREBASE_PROJECT_ID**
```
FIREBASE_PROJECT_ID=clipbolt-d2bf3
```

#### 2. **SECRET_KEY** (Generated for you)
```
SECRET_KEY=fE_T8VChxstoafoWpWeIxKdcnQckmdp8Fl08sJCrZ3I
```

#### 3. **ALGORITHM**
```
ALGORITHM=HS256
```

#### 4. **ACCESS_TOKEN_EXPIRE_MINUTES**
```
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### 5. **FIREBASE_CREDENTIALS** (JSON as string)
For Railway, instead of using a file path, you'll need to set the Firebase credentials as a JSON string:

```
FIREBASE_CREDENTIALS={"type":"service_account","project_id":"YOUR_PROJECT_ID","private_key_id":"YOUR_PRIVATE_KEY_ID","private_key":"-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n","client_email":"YOUR_SERVICE_ACCOUNT@YOUR_PROJECT.iam.gserviceaccount.com","client_id":"YOUR_CLIENT_ID","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/YOUR_SERVICE_ACCOUNT%40YOUR_PROJECT.iam.gserviceaccount.com","universe_domain":"googleapis.com"}
```

## 🎯 Step-by-Step Railway Deployment

### 1. **Go to Railway**
- Visit [railway.app](https://railway.app)
- Sign in with your GitHub account

### 2. **Create New Project**
- Click "New Project"
- Select "Deploy from GitHub repo"
- Choose your ClipVault repository

### 3. **Configure Root Directory**
- In project settings, set root directory to: `backend`
- This tells Railway to deploy only the backend folder

### 4. **Add Environment Variables**
- Go to your project dashboard
- Click on "Variables" tab
- Add each environment variable listed above

### 5. **Copy-Paste Ready Format**
For easy copy-pasting into Railway, here are your environment variables in Railway format:

```
FIREBASE_PROJECT_ID=YOUR_PROJECT_ID
SECRET_KEY=YOUR_SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FIREBASE_CREDENTIALS={"type":"service_account","project_id":"YOUR_PROJECT_ID","private_key_id":"YOUR_PRIVATE_KEY_ID","private_key":"-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n","client_email":"YOUR_SERVICE_ACCOUNT@YOUR_PROJECT.iam.gserviceaccount.com","client_id":"YOUR_CLIENT_ID","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/YOUR_SERVICE_ACCOUNT%40YOUR_PROJECT.iam.gserviceaccount.com","universe_domain":"googleapis.com"}
```

## ⚠️ Important Notes

1. **Root Directory**: Make sure to set the root directory to `backend` in Railway settings
2. **Port**: Railway automatically provides the `$PORT` environment variable - no need to set it
3. **HTTPS**: Railway automatically provides HTTPS for your deployed backend
4. **Domain**: Railway will give you a domain like `your-app-name.railway.app`

## 🔄 After Deployment

1. **Get your Railway URL**: Copy the deployment URL from Railway dashboard
2. **Update Frontend**: Use this URL as `VITE_API_URL` in your Vercel frontend deployment
3. **Test**: Visit `https://your-app-name.railway.app/docs` to test your API

## 💡 Pro Tips

- Railway automatically detects Python and installs dependencies from `requirements.txt`
- Your backend will auto-restart if it crashes
- Check the "Deploy" tab for build logs and troubleshooting
- Railway provides $5 free credit monthly (covers ~500 hours of runtime)

## 🆘 Troubleshooting

If deployment fails:
1. Check the deploy logs in Railway dashboard
2. Ensure all environment variables are set correctly
3. Verify the root directory is set to `backend`
4. Check that `requirements.txt` and `Procfile` exist in backend folder
