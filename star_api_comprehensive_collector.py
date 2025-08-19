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
backend_path = os.path.j            md_content = f"""# 📊 Star API Comprehensive Data Collection Report
            
**Generated:** {timestamp}  
**Usernames Analyzed:** {', '.join([f'@{u}' for u in usernames])}  
**Total Users:** {len(usernames)}
            
---
            
## 📋 Executive Summary
            
""".dirname(__file__), 'backend')
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
            
        def collect_comprehensive_user_data(self, username: str) -> dict:
            """
            Collect comprehensive data for a single user across all endpoints
            """
            print(f"🚀 Starting comprehensive data collection for: @{username}")
            print("=" * 60)
            
            user_data = {
                'username': username,
                'collection_start': datetime.now(IST).isoformat(),
                'data_points': {},
                'endpoint_results': {},
                'metrics': {},
                'errors': []
            }
            
            try:
                # 1. Profile Information
                print("📋 Collecting Profile Information...")
                profile_result = self._collect_profile_data(username)
                user_data['data_points']['profile'] = profile_result
                
                if profile_result.get('success') and profile_result.get('user_id'):
                    user_id = profile_result['user_id']
                    print(f"   ✅ Profile data collected - User ID: {user_id}")
                    
                    # 2. Media Posts
                    print("\\n📸 Collecting Media Posts...")
                    media_result = self._collect_media_data(user_id, username)
                    user_data['data_points']['media'] = media_result
                    
                    # 3. Stories
                    print("\\n📖 Collecting Stories...")
                    stories_result = self._collect_stories_data(user_id, username)
                    user_data['data_points']['stories'] = stories_result
                    
                    # 4. Highlights
                    print("\\n⭐ Collecting Highlights...")
                    highlights_result = self._collect_highlights_data(user_id, username)
                    user_data['data_points']['highlights'] = highlights_result
                    
                    # 5. Following/Followers
                    print("\\n👥 Collecting Following/Followers...")
                    social_result = self._collect_social_data(user_id, username)
                    user_data['data_points']['social'] = social_result
                    
                    # 6. Additional Data
                    print("\\n🔍 Collecting Additional Data...")
                    additional_result = self._collect_additional_data(user_id, username)
                    user_data['data_points']['additional'] = additional_result
                    
                else:
                    print("   ❌ Failed to get profile data - skipping other endpoints")
                    user_data['errors'].append("Failed to collect profile data")
                
            except Exception as e:
                error_msg = f"Error in comprehensive collection: {str(e)}"
                print(f"   ❌ {error_msg}")
                user_data['errors'].append(error_msg)
            
            user_data['collection_end'] = datetime.now(IST).isoformat()
            self.report_data['user_data_collected'][username] = user_data
            
            return user_data
        
        def _collect_profile_data(self, username: str) -> dict:
            """Collect profile information"""
            try:
                result = self.star_api.get_user_info_by_username(username)
                if result and result.get('data', {}).get('response', {}).get('body', {}).get('data'):
                    user_data = result['data']['response']['body']['data']['user']
                    
                    profile_info = {
                        'success': True,
                        'user_id': user_data.get('id'),
                        'username': user_data.get('username'),
                        'full_name': user_data.get('full_name'),
                        'biography': user_data.get('biography'),
                        'followers_count': user_data.get('edge_followed_by', {}).get('count', 0),
                        'following_count': user_data.get('edge_follow', {}).get('count', 0),
                        'media_count': user_data.get('edge_owner_to_timeline_media', {}).get('count', 0),
                        'is_verified': user_data.get('is_verified', False),
                        'is_private': user_data.get('is_private', False),
                        'is_business_account': user_data.get('is_business_account', False),
                        'profile_pic_url': user_data.get('profile_pic_url_hd'),
                        'external_url': user_data.get('external_url'),
                        'business_category': user_data.get('business_category_name'),
                        'raw_data_size': len(str(result))
                    }
                    
                    print(f"   📊 Profile Stats: {profile_info['followers_count']:,} followers, {profile_info['media_count']} posts")
                    return profile_info
                else:
                    return {'success': False, 'error': 'No profile data returned'}
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        def _collect_media_data(self, user_id: str, username: str) -> dict:
            """Collect media posts data"""
            try:
                result = self.star_api.get_user_media(user_id, count=50)
                if result and result.get('data', {}).get('response', {}).get('body', {}).get('data'):
                    media_data = result['data']['response']['body']['data']['user']['edge_owner_to_timeline_media']
                    media_count = media_data.get('count', 0)
                    edges = media_data.get('edges', [])
                    
                    # Analyze media types and engagement
                    media_analysis = {
                        'success': True,
                        'total_media': media_count,
                        'fetched_media': len(edges),
                        'media_types': {},
                        'engagement_stats': {
                            'total_likes': 0,
                            'total_comments': 0,
                            'avg_likes': 0,
                            'avg_comments': 0
                        },
                        'recent_posts': [],
                        'raw_data_size': len(str(result))
                    }
                    
                    for edge in edges[:10]:  # Analyze first 10 posts
                        node = edge.get('node', {})
                        media_type = 'photo'
                        if node.get('is_video'):
                            media_type = 'video'
                        elif node.get('edge_sidecar_to_children'):
                            media_type = 'carousel'
                        
                        media_analysis['media_types'][media_type] = media_analysis['media_types'].get(media_type, 0) + 1
                        
                        likes = node.get('edge_liked_by', {}).get('count', 0)
                        comments = node.get('edge_media_to_comment', {}).get('count', 0)
                        
                        media_analysis['engagement_stats']['total_likes'] += likes
                        media_analysis['engagement_stats']['total_comments'] += comments
                        
                        media_analysis['recent_posts'].append({
                            'shortcode': node.get('shortcode'),
                            'media_type': media_type,
                            'likes': likes,
                            'comments': comments,
                            'caption_preview': (node.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node', {}).get('text', ''))[:100]
                        })
                    
                    if edges:
                        media_analysis['engagement_stats']['avg_likes'] = media_analysis['engagement_stats']['total_likes'] // len(edges)
                        media_analysis['engagement_stats']['avg_comments'] = media_analysis['engagement_stats']['total_comments'] // len(edges)
                    
                    print(f"   📸 Media Analysis: {len(edges)} posts fetched, {media_analysis['media_types']}")
                    return media_analysis
                else:
                    return {'success': False, 'error': 'No media data returned'}
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        def _collect_stories_data(self, user_id: str, username: str) -> dict:
            """Collect stories data"""
            try:
                result = self.star_api.get_user_stories(user_id)
                if result:
                    stories_analysis = {
                        'success': True,
                        'has_stories': bool(result.get('data', {}).get('response', {}).get('body', {}).get('data')),
                        'raw_data_size': len(str(result))
                    }
                    print(f"   📖 Stories: {'Available' if stories_analysis['has_stories'] else 'None'}")
                    return stories_analysis
                else:
                    return {'success': False, 'error': 'No stories data returned'}
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        def _collect_highlights_data(self, user_id: str, username: str) -> dict:
            """Collect highlights data"""
            try:
                result = self.star_api.get_user_highlights(user_id)
                if result:
                    highlights_analysis = {
                        'success': True,
                        'has_highlights': bool(result.get('data', {}).get('response', {}).get('body', {}).get('data')),
                        'raw_data_size': len(str(result))
                    }
                    print(f"   ⭐ Highlights: {'Available' if highlights_analysis['has_highlights'] else 'None'}")
                    return highlights_analysis
                else:
                    return {'success': False, 'error': 'No highlights data returned'}
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        def _collect_social_data(self, user_id: str, username: str) -> dict:
            """Collect following/followers data"""
            social_analysis = {
                'following': {'success': False},
                'followers': {'success': False}
            }
            
            try:
                # Following
                following_result = self.star_api.get_user_following(user_id, count=20)
                if following_result:
                    social_analysis['following'] = {
                        'success': True,
                        'has_data': bool(following_result.get('data', {}).get('response', {}).get('body', {}).get('data')),
                        'raw_data_size': len(str(following_result))
                    }
                    print(f"   👥 Following: {'Available' if social_analysis['following']['has_data'] else 'Limited'}")
                
                time.sleep(1)  # Rate limiting
                
                # Followers (may be rate limited)
                followers_result = self.star_api.get_user_followers(user_id, count=20)
                if followers_result:
                    social_analysis['followers'] = {
                        'success': True,
                        'has_data': bool(followers_result.get('data', {}).get('response', {}).get('body', {}).get('data')),
                        'raw_data_size': len(str(followers_result))
                    }
                    print(f"   👥 Followers: {'Available' if social_analysis['followers']['has_data'] else 'Limited'}")
                
            except Exception as e:
                social_analysis['error'] = str(e)
                print(f"   ⚠️ Social data collection limited: {str(e)}")
            
            return social_analysis
        
        def _collect_additional_data(self, user_id: str, username: str) -> dict:
            """Collect additional data like guides, clips, etc."""
            additional_analysis = {}
            
            try:
                # Clips/Reels
                clips_result = self.star_api.get_user_clips(user_id, count=20)
                additional_analysis['clips'] = {
                    'success': bool(clips_result),
                    'has_data': bool(clips_result.get('data', {}).get('response', {}).get('body', {}).get('data')) if clips_result else False,
                    'raw_data_size': len(str(clips_result)) if clips_result else 0
                }
                
                time.sleep(1)  # Rate limiting
                
                # Guides
                guides_result = self.star_api.get_user_guides(user_id)
                additional_analysis['guides'] = {
                    'success': bool(guides_result),
                    'has_data': bool(guides_result.get('data', {}).get('response', {}).get('body', {}).get('data')) if guides_result else False,
                    'raw_data_size': len(str(guides_result)) if guides_result else 0
                }
                
                print(f"   🔍 Additional: Clips {'✅' if additional_analysis['clips']['has_data'] else '❌'}, Guides {'✅' if additional_analysis['guides']['has_data'] else '❌'}")
                
            except Exception as e:
                additional_analysis['error'] = str(e)
                print(f"   ⚠️ Additional data collection error: {str(e)}")
            
            return additional_analysis
        
        def generate_markdown_report(self, usernames: list) -> str:
            """
            Generate comprehensive Markdown report of collected data
            """
            timestamp = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')
            
            md_content = f\"\"\"# 📊 Star API Comprehensive Data Collection Report
            
**Generated:** {timestamp}  
**Usernames Analyzed:** {', '.join([f'@{u}' for u in usernames])}  
**Total Users:** {len(usernames)}
            
---
            
## 📋 Executive Summary
            
\"\"\"
            
            # Add summary statistics
            total_endpoints_tested = 0
            successful_collections = 0
            
            for username, user_data in self.report_data['user_data_collected'].items():
                total_endpoints_tested += len([k for k in user_data['data_points'].keys() if user_data['data_points'][k].get('success')])
                if user_data['data_points'].get('profile', {}).get('success'):
                    successful_collections += 1
            
            md_content += f\"\"\"
- **✅ Successful Collections:** {successful_collections}/{len(usernames)} users
- **📡 Total Endpoints Tested:** {total_endpoints_tested}
- **🕒 Collection Duration:** Comprehensive multi-endpoint analysis
- **📊 Data Quality:** Real-time Instagram data via Star API
            
---
            
\"\"\"
            
            # Add detailed user reports
            for username, user_data in self.report_data['user_data_collected'].items():
                md_content += self._generate_user_report_section(username, user_data)
            
            # Add technical summary
            md_content += self._generate_technical_summary()
            
            return md_content
        
        def _generate_user_report_section(self, username: str, user_data: dict) -> str:
            """Generate detailed report section for a single user"""
            
            profile_data = user_data['data_points'].get('profile', {})
            media_data = user_data['data_points'].get('media', {})
            
            section = f\"\"\"
## 👤 @{username} - Detailed Analysis
            
### 📊 Profile Overview
\"\"\"
            
            if profile_data.get('success'):
                section += f\"\"\"
- **Full Name:** {profile_data.get('full_name', 'N/A')}
- **Followers:** {profile_data.get('followers_count', 0):,}
- **Following:** {profile_data.get('following_count', 0):,}
- **Posts:** {profile_data.get('media_count', 0):,}
- **Verified:** {'✅' if profile_data.get('is_verified') else '❌'}
- **Private:** {'🔒' if profile_data.get('is_private') else '🌍'}
- **Business Account:** {'💼' if profile_data.get('is_business_account') else '👤'}
- **Biography:** {profile_data.get('biography', 'N/A')[:100]}...
\"\"\"
            else:
                section += "\\n❌ **Profile data collection failed**\\n"
            
            # Media Analysis
            section += "\\n### 📸 Content Analysis\\n"
            if media_data.get('success'):
                engagement = media_data.get('engagement_stats', {})
                media_types = media_data.get('media_types', {})
                
                section += f\"\"\"
- **Total Media:** {media_data.get('total_media', 0):,}
- **Analyzed Posts:** {media_data.get('fetched_media', 0)}
- **Media Types:** {', '.join([f'{k.title()}: {v}' for k, v in media_types.items()])}
- **Average Likes:** {engagement.get('avg_likes', 0):,}
- **Average Comments:** {engagement.get('avg_comments', 0):,}
- **Engagement Rate:** {(engagement.get('avg_likes', 0) + engagement.get('avg_comments', 0)) / max(profile_data.get('followers_count', 1), 1) * 100:.2f}%
                
#### 🔥 Recent Posts Performance
\"\"\"
                
                for i, post in enumerate(media_data.get('recent_posts', [])[:5], 1):
                    section += f\"\"\"
{i}. **{post['shortcode']}** ({post['media_type']}) - {post['likes']:,} likes, {post['comments']:,} comments
   *{post['caption_preview']}...*
\"\"\"
            else:
                section += "\\n❌ **Media data collection failed**\\n"
            
            # Other data points
            section += "\\n### 🔍 Additional Data Collection Status\\n"
            
            data_points = user_data['data_points']
            status_items = [
                ('📖 Stories', data_points.get('stories', {}).get('success', False)),
                ('⭐ Highlights', data_points.get('highlights', {}).get('success', False)),
                ('👥 Social Network', data_points.get('social', {}).get('following', {}).get('success', False)),
                ('🎬 Clips/Reels', data_points.get('additional', {}).get('clips', {}).get('success', False)),
                ('📚 Guides', data_points.get('additional', {}).get('guides', {}).get('success', False))
            ]
            
            for item_name, success in status_items:
                section += f"- {item_name}: {'✅ Available' if success else '❌ Limited/Failed'}\\n"
            
            if user_data.get('errors'):
                section += "\\n### ⚠️ Collection Errors\\n"
                for error in user_data['errors']:
                    section += f"- {error}\\n"
            
            section += "\\n---\\n"
            return section
        
        def _generate_technical_summary(self) -> str:
            """Generate technical summary section"""
            return f\"\"\"
## 🔧 Technical Summary
            
### 📡 Star API Endpoints Status
- **Profile Data:** Instagram user profile information
- **Media Posts:** Timeline posts with engagement metrics  
- **Stories:** Current active stories
- **Highlights:** Saved story highlights
- **Social Network:** Following/followers data (rate limited)
- **Clips/Reels:** Short-form video content
- **Guides:** User-created guides
            
### 📊 Data Quality Metrics
- **Real-time Data:** ✅ Direct from Instagram via Star API
- **Rate Limiting:** ⚠️ Some endpoints have usage limits
- **Data Freshness:** 🕒 Live data at collection time
- **Coverage:** 📈 Multi-dimensional Instagram analytics
            
### 🚀 Next Steps
1. **Database Storage:** Save collected data to analytics database
2. **Trend Analysis:** Compare data over time periods
3. **Engagement Insights:** Analyze post performance patterns
4. **Competitive Analysis:** Compare multiple accounts
5. **Content Strategy:** Use insights for content planning
            
---
            
*Report generated by Star API Comprehensive Collector*  
*Timestamp: {datetime.now(IST).isoformat()}*
\"\"\"
        
        def save_report(self, content: str, filename: str = None) -> str:
            """Save the markdown report to file"""
            if not filename:
                timestamp = datetime.now(IST).strftime('%Y%m%d_%H%M%S')
                filename = f"star_api_comprehensive_report_{timestamp}.md"
            
            filepath = os.path.join(os.path.dirname(__file__), filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"\\n📄 Report saved to: {filepath}")
            return filepath

    def main():
        """Main execution function"""
        print("🌟 Star API Comprehensive Data Collector")
        print("=" * 50)
        
        # Get API key
        api_key = os.getenv('RAPID_API_KEY') or os.getenv('API_KEY')
        if not api_key:
            print("❌ Error: API key not found in environment variables")
            print("   Please set RAPID_API_KEY or API_KEY in your .env file")
            return
        
        # Initialize collector
        collector = StarAPIComprehensiveCollector(api_key)
        
        # Get usernames to analyze
        print("\\n📝 Enter Instagram usernames to analyze (comma-separated):")
        print("   Example: nasa, spacex, tesla")
        usernames_input = input("   Usernames: ").strip()
        
        if not usernames_input:
            print("\\n🔍 Using default test usernames: nasa, instagram")
            usernames = ['nasa', 'instagram']
        else:
            usernames = [u.strip() for u in usernames_input.split(',')]
        
        print(f"\\n🎯 Analyzing {len(usernames)} account(s): {', '.join([f'@{u}' for u in usernames])}")
        print("\\n" + "="*60)
        
        # Collect data for each user
        for i, username in enumerate(usernames, 1):
            print(f"\\n\\n[{i}/{len(usernames)}] Collecting data for @{username}")
            print("-" * 40)
            
            try:
                collector.collect_comprehensive_user_data(username)
                print(f"\\n✅ Completed data collection for @{username}")
                
                # Add delay between users to respect rate limits
                if i < len(usernames):
                    print(f"\\n⏱️ Waiting 3 seconds before next user...")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"\\n❌ Error collecting data for @{username}: {str(e)}")
                collector.report_data['errors'].append(f"Failed to collect data for @{username}: {str(e)}")
        
        print("\\n\\n" + "="*60)
        print("📊 GENERATING COMPREHENSIVE REPORT")
        print("="*60)
        
        # Generate and save report
        try:
            report_content = collector.generate_markdown_report(usernames)
            report_path = collector.save_report(report_content)
            
            print(f"\\n🎉 SUCCESS! Comprehensive data collection completed!")
            print(f"\\n📄 Detailed report available at: {report_path}")
            print(f"\\n🔍 Report includes:")
            print("   • Profile analytics and metrics")
            print("   • Content performance analysis") 
            print("   • Engagement rate calculations")
            print("   • Media type distribution")
            print("   • Technical collection status")
            print("   • Next steps recommendations")
            
            return report_path
            
        except Exception as e:
            print(f"\\n❌ Error generating report: {str(e)}")
            return None

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running this from the project root directory")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
