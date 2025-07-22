import os
import json
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from cryptography.fernet import Fernet
import threading
import time
from typing import Dict, List, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests for mobile app

class NemonaBrain:
    def __init__(self):
        # Initialize encryption
        self.cipher_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.cipher_key)
        
        # Initialize database
        self.init_database()
        
        # API keys (set these in environment variables on Replit)
        self.openai_api_key = os.getenv('OPENAI_API_KEY', 'your-openai-key-here')
        self.news_api_key = os.getenv('NEWS_API_KEY', 'your-news-api-key-here')
        self.weather_api_key = os.getenv('WEATHER_API_KEY', 'your-weather-api-key-here')
        
        # Nemona's API access key
        self.nemona_api_key = os.getenv('NEMONA_API_KEY', 'nemona-secret-key-2024')
        
        # Memory and learning system
        self.conversation_memory = []
        self.reasoning_patterns = []
        self.learned_insights = []
        
        # Auto-learning thread
        self.start_auto_learning()
    
    def _get_or_create_encryption_key(self):
        """Get or create encryption key for data security"""
        key_file = 'nemona_encryption.key'
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def init_database(self):
        """Initialize SQLite database for learning and memory"""
        self.conn = sqlite3.connect('nemona_brain.db', check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_input TEXT,
                nemona_response TEXT,
                reasoning_chain TEXT,
                context_data TEXT,
                encrypted BOOLEAN DEFAULT 1
            )
        ''')
        
        # Learning insights table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                insight_type TEXT,
                content TEXT,
                confidence_score REAL,
                usage_count INTEGER DEFAULT 0
            )
        ''')
        
        # Money-making ideas table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS money_ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                idea TEXT,
                category TEXT,
                potential_earnings TEXT,
                difficulty_level TEXT,
                success_rate REAL
            )
        ''')
        
        self.conn.commit()
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def chain_of_thought_reasoning(self, user_input: str, context: Dict) -> Dict:
        """Advanced chain-of-thought reasoning system"""
        reasoning_steps = []
        
        # Step 1: Analyze user input
        analysis = {
            "input_analysis": f"User asked: {user_input}",
            "intent_detected": self._detect_intent(user_input),
            "context_relevant": bool(context),
            "timestamp": datetime.now().isoformat()
        }
        reasoning_steps.append(analysis)
        
        # Step 2: Retrieve relevant memories
        memories = self._retrieve_relevant_memories(user_input)
        if memories:
            reasoning_steps.append({
                "memory_retrieval": f"Found {len(memories)} relevant past conversations",
                "key_insights": [m['insight'] for m in memories[:3]]
            })
        
        # Step 3: Gather real-time data if needed
        real_time_data = self._gather_real_time_data(user_input)
        if real_time_data:
            reasoning_steps.append({
                "real_time_research": "Gathered current information",
                "data_sources": list(real_time_data.keys())
            })
        
        # Step 4: Generate response strategy
        strategy = self._generate_response_strategy(user_input, memories, real_time_data)
        reasoning_steps.append(strategy)
        
        # Step 5: Create final response
        final_response = self._generate_final_response(user_input, reasoning_steps, real_time_data)
        
        return {
            "reasoning_chain": reasoning_steps,
            "final_response": final_response,
            "confidence": self._calculate_confidence(reasoning_steps)
        }
    
    def _detect_intent(self, user_input: str) -> str:
        """Detect user intent from input"""
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ['money', 'earn', 'income', 'business', 'profit']):
            return 'money_making'
        elif any(word in user_input_lower for word in ['news', 'current', 'today', 'latest']):
            return 'news_request'
        elif any(word in user_input_lower for word in ['weather', 'temperature', 'forecast']):
            return 'weather_request'
        elif any(word in user_input_lower for word in ['crypto', 'bitcoin', 'ethereum', 'price']):
            return 'crypto_request'
        elif any(word in user_input_lower for word in ['learn', 'teach', 'explain', 'how']):
            return 'learning_request'
        else:
            return 'general_conversation'
    
    def _retrieve_relevant_memories(self, user_input: str) -> List[Dict]:
        """Retrieve relevant past conversations"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT user_input, nemona_response, reasoning_chain, timestamp 
            FROM conversations 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''')
        
        memories = []
        for row in cursor.fetchall():
            # Simple relevance scoring (can be improved with embeddings)
            relevance_score = self._calculate_relevance(user_input, row[0])
            if relevance_score > 0.3:
                memories.append({
                    'user_input': row[0],
                    'response': row[1],
                    'reasoning': row[2],
                    'timestamp': row[3],
                    'relevance': relevance_score,
                    'insight': f"Previously discussed similar topic with {relevance_score:.2f} relevance"
                })
        
        return sorted(memories, key=lambda x: x['relevance'], reverse=True)
    
    def _calculate_relevance(self, current_input: str, past_input: str) -> float:
        """Simple relevance calculation (can be improved)"""
        current_words = set(current_input.lower().split())
        past_words = set(past_input.lower().split())
        
        if not current_words or not past_words:
            return 0.0
        
        intersection = current_words.intersection(past_words)
        union = current_words.union(past_words)
        
        return len(intersection) / len(union)
    
    def _gather_real_time_data(self, user_input: str) -> Dict:
        """Gather real-time data from various sources"""
        intent = self._detect_intent(user_input)
        data = {}
        
        try:
            if intent == 'news_request' or 'news' in user_input.lower():
                data['news'] = self._get_latest_news()
            
            if intent == 'weather_request' or 'weather' in user_input.lower():
                data['weather'] = self._get_weather_data()
            
            if intent == 'crypto_request' or any(crypto in user_input.lower() for crypto in ['bitcoin', 'crypto', 'ethereum']):
                data['crypto'] = self._get_crypto_prices()
            
            if intent == 'money_making':
                data['money_ideas'] = self._generate_money_making_ideas()
            
            # Always get trending topics for context
            data['trends'] = self._get_trending_topics()
            
        except Exception as e:
            logger.error(f"Error gathering real-time data: {e}")
        
        return data
    
    def _get_latest_news(self) -> List[Dict]:
        """Get latest news from NewsAPI"""
        try:
            url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={self.news_api_key}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                articles = response.json().get('articles', [])[:5]
                return [{'title': a['title'], 'description': a['description'][:200]} for a in articles]
        except:
            # Fallback to free news source
            return [{'title': 'News Update', 'description': 'Unable to fetch real-time news at the moment.'}]
    
    def _get_weather_data(self) -> Dict:
        """Get weather data from OpenWeatherMap"""
        try:
            # Using a default city, can be made dynamic
            url = f"http://api.openweathermap.org/data/2.5/weather?q=New York&appid={self.weather_api_key}&units=metric"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'temperature': data['main']['temp'],
                    'description': data['weather'][0]['description'],
                    'humidity': data['main']['humidity']
                }
        except:
            return {'temperature': 'N/A', 'description': 'Weather data unavailable', 'humidity': 'N/A'}
    
    def _get_crypto_prices(self) -> Dict:
        """Get cryptocurrency prices from free API"""
        try:
            url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,cardano&vs_currencies=usd"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
        except:
            return {'bitcoin': {'usd': 'N/A'}, 'ethereum': {'usd': 'N/A'}}
    
    def _get_trending_topics(self) -> List[str]:
        """Get trending topics (simplified version)"""
        # This is a simplified version. In production, you'd use Google Trends API or Twitter API
        return ["AI technology", "Remote work", "Cryptocurrency", "Sustainable energy", "Digital marketing"]
    
    def _generate_money_making_ideas(self) -> List[Dict]:
        """Generate daily money-making ideas"""
        ideas = [
            {
                "idea": "Freelance writing for blogs and websites",
                "potential": "$20-50/day",
                "difficulty": "Easy",
                "category": "Writing",
                "steps": ["Sign up on Upwork/Fiverr", "Create portfolio", "Apply to jobs"]
            },
            {
                "idea": "Sell photos on stock photography sites",
                "potential": "$10-30/day",
                "difficulty": "Easy",
                "category": "Photography",
                "steps": ["Take high-quality photos", "Upload to Shutterstock/Unsplash", "Wait for sales"]
            },
            {
                "idea": "Create and sell digital templates",
                "potential": "$30-100/day",
                "difficulty": "Medium",
                "category": "Design",
                "steps": ["Design templates in Canva", "List on Etsy", "Market on social media"]
            },
            {
                "idea": "Offer virtual assistant services",
                "potential": "$25-75/day",
                "difficulty": "Easy",
                "category": "Services",
                "steps": ["List services on Belay/Time Etc", "Build client base", "Scale up"]
            },
            {
                "idea": "Create YouTube automation content",
                "potential": "$50-200/day",
                "difficulty": "Medium",
                "category": "Content",
                "steps": ["Choose niche", "Use AI tools for content", "Monetize with ads"]
            }
        ]
        
        # Add current date context
        today = datetime.now().strftime("%B %d, %Y")
        for idea in ideas:
            idea["date_suggested"] = today
        
        return ideas
    
    def _generate_response_strategy(self, user_input: str, memories: List, real_time_data: Dict) -> Dict:
        """Generate response strategy based on analysis"""
        strategy = {
            "approach": "conversational",
            "tone": "helpful and intelligent",
            "include_data": bool(real_time_data),
            "reference_memory": bool(memories),
            "reasoning": "Combining past experience with current data for optimal response"
        }
        
        intent = self._detect_intent(user_input)
        if intent == 'money_making':
            strategy["approach"] = "actionable_advice"
            strategy["focus"] = "practical steps and real opportunities"
        elif intent in ['news_request', 'weather_request', 'crypto_request']:
            strategy["approach"] = "informational"
            strategy["focus"] = "current data and context"
        
        return strategy
    
    def _generate_final_response(self, user_input: str, reasoning_steps: List, real_time_data: Dict) -> str:
        """Generate the final response using all gathered information"""
        intent = self._detect_intent(user_input)
        
        # Base response
        response = f"Hello! I'm Nemona, your advanced AI agent. Let me help you with that.\n\n"
        
        # Add intent-specific responses
        if intent == 'money_making':
            if 'money_ideas' in real_time_data:
                response += "💰 **Daily Money-Making Opportunities:**\n\n"
                for i, idea in enumerate(real_time_data['money_ideas'][:3], 1):
                    response += f"{i}. **{idea['idea']}**\n"
                    response += f"   • Potential: {idea['potential']}\n"
                    response += f"   • Difficulty: {idea['difficulty']}\n"
                    response += f"   • Steps: {', '.join(idea['steps'][:2])}\n\n"
        
        elif intent == 'news_request':
            if 'news' in real_time_data:
                response += "📰 **Latest News Headlines:**\n\n"
                for i, article in enumerate(real_time_data['news'][:3], 1):
                    response += f"{i}. {article['title']}\n"
                    response += f"   {article['description'][:150]}...\n\n"
        
        elif intent == 'weather_request':
            if 'weather' in real_time_data:
                weather = real_time_data['weather']
                response += f"🌤️ **Current Weather:**\n"
                response += f"Temperature: {weather['temperature']}°C\n"
                response += f"Conditions: {weather['description'].title()}\n"
                response += f"Humidity: {weather['humidity']}%\n\n"
        
        elif intent == 'crypto_request':
            if 'crypto' in real_time_data:
                crypto = real_time_data['crypto']
                response += "💎 **Cryptocurrency Prices:**\n\n"
                if 'bitcoin' in crypto:
                    response += f"Bitcoin: ${crypto['bitcoin']['usd']:,}\n"
                if 'ethereum' in crypto:
                    response += f"Ethereum: ${crypto['ethereum']['usd']:,}\n"
                response += "\n"
        
        # Add trending context
        if 'trends' in real_time_data:
            response += f"🔥 **Currently Trending:** {', '.join(real_time_data['trends'][:3])}\n\n"
        
        # Add reasoning insight
        response += f"🧠 **My Reasoning:** I analyzed your request using {len(reasoning_steps)} steps of logical thinking, "
        response += f"gathered real-time data from {len(real_time_data)} sources, and referenced my memory for context.\n\n"
        
        # Personalized touch
        response += "Is there anything specific you'd like me to elaborate on or help you with next?"
        
        return response
    
    def _calculate_confidence(self, reasoning_steps: List) -> float:
        """Calculate confidence score for the response"""
        base_confidence = 0.7
        
        # Increase confidence based on reasoning steps
        step_bonus = min(len(reasoning_steps) * 0.05, 0.2)
        
        # Increase confidence if real-time data was used
        data_bonus = 0.1 if any('real_time_research' in step for step in reasoning_steps if isinstance(step, dict)) else 0
        
        return min(base_confidence + step_bonus + data_bonus, 1.0)
    
    def save_conversation(self, user_input: str, nemona_response: str, reasoning_chain: List, context_data: Dict):
        """Save conversation for learning"""
        try:
            encrypted_response = self.encrypt_data(nemona_response)
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO conversations (user_input, nemona_response, reasoning_chain, context_data)
                VALUES (?, ?, ?, ?)
            ''', (
                user_input,
                encrypted_response,
                json.dumps(reasoning_chain),
                json.dumps(context_data)
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
    
    def start_auto_learning(self):
        """Start the auto-learning background process"""
        def learning_loop():
            while True:
                try:
                    self.analyze_and_improve()
                    time.sleep(3600)  # Learn every hour
                except Exception as e:
                    logger.error(f"Learning error: {e}")
                    time.sleep(1800)  # Retry in 30 minutes
        
        learning_thread = threading.Thread(target=learning_loop, daemon=True)
        learning_thread.start()
        logger.info("Auto-learning system started")
    
    def analyze_and_improve(self):
        """Analyze past conversations and improve reasoning"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT user_input, reasoning_chain, timestamp 
            FROM conversations 
            WHERE timestamp > datetime('now', '-7 days')
        ''')
        
        recent_conversations = cursor.fetchall()
        
        # Analyze patterns
        patterns = {}
        for conv in recent_conversations:
            user_input = conv[0]
            intent = self._detect_intent(user_input)
            
            if intent not in patterns:
                patterns[intent] = []
            patterns[intent].append(user_input)
        
        # Save insights
        for intent, examples in patterns.items():
            if len(examples) >= 3:  # Only if we have enough data
                insight = f"Users frequently ask about {intent}. Common patterns: {len(examples)} instances"
                
                cursor.execute('''
                    INSERT OR REPLACE INTO insights (insight_type, content, confidence_score)
                    VALUES (?, ?, ?)
                ''', (intent, insight, min(len(examples) / 10.0, 1.0)))
        
        self.conn.commit()
        logger.info(f"Analyzed {len(recent_conversations)} conversations, found {len(patterns)} patterns")

# Initialize Nemona's brain
nemona = NemonaBrain()

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'brain_status': 'active'
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json()
        
        # Verify API key
        api_key = data.get('api_key') or request.headers.get('X-API-Key')
        if api_key != nemona.nemona_api_key:
            return jsonify({'error': 'Invalid API key'}), 401
        
        user_input = data.get('message', '').strip()
        context = data.get('context', {})
        
        if not user_input:
            return jsonify({'error': 'Message is required'}), 400
        
        # Process with chain-of-thought reasoning
        result = nemona.chain_of_thought_reasoning(user_input, context)
        
        # Save conversation for learning
        nemona.save_conversation(
            user_input, 
            result['final_response'], 
            result['reasoning_chain'], 
            context
        )
        
        return jsonify({
            'response': result['final_response'],
            'reasoning_chain': result['reasoning_chain'],
            'confidence': result['confidence'],
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/vision', methods=['POST'])
def vision_analysis():
    """Vision analysis endpoint for camera input"""
    try:
        data = request.get_json()
        
        # Verify API key
        api_key = data.get('api_key') or request.headers.get('X-API-Key')
        if api_key != nemona.nemona_api_key:
            return jsonify({'error': 'Invalid API key'}), 401
        
        # This would integrate with vision AI services
        # For now, return a placeholder response
        image_data = data.get('image_base64', '')
        
        # Simulated vision analysis
        analysis = {
            'objects_detected': ['book', 'table', 'pen'],
            'text_detected': 'Sample text from OCR',
            'scene_description': 'This appears to be a workspace with reading materials',
            'confidence': 0.85
        }
        
        response = f"I can see {', '.join(analysis['objects_detected'])} in the image. "
        if analysis['text_detected']:
            response += f"I also detected text: '{analysis['text_detected']}'. "
        response += analysis['scene_description']
        
        return jsonify({
            'response': response,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Vision error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/money-ideas', methods=['GET'])
def get_money_ideas():
    """Get daily money-making ideas"""
    try:
        # Verify API key
        api_key = request.args.get('api_key') or request.headers.get('X-API-Key')
        if api_key != nemona.nemona_api_key:
            return jsonify({'error': 'Invalid API key'}), 401
        
        ideas = nemona._generate_money_making_ideas()
        
        return jsonify({
            'ideas': ideas,
            'count': len(ideas),
            'generated_at': datetime.now().isoformat(),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Money ideas error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get Nemona's learning statistics"""
    try:
        # Verify API key
        api_key = request.args.get('api_key') or request.headers.get('X-API-Key')
        if api_key != nemona.nemona_api_key:
            return jsonify({'error': 'Invalid API key'}), 401
        
        cursor = nemona.conn.cursor()
        
        # Get conversation count
        cursor.execute('SELECT COUNT(*) FROM conversations')
        conversation_count = cursor.fetchone()[0]
        
        # Get insights count
        cursor.execute('SELECT COUNT(*) FROM insights')
        insights_count = cursor.fetchone()[0]
        
        # Get recent activity
        cursor.execute('''
            SELECT COUNT(*) FROM conversations 
            WHERE timestamp > datetime('now', '-24 hours')
        ''')
        recent_conversations = cursor.fetchone()[0]
        
        return jsonify({
            'total_conversations': conversation_count,
            'total_insights': insights_count,
            'conversations_24h': recent_conversations,
            'learning_status': 'active',
            'uptime': 'continuous',
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create database tables on startup
    nemona.init_database()
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)