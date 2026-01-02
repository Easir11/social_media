"""
Web interface testing script for Barta 2.0
Tests key URLs and functionality through HTTP requests
"""

import requests
import time
from urllib.parse import urljoin

class WebInterfaceTester:
    def __init__(self, base_url='http://127.0.0.1:8000'):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def test_url(self, path, expected_status=200, description="", check_content=None):
        """Test a URL and record results"""
        url = urljoin(self.base_url, path)
        try:
            response = self.session.get(url, timeout=10)
            success = response.status_code == expected_status
            
            content_check = True
            if check_content and success:
                content_check = check_content in response.text
            
            result = {
                'url': path,
                'description': description,
                'expected_status': expected_status,
                'actual_status': response.status_code,
                'success': success and content_check,
                'content_check': content_check if check_content else None,
                'response_time': response.elapsed.total_seconds()
            }
            
            self.test_results.append(result)
            return result
            
        except requests.exceptions.RequestException as e:
            result = {
                'url': path,
                'description': description,
                'expected_status': expected_status,
                'actual_status': 'ERROR',
                'success': False,
                'error': str(e),
                'response_time': None
            }
            self.test_results.append(result)
            return result
    
    def test_authentication_flow(self):
        """Test authentication-related URLs"""
        print("Testing Authentication Flow...")
        
        # Test signup page
        self.test_url('/signup/', 200, "Signup page accessibility", "Sign Up")
        
        # Test signin page 
        self.test_url('/signin/', 200, "Signin page accessibility", "Sign In")
        
        # Test home page (should redirect for anonymous users)
        self.test_url('/', 302, "Home page redirect for anonymous users")
        
        return True
    
    def test_protected_pages(self):
        """Test that protected pages require authentication"""
        print("Testing Protected Pages...")
        
        protected_urls = [
            ('/profile/', "Profile page protection"),
            ('/friends/', "Friends page protection"), 
            ('/messages/', "Messages page protection"),
            ('/notifications/', "Notifications page protection"),
            ('/create-post/', "Create post page protection")
        ]
        
        for url, description in protected_urls:
            self.test_url(url, 302, description)  # Should redirect to login
    
    def test_static_resources(self):
        """Test static resources loading"""
        print("Testing Static Resources...")
        
        # Test that signin page loads CSS properly
        signin_result = self.test_url('/signin/', 200, "Signin page with CSS")
        if signin_result['success']:
            # Check if CSS is referenced
            url = urljoin(self.base_url, '/signin/')
            response = self.session.get(url)
            has_css = 'bootstrap' in response.text.lower() or 'style.css' in response.text
            
            self.test_results.append({
                'url': '/signin/ (CSS check)',
                'description': 'CSS resources referenced',
                'success': has_css,
                'content_check': has_css
            })
    
    def run_all_tests(self):
        """Run all web interface tests"""
        print("🌐 Starting Web Interface Testing...")
        print("=" * 50)
        
        # Test server availability
        try:
            response = self.session.get(self.base_url, timeout=5)
            server_running = True
            print(f"✅ Server is running at {self.base_url}")
        except:
            server_running = False
            print(f"❌ Server not accessible at {self.base_url}")
            return False
        
        if not server_running:
            return False
        
        # Run test suites
        self.test_authentication_flow()
        self.test_protected_pages()
        self.test_static_resources()
        
        return True
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 50)
        print("🧪 WEB INTERFACE TEST REPORT")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        print(f"\n📝 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['url']} - {result['description']}")
            
            if not result['success']:
                if 'error' in result:
                    print(f"      Error: {result['error']}")
                else:
                    print(f"      Expected: {result['expected_status']}, Got: {result['actual_status']}")
        
        # Performance summary
        response_times = [r['response_time'] for r in self.test_results if r['response_time'] is not None]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            print(f"\n⚡ PERFORMANCE:")
            print(f"   Average Response Time: {avg_time:.3f}s")
            print(f"   Slowest Response: {max_time:.3f}s")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = WebInterfaceTester()
    
    # Wait a moment for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    if tester.run_all_tests():
        all_passed = tester.generate_report()
        exit_code = 0 if all_passed else 1
    else:
        print("❌ Could not connect to server for testing")
        exit_code = 1
    
    print("\n🎉 Web interface testing completed!")
    exit(exit_code)