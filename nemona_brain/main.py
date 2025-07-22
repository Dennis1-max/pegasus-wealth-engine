#!/usr/bin/env python3
"""
🤖 NEMONA AI AGENT - REPLIT ENTRY POINT
This is the main file that Replit will run.

Simply click "Run" in Replit after setting up your environment variables!
"""

import os
import sys
from app import app, nemona

def main():
    print("🤖 Starting NEMONA AI Agent...")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ['NEMONA_API_KEY']
    optional_vars = ['NEWS_API_KEY', 'WEATHER_API_KEY', 'OPENAI_API_KEY']
    
    print("🔍 Checking environment variables...")
    
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
        else:
            print(f"✅ {var}: {'*' * 10}")
    
    missing_optional = []
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
        else:
            print(f"✅ {var}: {'*' * 10}")
    
    if missing_required:
        print(f"\n❌ MISSING REQUIRED VARIABLES: {', '.join(missing_required)}")
        print("🔧 Please add these in Replit's Secrets tab!")
        return
    
    if missing_optional:
        print(f"\n⚠️ MISSING OPTIONAL VARIABLES: {', '.join(missing_optional)}")
        print("ℹ️ These features will use fallback data.")
    
    print(f"\n🧠 Initializing Nemona's brain...")
    print(f"📊 Database: SQLite")
    print(f"🔒 Encryption: Active")
    print(f"🔄 Auto-learning: Running")
    
    # Get port from environment (Replit automatically sets this)
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"\n🚀 Starting server on {host}:{port}")
    print(f"🌐 Your Nemona API will be available at:")
    print(f"   Health Check: https://{os.environ.get('REPL_SLUG', 'your-repl')}.{os.environ.get('REPL_OWNER', 'username')}.repl.co/api/health")
    print(f"   Chat API: https://{os.environ.get('REPL_SLUG', 'your-repl')}.{os.environ.get('REPL_OWNER', 'username')}.repl.co/api/chat")
    
    print(f"\n💡 API Key for mobile app: {nemona.nemona_api_key}")
    print(f"\n🎉 Nemona is ready! The most advanced AI agent ever built!")
    print("=" * 50)
    
    # Run the Flask app
    app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    main()