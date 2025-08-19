"""
Simple Star API Data Test
"""
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Now we can import
try:
    from app_clean import app
    from models.database import db, Profile, MediaPost, MediaComment, FollowerData, HashtagData, ApiRequestLog
    from datetime import datetime, timedelta
    import pytz
    
    IST = pytz.timezone('Asia/Kolkata')
    
    def run_test():
        print("🚀 Testing Star API Data Integration")
        print("=" * 50)
        
        with app.app_context():
            # Test 1: Add a profile
            print("📋 Test 1: Adding NASA profile...")
            profile_data = {
                'username': 'nasa',
                'full_name': 'NASA',
                'biography': 'Explore the universe and discover our home planet.',
                'follower_count': 85700000,
                'following_count': 63,
                'is_verified': True,
                'is_business_account': True,
                'avg_engagement_rate': 3.2
            }
            
            profile = Profile.upsert_profile(profile_data)
            print(f"✅ Profile: {profile.username} ({profile.follower_count:,} followers)")
            
            # Test 2: Add media posts
            print("\n📸 Test 2: Adding media posts...")
            post_data = {
                'id': 'test_post_1',
                'username': 'nasa',
                'shortcode': 'ABC123',
                'link': 'https://instagram.com/p/ABC123/',
                'media_type': 'post',
                'caption': '🌍 Amazing Earth view from ISS! #NASA #Earth #Space',
                'hashtags': ['NASA', 'Earth', 'Space'],
                'like_count': 1500000,
                'comment_count': 8500,
                'save_count': 85000,
                'post_datetime_ist': datetime.now(IST)
            }
            
            post = MediaPost.upsert_media_post(post_data)
            print(f"✅ Post: {post.shortcode} ({post.like_count:,} likes)")
            
            # Test 3: Add hashtags
            print("\n🏷️ Test 3: Adding hashtags...")
            hashtag_data = [
                {'hashtag': 'NASA', 'media_id': 'test_post_1', 'position': 1},
                {'hashtag': 'Earth', 'media_id': 'test_post_1', 'position': 2},
                {'hashtag': 'Space', 'media_id': 'test_post_1', 'position': 3}
            ]
            HashtagData.bulk_upsert_hashtags(hashtag_data)
            print(f"✅ Added {len(hashtag_data)} hashtags")
            
            # Test 4: Add comment
            print("\n💬 Test 4: Adding comment...")
            comment_data = {
                'id': 'comment_1',
                'media_id': 'test_post_1',
                'username': 'space_fan',
                'full_name': 'Space Fan',
                'comment_text': 'Absolutely stunning! 🌍✨',
                'like_count': 250,
                'created_at': datetime.now(IST)
            }
            comment = MediaComment.upsert_comment(comment_data)
            print(f"✅ Comment: @{comment.username} - {comment.comment_text}")
            
            # Test 5: Add follower data
            print("\n📈 Test 5: Adding follower data...")
            follower_data = {
                'username': 'nasa',
                'date': datetime.now(IST).date(),
                'follower_count': 85700000,
                'following_count': 63,
                'media_count': 6801,
                'engagement_rate': 3.2
            }
            FollowerData.upsert_daily_data(follower_data)
            print(f"✅ Follower data for {follower_data['date']}")
            
            # Test 6: Log API request
            print("\n🔧 Test 6: Logging API request...")
            api_data = {
                'endpoint': '/instagram/profile',
                'username': 'nasa',
                'status_code': 200,
                'response_time_ms': 350,
                'success': True,
                'request_timestamp': datetime.now(IST)
            }
            ApiRequestLog.log_request(api_data)
            print(f"✅ API log: {api_data['endpoint']} ({api_data['response_time_ms']}ms)")
            
            # Summary
            print(f"\n📊 DATABASE SUMMARY:")
            print(f"   Profiles: {Profile.query.count()}")
            print(f"   Media Posts: {MediaPost.query.count()}")
            print(f"   Comments: {MediaComment.query.count()}")
            print(f"   Hashtags: {HashtagData.query.count()}")
            print(f"   Follower Data: {FollowerData.query.count()}")
            print(f"   API Logs: {ApiRequestLog.query.count()}")
            
            print(f"\n🎉 ALL TESTS PASSED!")
            return True
            
    if __name__ == "__main__":
        run_test()
        
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Test error: {e}")
    import traceback
    traceback.print_exc()
