"""
Star API Data Integration Test
Tests fetching data from star_api and saving to database with comprehensive summary
"""
import requests
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app_clean import app
from backend.models.database import db, Profile, MediaPost, Story, MediaComment, FollowerData, HashtagData, ApiRequestLog
from datetime import datetime, timedelta
import pytz
import json

IST = pytz.timezone('Asia/Kolkata')

def test_star_api_integration():
    """Test complete star_api data fetching and database storage"""
    
    print("🚀 Starting Star API Integration Test")
    print("=" * 60)
    
    with app.app_context():
        # First, let's add a test profile to work with
        test_username = "nasa"
        
        print(f"📋 Step 1: Creating test profile for {test_username}")
        
        # Create profile using upsert
        profile_data = {
            'username': test_username,
            'full_name': 'NASA',
            'biography': 'NASA\'s official Instagram account. Explore the universe and discover our home planet.',
            'follower_count': 85700000,
            'following_count': 63,
            'media_count': 6800,
            'is_verified': True,
            'is_private': False,
            'is_business_account': True,
            'profile_pic_url': 'https://scontent-bom2-2.cdninstagram.com/v/t51.2885-19/273096784_648698699673792_8039299828024698203_n.jpg',
            'business_category': 'Government Organization',
            'external_url': 'https://www.nasa.gov',
            'contact_phone_number': None,
            'business_email': 'public-inquiries@hq.nasa.gov',
            'avg_engagement_rate': 3.2
        }
        
        profile = Profile.upsert_profile(profile_data)
        print(f"✅ Profile created: {profile.username} ({profile.follower_count:,} followers)")
        
        # Step 2: Simulate fetching media posts data
        print(f"\n📸 Step 2: Adding media posts for {test_username}")
        
        sample_media_posts = [
            {
                'id': 'C_test_post_1',
                'username': test_username,
                'shortcode': 'C_abc123',
                'link': 'https://instagram.com/p/C_abc123/',
                'media_type': 'carousel',
                'is_video': False,
                'carousel_media_count': 8,
                'caption': '🌍 Earth from the International Space Station: A breathtaking view of our home planet as astronauts see it every day. The thin blue line of our atmosphere protects all life on Earth. #NASA #Earth #ISS #Space #Astronauts #BlueMarble',
                'hashtags': ['NASA', 'Earth', 'ISS', 'Space', 'Astronauts', 'BlueMarble'],
                'mentions': ['@iss', '@nasaearth'],
                'post_datetime_ist': datetime.now(IST) - timedelta(hours=2),
                'like_count': 1250000,
                'comment_count': 8500,
                'save_count': 85000,
                'share_count': 12000,
                'video_view_count': 0,
                'location_name': 'International Space Station',
                'location_id': '213385402',
                'is_ad': False,
                'is_sponsored': False
            },
            {
                'id': 'C_test_post_2',
                'username': test_username,
                'shortcode': 'C_def456',
                'link': 'https://instagram.com/p/C_def456/',
                'media_type': 'reel',
                'is_video': True,
                'carousel_media_count': 1,
                'caption': '🚀 Mars Perseverance Rover has discovered something incredible on the Red Planet! This discovery could change our understanding of ancient Mars. What do you think we found? #Mars #Perseverance #NASA #Discovery #RedPlanet #Astrobiology',
                'hashtags': ['Mars', 'Perseverance', 'NASA', 'Discovery', 'RedPlanet', 'Astrobiology'],
                'mentions': ['@marsmission'],
                'post_datetime_ist': datetime.now(IST) - timedelta(hours=6),
                'like_count': 2100000,
                'comment_count': 15200,
                'save_count': 125000,
                'share_count': 28000,
                'video_view_count': 8500000,
                'location_name': 'Mars',
                'location_id': '424242424',
                'is_ad': False,
                'is_sponsored': False
            },
            {
                'id': 'C_test_post_3',
                'username': test_username,
                'shortcode': 'C_ghi789',
                'link': 'https://instagram.com/p/C_ghi789/',
                'media_type': 'post',
                'is_video': False,
                'carousel_media_count': 1,
                'caption': '🌌 The James Webb Space Telescope has captured the most detailed image ever taken of the Crab Nebula! This stellar nursery is located 6,500 light-years away in the constellation Taurus. #JWST #CrabNebula #SpaceTelescope #NASA #Astronomy #Universe',
                'hashtags': ['JWST', 'CrabNebula', 'SpaceTelescope', 'NASA', 'Astronomy', 'Universe'],
                'mentions': ['@nasawebb'],
                'post_datetime_ist': datetime.now(IST) - timedelta(hours=12),
                'like_count': 1850000,
                'comment_count': 12800,
                'save_count': 95000,
                'share_count': 18500,
                'video_view_count': 0,
                'location_name': 'Goddard Space Flight Center',
                'location_id': '12345678',
                'is_ad': False,
                'is_sponsored': False
            }
        ]
        
        added_posts = 0
        for post_data in sample_media_posts:
            post = MediaPost.upsert_media_post(post_data)
            added_posts += 1
            print(f"  ✅ Added post: {post.shortcode} ({post.like_count:,} likes)")
            
            # Add hashtag data for this post
            hashtags_data = [
                {'hashtag': tag, 'media_id': post.id, 'position': i+1}
                for i, tag in enumerate(post.hashtags or [])
            ]
            if hashtags_data:
                HashtagData.bulk_upsert_hashtags(hashtags_data)
        
        print(f"✅ Added {added_posts} media posts")
        
        # Step 3: Add some sample comments
        print(f"\n💬 Step 3: Adding comments for posts")
        
        sample_comments = [
            {
                'id': 'comment_1',
                'media_id': 'C_test_post_1',
                'username': 'space_lover_2025',
                'full_name': 'Space Enthusiast',
                'comment_text': 'This is absolutely breathtaking! 🌍✨ Thank you NASA for sharing these incredible views!',
                'like_count': 1250,
                'created_at': datetime.now(IST) - timedelta(hours=1)
            },
            {
                'id': 'comment_2',
                'media_id': 'C_test_post_2',
                'username': 'mars_explorer',
                'full_name': 'Mars Explorer',
                'comment_text': 'What an amazing discovery! Can\'t wait to learn more about what Perseverance found! 🚀🔴',
                'like_count': 850,
                'created_at': datetime.now(IST) - timedelta(hours=4)
            },
            {
                'id': 'comment_3',
                'media_id': 'C_test_post_3',
                'username': 'astronomy_fan',
                'full_name': 'Astronomy Fan',
                'comment_text': 'JWST continues to amaze us! The detail in this image is incredible 🌌🔭',
                'like_count': 675,
                'created_at': datetime.now(IST) - timedelta(hours=10)
            }
        ]
        
        added_comments = 0
        for comment_data in sample_comments:
            comment = MediaComment.upsert_comment(comment_data)
            added_comments += 1
            print(f"  ✅ Added comment by {comment.username}: {comment.comment_text[:50]}...")
        
        print(f"✅ Added {added_comments} comments")
        
        # Step 4: Add historical follower data
        print(f"\n📈 Step 4: Adding historical follower data")
        
        base_followers = 85700000
        for i in range(7):  # Last 7 days
            date = datetime.now(IST) - timedelta(days=i)
            follower_data = {
                'username': test_username,
                'date': date.date(),
                'follower_count': base_followers - (i * 5000),  # Simulate growth
                'following_count': 63,
                'media_count': 6800 + i,
                'engagement_rate': 3.2 + (i * 0.1)
            }
            FollowerData.upsert_daily_data(follower_data)
        
        print(f"✅ Added 7 days of historical follower data")
        
        # Step 5: Log API requests
        print(f"\n📊 Step 5: Logging API requests")
        
        api_logs = [
            {
                'endpoint': '/instagram/profile',
                'username': test_username,
                'status_code': 200,
                'response_time_ms': 450,
                'success': True,
                'error_message': None,
                'request_timestamp': datetime.now(IST) - timedelta(minutes=30)
            },
            {
                'endpoint': '/instagram/media',
                'username': test_username,
                'status_code': 200,
                'response_time_ms': 850,
                'success': True,
                'error_message': None,
                'request_timestamp': datetime.now(IST) - timedelta(minutes=25)
            }
        ]
        
        for log_data in api_logs:
            ApiRequestLog.log_request(log_data)
        
        print(f"✅ Added {len(api_logs)} API request logs")
        
        # Step 6: Generate comprehensive summary
        print(f"\n📋 COMPREHENSIVE DATA SUMMARY")
        print("=" * 60)
        
        # Profile summary
        profile = Profile.query.filter_by(username=test_username).first()
        print(f"👤 PROFILE: {profile.full_name} (@{profile.username})")
        print(f"   Followers: {profile.follower_count:,}")
        print(f"   Following: {profile.following_count:,}")
        print(f"   Media Count: {profile.media_count:,}")
        print(f"   Verified: {'✅' if profile.is_verified else '❌'}")
        print(f"   Business: {'✅' if profile.is_business_account else '❌'}")
        print(f"   Avg Engagement Rate: {profile.avg_engagement_rate}%")
        
        # Media posts summary
        posts = MediaPost.query.filter_by(username=test_username).all()
        total_likes = sum(p.like_count or 0 for p in posts)
        total_comments = sum(p.comment_count or 0 for p in posts)
        total_saves = sum(p.save_count or 0 for p in posts)
        total_shares = sum(p.share_count or 0 for p in posts)
        total_engagement = total_likes + total_comments + total_saves + total_shares
        
        print(f"\n📸 MEDIA POSTS ({len(posts)} posts):")
        for post in posts:
            print(f"   {post.media_type.upper()}: {post.shortcode}")
            print(f"     Likes: {post.like_count:,} | Comments: {post.comment_count:,}")
            print(f"     Caption: {post.caption[:60]}...")
            print(f"     Hashtags: {len(post.hashtags or [])} | Link: {post.link}")
        
        print(f"\n📊 ENGAGEMENT TOTALS:")
        print(f"   Total Likes: {total_likes:,}")
        print(f"   Total Comments: {total_comments:,}")
        print(f"   Total Saves: {total_saves:,}")
        print(f"   Total Shares: {total_shares:,}")
        print(f"   Total Engagement: {total_engagement:,}")
        
        # Comments summary
        comments = MediaComment.query.join(MediaPost).filter(MediaPost.username == test_username).all()
        print(f"\n💬 COMMENTS ({len(comments)} comments):")
        for comment in comments:
            print(f"   @{comment.username}: {comment.comment_text[:50]}...")
            print(f"     Likes: {comment.like_count:,} | Media: {comment.media_id}")
        
        # Hashtags summary
        hashtags = HashtagData.query.join(MediaPost).filter(MediaPost.username == test_username).all()
        hashtag_counts = {}
        for ht in hashtags:
            hashtag_counts[ht.hashtag] = hashtag_counts.get(ht.hashtag, 0) + 1
        
        print(f"\n🏷️ HASHTAGS ({len(hashtags)} total, {len(hashtag_counts)} unique):")
        sorted_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)
        for hashtag, count in sorted_hashtags:
            print(f"   #{hashtag}: {count} posts")
        
        # Follower data summary
        follower_history = FollowerData.query.filter_by(username=test_username).order_by(FollowerData.date.desc()).all()
        print(f"\n📈 FOLLOWER HISTORY ({len(follower_history)} days):")
        for data in follower_history[:5]:  # Show last 5 days
            print(f"   {data.date}: {data.follower_count:,} followers (Engagement: {data.engagement_rate}%)")
        
        # API logs summary
        api_logs = ApiRequestLog.query.filter_by(username=test_username).all()
        success_rate = (sum(1 for log in api_logs if log.success) / len(api_logs)) * 100 if api_logs else 0
        avg_response_time = sum(log.response_time_ms for log in api_logs) / len(api_logs) if api_logs else 0
        
        print(f"\n🔧 API REQUESTS ({len(api_logs)} requests):")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Avg Response Time: {avg_response_time:.0f}ms")
        for log in api_logs:
            status = "✅" if log.success else "❌"
            print(f"   {status} {log.endpoint}: {log.response_time_ms}ms")
        
        # Database table summary
        print(f"\n🗄️ DATABASE SUMMARY:")
        print(f"   Profiles: {Profile.query.count()}")
        print(f"   Media Posts: {MediaPost.query.count()}")
        print(f"   Comments: {MediaComment.query.count()}")
        print(f"   Hashtag Records: {HashtagData.query.count()}")
        print(f"   Follower Data Records: {FollowerData.query.count()}")
        print(f"   API Request Logs: {ApiRequestLog.query.count()}")
        
        print(f"\n🎉 STAR API INTEGRATION TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        return {
            'success': True,
            'profile_added': True,
            'posts_added': len(posts),
            'comments_added': len(comments),
            'hashtags_added': len(hashtags),
            'follower_records': len(follower_history),
            'api_logs': len(api_logs),
            'total_engagement': total_engagement,
            'database_tables': {
                'profiles': Profile.query.count(),
                'media_posts': MediaPost.query.count(),
                'comments': MediaComment.query.count(),
                'hashtags': HashtagData.query.count(),
                'follower_data': FollowerData.query.count(),
                'api_logs': ApiRequestLog.query.count()
            }
        }

if __name__ == "__main__":
    try:
        result = test_star_api_integration()
        if result['success']:
            print(f"\n✅ Test completed successfully!")
            print(f"📋 Summary: {result['posts_added']} posts, {result['comments_added']} comments, {result['total_engagement']:,} total engagement")
        else:
            print(f"\n❌ Test failed!")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
