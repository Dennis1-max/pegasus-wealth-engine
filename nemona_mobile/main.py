import os
import json
import base64
import threading
import time
from datetime import datetime
import requests
from io import BytesIO

# Kivy imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.core.window import Window

# Camera and audio
try:
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path
    from jnius import autoclass
    ANDROID = True
except ImportError:
    ANDROID = False

# TTS and STT
try:
    import pyttsx3
    from speech_recognition import Recognizer, Microphone
    TTS_AVAILABLE = True
    STT_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    STT_AVAILABLE = False

# Camera
try:
    from kivy.uix.camera import Camera
    CAMERA_AVAILABLE = True
except ImportError:
    CAMERA_AVAILABLE = False

class ChatMessage(BoxLayout):
    """Individual chat message widget"""
    def __init__(self, message, is_user=True, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = '48dp'
        self.padding = [10, 5]
        
        # Message header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height='20dp')
        
        sender = Label(
            text=f"{'You' if is_user else 'Nemona'} • {datetime.now().strftime('%H:%M')}",
            size_hint_y=None,
            height='20dp',
            color=(0.7, 0.7, 0.7, 1),
            font_size='12sp',
            halign='left'
        )
        sender.bind(size=sender.setter('text_size'))
        header.add_widget(sender)
        
        # Message content
        content = Label(
            text=message,
            size_hint_y=None,
            color=(1, 1, 1, 1) if is_user else (0.9, 0.9, 0.9, 1),
            font_size='14sp',
            halign='left',
            valign='top',
            text_size=(None, None)
        )
        content.bind(size=content.setter('text_size'))
        content.bind(texture_size=content.setter('size'))
        
        self.add_widget(header)
        self.add_widget(content)
        
        # Update height based on content
        def update_height(*args):
            self.height = header.height + content.height + 20
        
        content.bind(texture_size=update_height)

class NemonaApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Nemona API configuration
        self.api_base_url = "https://your-replit-url.repl.co/api"  # Update with your Replit URL
        self.api_key = "nemona-secret-key-2024"
        
        # App state
        self.chat_history = []
        self.is_recording = False
        self.camera_active = False
        
        # Initialize TTS/STT
        if TTS_AVAILABLE:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
        
        if STT_AVAILABLE:
            self.recognizer = Recognizer()
            self.microphone = Microphone()
    
    def build(self):
        # Request permissions on Android
        if ANDROID:
            request_permissions([
                Permission.CAMERA,
                Permission.RECORD_AUDIO,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.INTERNET
            ])
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title = Label(
            text='🤖 NEMONA - Advanced AI Agent',
            size_hint_y=None,
            height='50dp',
            font_size='20sp',
            color=(0, 1, 0.5, 1),
            bold=True
        )
        main_layout.add_widget(title)
        
        # Status bar
        self.status_label = Label(
            text='Status: Ready • Connection: Checking...',
            size_hint_y=None,
            height='30dp',
            font_size='12sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        main_layout.add_widget(self.status_label)
        
        # Chat area
        chat_container = BoxLayout(orientation='vertical')
        
        # Chat history
        self.chat_scroll = ScrollView()
        self.chat_layout = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))
        self.chat_scroll.add_widget(self.chat_layout)
        chat_container.add_widget(self.chat_scroll)
        
        # Input area
        input_container = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', spacing=5)
        
        # Text input
        self.text_input = TextInput(
            hint_text='Type your message to Nemona...',
            multiline=False,
            size_hint_x=0.6
        )
        self.text_input.bind(on_text_validate=self.send_message)
        input_container.add_widget(self.text_input)
        
        # Send button
        send_btn = Button(
            text='Send',
            size_hint_x=0.2,
            background_color=(0, 0.8, 0.4, 1)
        )
        send_btn.bind(on_press=self.send_message)
        input_container.add_widget(send_btn)
        
        # Voice button
        self.voice_btn = Button(
            text='🎤',
            size_hint_x=0.1,
            background_color=(0.8, 0.4, 0, 1)
        )
        self.voice_btn.bind(on_press=self.toggle_voice_recording)
        input_container.add_widget(self.voice_btn)
        
        # Camera button
        self.camera_btn = Button(
            text='📷',
            size_hint_x=0.1,
            background_color=(0.4, 0.4, 0.8, 1)
        )
        self.camera_btn.bind(on_press=self.open_camera)
        input_container.add_widget(self.camera_btn)
        
        chat_container.add_widget(input_container)
        main_layout.add_widget(chat_container)
        
        # Features buttons
        features_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=5)
        
        money_btn = Button(
            text='💰 Money Ideas',
            background_color=(0.8, 0.6, 0, 1)
        )
        money_btn.bind(on_press=self.get_money_ideas)
        features_layout.add_widget(money_btn)
        
        news_btn = Button(
            text='📰 News',
            background_color=(0, 0.6, 0.8, 1)
        )
        news_btn.bind(on_press=self.get_news)
        features_layout.add_widget(news_btn)
        
        stats_btn = Button(
            text='📊 Stats',
            background_color=(0.6, 0, 0.8, 1)
        )
        stats_btn.bind(on_press=self.get_stats)
        features_layout.add_widget(stats_btn)
        
        main_layout.add_widget(features_layout)
        
        # Check connection on startup
        Clock.schedule_once(self.check_connection, 1)
        
        # Welcome message
        Clock.schedule_once(self.show_welcome_message, 2)
        
        return main_layout
    
    def check_connection(self, dt=None):
        """Check connection to Nemona's brain"""
        def check():
            try:
                response = requests.get(f"{self.api_base_url}/health", timeout=10)
                if response.status_code == 200:
                    Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 
                        'Status: Ready • Connection: Connected ✅'))
                else:
                    Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 
                        'Status: Ready • Connection: Error ❌'))
            except:
                Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 
                    'Status: Ready • Connection: Offline ⚠️ (Check Replit URL)'))
        
        threading.Thread(target=check, daemon=True).start()
    
    def show_welcome_message(self, dt=None):
        """Show welcome message from Nemona"""
        welcome_msg = """Hello! I'm Nemona, your advanced AI agent! 🤖

I can help you with:
• 💰 Daily money-making ideas ($10-100/day)
• 📰 Real-time news and trends
• 🌤️ Weather updates
• 💎 Cryptocurrency prices
• 🧠 Smart reasoning and learning
• 📷 Image analysis (camera)
• 🎤 Voice conversations

Just type a message or use voice/camera features!"""
        
        self.add_chat_message(welcome_msg, is_user=False)
    
    def add_chat_message(self, message, is_user=True):
        """Add a message to the chat"""
        chat_msg = ChatMessage(message, is_user)
        self.chat_layout.add_widget(chat_msg)
        
        # Scroll to bottom
        Clock.schedule_once(lambda dt: setattr(self.chat_scroll, 'scroll_y', 0), 0.1)
        
        # Store in history
        self.chat_history.append({
            'message': message,
            'is_user': is_user,
            'timestamp': datetime.now().isoformat()
        })
    
    def send_message(self, instance=None):
        """Send message to Nemona"""
        message = self.text_input.text.strip()
        if not message:
            return
        
        # Clear input
        self.text_input.text = ''
        
        # Add user message
        self.add_chat_message(message, is_user=True)
        
        # Update status
        self.status_label.text = 'Status: Thinking... 🧠'
        
        # Send to Nemona in background
        def send_to_nemona():
            try:
                payload = {
                    'message': message,
                    'api_key': self.api_key,
                    'context': {
                        'chat_history': self.chat_history[-5:],  # Last 5 messages for context
                        'timestamp': datetime.now().isoformat(),
                        'platform': 'mobile_app'
                    }
                }
                
                response = requests.post(
                    f"{self.api_base_url}/chat",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    nemona_response = result.get('response', 'Sorry, I could not process that.')
                    confidence = result.get('confidence', 0.0)
                    
                    # Add Nemona's response
                    Clock.schedule_once(lambda dt: self.add_chat_message(nemona_response, is_user=False))
                    
                    # Speak response if TTS available
                    if TTS_AVAILABLE:
                        self.speak_text(nemona_response)
                    
                    # Update status with confidence
                    Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 
                        f'Status: Ready • Confidence: {confidence:.1%}'))
                    
                else:
                    Clock.schedule_once(lambda dt: self.add_chat_message(
                        "Sorry, I'm having trouble connecting to my brain. Please check the connection.", 
                        is_user=False))
                    Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 
                        'Status: Connection Error ❌'))
                        
            except Exception as e:
                Clock.schedule_once(lambda dt: self.add_chat_message(
                    f"Connection error: {str(e)}. Please check your internet and Replit URL.", 
                    is_user=False))
                Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 
                    'Status: Error ❌'))
        
        threading.Thread(target=send_to_nemona, daemon=True).start()
    
    def speak_text(self, text):
        """Speak text using TTS"""
        if not TTS_AVAILABLE:
            return
        
        def speak():
            try:
                # Clean text for TTS (remove markdown and emojis)
                clean_text = text.replace('*', '').replace('#', '').replace('•', '')
                # Remove common emojis
                for emoji in ['🤖', '💰', '📰', '🌤️', '💎', '🧠', '📷', '🎤', '✅', '❌', '⚠️']:
                    clean_text = clean_text.replace(emoji, '')
                
                self.tts_engine.say(clean_text[:200])  # Limit length
                self.tts_engine.runAndWait()
            except Exception as e:
                Logger.error(f"TTS Error: {e}")
        
        threading.Thread(target=speak, daemon=True).start()
    
    def toggle_voice_recording(self, instance):
        """Toggle voice recording"""
        if not STT_AVAILABLE:
            self.add_chat_message("Voice recognition not available on this device.", is_user=False)
            return
        
        if self.is_recording:
            self.is_recording = False
            self.voice_btn.text = '🎤'
            self.voice_btn.background_color = (0.8, 0.4, 0, 1)
            self.status_label.text = 'Status: Processing voice...'
        else:
            self.is_recording = True
            self.voice_btn.text = '🔴'
            self.voice_btn.background_color = (1, 0, 0, 1)
            self.status_label.text = 'Status: Listening... 🎤'
            self.start_voice_recording()
    
    def start_voice_recording(self):
        """Start voice recording"""
        def record():
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                # Convert to text
                text = self.recognizer.recognize_google(audio)
                
                Clock.schedule_once(lambda dt: setattr(self.text_input, 'text', text))
                Clock.schedule_once(lambda dt: self.send_message())
                Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 'Status: Ready'))
                
            except Exception as e:
                Clock.schedule_once(lambda dt: self.add_chat_message(
                    f"Voice recognition error: {str(e)}", is_user=False))
                Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 'Status: Voice Error'))
            finally:
                self.is_recording = False
                Clock.schedule_once(lambda dt: setattr(self.voice_btn, 'text', '🎤'))
                Clock.schedule_once(lambda dt: setattr(self.voice_btn, 'background_color', (0.8, 0.4, 0, 1)))
        
        threading.Thread(target=record, daemon=True).start()
    
    def open_camera(self, instance):
        """Open camera for vision analysis"""
        if not CAMERA_AVAILABLE:
            self.add_chat_message("Camera not available on this device.", is_user=False)
            return
        
        # Create camera popup
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Camera widget
        camera = Camera(play=True, resolution=(640, 480))
        popup_layout.add_widget(camera)
        
        # Buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', spacing=10)
        
        capture_btn = Button(text='📸 Capture & Analyze', background_color=(0, 0.8, 0.4, 1))
        cancel_btn = Button(text='❌ Cancel', background_color=(0.8, 0.4, 0, 1))
        
        button_layout.add_widget(capture_btn)
        button_layout.add_widget(cancel_btn)
        popup_layout.add_widget(button_layout)
        
        # Create popup
        camera_popup = Popup(
            title='📷 Camera Vision Analysis',
            content=popup_layout,
            size_hint=(0.9, 0.8)
        )
        
        def capture_image(instance):
            try:
                # Export camera texture to image
                camera.export_to_png("temp_capture.png")
                
                # Convert to base64
                with open("temp_capture.png", "rb") as img_file:
                    img_base64 = base64.b64encode(img_file.read()).decode()
                
                # Send to Nemona for analysis
                self.analyze_image(img_base64)
                camera_popup.dismiss()
                
                # Clean up
                os.remove("temp_capture.png")
                
            except Exception as e:
                self.add_chat_message(f"Camera error: {str(e)}", is_user=False)
        
        capture_btn.bind(on_press=capture_image)
        cancel_btn.bind(on_press=camera_popup.dismiss)
        
        camera_popup.open()
    
    def analyze_image(self, image_base64):
        """Send image to Nemona for analysis"""
        self.add_chat_message("📷 Analyzing image...", is_user=True)
        self.status_label.text = 'Status: Analyzing image... 👁️'
        
        def send_image():
            try:
                payload = {
                    'image_base64': image_base64,
                    'api_key': self.api_key
                }
                
                response = requests.post(
                    f"{self.api_base_url}/vision",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    analysis_response = result.get('response', 'Could not analyze image.')
                    
                    Clock.schedule_once(lambda dt: self.add_chat_message(analysis_response, is_user=False))
                    Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 'Status: Ready'))
                    
                    # Speak the analysis
                    if TTS_AVAILABLE:
                        self.speak_text(analysis_response)
                else:
                    Clock.schedule_once(lambda dt: self.add_chat_message(
                        "Sorry, I couldn't analyze the image right now.", is_user=False))
                    
            except Exception as e:
                Clock.schedule_once(lambda dt: self.add_chat_message(
                    f"Image analysis error: {str(e)}", is_user=False))
        
        threading.Thread(target=send_image, daemon=True).start()
    
    def get_money_ideas(self, instance):
        """Get money-making ideas from Nemona"""
        self.add_chat_message("💰 Get me some money-making ideas for today!", is_user=True)
        self.send_message()
    
    def get_news(self, instance):
        """Get latest news from Nemona"""
        self.add_chat_message("📰 What's the latest news today?", is_user=True)
        self.send_message()
    
    def get_stats(self, instance):
        """Get Nemona's stats"""
        def get_stats_data():
            try:
                response = requests.get(
                    f"{self.api_base_url}/stats",
                    params={'api_key': self.api_key},
                    timeout=10
                )
                
                if response.status_code == 200:
                    stats = response.json()
                    stats_msg = f"""📊 **Nemona's Brain Statistics:**

🧠 Total Conversations: {stats.get('total_conversations', 0)}
💡 Insights Learned: {stats.get('total_insights', 0)}
📈 Recent Activity (24h): {stats.get('conversations_24h', 0)}
⚡ Learning Status: {stats.get('learning_status', 'Unknown')}
🔄 Uptime: {stats.get('uptime', 'Unknown')}

Last Updated: {datetime.now().strftime('%H:%M:%S')}"""
                    
                    Clock.schedule_once(lambda dt: self.add_chat_message(stats_msg, is_user=False))
                else:
                    Clock.schedule_once(lambda dt: self.add_chat_message(
                        "Could not retrieve stats at this time.", is_user=False))
                    
            except Exception as e:
                Clock.schedule_once(lambda dt: self.add_chat_message(
                    f"Stats error: {str(e)}", is_user=False))
        
        threading.Thread(target=get_stats_data, daemon=True).start()

# Run the app
if __name__ == '__main__':
    NemonaApp().run()