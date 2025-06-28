# Firebase Project Setup Guide

## Step 1: Create Firebase Project

1. **Go to Firebase Console**: https://console.firebase.google.com/
2. **Click "Create a project"**
3. **Enter project name**: `clipvault-prod` (or your preferred name)
4. **Disable Google Analytics** (optional for this project)
5. **Click "Create project"**

## Step 2: Enable Firestore Database

1. **In Firebase Console**, go to "Firestore Database"
2. **Click "Create database"**
3. **Choose "Start in production mode"** (we'll set rules later)
4. **Select a location** (choose closest to your users)
5. **Click "Done"**

## Step 3: Create Service Account

1. **Go to Project Settings** (gear icon → Project settings)
2. **Click "Service accounts" tab**
3. **Click "Generate new private key"**
4. **Download the JSON file**
5. **Rename it to**: `firebase-service-account-key.json`
6. **Move it to**: `f:\clipbolt 4\backend\firebase-service-account-key.json`

## Step 4: Get Project Configuration

1. **In Project Settings**, go to "General" tab
2. **Copy the "Project ID"** (you'll need this)
3. **Go to "Web apps"** section
4. **Click "Add app"** and register a web app
5. **Copy the Firebase config object** (you'll need the apiKey)

## Step 5: Update Environment Variables

Update your `.env` file with real Firebase credentials:

```env
# Firebase Configuration (REAL)
FIREBASE_PROJECT_ID=your-actual-project-id-here
FIREBASE_API_KEY=your-actual-api-key-here
GOOGLE_APPLICATION_CREDENTIALS=./firebase-service-account-key.json
FIREBASE_CREDENTIALS_PATH=./firebase-service-account-key.json
```

## Step 6: Set Firestore Security Rules

In Firebase Console → Firestore → Rules, use:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only access their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Clipboard items belong to users
    match /clipboard_items/{itemId} {
      allow read, write: if request.auth != null && resource.data.user_id == request.auth.uid;
    }
    
    // Devices belong to users  
    match /devices/{deviceId} {
      allow read, write: if request.auth != null && resource.data.user_id == request.auth.uid;
    }
    
    // Security settings belong to users
    match /security_settings/{settingId} {
      allow read, write: if request.auth != null && resource.data.user_id == request.auth.uid;
    }
    
    // Audit logs belong to users
    match /audit_logs/{logId} {
      allow read, write: if request.auth != null && resource.data.user_id == request.auth.uid;
    }
  }
}
```

## Next Steps

After completing these steps:
1. Replace the mock service account key with your real one
2. Update the .env file with your project credentials
3. Restart the backend server
4. Test the connection

The guide will walk you through each step!
