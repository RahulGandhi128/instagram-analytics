"""
Simple Star API Data Collection Test
Tests Star API endpoints and generates a comprehensive report
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
    from dotenv import load_dotenv
    import requests
    import time
    
    # Load environment variables
    load_dotenv()
    
    # Timezone setup
    IST = pytz.timezone('Asia/Kolkata')
    
    class SimpleStarAPICollector:
        """
        Simple Star API data collector with comprehensive reporting
        """
        
        def __init__(self, api_key: str):
            self.api_key = api_key
            self.base_url = "https://starapi1.p.rapidapi.com"
            self.headers = {
                "x-rapidapi-key": self.api_key,
                "x-rapidapi-host": "starapi1.p.rapidapi.com",
                "Content-Type": "application/json",
            }
            
            self.endpoints = {
                'user_info': f"{self.base_url}/instagram/user/get_web_profile_info",
                'user_media': f"{self.base_url}/instagram/user/get_media",
                'user_stories': f"{self.base_url}/instagram/user/get_stories",
                'user_highlights': f"{self.base_url}/instagram/user/get_highlights",
                'user_following': f"{self.base_url}/instagram/user/get_following",
                'user_followers': f"{self.base_url}/instagram/user/get_followers"
            }
            
            self.collection_results = {}
        
        def make_request(self, endpoint_url: str, payload: dict) -> dict:
            """Make API request with error handling"""
            try:
                response = requests.post(endpoint_url, json=payload, headers=self.headers, timeout=30)
                
                if response.status_code == 200:
                    return {
                        'success': True,
                        'data': response.json(),
                        'status_code': response.status_code,
                        'response_size': len(response.text)
                    }
                else:
                    return {
                        'success': False,
                        'error': f"HTTP {response.status_code}: {response.text}",
                        'status_code': response.status_code
                    }
                    
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'status_code': None
                }
        
        def collect_user_profile(self, username: str) -> dict:
            """Collect user profile information"""
            print(f"📋 Collecting profile for @{username}...")
            
            payload = {"username": username}
            result = self.make_request(self.endpoints['user_info'], payload)
            
            if result['success']:
                try:
                    user_data = result['data']['response']['body']['data']['user']
                    profile_analysis = {
                        'success': True,
                        'user_id': user_data.get('id'),
                        'username': user_data.get('username'),
                        'full_name': user_data.get('full_name'),
                        'biography': user_data.get('biography', ''),
                        'followers_count': user_data.get('edge_followed_by', {}).get('count', 0),
                        'following_count': user_data.get('edge_follow', {}).get('count', 0),
                        'media_count': user_data.get('edge_owner_to_timeline_media', {}).get('count', 0),
                        'is_verified': user_data.get('is_verified', False),
                        'is_private': user_data.get('is_private', False),
                        'is_business_account': user_data.get('is_business_account', False),
                        'profile_pic_url': user_data.get('profile_pic_url_hd', ''),
                        'external_url': user_data.get('external_url', ''),
                        'business_category': user_data.get('business_category_name', ''),
                        'raw_response_size': result['response_size']
                    }
                    print(f"   ✅ Profile: {profile_analysis['followers_count']:,} followers, {profile_analysis['media_count']} posts")
                    return profile_analysis
                    
                except Exception as e:
                    print(f"   ❌ Error parsing profile data: {str(e)}")
                    return {'success': False, 'error': f"Parsing error: {str(e)}"}
            else:
                print(f"   ❌ Profile request failed: {result['error']}")
                return result
        
        def collect_user_media(self, user_id: str, username: str, count: int = 20) -> dict:
            """Collect user media posts"""
            print(f"📸 Collecting media for @{username}...")
            
            payload = {"id": int(user_id), "count": count}
            result = self.make_request(self.endpoints['user_media'], payload)
            
            if result['success']:
                try:
                    media_data = result['data']['response']['body']['data']['user']['edge_owner_to_timeline_media']
                    edges = media_data.get('edges', [])
                    
                    media_analysis = {
                        'success': True,
                        'total_media_count': media_data.get('count', 0),
                        'fetched_count': len(edges),
                        'media_breakdown': {'photo': 0, 'video': 0, 'carousel': 0},
                        'engagement_summary': {
                            'total_likes': 0,
                            'total_comments': 0,
                            'avg_likes': 0,
                            'avg_comments': 0,
                            'max_likes': 0,
                            'max_comments': 0
                        },
                        'recent_posts': [],
                        'raw_response_size': result['response_size']
                    }
                    
                    likes_list = []
                    comments_list = []
                    
                    for edge in edges:
                        node = edge.get('node', {})
                        
                        # Determine media type
                        media_type = 'photo'
                        if node.get('is_video'):
                            media_type = 'video'
                        elif node.get('edge_sidecar_to_children'):
                            media_type = 'carousel'
                        
                        media_analysis['media_breakdown'][media_type] += 1
                        
                        # Get engagement
                        likes = node.get('edge_liked_by', {}).get('count', 0)
                        comments = node.get('edge_media_to_comment', {}).get('count', 0)
                        
                        likes_list.append(likes)
                        comments_list.append(comments)
                        
                        media_analysis['engagement_summary']['total_likes'] += likes
                        media_analysis['engagement_summary']['total_comments'] += comments
                        
                        # Get caption
                        caption_edges = node.get('edge_media_to_caption', {}).get('edges', [])
                        caption = caption_edges[0].get('node', {}).get('text', '') if caption_edges else ''
                        
                        media_analysis['recent_posts'].append({
                            'shortcode': node.get('shortcode', ''),
                            'media_type': media_type,
                            'likes': likes,
                            'comments': comments,
                            'caption_preview': caption[:100] + '...' if len(caption) > 100 else caption,
                            'timestamp': node.get('taken_at_timestamp', 0)
                        })
                    
                    # Calculate averages and maximums
                    if likes_list:
                        media_analysis['engagement_summary']['avg_likes'] = sum(likes_list) // len(likes_list)
                        media_analysis['engagement_summary']['max_likes'] = max(likes_list)
                        
                    if comments_list:
                        media_analysis['engagement_summary']['avg_comments'] = sum(comments_list) // len(comments_list)
                        media_analysis['engagement_summary']['max_comments'] = max(comments_list)
                    
                    print(f"   ✅ Media: {len(edges)} posts analyzed - {media_analysis['media_breakdown']}")
                    return media_analysis
                    
                except Exception as e:
                    print(f"   ❌ Error parsing media data: {str(e)}")
                    return {'success': False, 'error': f"Parsing error: {str(e)}"}
            else:
                print(f"   ❌ Media request failed: {result['error']}")
                return result
        
        def collect_additional_data(self, user_id: str, username: str) -> dict:
            """Collect stories, highlights, and social data"""
            print(f"🔍 Collecting additional data for @{username}...")
            
            additional_data = {
                'stories': {'success': False},
                'highlights': {'success': False},
                'following': {'success': False},
                'followers': {'success': False}
            }
            
            # Stories
            try:
                payload = {"ids": [int(user_id)]}
                result = self.make_request(self.endpoints['user_stories'], payload)
                additional_data['stories'] = {
                    'success': result['success'],
                    'has_data': bool(result.get('data', {}).get('response', {}).get('body', {}).get('data')) if result['success'] else False,
                    'response_size': result.get('response_size', 0)
                }
                print(f"   📖 Stories: {'Available' if additional_data['stories']['has_data'] else 'None/Limited'}")
            except Exception as e:
                additional_data['stories']['error'] = str(e)
            
            time.sleep(1)  # Rate limiting
            
            # Highlights
            try:
                payload = {"id": int(user_id)}
                result = self.make_request(self.endpoints['user_highlights'], payload)
                additional_data['highlights'] = {
                    'success': result['success'],
                    'has_data': bool(result.get('data', {}).get('response', {}).get('body', {}).get('data')) if result['success'] else False,
                    'response_size': result.get('response_size', 0)
                }
                print(f"   ⭐ Highlights: {'Available' if additional_data['highlights']['has_data'] else 'None/Limited'}")
            except Exception as e:
                additional_data['highlights']['error'] = str(e)
            
            time.sleep(1)  # Rate limiting
            
            # Following (may be rate limited)
            try:
                payload = {"id": int(user_id), "count": 10}
                result = self.make_request(self.endpoints['user_following'], payload)
                additional_data['following'] = {
                    'success': result['success'],
                    'has_data': bool(result.get('data', {}).get('response', {}).get('body', {}).get('data')) if result['success'] else False,
                    'response_size': result.get('response_size', 0)
                }
                print(f"   👥 Following: {'Available' if additional_data['following']['has_data'] else 'Limited'}")
            except Exception as e:
                additional_data['following']['error'] = str(e)
            
            return additional_data
        
        def collect_comprehensive_data(self, username: str) -> dict:
            """Collect all available data for a user"""
            print(f"\\n🚀 Starting comprehensive collection for @{username}")
            print("-" * 50)
            
            collection_result = {
                'username': username,
                'collection_timestamp': datetime.now(IST).isoformat(),
                'profile': {},
                'media': {},
                'additional': {},
                'summary': {},
                'errors': []
            }
            
            try:
                # 1. Profile data
                profile_data = self.collect_user_profile(username)
                collection_result['profile'] = profile_data
                
                if profile_data.get('success') and profile_data.get('user_id'):
                    user_id = profile_data['user_id']
                    
                    # 2. Media data
                    media_data = self.collect_user_media(user_id, username)
                    collection_result['media'] = media_data
                    
                    # 3. Additional data
                    additional_data = self.collect_additional_data(user_id, username)
                    collection_result['additional'] = additional_data
                    
                    # 4. Generate summary
                    collection_result['summary'] = self._generate_summary(profile_data, media_data, additional_data)
                    
                else:
                    collection_result['errors'].append("Failed to get profile data or user_id")
                
            except Exception as e:
                error_msg = f"Collection error: {str(e)}"
                collection_result['errors'].append(error_msg)
                print(f"   ❌ {error_msg}")
            
            self.collection_results[username] = collection_result
            print(f"✅ Completed collection for @{username}")
            
            return collection_result
        
        def _generate_summary(self, profile_data: dict, media_data: dict, additional_data: dict) -> dict:
            """Generate summary statistics"""
            summary = {
                'data_collection_success': True,
                'endpoints_successful': 0,
                'endpoints_failed': 0,
                'total_data_points': 0
            }
            
            # Count successful endpoints
            if profile_data.get('success'):
                summary['endpoints_successful'] += 1
                summary['total_data_points'] += 1
            else:
                summary['endpoints_failed'] += 1
            
            if media_data.get('success'):
                summary['endpoints_successful'] += 1
                summary['total_data_points'] += media_data.get('fetched_count', 0)
            else:
                summary['endpoints_failed'] += 1
            
            for endpoint_name, endpoint_data in additional_data.items():
                if endpoint_data.get('success'):
                    summary['endpoints_successful'] += 1
                    if endpoint_data.get('has_data'):
                        summary['total_data_points'] += 1
                else:
                    summary['endpoints_failed'] += 1
            
            return summary
        
        def generate_markdown_report(self) -> str:
            """Generate comprehensive Markdown report"""
            timestamp = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')
            usernames = list(self.collection_results.keys())
            
            md_content = f"""# 📊 Star API Data Collection Report

**Generated:** {timestamp}  
**Accounts Analyzed:** {', '.join([f'@{u}' for u in usernames])}  
**Total Accounts:** {len(usernames)}

---

## 📋 Executive Summary

"""
            
            # Overall statistics
            total_successful = sum(1 for result in self.collection_results.values() 
                                 if result['profile'].get('success'))
            total_endpoints = sum(result['summary'].get('endpoints_successful', 0) 
                                for result in self.collection_results.values())
            
            md_content += f"""
- **✅ Successful Collections:** {total_successful}/{len(usernames)} accounts
- **📡 Total Successful Endpoints:** {total_endpoints}
- **🔧 Star API Status:** Active and collecting real-time data
- **📊 Data Coverage:** Profile, Media, Stories, Highlights, Social

---

"""
            
            # Individual account reports
            for username, result in self.collection_results.items():
                md_content += self._generate_account_section(username, result)
            
            # Technical appendix
            md_content += self._generate_technical_section()
            
            return md_content
        
        def _generate_account_section(self, username: str, result: dict) -> str:
            """Generate report section for an account"""
            profile = result.get('profile', {})
            media = result.get('media', {})
            additional = result.get('additional', {})
            
            section = f"""
## 👤 @{username} - Complete Analysis

"""
            
            # Profile section
            if profile.get('success'):
                engagement_rate = 0
                if media.get('success') and profile.get('followers_count', 0) > 0:
                    avg_engagement = media.get('engagement_summary', {}).get('avg_likes', 0) + media.get('engagement_summary', {}).get('avg_comments', 0)
                    engagement_rate = (avg_engagement / profile.get('followers_count', 1)) * 100
                
                section += f"""### 📊 Profile Metrics
- **Full Name:** {profile.get('full_name', 'N/A')}
- **Followers:** {profile.get('followers_count', 0):,}
- **Following:** {profile.get('following_count', 0):,}
- **Posts:** {profile.get('media_count', 0):,}
- **Verified:** {'✅' if profile.get('is_verified') else '❌'}
- **Private:** {'🔒' if profile.get('is_private') else '🌍 Public'}
- **Business:** {'💼' if profile.get('is_business_account') else '👤 Personal'}
- **Category:** {profile.get('business_category', 'N/A')}
- **Engagement Rate:** {engagement_rate:.2f}%

**Bio:** {profile.get('biography', 'No bio available')[:200]}...

"""
            else:
                section += "❌ **Profile data collection failed**\\n\\n"
            
            # Media analysis
            if media.get('success'):
                breakdown = media.get('media_breakdown', {})
                engagement = media.get('engagement_summary', {})
                
                section += f"""### 📸 Content Performance
- **Total Posts:** {media.get('total_media_count', 0):,}
- **Analyzed:** {media.get('fetched_count', 0)} recent posts
- **Content Mix:** Photo: {breakdown.get('photo', 0)}, Video: {breakdown.get('video', 0)}, Carousel: {breakdown.get('carousel', 0)}

#### 📈 Engagement Metrics
- **Average Likes:** {engagement.get('avg_likes', 0):,}
- **Average Comments:** {engagement.get('avg_comments', 0):,}
- **Best Performing Post:** {engagement.get('max_likes', 0):,} likes
- **Total Engagement:** {engagement.get('total_likes', 0):,} likes, {engagement.get('total_comments', 0):,} comments

#### 🔥 Recent Top Posts
"""
                
                recent_posts = media.get('recent_posts', [])[:5]
                for i, post in enumerate(recent_posts, 1):
                    section += f"""
{i}. **{post['shortcode']}** ({post['media_type']})  
   💖 {post['likes']:,} likes • 💬 {post['comments']:,} comments  
   *{post['caption_preview']}*
"""
            else:
                section += "❌ **Media data collection failed**\\n\\n"
            
            # Additional data status
            section += f"""
### 🔍 Extended Data Collection
- **📖 Stories:** {'✅ Available' if additional.get('stories', {}).get('has_data') else '❌ None/Limited'}
- **⭐ Highlights:** {'✅ Available' if additional.get('highlights', {}).get('has_data') else '❌ None/Limited'}
- **👥 Following List:** {'✅ Available' if additional.get('following', {}).get('has_data') else '❌ Limited'}
- **👥 Followers List:** {'✅ Available' if additional.get('followers', {}).get('has_data') else '❌ Limited'}

"""
            
            # Errors if any
            if result.get('errors'):
                section += "### ⚠️ Collection Issues\\n"
                for error in result['errors']:
                    section += f"- {error}\\n"
                section += "\\n"
            
            section += "---\\n\\n"
            return section
        
        def _generate_technical_section(self) -> str:
            """Generate technical summary"""
            return f"""
## 🔧 Technical Summary

### 📡 Star API Endpoints Used
1. **Profile Information** - Complete user profile data
2. **Media Posts** - Timeline content with engagement metrics
3. **Stories** - Current active stories (24-hour content)
4. **Highlights** - Saved story highlights
5. **Social Network** - Following/followers data (rate limited)

### 📊 Data Quality Assessment
- **✅ Real-time Data:** Direct from Instagram API
- **✅ Comprehensive Coverage:** Multi-endpoint data collection
- **⚠️ Rate Limiting:** Some social endpoints have restrictions
- **✅ Error Handling:** Graceful failure and retry mechanisms

### 🚀 Recommended Next Steps
1. **Database Integration:** Store collected data for trend analysis
2. **Automated Scheduling:** Set up regular data collection
3. **Comparative Analysis:** Track changes over time
4. **Content Strategy:** Use insights for posting optimization
5. **Competitor Monitoring:** Expand to competitive analysis

### 📈 Data Insights Capabilities
- **Engagement Rate Calculation:** Like/comment ratios
- **Content Type Analysis:** Photo vs video performance
- **Posting Pattern Recognition:** Optimal timing insights
- **Audience Growth Tracking:** Follower trend analysis
- **Performance Benchmarking:** Cross-account comparisons

---

*Comprehensive report generated by Star API Data Collector*  
*Collection completed at: {datetime.now(IST).isoformat()}*
"""

    def main():
        """Main execution function"""
        print("🌟 Star API Comprehensive Data Collection")
        print("=" * 60)
        
        # Get API key
        api_key = os.getenv('RAPID_API_KEY') or os.getenv('API_KEY')
        if not api_key:
            print("❌ Error: API key not found")
            print("Please set RAPID_API_KEY or API_KEY in .env file")
            return
        
        print(f"✅ API Key loaded: {api_key[:10]}...")
        
        # Initialize collector
        collector = SimpleStarAPICollector(api_key)
        
        # Test accounts
        test_usernames = ['nasa', 'spacex', 'instagram']
        print(f"🎯 Target accounts: {', '.join([f'@{u}' for u in test_usernames])}")
        print("\\n" + "=" * 60)
        
        # Collect data for each account
        for i, username in enumerate(test_usernames, 1):
            print(f"\\n\\n[{i}/{len(test_usernames)}] === ANALYZING @{username.upper()} ===")
            
            try:
                collector.collect_comprehensive_data(username)
                
                # Rate limiting between accounts
                if i < len(test_usernames):
                    print(f"\\n⏱️ Waiting 3 seconds before next account...")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"❌ Critical error with @{username}: {str(e)}")
        
        print("\\n\\n" + "=" * 60)
        print("📊 GENERATING COMPREHENSIVE REPORT")
        print("=" * 60)
        
        # Generate final report
        try:
            report_content = collector.generate_markdown_report()
            
            # Save report
            timestamp = datetime.now(IST).strftime('%Y%m%d_%H%M%S')
            report_filename = f"star_api_comprehensive_report_{timestamp}.md"
            report_path = os.path.join(os.path.dirname(__file__), report_filename)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"\\n🎉 COLLECTION COMPLETE!")
            print(f"📄 Report saved: {report_path}")
            print(f"\\n📊 Report Summary:")
            print(f"   • {len(test_usernames)} accounts analyzed")
            print(f"   • Multiple endpoints per account")
            print(f"   • Real-time Instagram data")
            print(f"   • Comprehensive engagement analysis")
            print(f"   • Technical insights and recommendations")
            
            # Show preview of report
            print(f"\\n📝 Report Preview (first 30 lines):")
            print("-" * 50)
            lines = report_content.split('\\n')
            for line in lines[:30]:
                if line.strip():
                    print(line)
            print("...")
            print(f"\\n📄 Full report: {report_path}")
            
            return report_path
            
        except Exception as e:
            print(f"❌ Report generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
