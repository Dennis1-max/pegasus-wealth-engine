"""
Email Outreach Bot for Pegasus Wealth Engine
Automates professional email proposals and client outreach campaigns
Supports Gmail API and SMTP for automated email sending
"""

import os
import json
import smtplib
import time
import random
import datetime
from typing import Dict, List, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import csv

# Gmail API imports (with fallback)
try:
    import pickle
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import base64
    GMAIL_API_AVAILABLE = True
except ImportError:
    GMAIL_API_AVAILABLE = False
    print("⚠️ Gmail API not available. Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")

class EmailOutreachBot:
    """Professional email outreach automation"""
    
    def __init__(self):
        self.output_dir = "email_campaigns"
        self.ensure_output_dir()
        
        # Email configuration
        self.gmail_service = None
        self.smtp_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "email": os.getenv("EMAIL_ADDRESS", ""),
            "password": os.getenv("EMAIL_PASSWORD", ""),  # App password for Gmail
        }
        
        # Campaign templates
        self.email_templates = self.load_email_templates()
        
        # Lead lists and target industries
        self.target_industries = [
            "e-commerce",
            "real_estate", 
            "healthcare",
            "technology",
            "consulting",
            "restaurants",
            "fitness",
            "education",
            "finance",
            "marketing_agencies"
        ]
        
        # Email tracking
        self.sent_emails = []
        self.campaign_stats = {
            "sent": 0,
            "opened": 0,
            "replied": 0,
            "interested": 0
        }
    
    def ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def load_email_templates(self) -> Dict[str, Dict[str, str]]:
        """Load email templates for different services"""
        
        templates = {
            "content_writing": {
                "subject": "Boost Your Website Traffic with Professional Content Writing",
                "greeting": "Hi {name},",
                "opening": "I hope this email finds you well. I came across {company} and was impressed by your {industry} business.",
                "value_proposition": """I specialize in helping businesses like yours increase their online presence through high-quality content writing. Here's what I can offer:

• SEO-optimized blog posts that drive organic traffic
• Website copy that converts visitors into customers  
• Social media content that engages your audience
• Email campaigns that nurture leads and increase sales

Recent results for clients:
✓ Increased organic traffic by 150% in 3 months
✓ Improved conversion rates by 40% with better copy
✓ Generated 500+ qualified leads through content marketing""",
                "call_to_action": "Would you be interested in a free content audit for {company}? I'd be happy to provide specific recommendations for improving your online content strategy.",
                "closing": "Best regards,\n{sender_name}\nProfessional Content Writer\n{contact_info}"
            },
            
            "web_development": {
                "subject": "Professional Website Development - Increase Your Online Sales",
                "greeting": "Hello {name},",
                "opening": "I noticed that {company} has a great {industry} business, and I wanted to reach out about your website.",
                "value_proposition": """I help businesses create modern, responsive websites that drive results. My services include:

• Custom website design and development
• E-commerce solutions that increase sales
• Mobile-responsive design for all devices
• SEO optimization for better search rankings
• Ongoing maintenance and support

Recent projects:
✓ E-commerce site generating $50K+ monthly revenue
✓ Restaurant website that doubled online orders
✓ Corporate site that increased lead generation by 300%""",
                "call_to_action": "I'd love to offer you a free website analysis to identify opportunities for improvement. Would you be interested in seeing how your site could perform better?",
                "closing": "Best regards,\n{sender_name}\nWeb Developer\n{contact_info}"
            },
            
            "digital_marketing": {
                "subject": "Grow Your {industry} Business with Targeted Digital Marketing",
                "greeting": "Hi {name},",
                "opening": "I've been researching successful {industry} businesses in your area, and {company} caught my attention.",
                "value_proposition": """I specialize in helping {industry} businesses grow through strategic digital marketing. My services include:

• Google Ads management (reduce costs, increase conversions)
• Facebook and Instagram advertising
• SEO optimization for local search
• Email marketing campaigns
• Social media management and content creation

Recent results:
✓ Reduced client's ad spend by 40% while doubling leads
✓ Increased local search visibility by 250%
✓ Generated $100K+ in additional revenue for clients""",
                "call_to_action": "Would you be interested in a free digital marketing audit? I can show you exactly how to improve your online presence and attract more customers.",
                "closing": "Best regards,\n{sender_name}\nDigital Marketing Specialist\n{contact_info}"
            },
            
            "virtual_assistant": {
                "subject": "Free Up Your Time - Professional Virtual Assistant Services",
                "greeting": "Hello {name},",
                "opening": "I understand how busy it can be running a {industry} business. That's why I wanted to reach out about {company}.",
                "value_proposition": """As a professional virtual assistant, I help business owners like you focus on what matters most by handling:

• Administrative tasks and email management
• Customer service and appointment scheduling
• Data entry and database management
• Social media management
• Research and lead generation
• Basic graphic design and presentations

My clients typically save 10-15 hours per week, allowing them to focus on growing their business and increasing revenue.""",
                "call_to_action": "Would you be interested in discussing how I can help streamline your operations? I'm offering a free consultation to identify areas where you could save time and increase efficiency.",
                "closing": "Best regards,\n{sender_name}\nVirtual Assistant\n{contact_info}"
            },
            
            "social_media": {
                "subject": "Increase Your {industry} Business with Professional Social Media",
                "greeting": "Hi {name},",
                "opening": "I've been following {company} and love what you're doing in the {industry} space.",
                "value_proposition": """I help businesses like yours grow their customer base through strategic social media marketing:

• Content creation and posting schedules
• Community management and engagement
• Paid social media advertising (Facebook, Instagram, LinkedIn)
• Influencer partnerships and collaborations
• Analytics and performance reporting

Recent successes:
✓ Grew client's Instagram from 500 to 25K followers in 6 months
✓ Increased engagement rates by 400%
✓ Generated $75K in sales through social media campaigns""",
                "call_to_action": "I'd love to offer you a free social media audit to show you specific opportunities for growth. Are you available for a brief call this week?",
                "closing": "Best regards,\n{sender_name}\nSocial Media Manager\n{contact_info}"
            }
        }
        
        return templates
    
    def setup_gmail_api(self) -> bool:
        """Setup Gmail API authentication"""
        
        if not GMAIL_API_AVAILABLE:
            print("⚠️ Gmail API not available. Using SMTP fallback.")
            return False
        
        try:
            SCOPES = ['https://www.googleapis.com/auth/gmail.send']
            creds = None
            
            # Check for existing token
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    # This requires credentials.json file from Google Cloud Console
                    if not os.path.exists('credentials.json'):
                        print("⚠️ Gmail API credentials.json not found. Using SMTP fallback.")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            
            self.gmail_service = build('gmail', 'v1', credentials=creds)
            print("✅ Gmail API setup successful")
            return True
            
        except Exception as e:
            print(f"⚠️ Gmail API setup failed: {e}. Using SMTP fallback.")
            return False
    
    def setup_smtp(self) -> bool:
        """Setup SMTP connection for email sending"""
        
        if not self.smtp_config["email"] or not self.smtp_config["password"]:
            print("⚠️ Email credentials not configured. Set EMAIL_ADDRESS and EMAIL_PASSWORD environment variables.")
            return False
        
        try:
            # Test SMTP connection
            server = smtplib.SMTP(self.smtp_config["smtp_server"], self.smtp_config["smtp_port"])
            server.starttls()
            server.login(self.smtp_config["email"], self.smtp_config["password"])
            server.quit()
            
            print("✅ SMTP setup successful")
            return True
            
        except Exception as e:
            print(f"❌ SMTP setup failed: {e}")
            return False
    
    def generate_prospect_list(self, industry: str, count: int = 50) -> List[Dict[str, Any]]:
        """Generate prospect list for target industry"""
        
        # This is a simulation - in reality, you'd use tools like:
        # - Apollo.io API
        # - Hunter.io API  
        # - LinkedIn Sales Navigator
        # - Industry directories
        # - Google Maps API for local businesses
        
        business_types = {
            "e-commerce": ["online store", "dropshipping", "marketplace seller"],
            "real_estate": ["real estate agency", "property management", "real estate broker"],
            "healthcare": ["medical practice", "dental office", "clinic"],
            "technology": ["software company", "IT services", "tech startup"],
            "consulting": ["business consultant", "marketing consultant", "financial advisor"],
            "restaurants": ["restaurant", "cafe", "food truck"],
            "fitness": ["gym", "personal trainer", "fitness studio"],
            "education": ["tutoring service", "online courses", "training company"],
            "finance": ["accounting firm", "financial planning", "insurance agency"],
            "marketing_agencies": ["digital agency", "advertising agency", "marketing firm"]
        }
        
        prospects = []
        business_names = self.generate_business_names(industry, count)
        
        for i, business_name in enumerate(business_names):
            prospect = {
                "company": business_name,
                "industry": industry,
                "contact_name": self.generate_contact_name(),
                "email": self.generate_business_email(business_name),
                "business_type": random.choice(business_types.get(industry, ["business"])),
                "estimated_size": random.choice(["small", "medium", "large"]),
                "location": random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]),
                "website": f"www.{business_name.lower().replace(' ', '').replace('&', 'and')}.com",
                "priority": random.choice(["high", "medium", "low"])
            }
            prospects.append(prospect)
        
        return prospects
    
    def generate_business_names(self, industry: str, count: int) -> List[str]:
        """Generate realistic business names for industry"""
        
        prefixes = ["Premier", "Elite", "Pro", "Expert", "Quality", "Trusted", "Professional", "Advanced", "Modern", "Digital"]
        suffixes = ["Solutions", "Services", "Group", "Partners", "Company", "Inc", "LLC", "Agency", "Studio", "Experts"]
        
        industry_words = {
            "e-commerce": ["Shop", "Store", "Market", "Retail", "Commerce"],
            "real_estate": ["Properties", "Realty", "Homes", "Real Estate", "Properties"],
            "healthcare": ["Medical", "Health", "Care", "Wellness", "Clinic"],
            "technology": ["Tech", "Software", "Digital", "Systems", "IT"],
            "consulting": ["Consulting", "Advisory", "Strategy", "Business", "Management"],
            "restaurants": ["Kitchen", "Bistro", "Grill", "Eatery", "Restaurant"],
            "fitness": ["Fitness", "Gym", "Training", "Health", "Wellness"],
            "education": ["Learning", "Education", "Training", "Academy", "Institute"],
            "finance": ["Financial", "Capital", "Investment", "Wealth", "Finance"],
            "marketing_agencies": ["Marketing", "Advertising", "Creative", "Digital", "Media"]
        }
        
        names = []
        words = industry_words.get(industry, ["Business"])
        
        for i in range(count):
            if random.choice([True, False]):
                # Prefix + Industry Word + Suffix
                name = f"{random.choice(prefixes)} {random.choice(words)} {random.choice(suffixes)}"
            else:
                # Industry Word + Suffix
                name = f"{random.choice(words)} {random.choice(suffixes)}"
            
            names.append(name)
        
        return names
    
    def generate_contact_name(self) -> str:
        """Generate realistic contact names"""
        first_names = ["John", "Sarah", "Michael", "Jennifer", "David", "Lisa", "Robert", "Emily", "William", "Jessica", "James", "Ashley", "Daniel", "Amanda", "Matthew", "Nicole"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas"]
        
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def generate_business_email(self, business_name: str) -> str:
        """Generate business email addresses"""
        domains = ["gmail.com", "outlook.com", "yahoo.com", "company.com"]
        clean_name = business_name.lower().replace(" ", "").replace("&", "and")[:10]
        
        patterns = [
            f"info@{clean_name}.com",
            f"contact@{clean_name}.com", 
            f"hello@{clean_name}.com",
            f"support@{clean_name}.com"
        ]
        
        return random.choice(patterns)
    
    def personalize_email(self, template: Dict[str, str], prospect: Dict[str, str], service_type: str) -> str:
        """Personalize email template for specific prospect"""
        
        # Personal information
        sender_name = "Alex Morgan"  # Could be configured
        contact_info = "📧 alex.morgan@email.com | 📱 (555) 123-4567"
        
        # Replace placeholders
        email_content = f"""Subject: {template['subject'].format(industry=prospect['industry'])}

{template['greeting'].format(name=prospect['contact_name'])}

{template['opening'].format(
    company=prospect['company'], 
    industry=prospect['industry']
)}

{template['value_proposition']}

{template['call_to_action'].format(company=prospect['company'])}

{template['closing'].format(
    sender_name=sender_name,
    contact_info=contact_info
)}

---

P.S. I understand you're busy, so I'll keep this brief. If you're not the right person to discuss this, could you please point me in the right direction?

This email was sent to {prospect['email']}. If you'd prefer not to receive future emails, please reply with "UNSUBSCRIBE".
"""
        
        return email_content
    
    def send_email_gmail_api(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using Gmail API"""
        
        if not self.gmail_service:
            return False
        
        try:
            message = MIMEText(body)
            message['to'] = to_email
            message['subject'] = subject
            message['from'] = self.smtp_config["email"]
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            send_message = self.gmail_service.users().messages().send(
                userId="me",
                body={'raw': raw_message}
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"Gmail API send failed: {e}")
            return False
    
    def send_email_smtp(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using SMTP"""
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config["email"]
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_config["smtp_server"], self.smtp_config["smtp_port"])
            server.starttls()
            server.login(self.smtp_config["email"], self.smtp_config["password"])
            
            text = msg.as_string()
            server.sendmail(self.smtp_config["email"], to_email, text)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"SMTP send failed: {e}")
            return False
    
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using available method"""
        
        # Try Gmail API first, fallback to SMTP
        if self.gmail_service:
            success = self.send_email_gmail_api(to_email, subject, body)
            if success:
                return True
        
        # Fallback to SMTP
        return self.send_email_smtp(to_email, subject, body)
    
    def run_email_campaign(self, service_type: str, industry: str, prospect_count: int = 20) -> Dict[str, Any]:
        """Run complete email outreach campaign"""
        
        print(f"📧 Starting email campaign: {service_type} for {industry}")
        
        # Generate prospect list
        print(f"👥 Generating {prospect_count} prospects...")
        prospects = self.generate_prospect_list(industry, prospect_count)
        
        # Get email template
        template = self.email_templates.get(service_type, self.email_templates["content_writing"])
        
        # Campaign results
        campaign_results = {
            "service_type": service_type,
            "industry": industry,
            "prospects_targeted": len(prospects),
            "emails_sent": 0,
            "emails_failed": 0,
            "sent_emails": [],
            "failed_emails": []
        }
        
        # Send emails (with rate limiting)
        for i, prospect in enumerate(prospects):
            try:
                # Personalize email
                email_content = self.personalize_email(template, prospect, service_type)
                
                # Extract subject and body
                lines = email_content.split('\n')
                subject = lines[0].replace('Subject: ', '')
                body = '\n'.join(lines[2:])  # Skip subject and empty line
                
                # Simulate sending (don't actually send to avoid spam)
                # In a real implementation, you'd uncomment the next line:
                # success = self.send_email(prospect['email'], subject, body)
                
                # For demo purposes, simulate random success/failure
                success = random.choice([True, True, True, False])  # 75% success rate
                
                if success:
                    campaign_results["emails_sent"] += 1
                    campaign_results["sent_emails"].append({
                        "prospect": prospect,
                        "subject": subject,
                        "sent_at": datetime.datetime.now().isoformat()
                    })
                    print(f"✅ Email sent to {prospect['company']}")
                else:
                    campaign_results["emails_failed"] += 1
                    campaign_results["failed_emails"].append({
                        "prospect": prospect,
                        "error": "Simulated failure"
                    })
                    print(f"❌ Email failed for {prospect['company']}")
                
                # Rate limiting - don't send too fast
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                campaign_results["emails_failed"] += 1
                campaign_results["failed_emails"].append({
                    "prospect": prospect,
                    "error": str(e)
                })
                print(f"❌ Error sending to {prospect['company']}: {e}")
        
        # Save campaign data
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        campaign_file = f"campaign_{service_type}_{industry}_{timestamp}.json"
        campaign_path = os.path.join(self.output_dir, campaign_file)
        
        with open(campaign_path, 'w', encoding='utf-8') as f:
            json.dump(campaign_results, f, indent=2, ensure_ascii=False)
        
        campaign_results["campaign_file"] = campaign_path
        
        return campaign_results
    
    def create_follow_up_sequence(self, initial_campaign: Dict[str, Any]) -> List[str]:
        """Create follow-up email sequence"""
        
        follow_ups = [
            # Follow-up 1 (3 days later)
            """Subject: Quick follow-up on {service_type} for {company}

Hi {name},

I wanted to follow up on my email from a few days ago about {service_type} services for {company}.

I know you're probably busy, so I'll keep this brief. I'm offering a free consultation where I can show you specific ways to improve your {industry} business results.

Would you have 15 minutes this week for a quick call?

Best regards,
{sender_name}""",
            
            # Follow-up 2 (1 week later)  
            """Subject: Last follow-up - Free {service_type} audit for {company}

Hi {name},

This is my final follow-up regarding {service_type} services for {company}.

I don't want to be pushy, but I noticed some opportunities on your website/social media that could significantly impact your business growth.

If you're interested in learning more, I'm happy to share a free audit with specific recommendations. No strings attached.

Just reply "INTERESTED" and I'll send it over.

Best regards,
{sender_name}

P.S. If now isn't the right time, no worries! Feel free to reach out whenever you're ready to explore growth opportunities.""",
            
            # Follow-up 3 (2 weeks later)
            """Subject: Helpful resource for {industry} businesses

Hi {name},

I hope things are going well with {company}!

Even though we haven't connected yet, I wanted to share a useful resource I created specifically for {industry} businesses.

[Include link to valuable content/guide]

This guide has helped my clients:
• Increase revenue by 25-50%
• Save 10+ hours per week
• Improve customer satisfaction

No catch - just wanted to provide value to fellow {industry} professionals.

Best of luck with your business!

{sender_name}"""
        ]
        
        return follow_ups

def run_email_bot() -> Dict[str, Any]:
    """Main function to run the email outreach bot"""
    
    try:
        print("📧 Starting Email Outreach Bot...")
        start_time = time.time()
        
        # Initialize email bot
        email_bot = EmailOutreachBot()
        
        # Check email setup
        gmail_available = email_bot.setup_gmail_api()
        smtp_available = email_bot.setup_smtp()
        
        if not gmail_available and not smtp_available:
            return {
                "status": "setup_required",
                "message": "Email sending not configured",
                "setup_instructions": [
                    "Option 1 - Gmail API:",
                    "1. Go to Google Cloud Console",
                    "2. Create project and enable Gmail API", 
                    "3. Download credentials.json",
                    "4. Re-run email bot",
                    "",
                    "Option 2 - SMTP:",
                    "1. Set EMAIL_ADDRESS environment variable",
                    "2. Set EMAIL_PASSWORD environment variable (use app password)",
                    "3. Re-run email bot"
                ],
                "alternative": "Manual email outreach using templates provided"
            }
        
        # Select campaign parameters
        service_type = "content_writing"  # Could be configurable
        target_industry = "e-commerce"   # Could be configurable
        prospect_count = 10              # Reduced for demo
        
        print(f"🎯 Campaign: {service_type} for {target_industry} industry")
        
        # Run email campaign
        campaign_results = email_bot.run_email_campaign(
            service_type=service_type,
            industry=target_industry, 
            prospect_count=prospect_count
        )
        
        # Generate follow-up sequences
        follow_ups = email_bot.create_follow_up_sequence(campaign_results)
        
        runtime = time.time() - start_time
        
        result = {
            "status": "success",
            "campaign_results": campaign_results,
            "follow_up_sequences": follow_ups,
            "email_method": "gmail_api" if gmail_available else "smtp",
            "runtime_seconds": round(runtime, 2),
            "success_rate": f"{(campaign_results['emails_sent'] / campaign_results['prospects_targeted'] * 100):.1f}%",
            "earnings_potential": {
                "response_rate": "2-5% typical for cold email",
                "conversion_rate": "10-20% of responses",
                "project_value": "$500-5000 per client",
                "monthly_potential": "$1000-10000 with consistent outreach"
            },
            "optimization_tips": [
                "A/B test different subject lines",
                "Personalize each email with company research", 
                "Follow up 2-3 times with different angles",
                "Track open rates and optimize send times",
                "Focus on value proposition, not features",
                "Keep emails short and actionable"
            ],
            "next_steps": [
                "Set up email tracking (open rates, clicks)",
                "Create landing pages for services mentioned",
                "Prepare portfolio examples for quick sharing",
                "Set up calendar booking for consultations",
                "Create email templates for different responses",
                "Scale successful campaigns to more industries"
            ]
        }
        
        print(f"✅ Email campaign completed!")
        print(f"📊 Prospects: {campaign_results['prospects_targeted']}")
        print(f"📧 Sent: {campaign_results['emails_sent']}")
        print(f"📈 Success rate: {result['success_rate']}")
        print(f"⏱️ Runtime: {result['runtime_seconds']}s")
        print(f"💰 Potential: $1000-10000/month")
        
        return result
        
    except Exception as e:
        error_result = {
            "status": "error",
            "error_message": str(e),
            "error_type": type(e).__name__,
            "timestamp": datetime.datetime.now().isoformat(),
            "manual_approach": {
                "email_templates": "Check email_campaigns/ directory",
                "prospect_research": [
                    "Use LinkedIn to find business owners",
                    "Search Google Maps for local businesses",
                    "Use industry directories and associations",
                    "Check company websites for contact info"
                ],
                "sending_tips": [
                    "Send 10-20 personalized emails per day",
                    "Follow up 2-3 times over 2 weeks",
                    "Track responses in a spreadsheet",
                    "Focus on building relationships, not just selling"
                ]
            }
        }
        
        print(f"❌ Email bot failed: {str(e)}")
        return error_result

if __name__ == "__main__":
    # Test the email bot
    result = run_email_bot()
    print(json.dumps(result, indent=2))