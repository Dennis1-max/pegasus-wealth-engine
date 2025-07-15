"""
Pegasus Wealth Engine (PWE) App
Cross-platform mobile and desktop app for autonomous money-making
Built with Kivy for Android APK and PC EXE compatibility
"""

import os
import sys
import json
import sqlite3
import threading
import datetime
import asyncio
from typing import Dict, List, Any
import requests
import schedule
import time

# Kivy imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.switch import Switch
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.core.window import Window

# Voice recognition imports (with fallback)
try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    Logger.warning("Voice recognition not available. Install speech_recognition for voice control.")

# Configuration
from config import Config

class DatabaseManager:
    """Local SQLite database for app data and history"""
    
    def __init__(self):
        self.db_path = "pwe_app_history.db"
        self.init_database()
    
    def init_database(self):
        """Initialize local database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # App history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL,
                response TEXT NOT NULL,
                strategy_id TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                earnings REAL DEFAULT 0.0,
                success_rating INTEGER DEFAULT 0
            )
        ''')
        
        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Bot runs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_name TEXT NOT NULL,
                status TEXT NOT NULL,
                result TEXT,
                runtime REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        Logger.info("✅ Local database initialized")
    
    def save_conversation(self, prompt: str, response: str, strategy_id: str = None):
        """Save conversation to local database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO app_history (prompt, response, strategy_id)
                VALUES (?, ?, ?)
            ''', (prompt, response, strategy_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            Logger.error(f"Error saving conversation: {e}")
            return False
    
    def get_history(self, limit: int = 50) -> List[Dict]:
        """Get conversation history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM app_history 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "id": row[0],
                    "prompt": row[1],
                    "response": row[2],
                    "strategy_id": row[3],
                    "timestamp": row[4],
                    "earnings": row[5],
                    "success_rating": row[6]
                }
                for row in rows
            ]
        except Exception as e:
            Logger.error(f"Error getting history: {e}")
            return []
    
    def update_strategy_feedback(self, strategy_id: str, earnings: float, rating: int):
        """Update strategy with earnings and rating feedback"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE app_history 
                SET earnings = ?, success_rating = ?
                WHERE strategy_id = ?
            ''', (earnings, rating, strategy_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            Logger.error(f"Error updating feedback: {e}")
            return False

class APIClient:
    """Client for communicating with PWE API"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'PWE-App/1.0'
        })
    
    def health_check(self) -> bool:
        """Check if API is running"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            return response.status_code == 200
        except Exception as e:
            Logger.error(f"Health check failed: {e}")
            return False
    
    def generate_strategy(self, prompt: str) -> Dict[str, Any]:
        """Generate money-making strategy"""
        try:
            payload = {
                "prompt": prompt,
                "user_id": "pwe_app_user",
                "context": {"app_version": "1.0", "platform": "kivy"}
            }
            
            response = self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                Logger.error(f"API error: {response.status_code} - {response.text}")
                return {"error": f"API error: {response.status_code}"}
                
        except Exception as e:
            Logger.error(f"Error generating strategy: {e}")
            return {"error": str(e)}
    
    def get_top_strategies(self) -> Dict[str, Any]:
        """Get top recommended strategies"""
        try:
            response = self.session.get(f"{self.base_url}/v1/top-strategies", timeout=15)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API error: {response.status_code}"}
        except Exception as e:
            Logger.error(f"Error getting top strategies: {e}")
            return {"error": str(e)}
    
    def submit_feedback(self, strategy_id: str, success_score: int, earnings: float = 0.0):
        """Submit feedback for a strategy"""
        try:
            payload = {
                "strategy_id": strategy_id,
                "success_score": success_score,
                "earnings": earnings
            }
            
            response = self.session.post(
                f"{self.base_url}/v1/feedback",
                json=payload,
                timeout=10
            )
            
            return response.status_code == 200
        except Exception as e:
            Logger.error(f"Error submitting feedback: {e}")
            return False

class VoiceController:
    """Voice recognition controller"""
    
    def __init__(self):
        self.recognizer = None
        self.microphone = None
        self.listening = False
        
        if VOICE_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                
                # Adjust for ambient noise
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    
                Logger.info("✅ Voice recognition initialized")
            except Exception as e:
                Logger.error(f"Voice initialization failed: {e}")
                self.recognizer = None
    
    def listen_for_command(self, callback=None):
        """Listen for voice command"""
        if not self.recognizer:
            return "Voice recognition not available"
        
        try:
            Logger.info("🎤 Listening for voice command...")
            
            with self.microphone as source:
                # Listen for audio with timeout
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            # Recognize speech using Google Speech Recognition
            command = self.recognizer.recognize_google(audio)
            Logger.info(f"🎤 Voice command: {command}")
            
            if callback:
                callback(command)
            
            return command
            
        except sr.WaitTimeoutError:
            return "Listening timeout - no speech detected"
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError as e:
            return f"Speech recognition error: {e}"
        except Exception as e:
            return f"Voice error: {e}"

class BotRunner:
    """Automation bot execution manager"""
    
    def __init__(self):
        self.bot_results = {}
        self.running_bots = set()
    
    def run_bot(self, bot_name: str, callback=None):
        """Run a specific automation bot"""
        if bot_name in self.running_bots:
            return {"error": f"Bot {bot_name} is already running"}
        
        self.running_bots.add(bot_name)
        
        def bot_thread():
            try:
                Logger.info(f"🤖 Running bot: {bot_name}")
                start_time = time.time()
                
                # Import and run the specific bot
                if bot_name == "blog_bot":
                    from pwe_bots.blog_bot import run_blog_bot
                    result = run_blog_bot()
                elif bot_name == "ebook_bot":
                    from pwe_bots.ebook_bot import run_ebook_bot
                    result = run_ebook_bot()
                elif bot_name == "freelance_bot":
                    from pwe_bots.freelance_bot import run_freelance_bot
                    result = run_freelance_bot()
                elif bot_name == "email_bot":
                    from pwe_bots.email_bot import run_email_bot
                    result = run_email_bot()
                else:
                    result = {"error": f"Unknown bot: {bot_name}"}
                
                runtime = time.time() - start_time
                
                self.bot_results[bot_name] = {
                    "result": result,
                    "runtime": runtime,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                
                if callback:
                    callback(bot_name, result)
                
                Logger.info(f"✅ Bot {bot_name} completed in {runtime:.2f}s")
                
            except Exception as e:
                error_result = {"error": str(e)}
                self.bot_results[bot_name] = {
                    "result": error_result,
                    "runtime": time.time() - start_time,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                Logger.error(f"❌ Bot {bot_name} failed: {e}")
                
                if callback:
                    callback(bot_name, error_result)
            
            finally:
                self.running_bots.discard(bot_name)
        
        threading.Thread(target=bot_thread, daemon=True).start()
        
        return {"status": "started", "bot": bot_name}
    
    def run_all_bots(self, callback=None):
        """Run all available bots"""
        bots = ["blog_bot", "ebook_bot", "freelance_bot", "email_bot"]
        results = {}
        
        for bot in bots:
            result = self.run_bot(bot, callback)
            results[bot] = result
        
        return results
    
    def get_bot_status(self, bot_name: str = None):
        """Get status of bots"""
        if bot_name:
            return {
                "running": bot_name in self.running_bots,
                "last_result": self.bot_results.get(bot_name)
            }
        
        return {
            "running_bots": list(self.running_bots),
            "all_results": self.bot_results
        }

class PWEApp(App):
    """Main Pegasus Wealth Engine Application"""
    
    def build(self):
        """Build the main UI"""
        self.title = "Pegasus Wealth Engine"
        Window.size = (800, 600)
        
        # Initialize components
        self.db_manager = DatabaseManager()
        self.api_client = APIClient(Config.API_BASE_URL)
        self.voice_controller = VoiceController()
        self.bot_runner = BotRunner()
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = Label(
            text="🐎 Pegasus Wealth Engine",
            size_hint_y=0.1,
            font_size='24sp',
            bold=True
        )
        main_layout.add_widget(header)
        
        # Status bar
        self.status_label = Label(
            text="Initializing...",
            size_hint_y=0.05,
            font_size='14sp'
        )
        main_layout.add_widget(self.status_label)
        
        # Input section
        input_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=5)
        
        self.prompt_input = TextInput(
            hint_text="Enter your money-making goal (e.g., 'Earn me $500 today')",
            multiline=False,
            size_hint_x=0.7
        )
        input_layout.add_widget(self.prompt_input)
        
        generate_btn = Button(
            text="Generate\nPlan",
            size_hint_x=0.15
        )
        generate_btn.bind(on_press=self.generate_strategy)
        input_layout.add_widget(generate_btn)
        
        voice_btn = Button(
            text="🎤\nVoice",
            size_hint_x=0.15,
            disabled=not VOICE_AVAILABLE
        )
        voice_btn.bind(on_press=self.start_voice_input)
        input_layout.add_widget(voice_btn)
        
        main_layout.add_widget(input_layout)
        
        # Output section
        self.output_scroll = ScrollView(size_hint_y=0.4)
        self.output_label = Label(
            text="💡 Welcome to PWE! Enter your money-making goal above to get started.",
            text_size=(None, None),
            halign='left',
            valign='top',
            markup=True
        )
        self.output_scroll.add_widget(self.output_label)
        main_layout.add_widget(self.output_scroll)
        
        # Button panel
        button_layout = GridLayout(cols=4, size_hint_y=0.15, spacing=5)
        
        history_btn = Button(text="📚\nHistory")
        history_btn.bind(on_press=self.show_history)
        button_layout.add_widget(history_btn)
        
        bots_btn = Button(text="🤖\nRun Bots")
        bots_btn.bind(on_press=self.run_bots)
        button_layout.add_widget(bots_btn)
        
        top_strategies_btn = Button(text="⭐\nTop 3")
        top_strategies_btn.bind(on_press=self.show_top_strategies)
        button_layout.add_widget(top_strategies_btn)
        
        settings_btn = Button(text="⚙️\nSettings")
        settings_btn.bind(on_press=self.show_settings)
        button_layout.add_widget(settings_btn)
        
        main_layout.add_widget(button_layout)
        
        # Progress bar
        self.progress_bar = ProgressBar(
            size_hint_y=0.05,
            value=0,
            max=100
        )
        main_layout.add_widget(self.progress_bar)
        
        # Check API connectivity
        Clock.schedule_once(self.check_api_connectivity, 1)
        
        # Setup scheduler for automation
        self.setup_scheduler()
        
        return main_layout
    
    def check_api_connectivity(self, dt):
        """Check API connectivity on startup"""
        def check_thread():
            if self.api_client.health_check():
                Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', "✅ Connected to PWE API"), 0)
            else:
                Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', "❌ API offline - Check connection"), 0)
        
        threading.Thread(target=check_thread, daemon=True).start()
    
    def generate_strategy(self, instance):
        """Generate money-making strategy"""
        prompt = self.prompt_input.text.strip()
        if not prompt:
            self.show_popup("Error", "Please enter a money-making goal!")
            return
        
        self.update_status("🤖 Generating strategy...")
        self.progress_bar.value = 30
        
        def generate_thread():
            try:
                response = self.api_client.generate_strategy(prompt)
                
                if "error" in response:
                    Clock.schedule_once(lambda dt: self.handle_api_error(response["error"]), 0)
                else:
                    # Save to local database
                    self.db_manager.save_conversation(
                        prompt, 
                        response.get("response", ""), 
                        response.get("strategy_id")
                    )
                    
                    # Update UI
                    Clock.schedule_once(lambda dt: self.display_strategy(response), 0)
                
            except Exception as e:
                Clock.schedule_once(lambda dt: self.handle_api_error(str(e)), 0)
        
        threading.Thread(target=generate_thread, daemon=True).start()
    
    def display_strategy(self, response):
        """Display generated strategy in UI"""
        strategy = response.get("response", "No strategy generated")
        actions = response.get("suggested_actions", [])
        earnings = response.get("estimated_earnings", "Unknown")
        confidence = response.get("confidence", 0.0)
        
        # Format the output
        output_text = f"""[size=18][b]💰 Money-Making Strategy[/b][/size]
        
[b]Prompt:[/b] {self.prompt_input.text}

[b]Strategy:[/b]
{strategy}

[b]Quick Actions:[/b]"""
        
        for i, action in enumerate(actions, 1):
            output_text += f"\n{i}. {action}"
        
        output_text += f"""

[b]💵 Estimated Earnings:[/b] {earnings}
[b]🎯 Confidence:[/b] {confidence:.0%}
[b]🔗 Strategy ID:[/b] {response.get('strategy_id', 'N/A')}

[i]💡 Tip: Use the 'Run Bots' button to automate some of these actions![/i]"""
        
        self.output_label.text = output_text
        self.output_label.text_size = (self.output_scroll.width - 20, None)
        
        self.update_status("✅ Strategy generated successfully!")
        self.progress_bar.value = 100
        
        # Clear progress bar after delay
        Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', 0), 3)
        
        # Clear input
        self.prompt_input.text = ""
    
    def handle_api_error(self, error_msg):
        """Handle API errors gracefully"""
        self.output_label.text = f"""[color=ff6666][size=18][b]⚠️ Connection Issue[/b][/size][/color]

Unable to connect to PWE API: {error_msg}

[b]💡 Troubleshooting:[/b]
1. Check your internet connection
2. Verify API URL in settings: {Config.API_BASE_URL}
3. Ensure PWE API server is running
4. Try again in a few moments

[b]🔧 Quick Fix:[/b]
• Go to Settings to update API URL
• Use offline mode for basic strategies"""
        
        self.output_label.text_size = (self.output_scroll.width - 20, None)
        self.update_status("❌ API connection failed")
        self.progress_bar.value = 0
    
    def start_voice_input(self, instance):
        """Start voice input recognition"""
        if not self.voice_controller.recognizer:
            self.show_popup("Voice Error", "Voice recognition not available.\nInstall speech_recognition package.")
            return
        
        self.update_status("🎤 Listening for voice command...")
        
        def voice_thread():
            command = self.voice_controller.listen_for_command()
            
            if "error" not in command.lower() and "timeout" not in command.lower():
                # Valid voice command received
                Clock.schedule_once(lambda dt: self.process_voice_command(command), 0)
            else:
                Clock.schedule_once(lambda dt: self.update_status(f"🎤 {command}"), 0)
        
        threading.Thread(target=voice_thread, daemon=True).start()
    
    def process_voice_command(self, command):
        """Process recognized voice command"""
        # Set the command as input and trigger generation
        self.prompt_input.text = command
        self.update_status(f"🎤 Voice: {command}")
        self.generate_strategy(None)
    
    def run_bots(self, instance):
        """Run automation bots"""
        self.update_status("🤖 Starting automation bots...")
        
        def bot_callback(bot_name, result):
            status_msg = f"✅ {bot_name} completed" if "error" not in result else f"❌ {bot_name} failed"
            Clock.schedule_once(lambda dt: self.update_status(status_msg), 0)
        
        self.bot_runner.run_all_bots(bot_callback)
        
        # Show bot status popup
        self.show_bot_status_popup()
    
    def show_bot_status_popup(self):
        """Show bot execution status popup"""
        content = BoxLayout(orientation='vertical', spacing=10)
        
        status_label = Label(
            text="🤖 Automation Bots Running...\n\nBot Status:",
            size_hint_y=0.3
        )
        content.add_widget(status_label)
        
        bot_info = Label(
            text="📝 Blog Bot: Writing articles\n📚 eBook Bot: Creating eBooks\n💼 Freelance Bot: Sending proposals\n📧 Email Bot: Managing outreach",
            size_hint_y=0.5
        )
        content.add_widget(bot_info)
        
        close_btn = Button(
            text="Close",
            size_hint_y=0.2
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title="Automation Bots",
            content=content,
            size_hint=(0.8, 0.6)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_history(self, instance):
        """Show conversation history"""
        history = self.db_manager.get_history(20)
        
        content = BoxLayout(orientation='vertical', spacing=5)
        
        scroll = ScrollView()
        history_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        history_layout.bind(minimum_height=history_layout.setter('height'))
        
        if history:
            for item in history:
                item_text = f"🕐 {item['timestamp'][:19]}\n💭 {item['prompt'][:100]}...\n💡 {item['response'][:100]}...\n"
                if item['earnings'] > 0:
                    item_text += f"💰 Earned: ${item['earnings']:.2f}\n"
                
                item_label = Label(
                    text=item_text,
                    text_size=(None, None),
                    size_hint_y=None,
                    height=120
                )
                history_layout.add_widget(item_label)
        else:
            no_history_label = Label(text="No history yet. Generate your first strategy!")
            history_layout.add_widget(no_history_label)
        
        scroll.add_widget(history_layout)
        content.add_widget(scroll)
        
        close_btn = Button(text="Close", size_hint_y=0.1)
        content.add_widget(close_btn)
        
        popup = Popup(
            title="Conversation History",
            content=content,
            size_hint=(0.9, 0.8)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_top_strategies(self, instance):
        """Show top 3 recommended strategies"""
        self.update_status("📊 Getting top strategies...")
        
        def get_strategies_thread():
            strategies = self.api_client.get_top_strategies()
            Clock.schedule_once(lambda dt: self.display_top_strategies(strategies), 0)
        
        threading.Thread(target=get_strategies_thread, daemon=True).start()
    
    def display_top_strategies(self, data):
        """Display top strategies in popup"""
        content = BoxLayout(orientation='vertical', spacing=10)
        
        if "error" in data:
            error_label = Label(text=f"❌ Error loading strategies: {data['error']}")
            content.add_widget(error_label)
        else:
            strategies = data.get("strategies", [])
            
            scroll = ScrollView()
            strategies_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
            strategies_layout.bind(minimum_height=strategies_layout.setter('height'))
            
            for i, strategy in enumerate(strategies, 1):
                strategy_text = f"""[b]{i}. {strategy.get('title', 'Strategy')}[/b]
                
{strategy.get('description', 'No description')}

💰 Earnings: {strategy.get('estimated_earnings', 'Unknown')}
⏰ Time: {strategy.get('time_required', 'Unknown')}
📊 Success Rate: {strategy.get('success_rate', 0)*100:.0f}%
🎯 Difficulty: {strategy.get('difficulty', 'Unknown')}"""
                
                strategy_label = Label(
                    text=strategy_text,
                    markup=True,
                    text_size=(None, None),
                    size_hint_y=None,
                    height=150
                )
                strategies_layout.add_widget(strategy_label)
            
            scroll.add_widget(strategies_layout)
            content.add_widget(scroll)
        
        close_btn = Button(text="Close", size_hint_y=0.1)
        content.add_widget(close_btn)
        
        popup = Popup(
            title="⭐ Top 3 Strategies Today",
            content=content,
            size_hint=(0.9, 0.8)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
        
        self.update_status("✅ Top strategies loaded")
    
    def show_settings(self, instance):
        """Show settings popup"""
        content = BoxLayout(orientation='vertical', spacing=10)
        
        # API URL setting
        api_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2)
        api_layout.add_widget(Label(text="API URL:", size_hint_x=0.3))
        
        api_input = TextInput(
            text=Config.API_BASE_URL,
            multiline=False,
            size_hint_x=0.7
        )
        api_layout.add_widget(api_input)
        content.add_widget(api_layout)
        
        # Voice control toggle
        voice_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15)
        voice_layout.add_widget(Label(text="Voice Control:", size_hint_x=0.7))
        
        voice_switch = Switch(
            active=VOICE_AVAILABLE,
            size_hint_x=0.3
        )
        voice_layout.add_widget(voice_switch)
        content.add_widget(voice_layout)
        
        # Automation schedule
        schedule_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15)
        schedule_layout.add_widget(Label(text="Auto-run Bots:", size_hint_x=0.5))
        
        schedule_spinner = Spinner(
            text="Disabled",
            values=["Disabled", "Daily 9AM", "Daily 9AM & 6PM", "Every 4 hours"],
            size_hint_x=0.5
        )
        schedule_layout.add_widget(schedule_spinner)
        content.add_widget(schedule_layout)
        
        # Buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2)
        
        save_btn = Button(text="Save Settings")
        test_api_btn = Button(text="Test API")
        close_btn = Button(text="Close")
        
        button_layout.add_widget(save_btn)
        button_layout.add_widget(test_api_btn)
        button_layout.add_widget(close_btn)
        content.add_widget(button_layout)
        
        # Info section
        info_text = f"""[b]App Version:[/b] 1.0.0
[b]Database:[/b] {self.db_manager.db_path}
[b]Voice Support:[/b] {'✅ Available' if VOICE_AVAILABLE else '❌ Unavailable'}
[b]Last Update:[/b] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"""
        
        info_label = Label(
            text=info_text,
            markup=True,
            size_hint_y=0.3
        )
        content.add_widget(info_label)
        
        popup = Popup(
            title="⚙️ Settings",
            content=content,
            size_hint=(0.9, 0.8)
        )
        
        def save_settings(instance):
            Config.API_BASE_URL = api_input.text.strip()
            self.api_client = APIClient(Config.API_BASE_URL)
            self.show_popup("Settings", "Settings saved successfully!")
        
        def test_api(instance):
            if self.api_client.health_check():
                self.show_popup("API Test", "✅ API connection successful!")
            else:
                self.show_popup("API Test", "❌ API connection failed!")
        
        save_btn.bind(on_press=save_settings)
        test_api_btn.bind(on_press=test_api)
        close_btn.bind(on_press=popup.dismiss)
        
        popup.open()
    
    def setup_scheduler(self):
        """Setup automation scheduler"""
        def run_scheduled_tasks():
            # Schedule bots to run at 9AM and 6PM
            schedule.every().day.at("09:00").do(self.scheduled_bot_run)
            schedule.every().day.at("18:00").do(self.scheduled_bot_run)
            
            # Check for scheduled tasks every minute
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        # Run scheduler in background thread
        threading.Thread(target=run_scheduled_tasks, daemon=True).start()
    
    def scheduled_bot_run(self):
        """Run bots on schedule"""
        Logger.info("⏰ Running scheduled automation bots")
        self.bot_runner.run_all_bots()
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.text = message
        Logger.info(f"Status: {message}")
    
    def show_popup(self, title, message):
        """Show simple popup message"""
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message))
        
        close_btn = Button(text="OK", size_hint_y=0.3)
        content.add_widget(close_btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.7, 0.4)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == "__main__":
    # Ensure bot modules are available
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    
    # Run the app
    PWEApp().run()