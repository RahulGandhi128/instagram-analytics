"""
Comprehensive Test Suite for Star API Service
Tests all endpoints and data collection functionality
"""
import requests
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class StarAPITester:
    def __init__(self, base_url="http://localhost:5000/api"):
        self.base_url = base_url
        self.test_username = "instagram"  # Safe test username
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'base_url': base_url,
            'test_username': self.test_username,
            'endpoint_tests': {},
            'database_tests': {},
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0
            }
        }
    
    def log_result(self, test_name, success, details=None, error=None):
        """Log test result"""
        self.results['summary']['total_tests'] += 1
        if success:
            self.results['summary']['passed'] += 1
            status = "PASS"
        else:
            self.results['summary']['failed'] += 1
            status = "FAIL"
        
        self.results['endpoint_tests'][test_name] = {
            'status': status,
            'success': success,
            'details': details,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"[{status}] {test_name}")
        if error:
            print(f"    Error: {error}")
        if details:
            print(f"    Details: {details}")
    
    def test_endpoint(self, endpoint, method="GET", data=None):
        """Test an API endpoint"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=30)
            else:
                return False, f"Unsupported method: {method}"
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                return True, result.get('data', {})
            else:
                return False, result.get('error', 'Unknown error')
                
        except requests.exceptions.Timeout:
            return False, "Request timeout"
        except requests.exceptions.RequestException as e:
            return False, f"Request error: {str(e)}"
        except json.JSONDecodeError:
            return False, "Invalid JSON response"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def test_database_status(self):
        """Test database status endpoint"""
        print("\\n=== Testing Database Status ===")
        
        success, data = self.test_endpoint("/star-api/database-status")
        
        if success:
            self.results['database_tests']['status'] = data
            self.log_result(
                "database_status",
                True,
                f"Profiles: {data.get('profiles', 0)}, "
                f"Media: {data.get('media_posts', 0)}, "
                f"Stories: {data.get('stories', 0)}"
            )
        else:
            self.log_result("database_status", False, error=data)
    
    def test_star_api_endpoints(self):
        """Test all Star API endpoints"""
        print("\\n=== Testing Star API Endpoints ===")
        
        # Test endpoint testing functionality
        success, data = self.test_endpoint(
            "/star-api/test-endpoints",
            "POST",
            {"username": self.test_username}
        )
        
        if success:
            test_results = data
            endpoint_results = test_results.get('endpoint_results', {})
            
            for endpoint_name, result in endpoint_results.items():
                self.log_result(
                    f"star_api_{endpoint_name}",
                    result['status'] == 'success',
                    f"Data size: {result.get('data_size', 0)} bytes" if result['status'] == 'success' else None,
                    result.get('error') if result['status'] != 'success' else None
                )
        else:
            self.log_result("star_api_test_endpoints", False, error=data)
    
    def test_individual_endpoints(self):
        """Test individual Star API endpoints"""
        print("\\n=== Testing Individual Star API Endpoints ===")
        
        # Test user info
        success, data = self.test_endpoint(f"/star-api/user-info/{self.test_username}")
        self.log_result(
            "user_info_endpoint",
            success,
            f"Response size: {len(str(data))} chars" if success else None,
            data if not success else None
        )
        
        # Test user media
        success, data = self.test_endpoint(f"/star-api/user-media/{self.test_username}?count=10")
        self.log_result(
            "user_media_endpoint",
            success,
            f"Response size: {len(str(data))} chars" if success else None,
            data if not success else None
        )
        
        # Test user stories
        success, data = self.test_endpoint(f"/star-api/user-stories/{self.test_username}")
        self.log_result(
            "user_stories_endpoint",
            success,
            f"Response size: {len(str(data))} chars" if success else None,
            data if not success else None
        )
    
    def test_comprehensive_collection(self):
        """Test comprehensive data collection"""
        print("\\n=== Testing Comprehensive Data Collection ===")
        
        success, data = self.test_endpoint(
            f"/star-api/collect-comprehensive/{self.test_username}",
            "POST"
        )
        
        if success:
            collection_result = data
            data_collected = collection_result.get('data_collected', {})
            errors = collection_result.get('errors', [])
            
            self.log_result(
                "comprehensive_collection",
                collection_result.get('success', False),
                f"Data collected: {list(data_collected.keys())}, Errors: {len(errors)}",
                "; ".join(errors) if errors else None
            )
        else:
            self.log_result("comprehensive_collection", False, error=data)
    
    def test_existing_instagram_api(self):
        """Test existing Instagram API endpoints for comparison"""
        print("\\n=== Testing Existing Instagram API Endpoints ===")
        
        # Test existing fetch endpoint
        success, data = self.test_endpoint("/fetch-data", "POST")
        self.log_result(
            "existing_fetch_data",
            success,
            "Existing API working" if success else None,
            data if not success else None
        )
        
        # Test analytics endpoints
        success, data = self.test_endpoint("/analytics/summary-stats")
        self.log_result(
            "existing_analytics",
            success,
            f"Analytics data available" if success else None,
            data if not success else None
        )
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\\n" + "="*60)
        print("STAR API TEST REPORT")
        print("="*60)
        
        # Summary
        summary = self.results['summary']
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success Rate: {(summary['passed']/summary['total_tests']*100):.1f}%" if summary['total_tests'] > 0 else "N/A")
        
        # Failed tests
        failed_tests = [
            name for name, result in self.results['endpoint_tests'].items()
            if not result['success']
        ]
        
        if failed_tests:
            print(f"\\nFailed Tests ({len(failed_tests)}):")
            for test_name in failed_tests:
                error = self.results['endpoint_tests'][test_name]['error']
                print(f"  - {test_name}: {error}")
        
        # Database status
        if 'status' in self.results['database_tests']:
            db_status = self.results['database_tests']['status']
            print(f"\\nDatabase Status:")
            print(f"  - Profiles: {db_status.get('profiles', 0)}")
            print(f"  - Media Posts: {db_status.get('media_posts', 0)}")
            print(f"  - Stories: {db_status.get('stories', 0)}")
            print(f"  - Daily Metrics: {db_status.get('daily_metrics', 0)}")
        
        # Recommendations
        print(f"\\nRecommendations:")
        if summary['failed'] == 0:
            print("  ✅ All tests passed! Star API integration is working perfectly.")
        elif summary['failed'] < summary['total_tests'] / 2:
            print("  ⚠️  Most tests passed. Check failed endpoints for minor issues.")
        else:
            print("  ❌ Many tests failed. Check API key configuration and network connectivity.")
        
        print("\\n" + "="*60)
        
        return self.results
    
    def save_report(self, filename=None):
        """Save test report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"star_api_test_report_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\\nTest report saved to: {filename}")
            return filename
        except Exception as e:
            print(f"\\nFailed to save report: {e}")
            return None
    
    def run_all_tests(self):
        """Run all tests"""
        print("Starting Star API Comprehensive Test Suite...")
        print(f"Test Username: {self.test_username}")
        print(f"Base URL: {self.base_url}")
        print(f"Timestamp: {self.results['timestamp']}")
        
        # Run all test categories
        self.test_database_status()
        time.sleep(1)  # Small delay between test categories
        
        self.test_existing_instagram_api()
        time.sleep(1)
        
        self.test_individual_endpoints()
        time.sleep(2)  # Longer delay before comprehensive tests
        
        self.test_star_api_endpoints()
        time.sleep(2)
        
        self.test_comprehensive_collection()
        
        # Generate and save report
        report = self.generate_report()
        self.save_report()
        
        return report

def main():
    """Main function to run tests"""
    print("Star API Service Test Suite")
    print("=" * 40)
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:5000/api/analytics/summary-stats", timeout=5)
        print("✅ Backend server is running")
    except:
        print("❌ Backend server is not running. Please start it first:")
        print("   cd backend && python app.py")
        return
    
    # Check API key
    api_key = os.getenv('API_KEY')
    if not api_key:
        print("❌ API_KEY not found in environment variables")
        print("   Please check your .env file")
        return
    else:
        print("✅ API key found")
    
    # Run tests
    tester = StarAPITester()
    results = tester.run_all_tests()
    
    # Return results for programmatic use
    return results

if __name__ == "__main__":
    main()
