#!/usr/bin/env python3
"""
🧪 NEMONA TEST SUITE
Test all features of Nemona AI Agent

Run this script to verify your Nemona setup is working correctly.
"""

import requests
import json
import time
from datetime import datetime

class NemonaTest:
    def __init__(self, base_url, api_key):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.test_results = []
        
    def run_test(self, test_name, test_function):
        """Run a single test and track results"""
        print(f"\n🧪 Testing: {test_name}")
        print("-" * 50)
        
        try:
            start_time = time.time()
            result = test_function()
            end_time = time.time()
            duration = end_time - start_time
            
            if result:
                print(f"✅ PASSED ({duration:.2f}s)")
                self.test_results.append({
                    'test': test_name,
                    'status': 'PASSED',
                    'duration': duration,
                    'details': result
                })
                return True
            else:
                print(f"❌ FAILED ({duration:.2f}s)")
                self.test_results.append({
                    'test': test_name,
                    'status': 'FAILED',
                    'duration': duration,
                    'details': None
                })
                return False
                
        except Exception as e:
            print(f"💥 ERROR: {str(e)}")
            self.test_results.append({
                'test': test_name,
                'status': 'ERROR',
                'duration': 0,
                'details': str(e)
            })
            return False
    
    def test_health_check(self):
        """Test if Nemona's brain is online and healthy"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"Status: {data.get('status')}")
                print(f"Brain Status: {data.get('brain_status')}")
                print(f"Version: {data.get('version')}")
                return data.get('status') == 'healthy'
            else:
                print(f"HTTP Error: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Connection Error: {e}")
            return False
    
    def test_basic_chat(self):
        """Test basic chat functionality"""
        test_message = "Hello Nemona! This is a test message. Can you respond?"
        
        payload = {
            'message': test_message,
            'api_key': self.api_key,
            'context': {
                'test_mode': True,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data.get('response', '')[:200]}...")
            print(f"Confidence: {data.get('confidence', 0):.1%}")
            print(f"Reasoning Steps: {len(data.get('reasoning_chain', []))}")
            return len(data.get('response', '')) > 10
        else:
            print(f"Chat Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def test_money_ideas(self):
        """Test money-making ideas generation"""
        test_message = "Give me some money-making ideas for today"
        
        payload = {
            'message': test_message,
            'api_key': self.api_key,
            'context': {'test_mode': True}
        }
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '').lower()
            
            # Check if response contains money-related keywords
            money_keywords = ['money', 'earn', 'income', '$', 'profit', 'business']
            found_keywords = [kw for kw in money_keywords if kw in response_text]
            
            print(f"Found money keywords: {found_keywords}")
            print(f"Response length: {len(data.get('response', ''))}")
            
            return len(found_keywords) >= 2 and len(data.get('response', '')) > 50
        else:
            print(f"Money Ideas Error: {response.status_code}")
            return False
    
    def test_news_request(self):
        """Test news data retrieval"""
        test_message = "What's the latest news today?"
        
        payload = {
            'message': test_message,
            'api_key': self.api_key,
            'context': {'test_mode': True}
        }
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '').lower()
            
            # Check if response contains news-related content
            news_keywords = ['news', 'headlines', 'today', 'latest', 'current']
            found_keywords = [kw for kw in news_keywords if kw in response_text]
            
            print(f"Found news keywords: {found_keywords}")
            return len(found_keywords) >= 2
        else:
            print(f"News Request Error: {response.status_code}")
            return False
    
    def test_crypto_prices(self):
        """Test cryptocurrency price retrieval"""
        test_message = "What's the current Bitcoin price?"
        
        payload = {
            'message': test_message,
            'api_key': self.api_key,
            'context': {'test_mode': True}
        }
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '').lower()
            
            # Check if response contains crypto-related content
            crypto_keywords = ['bitcoin', 'crypto', 'price', '$', 'usd']
            found_keywords = [kw for kw in crypto_keywords if kw in response_text]
            
            print(f"Found crypto keywords: {found_keywords}")
            return len(found_keywords) >= 2
        else:
            print(f"Crypto Request Error: {response.status_code}")
            return False
    
    def test_reasoning_system(self):
        """Test chain-of-thought reasoning"""
        test_message = "How can I learn programming and make money from it?"
        
        payload = {
            'message': test_message,
            'api_key': self.api_key,
            'context': {'test_mode': True}
        }
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            reasoning_chain = data.get('reasoning_chain', [])
            
            print(f"Reasoning steps: {len(reasoning_chain)}")
            
            # Print reasoning details
            for i, step in enumerate(reasoning_chain[:3], 1):
                if isinstance(step, dict):
                    step_type = list(step.keys())[0] if step else 'unknown'
                    print(f"  Step {i}: {step_type}")
            
            return len(reasoning_chain) >= 3
        else:
            print(f"Reasoning Test Error: {response.status_code}")
            return False
    
    def test_vision_endpoint(self):
        """Test vision analysis endpoint (without actual image)"""
        # Create a dummy base64 encoded image (1x1 pixel)
        dummy_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
        payload = {
            'image_base64': dummy_image,
            'api_key': self.api_key
        }
        
        response = requests.post(
            f"{self.base_url}/api/vision",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Vision Response: {data.get('response', '')[:100]}...")
            analysis = data.get('analysis', {})
            print(f"Objects detected: {analysis.get('objects_detected', [])}")
            return 'response' in data
        else:
            print(f"Vision Test Error: {response.status_code}")
            return False
    
    def test_stats_endpoint(self):
        """Test statistics endpoint"""
        response = requests.get(
            f"{self.base_url}/api/stats",
            params={'api_key': self.api_key},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total Conversations: {data.get('total_conversations', 0)}")
            print(f"Total Insights: {data.get('total_insights', 0)}")
            print(f"Recent Activity: {data.get('conversations_24h', 0)}")
            print(f"Learning Status: {data.get('learning_status', 'Unknown')}")
            return 'total_conversations' in data
        else:
            print(f"Stats Test Error: {response.status_code}")
            return False
    
    def test_api_security(self):
        """Test API key security"""
        # Test with wrong API key
        payload = {
            'message': "Test with wrong key",
            'api_key': 'wrong-key-12345'
        }
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 401:
            print("✅ API security working - unauthorized access blocked")
            return True
        else:
            print(f"⚠️ Security issue - expected 401, got {response.status_code}")
            return False
    
    def test_learning_system(self):
        """Test if learning system is working"""
        # Send a few messages to trigger learning
        messages = [
            "Tell me about artificial intelligence",
            "What is machine learning?",
            "How does AI work?"
        ]
        
        learning_indicators = 0
        
        for msg in messages:
            payload = {
                'message': msg,
                'api_key': self.api_key,
                'context': {'test_mode': True}
            }
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                reasoning = data.get('reasoning_chain', [])
                
                # Look for memory retrieval in reasoning
                for step in reasoning:
                    if isinstance(step, dict) and 'memory_retrieval' in step:
                        learning_indicators += 1
                        break
        
        print(f"Learning indicators found: {learning_indicators}/{len(messages)}")
        return learning_indicators > 0
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*60)
        print("🏁 NEMONA TEST RESULTS")
        print("="*60)
        
        passed = sum(1 for result in self.test_results if result['status'] == 'PASSED')
        failed = sum(1 for result in self.test_results if result['status'] == 'FAILED')
        errors = sum(1 for result in self.test_results if result['status'] == 'ERROR')
        total = len(self.test_results)
        
        print(f"\nSUMMARY:")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"💥 Errors: {errors}")
        print(f"📊 Total: {total}")
        print(f"🎯 Success Rate: {(passed/total)*100:.1f}%")
        
        print(f"\nDETAILED RESULTS:")
        for result in self.test_results:
            status_emoji = "✅" if result['status'] == 'PASSED' else "❌" if result['status'] == 'FAILED' else "💥"
            print(f"{status_emoji} {result['test']} ({result['duration']:.2f}s)")
        
        # Overall assessment
        if passed == total:
            print(f"\n🎉 EXCELLENT! Nemona is fully operational!")
            print(f"🚀 All systems are working perfectly. You can start using Nemona!")
        elif passed >= total * 0.8:
            print(f"\n👍 GOOD! Nemona is mostly working.")
            print(f"🔧 Some features may need attention, but core functionality is solid.")
        elif passed >= total * 0.5:
            print(f"\n⚠️ PARTIAL! Nemona has some issues.")
            print(f"🛠️ Several features need fixing before full deployment.")
        else:
            print(f"\n🚨 CRITICAL! Nemona has major issues.")
            print(f"🔧 Please check your setup and configuration.")

def main():
    print("🤖 NEMONA AI AGENT - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    # Configuration (edit these with your values)
    base_url = input("Enter your Replit URL (e.g., https://nemona-brain.username.repl.co): ").strip()
    
    if not base_url:
        print("❌ No URL provided. Using default...")
        base_url = "https://your-replit-url.repl.co"
    
    api_key = input("Enter your API key (press Enter for default): ").strip()
    if not api_key:
        api_key = "nemona-secret-key-2024"
    
    print(f"\n🔗 Testing URL: {base_url}")
    print(f"🔑 Using API Key: {api_key[:10]}...")
    print("\n🚀 Starting tests...\n")
    
    # Initialize test suite
    tester = NemonaTest(base_url, api_key)
    
    # Run all tests
    tests = [
        ("Health Check", tester.test_health_check),
        ("API Security", tester.test_api_security),
        ("Basic Chat", tester.test_basic_chat),
        ("Money Ideas", tester.test_money_ideas),
        ("News Request", tester.test_news_request),
        ("Crypto Prices", tester.test_crypto_prices),
        ("Reasoning System", tester.test_reasoning_system),
        ("Vision Endpoint", tester.test_vision_endpoint),
        ("Stats Endpoint", tester.test_stats_endpoint),
        ("Learning System", tester.test_learning_system),
    ]
    
    for test_name, test_func in tests:
        tester.run_test(test_name, test_func)
        time.sleep(1)  # Brief pause between tests
    
    # Generate final report
    tester.generate_report()
    
    print(f"\n📝 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Tested URL: {base_url}")

if __name__ == "__main__":
    main()