"""
Star API Comprehensive Data Collector
Collects and documents all available Instagram data using Star API endpoints
Generates detailed Markdown reports for analysis
"""
import sys
import os
import json
from datetime import datetime
import pytz

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

try:
    from services.star_api_service import StarAPIService
    from dotenv import load_dotenv
    import time
    
    # Load environment variables
    load_dotenv()
    
    # Timezone setup
    IST = pytz.timezone('Asia/Kolkata')
    
    class StarAPIComprehensiveCollector:
        """
        Comprehensive Star API data collector with detailed reporting
        """
        
        def __init__(self, api_key: str):
            self.api_key = api_key
            self.star_api = StarAPIService(api_key)
            self.report_data = {
                'collection_timestamp': datetime.now(IST).isoformat(),
                'endpoints_tested': {},
                'user_data_collected': {},
                'summary_stats': {},
                'errors': []
            }
        
        def collect_user_data(self, username: str) -> dict:
            """Collect comprehensive data for a single user"""
            print(f"🚀 Collecting data for: @{username}")
            
            user_data = {
                'username': username,
                'collection_start': datetime.now(IST).isoformat(),
                'data_points': {},
                'errors': []
            }
            
            try:
                # 1. Profile Information
                print("📋 Collecting profile...")
                profile_result = self.star_api.get_user_info_by_username(username)
                if profile_result and profile_result.get('data'):
                    user_data['data_points']['profile'] = self._analyze_profile(profile_result)
                    print(f"   ✅ Profile data collected")
                    
                    # Extract user ID for other endpoints
                    try:
                        user_id = profile_result['data']['response']['body']['data']['user']['id']
                        
                        # 2. Media Posts
                        print("📸 Collecting media...")
                        media_result = self.star_api.get_user_media(user_id, count=20)
                        if media_result:
                            user_data['data_points']['media'] = self._analyze_media(media_result)
                            print(f"   ✅ Media data collected")
                        
                        # 3. Stories
                        print("📖 Collecting stories...")
                        stories_result = self.star_api.get_user_stories(user_id)
                        if stories_result:
                            user_data['data_points']['stories'] = {'success': True, 'has_data': bool(stories_result.get('data'))}
                            print(f"   ✅ Stories data collected")
                        
                        # 4. Highlights
                        print("⭐ Collecting highlights...")
                        highlights_result = self.star_api.get_user_highlights(user_id)
                        if highlights_result:
                            user_data['data_points']['highlights'] = {'success': True, 'has_data': bool(highlights_result.get('data'))}
                            print(f"   ✅ Highlights data collected")
                            
                    except Exception as e:
                        user_data['errors'].append(f"Failed to extract user_id: {str(e)}")
                        
                else:
                    user_data['errors'].append("Failed to get profile data")
                    
            except Exception as e:
                user_data['errors'].append(f"Collection error: {str(e)}")
            
            self.report_data['user_data_collected'][username] = user_data
            return user_data
        
        def _analyze_profile(self, profile_result: dict) -> dict:
            """Analyze profile data"""
            try:
                user_data = profile_result['data']['response']['body']['data']['user']
                return {
                    'success': True,
                    'username': user_data.get('username'),
                    'full_name': user_data.get('full_name'),
                    'followers_count': user_data.get('edge_followed_by', {}).get('count', 0),
                    'following_count': user_data.get('edge_follow', {}).get('count', 0),
                    'media_count': user_data.get('edge_owner_to_timeline_media', {}).get('count', 0),
                    'is_verified': user_data.get('is_verified', False),
                    'is_private': user_data.get('is_private', False),
                    'biography': user_data.get('biography', ''),
                    'user_id': user_data.get('id')
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        def _analyze_media(self, media_result: dict) -> dict:
            """Analyze media data"""
            try:
                media_data = media_result['data']['response']['body']['data']['user']['edge_owner_to_timeline_media']
                edges = media_data.get('edges', [])
                
                analysis = {
                    'success': True,
                    'total_media': media_data.get('count', 0),
                    'fetched_count': len(edges),
                    'media_types': {},
                    'engagement': {'total_likes': 0, 'total_comments': 0}
                }
                
                for edge in edges:
                    node = edge.get('node', {})
                    media_type = 'photo'
                    if node.get('is_video'):
                        media_type = 'video'
                    elif node.get('edge_sidecar_to_children'):
                        media_type = 'carousel'
                    
                    analysis['media_types'][media_type] = analysis['media_types'].get(media_type, 0) + 1
                    analysis['engagement']['total_likes'] += node.get('edge_liked_by', {}).get('count', 0)
                    analysis['engagement']['total_comments'] += node.get('edge_media_to_comment', {}).get('count', 0)
                
                return analysis
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        def generate_markdown_report(self, usernames: list) -> str:
            """Generate comprehensive Markdown report"""
            timestamp = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')
            
            md_content = f"""# 📊 Star API Comprehensive Data Collection Report

**Generated:** {timestamp}  
**Usernames Analyzed:** {', '.join([f'@{u}' for u in usernames])}

---

## 📋 Executive Summary

"""
            
            # Summary statistics
            successful_collections = len([u for u, data in self.report_data['user_data_collected'].items() 
                                        if data['data_points'].get('profile', {}).get('success')])
            
            md_content += f"""
- **✅ Successful Collections:** {successful_collections}/{len(usernames)} users
- **🔧 Star API Status:** Active and collecting real-time data
- **📊 Data Types:** Profile, Media, Stories, Highlights

---

"""
            
            # Individual user reports
            for username, user_data in self.report_data['user_data_collected'].items():
                md_content += self._generate_user_section(username, user_data)
            
            # Technical summary
            md_content += f"""
## 🔧 Technical Summary

### Star API Endpoints Used
- **Profile Data:** User information and basic metrics
- **Media Posts:** Timeline content with engagement data
- **Stories:** Current active stories
- **Highlights:** Saved story highlights

### Data Quality
- **Real-time:** ✅ Live data from Instagram
- **Comprehensive:** ✅ Multi-endpoint collection
- **Rate Limited:** ⚠️ Some endpoints have usage restrictions

---

*Report generated by Star API Comprehensive Collector*  
*Timestamp: {datetime.now(IST).isoformat()}*
"""
            
            return md_content
        
        def _generate_user_section(self, username: str, user_data: dict) -> str:
            """Generate report section for a user"""
            profile = user_data['data_points'].get('profile', {})
            media = user_data['data_points'].get('media', {})
            
            section = f"""
## 👤 @{username} Analysis

"""
            
            if profile.get('success'):
                section += f"""### 📊 Profile Metrics
- **Full Name:** {profile.get('full_name', 'N/A')}
- **Followers:** {profile.get('followers_count', 0):,}
- **Following:** {profile.get('following_count', 0):,}
- **Posts:** {profile.get('media_count', 0):,}
- **Verified:** {'✅' if profile.get('is_verified') else '❌'}
- **Private:** {'🔒' if profile.get('is_private') else '🌍'}
- **Bio:** {profile.get('biography', 'N/A')[:100]}...

"""
            else:
                section += "❌ **Profile data collection failed**\n\n"
            
            if media.get('success'):
                engagement = media.get('engagement', {})
                types = media.get('media_types', {})
                
                section += f"""### 📸 Content Analysis
- **Total Posts:** {media.get('total_media', 0):,}
- **Analyzed:** {media.get('fetched_count', 0)} recent posts
- **Media Types:** {', '.join([f'{k}: {v}' for k, v in types.items()])}
- **Total Likes:** {engagement.get('total_likes', 0):,}
- **Total Comments:** {engagement.get('total_comments', 0):,}

"""
            
            # Collection status
            section += f"""### 🔍 Collection Status
- **Profile:** {'✅' if profile.get('success') else '❌'}
- **Media:** {'✅' if media.get('success') else '❌'}
- **Stories:** {'✅' if user_data['data_points'].get('stories', {}).get('success') else '❌'}
- **Highlights:** {'✅' if user_data['data_points'].get('highlights', {}).get('success') else '❌'}

"""
            
            if user_data.get('errors'):
                section += "### ⚠️ Errors\n"
                for error in user_data['errors']:
                    section += f"- {error}\n"
                section += "\n"
            
            section += "---\n\n"
            return section
        
        def save_report(self, content: str, filename: str = None) -> str:
            """Save markdown report to file"""
            if not filename:
                timestamp = datetime.now(IST).strftime('%Y%m%d_%H%M%S')
                filename = f"star_api_report_{timestamp}.md"
            
            filepath = os.path.join(os.path.dirname(__file__), filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return filepath

    def main():
        """Main execution function"""
        print("🌟 Star API Comprehensive Data Collector")
        print("=" * 50)
        
        # Get API key
        api_key = os.getenv('RAPID_API_KEY') or os.getenv('API_KEY')
        if not api_key:
            print("❌ Error: API key not found")
            print("Please set RAPID_API_KEY or API_KEY in .env file")
            return
        
        print(f"✅ API Key found: {api_key[:10]}...")
        
        # Initialize collector
        collector = StarAPIComprehensiveCollector(api_key)
        
        # Default usernames for comprehensive analysis
        usernames = ['nasa', 'spacex', 'tesla']
        print(f"🎯 Analyzing accounts: {', '.join([f'@{u}' for u in usernames])}")
        print("\n" + "="*50)
        
        # Collect data
        for i, username in enumerate(usernames, 1):
            print(f"\n[{i}/{len(usernames)}] Processing @{username}")
            print("-" * 30)
            
            try:
                collector.collect_user_data(username)
                print(f"✅ Completed @{username}")
                
                if i < len(usernames):
                    print("⏱️ Waiting 2 seconds...")
                    time.sleep(2)
                    
            except Exception as e:
                print(f"❌ Error with @{username}: {str(e)}")
        
        print("\n" + "="*50)
        print("📊 GENERATING REPORT")
        print("="*50)
        
        # Generate report
        try:
            report_content = collector.generate_markdown_report(usernames)
            report_path = collector.save_report(report_content)
            
            print(f"\n🎉 SUCCESS!")
            print(f"📄 Report saved: {report_path}")
            print(f"\n📊 Report includes:")
            print("   • Profile analytics")
            print("   • Content analysis")
            print("   • Engagement metrics")
            print("   • Collection status")
            
            # Show first few lines of report
            lines = report_content.split('\n')[:20]
            print(f"\n📝 Report preview:")
            print("-" * 30)
            for line in lines:
                print(line)
            print("...")
            
            return report_path
            
        except Exception as e:
            print(f"❌ Report generation error: {str(e)}")
            return None

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Ensure you're in the project root directory")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
