# 🔥 Firebase Setup Guide for EduGrade AI Platform

## ✅ Firebase Credentials Setup Complete!

Your Firebase credentials have been properly configured. Here's what was set up:

### 📁 File Structure
```
Mark-AI/
├── config/
│   └── firebase-credentials.json  ✅ (Your service account key)
├── config.env                     ✅ (Environment configuration)
└── serviceAccountKey.json         ✅ (Original file)
```

### 🔧 Configuration Details

**Firebase Project**: `edugrade-ai-ddc46`
**Service Account**: `firebase-adminsdk-fbsvc@edugrade-ai-ddc46.iam.gserviceaccount.com`
**Credentials File**: `config/firebase-credentials.json`

### 🚀 How to Use

#### Option 1: Quick Start (Recommended)
```bash
# Run the environment setup script
python setup_environment.py

# Start the platform
python start_edugrade.py
```

#### Option 2: Manual Setup
```bash
# Set environment variables manually
set FIREBASE_CREDENTIALS_PATH=config/firebase-credentials.json
set FIREBASE_PROJECT_ID=edugrade-ai-ddc46
set GEMINI_API_KEY=AIzaSyDJ3iS2d7ecuMOamMcNWUHxHl729QgDH3U
set PERPLEXITY_API_KEY=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

# Start the platform
python start_edugrade.py
```

### 🔐 Security Notes

1. **Never commit credentials to version control**
2. **Keep your service account key secure**
3. **Use environment variables in production**
4. **Rotate keys regularly**

### 📋 Environment Variables Set

| Variable | Value | Purpose |
|----------|-------|---------|
| `FIREBASE_CREDENTIALS_PATH` | `config/firebase-credentials.json` | Path to Firebase credentials |
| `FIREBASE_PROJECT_ID` | `edugrade-ai-ddc46` | Firebase project ID |
| `FIREBASE_STORAGE_BUCKET` | `edugrade-ai-ddc46.appspot.com` | Firebase storage bucket |
| `GEMINI_API_KEY` | `AIzaSyDJ3iS2d7ecuMOamMcNWUHxHl729QgDH3U` | Google Gemini AI API key |
| `PERPLEXITY_API_KEY` | `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` | Perplexity API key |
| `SECRET_KEY` | `XkDrRrILR3HMdlZXSeoKzGKQSU1BeP7ASGl5usFHpac` | Application secret key |

### 🧪 Testing Firebase Connection

The platform will automatically test the Firebase connection when it starts. You should see:

```
✅ Firebase initialized with credentials from config/firebase-credentials.json
✅ Firebase Storage initialized
✅ Firebase initialized successfully
```

### 🔐 Security Management

#### Generate New SECRET_KEY
If you need to generate a new SECRET_KEY for security reasons:

```bash
# Generate and update SECRET_KEY
python setup_environment.py --generate-secret
```

#### SECRET_KEY Security
- **Keep it secret**: Never share your SECRET_KEY
- **Use in production**: Always use a strong, unique SECRET_KEY in production
- **Rotate regularly**: Generate new keys periodically for security
- **Environment variables**: Store in environment variables, not in code

### 🚨 Troubleshooting

#### If Firebase connection fails:
1. **Check file path**: Ensure `config/firebase-credentials.json` exists
2. **Check permissions**: Verify the service account has proper permissions
3. **Check project ID**: Ensure `edugrade-ai-ddc46` is correct
4. **Check internet**: Ensure you have internet connectivity

#### If you see "Firebase Storage not available":
- This is normal if Storage isn't enabled in your Firebase project
- The platform will still work with Firestore database

#### If SECRET_KEY is missing:
- Run: `python setup_environment.py --generate-secret`
- Or manually set: `SECRET_KEY=your_secure_key_here`

### 🎯 Next Steps

1. **Run the platform**: `python start_edugrade.py`
2. **Open dashboard**: http://localhost:8501
3. **Create your first exam**
4. **Upload test answer sheets**
5. **Review AI-generated grades**

### 📞 Support

If you encounter any issues:
1. Check the logs in the terminal
2. Verify all environment variables are set
3. Ensure Firebase project is active
4. Check API key validity

---

**🎉 Your Firebase setup is complete and ready to use!**
