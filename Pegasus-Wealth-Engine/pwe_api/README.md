# Pegasus Wealth Engine (PWE) API

🤖 **AI-powered autonomous money-making strategy generator**

The PWE API is the brain of the Pegasus Wealth Engine system, providing intelligent money-making strategies using Facebook's OPT-1.3B language model and learning from user feedback.

## ✨ Features

- **AI-Powered Strategies**: Uses facebook/opt-1.3b model for intelligent strategy generation
- **Memory System**: SQLite database stores all conversations and learns from feedback
- **Similar Query Detection**: Finds and improves upon similar past strategies
- **Performance Tracking**: Tracks success rates and earnings for continuous improvement
- **RESTful API**: Clean endpoints for integration with mobile/desktop apps
- **Automatic Fallback**: Works even when AI model is unavailable

## 📡 API Endpoints

### Health Check
```bash
GET /
# Returns: {"status": "✅ PWE API is running!", ...}
```

### Generate Strategy
```bash
POST /v1/chat/completions
Content-Type: application/json

{
  "prompt": "Earn me $500 today",
  "user_id": "optional_user_id",
  "context": {}
}
```

### Get History
```bash
GET /v1/history
# Returns conversation history and top performing strategies
```

### Submit Feedback
```bash
POST /v1/feedback
Content-Type: application/json

{
  "strategy_id": "123",
  "success_score": 8,
  "earnings": 250.0
}
```

### Get Top Strategies
```bash
GET /v1/top-strategies
# Returns top 3 recommended strategies for today
```

## 🚀 Quick Start

### Local Development

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Run the API**
```bash
python main.py
```

3. **Test the API**
```bash
curl http://localhost:8000/
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"prompt": "How can I earn $100 today?"}'
```

### Deploy to Render (Recommended)

1. **Connect to GitHub**
   - Push this code to your GitHub repository
   - Connect your Render account to GitHub

2. **Create New Web Service**
   - Choose your repository
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `python main.py`
   - Environment: `python-3.10`

3. **Environment Variables** (Optional)
   - `PORT`: Auto-set by Render
   - `PYTHONPATH`: `/opt/render/project/src`

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Get your API URL: `https://your-app-name.onrender.com`

### Deploy to Railway

1. **Connect Repository**
   - Link your GitHub repo to Railway
   - Railway auto-detects Python and installs requirements

2. **Set Start Command**
   - Add `Procfile`: `web: python main.py`
   - Or set start command in Railway dashboard

3. **Deploy**
   - Railway automatically deploys on git push
   - Get your URL from the Railway dashboard

### Deploy to Heroku

1. **Install Heroku CLI**
```bash
# Login to Heroku
heroku login

# Create new app
heroku create your-pwe-api

# Add Python buildpack
heroku buildpacks:add heroku/python

# Deploy
git add .
git commit -m "Deploy PWE API"
git push heroku main
```

2. **Scale the App**
```bash
heroku ps:scale web=1
```

## 🔧 Configuration

### Environment Variables

- `PORT`: Server port (default: 8000)
- `DATABASE_URL`: SQLite database path (default: history.db)
- `MODEL_NAME`: Hugging Face model (default: facebook/opt-1.3b)
- `DEBUG`: Enable debug mode (default: False)

### Database

The API automatically creates `history.db` SQLite database with these tables:

- **conversations**: Stores all prompts, responses, and feedback
- **strategies**: Categorized strategy templates and performance metrics

### AI Model

- **Primary**: facebook/opt-1.3b (1.3B parameters, good balance of quality/speed)
- **Fallback**: Rule-based strategy generation when model unavailable
- **Future**: Easy to upgrade to larger models (opt-6.7b, opt-30b, etc.)

## 📊 Monitoring

### Health Check
Monitor your API health:
```bash
curl https://your-api-url.onrender.com/
```

### Logs
View real-time logs:
```bash
# Render
View in Render dashboard > Logs

# Railway  
railway logs

# Heroku
heroku logs --tail
```

### Performance
- Average response time: 2-5 seconds
- Model loading time: 30-60 seconds (first request)
- Database queries: <100ms
- Memory usage: 4-8GB (with model loaded)

## 🔐 Security

- **CORS**: Configured to allow all origins (customize for production)
- **Rate Limiting**: Add nginx or CloudFlare for production
- **API Keys**: Add authentication middleware if needed
- **HTTPS**: Always use HTTPS in production

## 🛠️ Troubleshooting

### Model Loading Issues
```python
# If model fails to load, API falls back to rule-based strategies
# Check logs for specific errors:
# - Insufficient memory (need 4GB+ RAM)
# - Network issues downloading model
# - PyTorch/CUDA compatibility
```

### Database Issues
```python
# SQLite database is automatically created
# If corrupted, delete history.db and restart
# For production, consider PostgreSQL
```

### Memory Issues
```python
# Model requires 4-8GB RAM
# Use smaller model for limited resources:
# Change model_name to "facebook/opt-350m"
```

## 📈 Scaling

### Horizontal Scaling
- Deploy multiple instances behind load balancer
- Use shared database (PostgreSQL/MySQL)
- Cache responses with Redis

### Model Optimization
- Use model quantization (int8/int4)
- GPU acceleration with CUDA
- Model distillation for smaller footprint

### Database Optimization
- Add indexes for frequently queried columns
- Implement database connection pooling
- Use read replicas for analytics

## 🔄 Updates

The API is designed for easy updates:

1. **Model Upgrades**: Change `model_name` variable
2. **Feature Additions**: Add new endpoints to `main.py`
3. **Database Migrations**: Update schema in `init_database()`
4. **Dependency Updates**: Update `requirements.txt`

## 📝 API Documentation

Once deployed, visit your API URL for interactive documentation:
- Swagger UI: `https://your-api-url/docs`
- ReDoc: `https://your-api-url/redoc`

## 🆘 Support

For issues or questions:
1. Check the logs for error messages
2. Verify all dependencies are installed
3. Test locally before deploying
4. Ensure sufficient memory/CPU resources

## 🌟 Next Steps

After deployment:
1. **Test the API** with sample requests
2. **Configure the mobile app** to use your API URL
3. **Set up monitoring** and alerts
4. **Scale resources** based on usage
5. **Add authentication** for production use

---

🚀 **Your PWE API is now ready to power autonomous money-making strategies!**