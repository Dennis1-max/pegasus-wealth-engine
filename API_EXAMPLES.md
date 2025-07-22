# 🚀 NEMONA API EXAMPLES

## 📋 Overview

Nemona provides a RESTful API that you can integrate into any application. Here are practical examples of how to use each endpoint.

**Base URL:** `https://your-replit-name.username.repl.co/api`  
**API Key:** `nemona-secret-key-2024` (set in Replit Secrets)

---

## 🔍 1. Health Check

Check if Nemona's brain is online and healthy.

### Request
```bash
curl -X GET "https://your-replit-url.repl.co/api/health"
```

### Response
```json
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00.123456",
    "version": "1.0.0",
    "brain_status": "active"
}
```

---

## 💬 2. Chat API

Send messages to Nemona and get intelligent responses with reasoning.

### Basic Chat
```python
import requests

url = "https://your-replit-url.repl.co/api/chat"
payload = {
    "message": "Hello Nemona! How can you help me today?",
    "api_key": "nemona-secret-key-2024",
    "context": {
        "user_id": "user123",
        "session_id": "session456"
    }
}

response = requests.post(url, json=payload)
data = response.json()

print("Nemona:", data["response"])
print("Confidence:", f"{data['confidence']:.1%}")
print("Reasoning Steps:", len(data["reasoning_chain"]))
```

### Money-Making Ideas
```python
payload = {
    "message": "Give me 5 ways to make $50 today",
    "api_key": "nemona-secret-key-2024"
}

response = requests.post(url, json=payload)
# Nemona will provide specific, actionable money-making ideas
```

### Real-Time News
```python
payload = {
    "message": "What's happening in the news today?",
    "api_key": "nemona-secret-key-2024"
}

response = requests.post(url, json=payload)
# Nemona will fetch and summarize latest news
```

### Crypto Prices
```python
payload = {
    "message": "What's the current Bitcoin and Ethereum price?",
    "api_key": "nemona-secret-key-2024"
}

response = requests.post(url, json=payload)
# Nemona will provide real-time cryptocurrency prices
```

---

## 👁️ 3. Vision Analysis

Send images to Nemona for analysis and description.

### Image Analysis
```python
import base64

# Read and encode image
with open("image.jpg", "rb") as image_file:
    image_base64 = base64.b64encode(image_file.read()).decode()

url = "https://your-replit-url.repl.co/api/vision"
payload = {
    "image_base64": image_base64,
    "api_key": "nemona-secret-key-2024"
}

response = requests.post(url, json=payload)
data = response.json()

print("Analysis:", data["response"])
print("Objects detected:", data["analysis"]["objects_detected"])
print("Text detected:", data["analysis"]["text_detected"])
```

### Camera Integration (Mobile)
```javascript
// JavaScript example for mobile apps
function analyzeCamera() {
    const canvas = document.getElementById('camera-canvas');
    const imageData = canvas.toDataURL('image/jpeg');
    const base64Data = imageData.split(',')[1]; // Remove data:image/jpeg;base64,
    
    fetch('https://your-replit-url.repl.co/api/vision', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image_base64: base64Data,
            api_key: 'nemona-secret-key-2024'
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Nemona sees:', data.response);
    });
}
```

---

## 💰 4. Money Ideas API

Get specific money-making opportunities.

### Direct Money Ideas
```python
url = "https://your-replit-url.repl.co/api/money-ideas"
params = {
    "api_key": "nemona-secret-key-2024"
}

response = requests.get(url, params=params)
data = response.json()

print(f"Found {data['count']} money-making ideas:")
for i, idea in enumerate(data['ideas'], 1):
    print(f"\n{i}. {idea['idea']}")
    print(f"   Potential: {idea['potential']}")
    print(f"   Difficulty: {idea['difficulty']}")
    print(f"   Category: {idea['category']}")
    print(f"   Steps: {', '.join(idea['steps'][:2])}")
```

---

## 📊 5. Statistics API

Get Nemona's learning and usage statistics.

### Brain Stats
```python
url = "https://your-replit-url.repl.co/api/stats"
params = {
    "api_key": "nemona-secret-key-2024"
}

response = requests.get(url, params=params)
data = response.json()

print("📊 Nemona's Brain Statistics:")
print(f"Total Conversations: {data['total_conversations']}")
print(f"Insights Learned: {data['total_insights']}")
print(f"24h Activity: {data['conversations_24h']}")
print(f"Learning Status: {data['learning_status']}")
print(f"Uptime: {data['uptime']}")
```

---

## 🔐 6. Security Examples

### API Key Authentication
```python
# All API calls require the API key
headers = {
    'X-API-Key': 'nemona-secret-key-2024'  # Alternative to payload
}

# Or in the payload
payload = {
    "message": "Hello",
    "api_key": "nemona-secret-key-2024"
}

# Wrong API key will return 401 Unauthorized
wrong_payload = {
    "message": "Hello",
    "api_key": "wrong-key"
}
# Response: {"error": "Invalid API key"}, Status: 401
```

### Rate Limiting (Future)
```python
# In production, implement rate limiting
import time

def make_request_with_retry(payload, max_retries=3):
    for attempt in range(max_retries):
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:  # Rate limited
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Rate limited, waiting {wait_time}s...")
            time.sleep(wait_time)
        else:
            break
    
    return None
```

---

## 🤖 7. Complete Integration Example

Here's a complete example of building a simple chatbot that uses all of Nemona's features:

```python
import requests
import json
from datetime import datetime

class NemonaClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session_history = []
    
    def chat(self, message, include_context=True):
        """Send a chat message to Nemona"""
        payload = {
            "message": message,
            "api_key": self.api_key,
            "context": {
                "chat_history": self.session_history[-5:] if include_context else [],
                "timestamp": datetime.now().isoformat(),
                "client": "python_sdk"
            }
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Store in session history
                self.session_history.append({
                    "user": message,
                    "nemona": data["response"],
                    "timestamp": datetime.now().isoformat(),
                    "confidence": data.get("confidence", 0)
                })
                
                return data
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except requests.exceptions.RequestException as e:
            return {"error": f"Connection error: {str(e)}"}
    
    def analyze_image(self, image_path):
        """Analyze an image with Nemona's vision"""
        import base64
        
        with open(image_path, "rb") as img_file:
            image_base64 = base64.b64encode(img_file.read()).decode()
        
        payload = {
            "image_base64": image_base64,
            "api_key": self.api_key
        }
        
        response = requests.post(f"{self.base_url}/api/vision", json=payload, timeout=30)
        return response.json() if response.status_code == 200 else {"error": response.text}
    
    def get_money_ideas(self):
        """Get money-making ideas"""
        response = requests.get(
            f"{self.base_url}/api/money-ideas",
            params={"api_key": self.api_key},
            timeout=10
        )
        return response.json() if response.status_code == 200 else {"error": response.text}
    
    def get_stats(self):
        """Get Nemona's statistics"""
        response = requests.get(
            f"{self.base_url}/api/stats",
            params={"api_key": self.api_key},
            timeout=10
        )
        return response.json() if response.status_code == 200 else {"error": response.text}

# Usage example
def main():
    # Initialize Nemona client
    nemona = NemonaClient(
        base_url="https://your-replit-url.repl.co",
        api_key="nemona-secret-key-2024"
    )
    
    print("🤖 Nemona Chat Interface")
    print("Type 'quit' to exit, 'stats' for statistics, 'money' for ideas")
    print("-" * 50)
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'quit':
            break
        elif user_input.lower() == 'stats':
            stats = nemona.get_stats()
            print(f"📊 Conversations: {stats.get('total_conversations', 0)}")
            print(f"📊 Insights: {stats.get('total_insights', 0)}")
            continue
        elif user_input.lower() == 'money':
            ideas = nemona.get_money_ideas()
            print("💰 Money-making ideas:")
            for i, idea in enumerate(ideas.get('ideas', [])[:3], 1):
                print(f"{i}. {idea['idea']} ({idea['potential']})")
            continue
        
        if user_input:
            result = nemona.chat(user_input)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"🤖 Nemona: {result['response']}")
                print(f"🧠 Confidence: {result.get('confidence', 0):.1%}")

if __name__ == "__main__":
    main()
```

---

## 🔧 8. Error Handling

### Common Error Responses

**401 Unauthorized:**
```json
{
    "error": "Invalid API key"
}
```

**400 Bad Request:**
```json
{
    "error": "Message is required"
}
```

**500 Internal Server Error:**
```json
{
    "error": "Internal server error"
}
```

### Best Practices

1. **Always check status codes** before processing responses
2. **Implement retry logic** with exponential backoff
3. **Validate input data** before sending to API
4. **Handle timeouts gracefully** (set reasonable timeout values)
5. **Log errors** for debugging purposes

---

## 🚀 9. Advanced Features

### Custom Context
```python
# Send custom context for better responses
payload = {
    "message": "Help me with my business",
    "api_key": "nemona-secret-key-2024",
    "context": {
        "user_profile": {
            "business_type": "e-commerce",
            "experience_level": "beginner",
            "budget": "under_1000"
        },
        "previous_topics": ["marketing", "social_media"],
        "goals": ["increase_sales", "build_brand"]
    }
}
```

### Batch Processing
```python
# Process multiple messages efficiently
messages = [
    "What's the weather like?",
    "Give me crypto prices",
    "How can I make money online?"
]

results = []
for msg in messages:
    result = nemona.chat(msg, include_context=False)  # Disable context for speed
    results.append(result)
    time.sleep(0.5)  # Small delay to avoid overwhelming
```

### Webhook Integration (Future)
```python
# Set up webhooks for real-time notifications
webhook_config = {
    "url": "https://your-app.com/nemona-webhook",
    "events": ["new_insight", "learning_milestone", "error_alert"],
    "api_key": "nemona-secret-key-2024"
}

# Nemona will send POST requests to your webhook URL when events occur
```

---

## 📞 Support

For API support:
1. Check the status endpoint: `/api/health`
2. Verify your API key is correct
3. Ensure your Replit app is running
4. Check the console logs in Replit for errors

**Remember: Nemona learns from every interaction, so the more you use it, the smarter it becomes!** 🧠✨