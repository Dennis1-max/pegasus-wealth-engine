"""
eBook Creation and Publishing Bot for Pegasus Wealth Engine
Converts blog content to professional PDFs and uploads to Gumroad for passive income
"""

import os
import json
import glob
import datetime
import time
from typing import Dict, List, Any
import requests
from pathlib import Path

# PDF generation (install: pip install reportlab)
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ ReportLab not available. Install with: pip install reportlab")

class EBookGenerator:
    """Professional eBook generator and publisher"""
    
    def __init__(self):
        self.input_dir = "generated_blogs"
        self.output_dir = "generated_ebooks"
        self.ensure_output_dir()
        
        # Gumroad API settings (user needs to configure)
        self.gumroad_api_key = os.getenv("GUMROAD_API_KEY", "")
        self.gumroad_api_url = "https://api.gumroad.com/v2"
        
    def ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def find_blog_articles(self) -> List[str]:
        """Find available blog articles to convert"""
        if not os.path.exists(self.input_dir):
            return []
        
        # Find markdown files
        md_files = glob.glob(os.path.join(self.input_dir, "*.md"))
        return sorted(md_files, key=os.path.getmtime, reverse=True)  # Most recent first
    
    def read_article_content(self, filepath: str) -> Dict[str, Any]:
        """Read and parse article content"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Extract title (first line starting with #)
            title = "Untitled"
            for line in lines:
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
            
            # Extract metadata
            metadata = {}
            content_start = 0
            
            for i, line in enumerate(lines):
                if line.startswith('*') and ':' in line:
                    # Parse metadata like "*Published: Date*"
                    key_value = line.strip('*').split(':', 1)
                    if len(key_value) == 2:
                        metadata[key_value[0].strip()] = key_value[1].strip()
                elif line.startswith('# '):
                    content_start = i
                    break
            
            # Clean content for PDF
            clean_content = []
            skip_next = False
            
            for line in lines[content_start:]:
                if skip_next:
                    skip_next = False
                    continue
                    
                # Skip certain markdown elements
                if line.startswith('---') or line.startswith('*Tags:') or line.startswith('*This article'):
                    continue
                    
                clean_content.append(line)
            
            return {
                "title": title,
                "content": '\n'.join(clean_content),
                "metadata": metadata,
                "word_count": len(' '.join(clean_content).split()),
                "source_file": filepath
            }
            
        except Exception as e:
            print(f"Error reading article {filepath}: {e}")
            return None
    
    def create_ebook_bundle(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create an eBook bundle from multiple articles"""
        
        if not articles:
            return None
        
        # Determine bundle theme based on articles
        common_themes = self.extract_common_themes(articles)
        bundle_title = self.generate_bundle_title(common_themes, len(articles))
        
        # Create comprehensive eBook content
        bundle_content = self.create_bundle_content(bundle_title, articles)
        
        return {
            "title": bundle_title,
            "content": bundle_content,
            "article_count": len(articles),
            "total_word_count": sum(article["word_count"] for article in articles),
            "themes": common_themes,
            "articles": [article["title"] for article in articles]
        }
    
    def extract_common_themes(self, articles: List[Dict[str, Any]]) -> List[str]:
        """Extract common themes from articles"""
        
        # Simple keyword extraction from titles
        all_words = []
        for article in articles:
            title_words = article["title"].lower().split()
            all_words.extend(title_words)
        
        # Find most common meaningful words
        word_freq = {}
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "how", "what", "why", "when", "where"}
        
        for word in all_words:
            clean_word = ''.join(c for c in word if c.isalnum()).lower()
            if len(clean_word) > 3 and clean_word not in stop_words:
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
        
        # Return top themes
        sorted_themes = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [theme[0].title() for theme in sorted_themes[:3]]
    
    def generate_bundle_title(self, themes: List[str], article_count: int) -> str:
        """Generate an attractive bundle title"""
        
        year = datetime.datetime.now().year
        
        if themes:
            main_theme = themes[0]
            title_templates = [
                f"The Complete {main_theme} Guide: {article_count} Essential Articles",
                f"Master {main_theme}: A {article_count}-Part Series",
                f"{main_theme} Mastery Bundle: {article_count} Expert Insights",
                f"The Ultimate {main_theme} Collection ({year} Edition)",
                f"{article_count} Proven {main_theme} Strategies That Work"
            ]
            return title_templates[article_count % len(title_templates)]
        else:
            return f"The Complete Guide Collection: {article_count} Essential Articles"
    
    def create_bundle_content(self, title: str, articles: List[Dict[str, Any]]) -> str:
        """Create comprehensive eBook content"""
        
        content = f"# {title}\n\n"
        
        # Add cover page content
        content += f"""
*Published: {datetime.datetime.now().strftime('%B %Y')}*
*Edition: Digital PDF*
*Articles: {len(articles)}*
*Total Length: {sum(article['word_count'] for article in articles):,} words*

---

## About This Collection

This comprehensive guide brings together {len(articles)} carefully selected articles 
covering essential topics and strategies. Each article provides actionable insights 
and practical techniques you can implement immediately.

Whether you're a beginner looking to get started or an experienced professional 
seeking to refine your skills, this collection offers valuable perspectives and 
proven methods for success.

## What You'll Learn

"""
        
        # Add table of contents
        content += "## Table of Contents\n\n"
        for i, article in enumerate(articles, 1):
            content += f"{i}. {article['title']}\n"
        
        content += "\n---\n\n"
        
        # Add each article
        for i, article in enumerate(articles, 1):
            content += f"# Chapter {i}: {article['title']}\n\n"
            content += article['content'] + "\n\n"
            
            if i < len(articles):  # Don't add page break after last article
                content += "---\n\n"
        
        # Add conclusion
        content += self.create_bundle_conclusion(articles)
        
        return content
    
    def create_bundle_conclusion(self, articles: List[Dict[str, Any]]) -> str:
        """Create conclusion for the eBook bundle"""
        
        return f"""
# Conclusion

Thank you for reading this comprehensive collection of {len(articles)} articles. 
We've covered a wide range of topics and strategies designed to help you achieve 
your goals and succeed in your endeavors.

## Key Takeaways

- **Take Action**: Knowledge without action is worthless. Choose one strategy from 
  this collection and implement it this week.

- **Be Consistent**: Success comes from consistent effort over time. Apply these 
  principles regularly for best results.

- **Stay Updated**: The world is constantly changing. Keep learning and adapting 
  your strategies as needed.

- **Share Your Success**: When these strategies work for you, share your experience 
  to help others achieve similar results.

## What's Next?

1. **Review and Prioritize**: Go through your notes and identify the most relevant 
   strategies for your current situation.

2. **Create an Action Plan**: Choose 2-3 key strategies and create a step-by-step 
   implementation plan.

3. **Track Your Progress**: Monitor your results and adjust your approach based 
   on what works best for you.

4. **Connect with Others**: Join communities and networks of like-minded individuals 
   who share your interests and goals.

## Stay Connected

This collection represents just the beginning of your journey. Continue to seek 
out new knowledge, test different approaches, and refine your strategies based 
on real-world results.

Remember: every expert was once a beginner. The difference is that they took 
action and persisted through challenges. You have everything you need to succeed 
- now it's time to put these insights into practice.

---

*© {datetime.datetime.now().year} - This digital product is for personal use only. 
Redistribution or resale is prohibited without express written permission.*

**Thank you for your purchase and commitment to continuous learning!**
"""
    
    def convert_to_pdf(self, ebook_data: Dict[str, Any]) -> str:
        """Convert eBook content to PDF"""
        
        if not PDF_AVAILABLE:
            # Create simple text file instead
            return self.create_text_fallback(ebook_data)
        
        try:
            # Create safe filename
            safe_title = "".join(c for c in ebook_data['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')[:50]
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{safe_title}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Create custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.darkblue,
                spaceAfter=30,
                alignment=1  # Center
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.darkblue,
                spaceBefore=20,
                spaceAfter=12
            )
            
            body_style = ParagraphStyle(
                'CustomBody',
                parent=styles['Normal'],
                fontSize=11,
                leading=14,
                spaceBefore=6,
                spaceAfter=6
            )
            
            # Build PDF content
            story = []
            
            # Process content line by line
            lines = ebook_data['content'].split('\n')
            
            for line in lines:
                line = line.strip()
                
                if not line:
                    story.append(Spacer(1, 6))
                elif line.startswith('# '):
                    # Main title or chapter title
                    title_text = line[2:].strip()
                    story.append(Paragraph(title_text, title_style))
                    story.append(Spacer(1, 20))
                elif line.startswith('## '):
                    # Section heading
                    heading_text = line[3:].strip()
                    story.append(Paragraph(heading_text, heading_style))
                elif line.startswith('### '):
                    # Subsection
                    sub_text = line[4:].strip()
                    story.append(Paragraph(f"<b>{sub_text}</b>", body_style))
                elif line.startswith('---'):
                    # Page break or separator
                    story.append(PageBreak())
                elif line.startswith('*') and line.endswith('*'):
                    # Italic metadata
                    meta_text = line[1:-1]
                    story.append(Paragraph(f"<i>{meta_text}</i>", body_style))
                elif line.startswith('**') and line.endswith('**'):
                    # Bold text
                    bold_text = line[2:-2]
                    story.append(Paragraph(f"<b>{bold_text}</b>", body_style))
                else:
                    # Regular paragraph
                    if line:
                        # Clean up markdown-style formatting
                        clean_line = line.replace('**', '').replace('*', '')
                        story.append(Paragraph(clean_line, body_style))
            
            # Build PDF
            doc.build(story)
            
            return filepath
            
        except Exception as e:
            print(f"Error creating PDF: {e}")
            return self.create_text_fallback(ebook_data)
    
    def create_text_fallback(self, ebook_data: Dict[str, Any]) -> str:
        """Create text file fallback when PDF creation fails"""
        
        safe_title = "".join(c for c in ebook_data['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')[:50]
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{safe_title}.txt"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(ebook_data['content'])
        
        return filepath
    
    def upload_to_gumroad(self, ebook_path: str, ebook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload eBook to Gumroad for sale"""
        
        if not self.gumroad_api_key:
            return {
                "status": "skipped",
                "reason": "Gumroad API key not configured",
                "setup_instructions": [
                    "1. Create a Gumroad account at gumroad.com",
                    "2. Go to Settings > Advanced > API",
                    "3. Generate API key",
                    "4. Set environment variable: GUMROAD_API_KEY=your_key",
                    "5. Re-run the eBook bot"
                ]
            }
        
        try:
            # Prepare product data
            price = self.calculate_suggested_price(ebook_data)
            
            product_data = {
                "name": ebook_data['title'],
                "description": self.create_product_description(ebook_data),
                "price": price,
                "url": self.create_product_url(ebook_data['title']),
                "published": "true",
                "require_shipping": "false",
                "content_type": "digital"
            }
            
            # Create product
            headers = {
                "Authorization": f"Bearer {self.gumroad_api_key}",
                "Content-Type": "application/json"
            }
            
            # Note: This is a simplified example. 
            # Actual Gumroad API implementation would require file upload handling
            response = requests.post(
                f"{self.gumroad_api_url}/products",
                headers=headers,
                json=product_data,
                timeout=30
            )
            
            if response.status_code == 200:
                product_info = response.json()
                return {
                    "status": "success",
                    "product_id": product_info.get("product", {}).get("id"),
                    "product_url": product_info.get("product", {}).get("short_url"),
                    "price": price,
                    "upload_method": "API"
                }
            else:
                return {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "manual_upload_required": True
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "manual_upload_guide": [
                    "1. Go to gumroad.com and log in",
                    "2. Click 'Upload' to create new product",
                    "3. Upload your PDF file",
                    "4. Set title, description, and price",
                    "5. Publish and share your product link"
                ]
            }
    
    def calculate_suggested_price(self, ebook_data: Dict[str, Any]) -> int:
        """Calculate suggested price based on content"""
        
        # Base price calculation
        word_count = ebook_data.get('total_word_count', 0)
        article_count = ebook_data.get('article_count', 1)
        
        # Price per 1000 words
        base_price = max(5, (word_count // 1000) * 3)
        
        # Bonus for multiple articles
        multi_article_bonus = max(0, (article_count - 1) * 2)
        
        # Final price (in cents for Gumroad API)
        suggested_price = (base_price + multi_article_bonus) * 100
        
        # Price ranges: $5-50
        return max(500, min(5000, suggested_price))
    
    def create_product_description(self, ebook_data: Dict[str, Any]) -> str:
        """Create compelling product description"""
        
        return f"""
📚 **{ebook_data['title']}**

Get instant access to this comprehensive {ebook_data.get('article_count', 1)}-part guide covering essential strategies and actionable insights.

**What's Included:**
• {ebook_data.get('total_word_count', 0):,} words of expert content
• {ebook_data.get('article_count', 1)} detailed articles/chapters
• Practical tips and real-world examples
• Actionable strategies you can implement immediately

**Perfect For:**
✅ Entrepreneurs and business owners
✅ Professionals seeking to improve their skills
✅ Anyone looking for practical, actionable advice
✅ Students and continuous learners

**Instant Download:** PDF format, compatible with all devices

💡 **Bonus:** Lifetime access and any future updates included!

---

⭐ Don't wait - start implementing these strategies today!
"""
    
    def create_product_url(self, title: str) -> str:
        """Create SEO-friendly product URL"""
        clean_title = "".join(c for c in title.lower() if c.isalnum() or c == ' ')
        url_slug = clean_title.replace(' ', '-')[:50].rstrip('-')
        return url_slug

def run_ebook_bot() -> Dict[str, Any]:
    """Main function to run the eBook creation and publishing bot"""
    
    try:
        print("📚 Starting eBook Creation Bot...")
        start_time = time.time()
        
        # Initialize eBook generator
        generator = EBookGenerator()
        
        # Find blog articles
        print("🔍 Searching for blog articles...")
        article_files = generator.find_blog_articles()
        
        if not article_files:
            return {
                "status": "no_content",
                "message": "No blog articles found to convert",
                "suggestion": "Run the blog bot first to generate content"
            }
        
        print(f"📄 Found {len(article_files)} blog articles")
        
        # Read articles (up to 5 for a good bundle)
        articles = []
        for filepath in article_files[:5]:
            article_data = generator.read_article_content(filepath)
            if article_data:
                articles.append(article_data)
        
        if not articles:
            return {
                "status": "error",
                "message": "Could not read any article content"
            }
        
        print(f"📖 Processing {len(articles)} articles for eBook...")
        
        # Create eBook bundle
        print("🎨 Creating eBook bundle...")
        ebook_data = generator.create_ebook_bundle(articles)
        
        if not ebook_data:
            return {
                "status": "error", 
                "message": "Could not create eBook bundle"
            }
        
        # Convert to PDF
        print("📄 Converting to PDF...")
        pdf_path = generator.convert_to_pdf(ebook_data)
        
        # Upload to Gumroad
        print("🚀 Uploading to Gumroad...")
        upload_result = generator.upload_to_gumroad(pdf_path, ebook_data)
        
        runtime = time.time() - start_time
        
        result = {
            "status": "success",
            "ebook_title": ebook_data['title'],
            "articles_included": ebook_data['article_count'],
            "total_word_count": ebook_data['total_word_count'],
            "pdf_file": pdf_path,
            "file_size_mb": round(os.path.getsize(pdf_path) / (1024*1024), 2) if os.path.exists(pdf_path) else 0,
            "suggested_price": f"${generator.calculate_suggested_price(ebook_data) / 100:.2f}",
            "upload_result": upload_result,
            "runtime_seconds": round(runtime, 2),
            "monetization_potential": {
                "digital_sales": "$50-500/month per ebook",
                "bundle_deals": "$100-1000/month",
                "affiliate_commissions": "10-50% per sale",
                "licensing": "$200-2000/license"
            },
            "next_steps": [
                "Set up Gumroad account if not done",
                "Upload PDF manually if API failed",
                "Create marketing materials",
                "Share on social media",
                "Add to email marketing campaigns",
                "Create video previews",
                "Set up affiliate program"
            ]
        }
        
        print(f"✅ eBook created successfully!")
        print(f"📘 Title: {result['ebook_title']}")
        print(f"📊 Articles: {result['articles_included']}")
        print(f"📈 Words: {result['total_word_count']:,}")
        print(f"💰 Suggested price: {result['suggested_price']}")
        print(f"⏱️ Creation time: {result['runtime_seconds']}s")
        
        return result
        
    except Exception as e:
        error_result = {
            "status": "error",
            "error_message": str(e),
            "error_type": type(e).__name__,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        print(f"❌ eBook bot failed: {str(e)}")
        return error_result

if __name__ == "__main__":
    # Test the eBook bot
    result = run_ebook_bot()
    print(json.dumps(result, indent=2))