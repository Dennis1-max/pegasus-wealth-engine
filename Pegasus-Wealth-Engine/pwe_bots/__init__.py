"""
Pegasus Wealth Engine (PWE) Automation Bots
Autonomous money-making automation scripts
"""

from .blog_bot import run_blog_bot
from .ebook_bot import run_ebook_bot
from .freelance_bot import run_freelance_bot
from .email_bot import run_email_bot

__version__ = "1.0.0"
__author__ = "PWE Team"

# Available bot functions
AVAILABLE_BOTS = {
    "blog_bot": run_blog_bot,
    "ebook_bot": run_ebook_bot,
    "freelance_bot": run_freelance_bot,
    "email_bot": run_email_bot
}

def run_all_bots():
    """Run all available bots"""
    results = {}
    
    for bot_name, bot_function in AVAILABLE_BOTS.items():
        try:
            results[bot_name] = bot_function()
        except Exception as e:
            results[bot_name] = {"error": str(e)}
    
    return results

def get_bot_info():
    """Get information about available bots"""
    return {
        "blog_bot": {
            "name": "Blog Writing Bot",
            "description": "Automatically writes high-quality blog articles",
            "earnings_potential": "$50-200/article",
            "time_required": "15-30 minutes"
        },
        "ebook_bot": {
            "name": "eBook Creation Bot",
            "description": "Converts blogs to PDFs and uploads to Gumroad",
            "earnings_potential": "$100-500/ebook",
            "time_required": "30-60 minutes"
        },
        "freelance_bot": {
            "name": "Freelance Proposal Bot",
            "description": "Automates proposal sending on Upwork/Fiverr",
            "earnings_potential": "$500-2000/month",
            "time_required": "10-20 minutes"
        },
        "email_bot": {
            "name": "Email Outreach Bot",
            "description": "Sends professional proposals via email",
            "earnings_potential": "$200-1000/month",
            "time_required": "5-15 minutes"
        }
    }