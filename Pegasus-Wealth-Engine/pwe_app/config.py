"""
Configuration file for Pegasus Wealth Engine App
Modify these settings based on your deployment
"""

import os

class Config:
    """Configuration settings for PWE App"""
    
    # API Configuration
    # Replace with your deployed API URL
    API_BASE_URL = os.getenv("PWE_API_URL", "http://localhost:8000")
    
    # For deployed API, use one of these examples:
    # API_BASE_URL = "https://your-pwe-api.onrender.com"
    # API_BASE_URL = "https://your-pwe-api.railway.app"
    # API_BASE_URL = "https://your-pwe-api.herokuapp.com"
    
    # App Settings
    APP_NAME = "Pegasus Wealth Engine"
    APP_VERSION = "1.0.0"
    
    # Database Settings
    LOCAL_DB_NAME = "pwe_app_history.db"
    
    # Voice Recognition Settings
    VOICE_TIMEOUT = 5  # seconds
    VOICE_PHRASE_LIMIT = 10  # seconds
    
    # Bot Automation Settings
    BOT_AUTO_RUN = False
    BOT_SCHEDULE_MORNING = "09:00"
    BOT_SCHEDULE_EVENING = "18:00"
    
    # UI Settings
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    THEME_COLOR = [0.2, 0.4, 0.8, 1]  # Blue theme
    
    # API Timeouts
    API_TIMEOUT = 30  # seconds for strategy generation
    API_HEALTH_TIMEOUT = 10  # seconds for health checks
    
    # Automation Settings
    MAX_CONCURRENT_BOTS = 4
    BOT_RETRY_ATTEMPTS = 3
    BOT_RETRY_DELAY = 5  # seconds
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "pwe_app.log"
    
    # Security (for future use)
    API_KEY = os.getenv("PWE_API_KEY", None)
    USER_TOKEN = os.getenv("PWE_USER_TOKEN", None)
    
    @classmethod
    def get_api_headers(cls):
        """Get API headers with authentication if available"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"{cls.APP_NAME}/{cls.APP_VERSION}"
        }
        
        if cls.API_KEY:
            headers["X-API-Key"] = cls.API_KEY
        
        if cls.USER_TOKEN:
            headers["Authorization"] = f"Bearer {cls.USER_TOKEN}"
        
        return headers
    
    @classmethod
    def validate_api_url(cls, url: str) -> bool:
        """Validate API URL format"""
        return url.startswith(("http://", "https://")) and len(url) > 10
    
    @classmethod
    def update_api_url(cls, new_url: str):
        """Update API URL with validation"""
        if cls.validate_api_url(new_url):
            cls.API_BASE_URL = new_url.rstrip('/')
            return True
        return False

# Development/Testing Configurations
class DevelopmentConfig(Config):
    """Development configuration"""
    API_BASE_URL = "http://localhost:8000"
    LOG_LEVEL = "DEBUG"
    BOT_AUTO_RUN = False

class ProductionConfig(Config):
    """Production configuration"""
    # Set your production API URL here
    API_BASE_URL = os.getenv("PWE_API_URL", "https://your-pwe-api.onrender.com")
    LOG_LEVEL = "INFO"
    BOT_AUTO_RUN = True

# Select configuration based on environment
ENV = os.getenv("PWE_ENV", "development").lower()

if ENV == "production":
    Config = ProductionConfig
elif ENV == "development":
    Config = DevelopmentConfig

# Export for easy importing
__all__ = ["Config"]