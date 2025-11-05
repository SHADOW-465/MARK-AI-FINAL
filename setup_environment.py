#!/usr/bin/env python3
"""
Environment Setup Script for EduGrade AI Platform
"""

import os
import sys
import secrets
from pathlib import Path

def setup_environment():
    """Set up environment variables for EduGrade AI Platform"""
    
    print("🎓 EduGrade AI Platform - Environment Setup")
    print("=" * 50)
    
    # Check if Firebase credentials exist
    firebase_creds_path = "config/firebase-credentials.json"
    if os.path.exists(firebase_creds_path):
        print(f"✅ Firebase credentials found: {firebase_creds_path}")
    else:
        print(f"❌ Firebase credentials not found: {firebase_creds_path}")
        print("   Please ensure your serviceAccountKey.json is copied to config/firebase-credentials.json")
        return False
    
    # Check if config.env exists
    config_file = "config.env"
    if os.path.exists(config_file):
        print(f"✅ Configuration file found: {config_file}")
        
        # Load and validate configuration
        with open(config_file, 'r') as f:
            config_content = f.read()
            
        # Check for API keys
        if "GEMINI_API_KEY=AIzaSyDJ3iS2d7ecuMOamMcNWUHxHl729QgDH3U" in config_content:
            print("✅ Gemini API key configured")
        else:
            print("⚠️  Gemini API key not configured")
            
        if "PERPLEXITY_API_KEY=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" in config_content:
            print("✅ Perplexity API key configured")
        else:
            print("⚠️  Perplexity API key not configured")
            
        # Check Firebase project ID
        if "FIREBASE_PROJECT_ID=edugrade-ai-ddc46" in config_content:
            print("✅ Firebase project ID configured")
        else:
            print("⚠️  Firebase project ID not configured")
            
        # Check SECRET_KEY
        if "SECRET_KEY=XkDrRrILR3HMdlZXSeoKzGKQSU1BeP7ASGl5usFHpac" in config_content:
            print("✅ SECRET_KEY configured")
        else:
            print("⚠️  SECRET_KEY not configured")
            
    else:
        print(f"❌ Configuration file not found: {config_file}")
        return False
    
    # Set environment variables
    print("\n🔧 Setting environment variables...")
    
    # Load config.env into environment
    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
    
    print("✅ Environment variables loaded")
    
    # Verify critical environment variables
    critical_vars = [
        "GEMINI_API_KEY",
        "PERPLEXITY_API_KEY", 
        "FIREBASE_PROJECT_ID",
        "FIREBASE_CREDENTIALS_PATH",
        "SECRET_KEY"
    ]
    
    print("\n📋 Verifying environment variables...")
    all_set = True
    
    for var in critical_vars:
        if os.getenv(var):
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Not set")
            all_set = False
    
    if all_set:
        print("\n🎉 Environment setup complete!")
        print("\n📖 Next steps:")
        print("1. Run: python start_edugrade.py")
        print("2. Open: http://localhost:8501")
        print("3. Start using the platform!")
        return True
    else:
        print("\n❌ Some environment variables are missing")
        print("Please check your config.env file")
        return False

def generate_secret_key():
    """Generate a new SECRET_KEY"""
    return secrets.token_urlsafe(32)

def update_secret_key():
    """Update SECRET_KEY in config file"""
    config_file = "config.env"
    if os.path.exists(config_file):
        # Read current config
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Generate new secret key
        new_secret = generate_secret_key()
        
        # Replace old secret key
        import re
        content = re.sub(r'SECRET_KEY=.*', f'SECRET_KEY={new_secret}', content)
        
        # Write back to file
        with open(config_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Generated new SECRET_KEY: {new_secret}")
        return True
    else:
        print("❌ Config file not found")
        return False

def test_firebase_connection():
    """Test Firebase connection"""
    print("\n🔥 Testing Firebase connection...")
    
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        # Initialize Firebase
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "config/firebase-credentials.json")
        
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        
        # Test Firestore connection
        db = firestore.client()
        
        # Try a simple read operation
        test_doc = db.collection('health_check').document('test').get()
        
        print("✅ Firebase connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Firebase connection failed: {str(e)}")
        return False

def main():
    """Main function"""
    print("🎓 EduGrade AI Platform - Environment Setup")
    print("=" * 50)
    
    # Check if user wants to generate new SECRET_KEY
    if len(sys.argv) > 1 and sys.argv[1] == "--generate-secret":
        print("\n🔐 Generating new SECRET_KEY...")
        if update_secret_key():
            print("✅ SECRET_KEY updated successfully")
        else:
            print("❌ Failed to update SECRET_KEY")
        return
    
    if setup_environment():
        # Test Firebase connection
        test_firebase_connection()
    else:
        print("\n❌ Environment setup failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
