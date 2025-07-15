"""
Pegasus Wealth Engine (PWE) API
AI-powered autonomous money-making strategy generator
"""

import os
import sqlite3
import json
import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
import logging
import hashlib

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Pegasus Wealth Engine API",
    description="AI-powered autonomous money-making strategy generator",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database initialization
def init_database():
    """Initialize SQLite database for storing conversation history"""
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_hash TEXT UNIQUE,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            success_score INTEGER DEFAULT 0,
            earnings REAL DEFAULT 0.0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS strategies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            strategy TEXT NOT NULL,
            success_rate REAL DEFAULT 0.0,
            avg_earnings REAL DEFAULT 0.0,
            last_used DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("✅ Database initialized successfully")

# AI Model initialization
class AIEngine:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.generator = None
        self.load_model()
    
    def load_model(self):
        """Load the Hugging Face model for text generation"""
        try:
            model_name = "facebook/opt-1.3b"
            logger.info(f"🤖 Loading AI model: {model_name}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            
            # Create text generation pipeline
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if torch.cuda.is_available() else -1
            )
            
            logger.info("✅ AI model loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Error loading AI model: {str(e)}")
            # Fallback to a smaller model or simple responses
            self.model = None
            self.tokenizer = None
            self.generator = None
    
    def generate_money_strategy(self, prompt: str) -> str:
        """Generate money-making strategy based on user prompt"""
        try:
            # Enhanced prompt for money-making strategies
            enhanced_prompt = f"""
As an expert financial strategist and entrepreneur, provide a detailed, actionable money-making strategy for: "{prompt}"

Consider these factors:
1. Timeline and realistic expectations
2. Required skills and resources
3. Step-by-step action plan
4. Potential earnings and ROI
5. Risk assessment and mitigation
6. Scalability options

Strategy:"""

            if self.generator:
                # Use AI model for generation
                response = self.generator(
                    enhanced_prompt,
                    max_length=500,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                
                generated_text = response[0]['generated_text']
                # Extract only the strategy part (after "Strategy:")
                strategy = generated_text.split("Strategy:")[-1].strip()
                
            else:
                # Fallback strategy generation
                strategy = self.generate_fallback_strategy(prompt)
            
            return strategy
            
        except Exception as e:
            logger.error(f"❌ Error generating strategy: {str(e)}")
            return self.generate_fallback_strategy(prompt)
    
    def generate_fallback_strategy(self, prompt: str) -> str:
        """Fallback strategy generator when AI model is not available"""
        strategies = {
            "freelance": """
1. Create profiles on Upwork, Fiverr, and Freelancer
2. Identify your core skills (writing, design, programming, etc.)
3. Start with competitive pricing to build reviews
4. Focus on quick turnaround projects initially
5. Gradually increase rates as you build reputation
6. Aim for $20-50/hour within first month
7. Scale by offering package deals and retainer clients
""",
            "online": """
1. Choose a profitable niche (health, finance, tech)
2. Create valuable content (blog, YouTube, social media)
3. Build an email list of potential customers
4. Develop digital products (courses, ebooks, tools)
5. Use affiliate marketing for passive income
6. Monetize through ads, sponsorships, and partnerships
7. Scale with automation and outsourcing
""",
            "ecommerce": """
1. Research trending products with low competition
2. Find reliable suppliers (Alibaba, local manufacturers)
3. Create an online store (Shopify, Amazon FBA)
4. Optimize product listings with SEO
5. Run targeted social media ads
6. Focus on customer service and reviews
7. Expand product line based on successful items
""",
            "investment": """
1. Start with index funds for stable growth
2. Learn about dividend stocks for passive income
3. Consider REITs for real estate exposure
4. Use dollar-cost averaging for consistent investing
5. Keep emergency fund of 3-6 months expenses
6. Diversify across asset classes and sectors
7. Reinvest profits to compound returns
"""
        }
        
        # Determine category based on prompt keywords
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ["freelance", "gig", "service"]):
            category = "freelance"
        elif any(word in prompt_lower for word in ["online", "digital", "internet"]):
            category = "online"
        elif any(word in prompt_lower for word in ["sell", "product", "ecommerce"]):
            category = "ecommerce"
        elif any(word in prompt_lower for word in ["invest", "stock", "crypto"]):
            category = "investment"
        else:
            category = "online"  # Default
        
        base_strategy = strategies[category]
        
        # Customize based on prompt
        customized = f"""
**Money-Making Strategy for: {prompt}**

{base_strategy}

**Quick Start Actions:**
1. Set up necessary accounts today
2. Complete profile/setup within 24 hours
3. Launch first offering within 48 hours
4. Track daily progress and earnings
5. Optimize based on results weekly

**Expected Timeline:**
- Week 1: Setup and first attempts ($0-50)
- Week 2-4: Build momentum ($50-200/week)
- Month 2-3: Scale operations ($200-500/week)
- Month 4+: Full optimization ($500+/week)

Remember: Success requires consistent action and adaptation!
"""
        
        return customized

# Initialize AI engine
ai_engine = AIEngine()

# Pydantic models
class ChatRequest(BaseModel):
    prompt: str
    user_id: str = "default"
    context: Dict[str, Any] = {}

class ChatResponse(BaseModel):
    response: str
    strategy_id: str
    confidence: float
    suggested_actions: List[str]
    estimated_earnings: str
    timestamp: str

class HistoryResponse(BaseModel):
    conversations: List[Dict[str, Any]]
    total_strategies: int
    top_performing: List[Dict[str, Any]]

# Helper functions
def get_prompt_hash(prompt: str) -> str:
    """Generate hash for prompt to check for similar queries"""
    return hashlib.md5(prompt.lower().encode()).hexdigest()

def save_conversation(prompt: str, response: str) -> str:
    """Save conversation to database and return strategy ID"""
    try:
        conn = sqlite3.connect('history.db')
        cursor = conn.cursor()
        
        prompt_hash = get_prompt_hash(prompt)
        timestamp = datetime.datetime.now().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO conversations 
            (prompt_hash, prompt, response, timestamp) 
            VALUES (?, ?, ?, ?)
        ''', (prompt_hash, prompt, response, timestamp))
        
        strategy_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return str(strategy_id)
        
    except Exception as e:
        logger.error(f"❌ Error saving conversation: {str(e)}")
        return "temp_" + str(datetime.datetime.now().timestamp())

def get_similar_strategies(prompt: str) -> List[Dict[str, Any]]:
    """Get similar strategies from database"""
    try:
        conn = sqlite3.connect('history.db')
        cursor = conn.cursor()
        
        # Simple keyword matching (can be enhanced with embeddings)
        words = prompt.lower().split()
        query_conditions = " OR ".join([f"LOWER(prompt) LIKE '%{word}%'" for word in words[:5]])
        
        cursor.execute(f'''
            SELECT * FROM conversations 
            WHERE {query_conditions}
            ORDER BY timestamp DESC 
            LIMIT 5
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "prompt": row[2],
                "response": row[3],
                "timestamp": row[4],
                "success_score": row[5]
            }
            for row in results
        ]
        
    except Exception as e:
        logger.error(f"❌ Error getting similar strategies: {str(e)}")
        return []

def extract_suggested_actions(strategy: str) -> List[str]:
    """Extract actionable items from strategy"""
    actions = []
    lines = strategy.split('\n')
    
    for line in lines:
        line = line.strip()
        if any(line.startswith(prefix) for prefix in ['1.', '2.', '3.', '4.', '5.', '-', '•']):
            # Clean up the action
            action = line.lstrip('123456789.-• ').strip()
            if action and len(action) > 10:
                actions.append(action)
    
    return actions[:5]  # Return top 5 actions

def estimate_earnings(prompt: str, strategy: str) -> str:
    """Estimate potential earnings based on strategy"""
    prompt_lower = prompt.lower()
    
    # Extract any dollar amounts mentioned in prompt
    import re
    amounts = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', prompt)
    
    if amounts:
        target_amount = amounts[0].replace(',', '')
        return f"Target: ${target_amount} (as specified)"
    
    # Default estimates based on strategy type
    if any(word in prompt_lower for word in ["day", "today", "quickly"]):
        return "$50-200 (short-term)"
    elif any(word in prompt_lower for word in ["week", "weekly"]):
        return "$200-1000 (weekly potential)"
    elif any(word in prompt_lower for word in ["month", "monthly"]):
        return "$1000-5000 (monthly potential)"
    else:
        return "$100-500 (typical range)"

# API Routes
@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "✅ PWE API is running!",
        "version": "1.0.0",
        "ai_model": "facebook/opt-1.3b" if ai_engine.model else "fallback",
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.post("/v1/chat/completions", response_model=ChatResponse)
async def chat_completions(request: ChatRequest):
    """Generate money-making strategy based on user prompt"""
    try:
        # Check for similar strategies first
        similar_strategies = get_similar_strategies(request.prompt)
        
        # Generate new strategy
        strategy = ai_engine.generate_money_strategy(request.prompt)
        
        # If we have similar strategies, enhance the response
        if similar_strategies:
            strategy += f"\n\n**📊 Based on {len(similar_strategies)} similar queries, here are additional insights:**\n"
            for i, similar in enumerate(similar_strategies[:2], 1):
                strategy += f"{i}. Previous approach: {similar['prompt'][:100]}...\n"
        
        # Save conversation
        strategy_id = save_conversation(request.prompt, strategy)
        
        # Extract actionable items
        suggested_actions = extract_suggested_actions(strategy)
        
        # Estimate earnings
        estimated_earnings = estimate_earnings(request.prompt, strategy)
        
        # Calculate confidence based on model availability and similar strategies
        confidence = 0.8 if ai_engine.model else 0.6
        if similar_strategies:
            confidence += 0.1
        
        response = ChatResponse(
            response=strategy,
            strategy_id=strategy_id,
            confidence=min(confidence, 0.95),
            suggested_actions=suggested_actions,
            estimated_earnings=estimated_earnings,
            timestamp=datetime.datetime.now().isoformat()
        )
        
        logger.info(f"✅ Generated strategy for: {request.prompt[:50]}...")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in chat completions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating strategy: {str(e)}")

@app.get("/v1/history", response_model=HistoryResponse)
async def get_history():
    """Get conversation history and analytics"""
    try:
        conn = sqlite3.connect('history.db')
        cursor = conn.cursor()
        
        # Get all conversations
        cursor.execute('''
            SELECT * FROM conversations 
            ORDER BY timestamp DESC 
            LIMIT 50
        ''')
        conversations = cursor.fetchall()
        
        # Get top performing strategies
        cursor.execute('''
            SELECT * FROM conversations 
            WHERE success_score > 0
            ORDER BY success_score DESC, earnings DESC
            LIMIT 10
        ''')
        top_performing = cursor.fetchall()
        
        conn.close()
        
        return HistoryResponse(
            conversations=[
                {
                    "id": row[0],
                    "prompt": row[2],
                    "response": row[3][:200] + "...",  # Truncated
                    "timestamp": row[4],
                    "success_score": row[5],
                    "earnings": row[6]
                }
                for row in conversations
            ],
            total_strategies=len(conversations),
            top_performing=[
                {
                    "id": row[0],
                    "prompt": row[2],
                    "success_score": row[5],
                    "earnings": row[6]
                }
                for row in top_performing
            ]
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")

@app.post("/v1/feedback")
async def submit_feedback(strategy_id: str, success_score: int, earnings: float = 0.0):
    """Submit feedback for a strategy to improve future recommendations"""
    try:
        conn = sqlite3.connect('history.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE conversations 
            SET success_score = ?, earnings = ?
            WHERE id = ?
        ''', (success_score, earnings, int(strategy_id)))
        
        conn.commit()
        conn.close()
        
        return {"status": "✅ Feedback submitted successfully", "strategy_id": strategy_id}
        
    except Exception as e:
        logger.error(f"❌ Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")

@app.get("/v1/top-strategies")
async def get_top_strategies():
    """Get top 3 recommended strategies for today"""
    try:
        # This would normally use ML to predict best strategies
        # For now, return curated high-success strategies
        
        top_strategies = [
            {
                "title": "Freelance Content Writing",
                "description": "Write articles for businesses and blogs",
                "estimated_earnings": "$100-300/day",
                "time_required": "4-6 hours",
                "difficulty": "Medium",
                "success_rate": 0.85
            },
            {
                "title": "Social Media Management",
                "description": "Manage social media accounts for small businesses",
                "estimated_earnings": "$50-200/day", 
                "time_required": "2-4 hours",
                "difficulty": "Easy",
                "success_rate": 0.75
            },
            {
                "title": "Online Tutoring",
                "description": "Teach subjects you're knowledgeable in",
                "estimated_earnings": "$75-250/day",
                "time_required": "3-5 hours", 
                "difficulty": "Medium",
                "success_rate": 0.80
            }
        ]
        
        return {
            "strategies": top_strategies,
            "generated_at": datetime.datetime.now().isoformat(),
            "next_update": "tomorrow_9am"
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting top strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting top strategies: {str(e)}")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and AI model on startup"""
    init_database()
    logger.info("🚀 Pegasus Wealth Engine API started successfully!")

if __name__ == "__main__":
    # Run the API server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=False,
        log_level="info"
    )