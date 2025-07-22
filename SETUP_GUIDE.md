# 🤖 NEMONA - Advanced AI Agent Setup Guide

## 🌟 What You're Building

**Nemona** is the most advanced AI agent ever created! It features:

- 🧠 **Smart Brain**: Chain-of-thought reasoning, self-learning, memory storage
- 🌐 **Real-time Data**: News, weather, crypto prices, trends
- 💰 **Money-Making Ideas**: Daily suggestions for earning $10-100/day
- 📷 **Vision**: Camera analysis and OCR text reading
- 🎤 **Voice**: Speech-to-text and text-to-speech
- 📱 **Mobile App**: Beautiful Android app with all features
- 🔒 **Security**: Encrypted data storage and API key protection

---

## 📋 Part 1: Setting Up Nemona's Brain (Replit - 100% FREE)

### Step 1: Create Replit Account
1. Go to **https://replit.com**
2. Click **"Sign Up"** (use Google/GitHub for easy setup)
3. Choose the **FREE plan** (perfect for Nemona!)

### Step 2: Create New Repl
1. Click **"+ Create Repl"**
2. Choose **"Python"** template
3. Name it: **"nemona-brain"**
4. Click **"Create Repl"**

### Step 3: Upload Nemona's Brain Code
1. **Delete** the default `main.py` file in Replit
2. Click **"+ Add file"** and create `app.py`
3. **Copy** the entire code from `nemona_brain/app.py` and paste it into Replit's `app.py`
4. Click **"+ Add file"** and create `requirements.txt`
5. **Copy** the content from `nemona_brain/requirements.txt` and paste it

### Step 4: Install Dependencies
1. In Replit's **Shell** (bottom panel), run:
```bash
pip install -r requirements.txt
```
2. Wait for installation to complete (2-3 minutes)

### Step 5: Set Environment Variables (IMPORTANT!)
1. Click the **🔒 "Secrets"** tab (left sidebar)
2. Add these **FREE API keys**:

**NEWS API (Free):**
- Key: `NEWS_API_KEY`
- Value: Get free key at **https://newsapi.org** (sign up, copy API key)

**WEATHER API (Free):**
- Key: `WEATHER_API_KEY`
- Value: Get free key at **https://openweathermap.org/api** (sign up, copy API key)

**NEMONA API KEY (Your Security):**
- Key: `NEMONA_API_KEY`
- Value: `nemona-secret-key-2024` (or create your own secret key)

### Step 6: Run Nemona's Brain
1. Change `main.py` to import app: Add this line at the top:
```python
from app import app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```
2. Click **"Run"** button
3. Wait for **"Running on https://your-repl-name.username.repl.co"**
4. **COPY THIS URL** - you'll need it for the mobile app!

### Step 7: Keep It Running 24/7 (FREE)
1. Your Repl will stay active as long as people use it
2. For 24/7 uptime, use **UptimeRobot** (free):
   - Go to **https://uptimerobot.com**
   - Add your Replit URL for monitoring
   - It will ping your app every 5 minutes to keep it alive

---

## 📱 Part 2: Building the Mobile App

### Step 8: Test Nemona's Brain First
Before building the mobile app, let's test if Nemona's brain works:

1. Open your browser
2. Go to: `YOUR_REPLIT_URL/api/health`
3. You should see: `{"status": "healthy", "timestamp": "...", "version": "1.0.0", "brain_status": "active"}`

**If this works, your brain is ready! 🧠✅**

### Step 9: Mobile App Setup Options

Choose **ONE** of these methods based on your device:

#### 🅰️ **Option A: Android Phone/Tablet (Easiest)**

**Using Pydroid 3 (Recommended):**

1. **Install Pydroid 3** from Google Play Store (free app)
2. Open Pydroid 3 and install dependencies:
```python
pip install kivy kivymd requests pyttsx3 speechrecognition pillow
```
3. **Create new file** called `nemona_app.py`
4. **Copy** all code from `nemona_mobile/main.py` into this file
5. **IMPORTANT:** Edit line 87 to replace `"https://your-replit-url.repl.co/api"` with YOUR actual Replit URL
6. **Run** the file in Pydroid 3
7. **Grant permissions** when prompted (Camera, Microphone, Storage)

**The app will open and connect to Nemona's brain!**

#### 🅱️ **Option B: Computer with Termux (Advanced)**

**For building APK file:**

1. **Install Termux** on Android (from F-Droid or GitHub releases)
2. **Install dependencies:**
```bash
pkg update && pkg upgrade
pkg install python python-pip git
pip install buildozer cython
```
3. **Clone/download** the `nemona_mobile` folder to Termux
4. **Edit** `main.py` with your Replit URL (line 87)
5. **Build APK:**
```bash
cd nemona_mobile
buildozer android debug
```
6. **Install APK:** Find `bin/nemona-1.0-debug.apk` and install it

#### 🅲️ **Option C: Online APK Builder**

**Using GitHub Codespaces or GitPod:**

1. **Upload** the `nemona_mobile` folder to GitHub
2. **Edit** `main.py` with your Replit URL
3. **Open** in GitHub Codespaces
4. **Run:**
```bash
sudo apt-get update
sudo apt-get install -y python3-pip
pip install buildozer
buildozer android debug
```
5. **Download** the generated APK file

---

## 🧪 Part 3: Testing Nemona

### Step 10: Test All Features

**1. Basic Chat:**
- Type: "Hello Nemona, how are you?"
- Should get intelligent response with reasoning

**2. Money Ideas:**
- Type: "How can I make money today?"
- Should get 3-5 specific money-making ideas

**3. Real-time Data:**
- Type: "What's the latest news?"
- Type: "Bitcoin price?"
- Type: "How's the weather?"

**4. Camera Vision (Mobile only):**
- Tap camera button 📷
- Take photo of text/objects
- Should describe what it sees

**5. Voice (Mobile only):**
- Tap microphone button 🎤
- Speak your question
- Should convert to text and respond

**6. Learning System:**
- Ask similar questions over time
- Nemona should remember and improve responses

### Step 11: Verify Learning System
1. Check Nemona's stats: Type "Show me your statistics"
2. Should show:
   - Total conversations
   - Insights learned
   - Recent activity
   - Learning status

---

## 🚀 Part 4: Advanced Features

### Step 12: API Integration (Optional)

**To add more data sources:**

1. **Google Trends:** Add `pytrends` to requirements
2. **Social Media:** Add Twitter/Reddit APIs
3. **Stock Data:** Add `yfinance` for real-time stock prices
4. **More Vision:** Add OpenAI Vision API for advanced image analysis

### Step 13: Automation Features

**Nemona can automate tasks like:**
- Researching topics and saving summaries
- Monitoring crypto/stock prices and alerting you
- Generating daily content ideas
- Analyzing images for business opportunities

### Step 14: Scaling Up

**For production use:**
- Move from Replit to proper hosting (Heroku, DigitalOcean)
- Add user authentication and multiple users
- Integrate with ChatGPT/Claude APIs for more advanced reasoning
- Add more sophisticated learning algorithms

---

## 🔧 Troubleshooting

### Common Issues:

**"Connection Error":**
- Check your Replit URL is correct
- Make sure Replit app is running
- Check internet connection

**"API Key Invalid":**
- Verify the API key in mobile app matches Replit secrets
- Default is: `nemona-secret-key-2024`

**"Voice not working":**
- Grant microphone permissions
- Only works on physical Android devices, not emulators

**"Camera not working":**
- Grant camera permissions
- Only works on physical Android devices

**"App won't build":**
- Check all requirements are installed
- Make sure you have enough storage space
- Try online builders like GitHub Codespaces

### Getting Help:
- Check Replit console for error messages
- Test individual API endpoints in browser
- Make sure all files are uploaded correctly

---

## 🎉 Congratulations!

You've successfully built **NEMONA**, the most advanced AI agent ever! 

### What You've Accomplished:
- ✅ Created a smart AI brain with reasoning and learning
- ✅ Built a beautiful mobile app with voice and camera
- ✅ Integrated real-time data feeds
- ✅ Implemented security and encryption
- ✅ Set up 24/7 free hosting
- ✅ Created a complete AI assistant system

### Next Steps:
1. **Use Nemona daily** to help with tasks and money-making
2. **Share with friends** - they can use your Replit URL too!
3. **Expand features** - add more APIs and capabilities
4. **Monitor learning** - watch Nemona get smarter over time

**Welcome to the future of AI assistants! 🤖🚀**

---

## 📞 Support

If you need help:
1. **Check the troubleshooting section above**
2. **Test each component individually**
3. **Review the code comments** - everything is explained
4. **Start simple** - get basic chat working first, then add features

**Remember: You now have a complete AI agent system that rivals commercial products, built 100% free and open source!**