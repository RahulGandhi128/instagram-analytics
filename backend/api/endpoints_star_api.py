"""
Star API Endpoints - Instagram data collection using Star API
"""
from flask import Blueprint, request, jsonify
from services.star_api_service import create_star_api_service
from services.star_api_data_service import create_star_api_data_service
from models.database import db, Profile, MediaPost, Story, Highlight, FollowerData, MediaComment, HashtagData
import os

star_api_bp = Blueprint('star_api', __name__)

@star_api_bp.route('/star-api/collect-user-data/<username>', methods=['POST'])
def collect_user_data(username):
    """
    Alias for collect_comprehensive_data - collects comprehensive data for a user
    """
    return collect_comprehensive_data(username)

@star_api_bp.route('/star-api/collection-status/<username>', methods=['GET'])
def get_collection_status(username):
    """
    Get data collection status for a user
    """
    try:
        # Check if profile exists and when it was last updated
        profile = Profile.query.filter_by(username=username).first()
        
        if not profile:
            return jsonify({
                'success': True,
                'data': {
                    'status': 'not_collected',
                    'last_updated': None,
                    'profile_exists': False
                }
            })
        
        # Count collected data
        media_count = MediaPost.query.filter_by(username=username).count()
        stories_count = Story.query.filter_by(username=username).count()
        highlights_count = Highlight.query.filter_by(username=username).count()
        
        return jsonify({
            'success': True,
            'data': {
                'status': 'collected' if media_count > 0 else 'profile_only',
                'last_updated': profile.last_updated.isoformat() if profile.last_updated else None,
                'profile_exists': True,
                'data_counts': {
                    'media_posts': media_count,
                    'stories': stories_count,
                    'highlights': highlights_count
                },
                'profile_info': {
                    'follower_count': profile.follower_count,
                    'following_count': profile.following_count,
                    'media_count': profile.media_count,
                    'is_verified': profile.is_verified,
                    'is_private': profile.is_private
                }
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@star_api_bp.route('/star-api/collect-comprehensive/<username>', methods=['POST'])
def collect_comprehensive_data(username):
    """
    Collect comprehensive data for a user using Star API Data Service
    Follows the documented UPSERT strategy from DATABASE_SERVICE_DOCUMENTATION.md
    """
    try:
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key not configured'
            }), 500

        # Create comprehensive data service
        data_service = create_star_api_data_service(api_key)
        
        # Collect all comprehensive data with UPSERT strategy
        result = data_service.collect_comprehensive_data(username)
        
        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@star_api_bp.route('/star-api/test-endpoints', methods=['POST'])
def test_star_api_endpoints():
    """
    Test Star API endpoints
    """
    try:
        data = request.get_json()
        username = data.get('username', 'nasa')
        
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key not configured'
            }), 500

        star_service = create_star_api_service(api_key)
        
        # Test multiple endpoints
        results = {}
        
        # Test user info
        try:
            user_info = star_service.get_user_info_by_username(username)
            results['user_info'] = {'success': True, 'data': user_info}
        except Exception as e:
            results['user_info'] = {'success': False, 'error': str(e)}
        
        return jsonify({
            'success': True,
            'data': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@star_api_bp.route('/star-api/user-info/<username>', methods=['GET'])
def get_star_user_info(username):
    """
    Get user info using Star API
    """
    try:
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key not configured'
            }), 500

        star_service = create_star_api_service(api_key)
        user_info = star_service.get_user_info_by_username(username)
        
        if user_info:
            return jsonify({
                'success': True,
                'data': user_info
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch user info'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@star_api_bp.route('/star-api/user-media/<username>', methods=['GET'])
def get_star_user_media(username):
    """
    Get user media using Star API
    """
    try:
        count = request.args.get('count', 50, type=int)
        
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key not configured'
            }), 500
        
        star_service = create_star_api_service(api_key)
        
        # First get user info to extract user_id
        user_info = star_service.get_user_info_by_username(username)
        if not user_info:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Extract user_id with improved logic for different response structures
        try:
            print(f"DEBUG MEDIA: user_info structure = {list(user_info.keys())}")
            
            # Try different extraction paths based on the actual structure
            user_id = None
            
            # Path 1: data.response.body.data.user.id (expected from service)
            if 'data' in user_info and 'response' in user_info['data']:
                try:
                    user_id = user_info['data']['response']['body']['data']['user']['id']
                    print(f"DEBUG MEDIA: Extracted user_id via data.response path = {user_id}")
                except (KeyError, TypeError):
                    pass
            
            # Path 2: status.response.body.data.user.id (actual from API routes)
            if user_id is None and 'status' in user_info and 'response' in user_info:
                try:
                    user_id = user_info['response']['body']['data']['user']['id']
                    print(f"DEBUG MEDIA: Extracted user_id via status.response path = {user_id}")
                except (KeyError, TypeError):
                    pass
            
            # Path 3: direct response.body.data.user.id
            if user_id is None and 'response' in user_info:
                try:
                    user_id = user_info['response']['body']['data']['user']['id']
                    print(f"DEBUG MEDIA: Extracted user_id via direct response path = {user_id}")
                except (KeyError, TypeError):
                    pass
            
            if user_id is None:
                raise KeyError("Could not find user_id in any expected path")
                
            print(f"DEBUG MEDIA: Successfully extracted user_id = {user_id}")
            
        except (KeyError, TypeError) as e:
            print(f"DEBUG MEDIA: Failed to extract user_id: {e}")
            print(f"DEBUG MEDIA: Full response structure: {user_info}")
            return jsonify({
                'success': False,
                'error': f'Could not extract user ID: {e}',
                'debug_structure': list(user_info.keys()) if isinstance(user_info, dict) else str(type(user_info))
            }), 500
        
        # Get media using user_id
        media_data = star_service.get_user_media(user_id, count)
        
        if media_data:
            return jsonify({
                'success': True,
                'data': media_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch media data'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@star_api_bp.route('/star-api/user-stories/<username>', methods=['GET'])
def get_star_user_stories(username):
    """
    Get user stories using Star API
    """
    try:
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key not configured'
            }), 500
        
        star_service = create_star_api_service(api_key)
        
        # First get user info to extract user_id
        user_info = star_service.get_user_info_by_username(username)
        if not user_info:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Extract user_id with improved logic for different response structures
        try:
            print(f"DEBUG STORIES: user_info structure = {list(user_info.keys())}")
            
            # Try different extraction paths based on the actual structure
            user_id = None
            
            # Path 1: data.response.body.data.user.id (expected from service)
            if 'data' in user_info and 'response' in user_info['data']:
                try:
                    user_id = user_info['data']['response']['body']['data']['user']['id']
                    print(f"DEBUG STORIES: Extracted user_id via data.response path = {user_id}")
                except (KeyError, TypeError):
                    pass
            
            # Path 2: status.response.body.data.user.id (actual from API routes)
            if user_id is None and 'status' in user_info and 'response' in user_info:
                try:
                    user_id = user_info['response']['body']['data']['user']['id']
                    print(f"DEBUG STORIES: Extracted user_id via status.response path = {user_id}")
                except (KeyError, TypeError):
                    pass
            
            # Path 3: direct response.body.data.user.id
            if user_id is None and 'response' in user_info:
                try:
                    user_id = user_info['response']['body']['data']['user']['id']
                    print(f"DEBUG STORIES: Extracted user_id via direct response path = {user_id}")
                except (KeyError, TypeError):
                    pass
            
            if user_id is None:
                raise KeyError("Could not find user_id in any expected path")
                
            print(f"DEBUG STORIES: Successfully extracted user_id = {user_id}")
            
        except (KeyError, TypeError) as e:
            print(f"DEBUG STORIES: Failed to extract user_id: {e}")
            print(f"DEBUG STORIES: Full response structure: {user_info}")
            return jsonify({
                'success': False,
                'error': f'Could not extract user ID: {e}',
                'debug_structure': list(user_info.keys()) if isinstance(user_info, dict) else str(type(user_info))
            }), 500
        
        # Get stories using user_id
        stories_data = star_service.get_user_stories(user_id)
        
        if stories_data:
            return jsonify({
                'success': True,
                'data': stories_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch stories data'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@star_api_bp.route('/star-api/database-status', methods=['GET'])
def get_database_status():
    """
    Get database status for Star API data
    """
    try:
        # Count records in each table
        profile_count = Profile.query.count()
        media_count = MediaPost.query.count()
        story_count = Story.query.count()
        highlight_count = Highlight.query.count()
        follower_count = FollowerData.query.count()
        comment_count = MediaComment.query.count()
        hashtag_count = HashtagData.query.count()
        
        status = {
            'database_tables': {
                'profiles': profile_count,
                'media_posts': media_count,
                'stories': story_count,
                'highlights': highlight_count,
                'follower_data': follower_count,
                'media_comments': comment_count,
                'hashtag_data': hashtag_count
            },
            'total_records': (
                profile_count + media_count + story_count + 
                highlight_count + follower_count + comment_count + hashtag_count
            )
        }
        
        return jsonify({
            'success': True,
            'data': status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@star_api_bp.route('/star-api/user-followers/<username>', methods=['GET'])
def get_star_user_followers(username):
    """
    Get user followers using Star API
    """
    try:
        count = request.args.get('count', 50, type=int)
        
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key not configured'
            }), 500
        
        star_service = create_star_api_service(api_key)
        
        # First get user info to extract user_id
        user_info = star_service.get_user_info_by_username(username)
        if not user_info:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Extract user_id (using the same logic as other endpoints)
        try:
            user_id = None
            if 'status' in user_info and 'response' in user_info:
                user_id = user_info['response']['body']['data']['user']['id']
            elif 'data' in user_info and 'response' in user_info['data']:
                user_id = user_info['data']['response']['body']['data']['user']['id']
            elif 'response' in user_info:
                user_id = user_info['response']['body']['data']['user']['id']
            else:
                raise KeyError("Unknown response structure")
                
            print(f"DEBUG FOLLOWERS: Successfully extracted user_id = {user_id}")
        except (KeyError, TypeError) as e:
            print(f"DEBUG FOLLOWERS: Failed to extract user_id: {e}")
            return jsonify({
                'success': False,
                'error': f'Could not extract user ID: {e}'
            }), 500
        
        # Get followers using user_id
        followers_data = star_service.get_user_followers(user_id, count)
        
        if followers_data:
            return jsonify({
                'success': True,
                'data': followers_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch followers data'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@star_api_bp.route('/star-api/user-following/<username>', methods=['GET'])
def get_star_user_following(username):
    """
    Get user following using Star API
    """
    try:
        count = request.args.get('count', 50, type=int)
        
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key not configured'
            }), 500
        
        star_service = create_star_api_service(api_key)
        
        # First get user info to extract user_id
        user_info = star_service.get_user_info_by_username(username)
        if not user_info:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Extract user_id (using the same logic as other endpoints)
        try:
            user_id = None
            if 'status' in user_info and 'response' in user_info:
                user_id = user_info['response']['body']['data']['user']['id']
            elif 'data' in user_info and 'response' in user_info['data']:
                user_id = user_info['data']['response']['body']['data']['user']['id']
            elif 'response' in user_info:
                user_id = user_info['response']['body']['data']['user']['id']
            else:
                raise KeyError("Unknown response structure")
                
            print(f"DEBUG FOLLOWING: Successfully extracted user_id = {user_id}")
        except (KeyError, TypeError) as e:
            print(f"DEBUG FOLLOWING: Failed to extract user_id: {e}")
            return jsonify({
                'success': False,
                'error': f'Could not extract user ID: {e}'
            }), 500
        
        # Get following using user_id
        following_data = star_service.get_user_following(user_id, count)
        
        if following_data:
            return jsonify({
                'success': True,
                'data': following_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch following data'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@star_api_bp.route('/star-api/user-highlights/<username>', methods=['GET'])
def get_star_user_highlights(username):
    """
    Get user highlights using Star API
    """
    try:
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key not configured'
            }), 500
        
        star_service = create_star_api_service(api_key)
        
        # First get user info to extract user_id
        user_info = star_service.get_user_info_by_username(username)
        if not user_info:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Extract user_id (using the same logic as other endpoints)
        try:
            user_id = None
            if 'status' in user_info and 'response' in user_info:
                user_id = user_info['response']['body']['data']['user']['id']
            elif 'data' in user_info and 'response' in user_info['data']:
                user_id = user_info['data']['response']['body']['data']['user']['id']
            elif 'response' in user_info:
                user_id = user_info['response']['body']['data']['user']['id']
            else:
                raise KeyError("Unknown response structure")
                
            print(f"DEBUG HIGHLIGHTS: Successfully extracted user_id = {user_id}")
        except (KeyError, TypeError) as e:
            print(f"DEBUG HIGHLIGHTS: Failed to extract user_id: {e}")
            return jsonify({
                'success': False,
                'error': f'Could not extract user ID: {e}'
            }), 500
        
        # Get highlights using user_id
        highlights_data = star_service.get_user_highlights(user_id)
        
        if highlights_data:
            return jsonify({
                'success': True,
                'data': highlights_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch highlights data'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@star_api_bp.route('/star-api/user-live/<username>', methods=['GET'])
def get_star_user_live(username):
    """
    Get user live streams using Star API
    """
    try:
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key not configured'
            }), 500
        
        star_service = create_star_api_service(api_key)
        
        # First get user info to extract user_id
        user_info = star_service.get_user_info_by_username(username)
        if not user_info:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Extract user_id (using the same logic as other endpoints)
        try:
            user_id = None
            if 'status' in user_info and 'response' in user_info:
                user_id = user_info['response']['body']['data']['user']['id']
            elif 'data' in user_info and 'response' in user_info['data']:
                user_id = user_info['data']['response']['body']['data']['user']['id']
            elif 'response' in user_info:
                user_id = user_info['response']['body']['data']['user']['id']
            else:
                raise KeyError("Unknown response structure")
                
            print(f"DEBUG LIVE: Successfully extracted user_id = {user_id}")
        except (KeyError, TypeError) as e:
            print(f"DEBUG LIVE: Failed to extract user_id: {e}")
            return jsonify({
                'success': False,
                'error': f'Could not extract user ID: {e}'
            }), 500
        
        # Get live streams using user_id
        live_data = star_service.get_user_live(user_id)
        
        if live_data:
            return jsonify({
                'success': True,
                'data': live_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch live data'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Additional Star API endpoints for comprehensive data collection

@star_api_bp.route('/star-api/user-similar/<username>', methods=['GET'])
def get_star_user_similar_accounts(username):
    """Get similar accounts for a user"""
    try:
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        star_service = create_star_api_service(api_key)
        
        # Get user info to extract user_id
        user_info = star_service.get_user_info_by_username(username)
        if not user_info:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Extract user_id
        try:
            if 'status' in user_info and 'response' in user_info:
                user_id = user_info['response']['body']['data']['user']['id']
            else:
                user_id = user_info['data']['response']['body']['data']['user']['id']
        except (KeyError, TypeError) as e:
            return jsonify({'success': False, 'error': f'Could not extract user ID: {e}'}), 500
        
        similar_data = star_service.get_similar_accounts(user_id)
        
        if similar_data:
            return jsonify({
                'success': True,
                'data': similar_data
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to fetch similar accounts'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@star_api_bp.route('/star-api/search/users', methods=['GET'])
def search_star_users():
    """Search for users"""
    try:
        query = request.args.get('query')
        if not query:
            return jsonify({'success': False, 'error': 'Query parameter is required'}), 400
        
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        star_service = create_star_api_service(api_key)
        search_data = star_service.search_users(query)
        
        if search_data:
            return jsonify({
                'success': True,
                'data': search_data
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to search users'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@star_api_bp.route('/star-api/location/info/<location_id>', methods=['GET'])
def get_star_location_info(location_id):
    """Get location information"""
    try:
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        star_service = create_star_api_service(api_key)
        location_data = star_service.get_location_info(location_id)
        
        if location_data:
            return jsonify({
                'success': True,
                'data': location_data
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to fetch location info'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@star_api_bp.route('/star-api/location/media/<location_id>', methods=['GET'])
def get_star_location_media(location_id):
    """Get media from a location"""
    try:
        tab = request.args.get('tab', 'ranked')
        
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        star_service = create_star_api_service(api_key)
        media_data = star_service.get_location_media(location_id, tab)
        
        if media_data:
            return jsonify({
                'success': True,
                'data': media_data
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to fetch location media'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@star_api_bp.route('/star-api/search/locations', methods=['GET'])
def search_star_locations():
    """Search for locations"""
    try:
        query = request.args.get('query')
        if not query:
            return jsonify({'success': False, 'error': 'Query parameter is required'}), 400
        
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        star_service = create_star_api_service(api_key)
        search_data = star_service.search_locations(query)
        
        if search_data:
            return jsonify({
                'success': True,
                'data': search_data
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to search locations'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@star_api_bp.route('/star-api/hashtag/info/<hashtag_name>', methods=['GET'])
def get_star_hashtag_info(hashtag_name):
    """Get hashtag information"""
    try:
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        star_service = create_star_api_service(api_key)
        hashtag_data = star_service.get_hashtag_info_by_name(hashtag_name)
        
        if hashtag_data:
            return jsonify({
                'success': True,
                'data': hashtag_data
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to fetch hashtag info'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@star_api_bp.route('/star-api/hashtag/media/<hashtag_name>', methods=['GET'])
def get_star_hashtag_media(hashtag_name):
    """Get media from a hashtag"""
    try:
        tab = request.args.get('tab', 'top')
        
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        star_service = create_star_api_service(api_key)
        media_data = star_service.get_hashtag_media_by_name(hashtag_name, tab)
        
        if media_data:
            return jsonify({
                'success': True,
                'data': media_data
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to fetch hashtag media'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@star_api_bp.route('/star-api/highlight/stories', methods=['POST'])
def get_star_highlight_stories():
    """Get stories from highlights"""
    try:
        data = request.get_json()
        highlight_ids = data.get('highlight_ids', [])
        
        if not highlight_ids:
            return jsonify({'success': False, 'error': 'highlight_ids are required'}), 400
        
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        star_service = create_star_api_service(api_key)
        stories_data = star_service.get_highlight_stories(highlight_ids)
        
        if stories_data:
            return jsonify({
                'success': True,
                'data': stories_data
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to fetch highlight stories'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@star_api_bp.route('/star-api/comment/likes/<comment_id>', methods=['GET'])
def get_star_comment_likes(comment_id):
    """Get likes on a comment"""
    try:
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        star_service = create_star_api_service(api_key)
        likes_data = star_service.get_comment_likes(comment_id)
        
        if likes_data:
            return jsonify({
                'success': True,
                'data': likes_data
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to fetch comment likes'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@star_api_bp.route('/star-api/comment/replies/<comment_id>', methods=['GET'])
def get_star_comment_replies(comment_id):
    """Get replies to a comment"""
    try:
        media_id = request.args.get('media_id')
        if not media_id:
            return jsonify({'success': False, 'error': 'media_id parameter is required'}), 400
        
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        star_service = create_star_api_service(api_key)
        replies_data = star_service.get_comment_replies(comment_id, media_id)
        
        if replies_data:
            return jsonify({
                'success': True,
                'data': replies_data
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to fetch comment replies'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@star_api_bp.route('/star-api/audio/media/<audio_id>', methods=['GET'])
def get_star_audio_media(audio_id):
    """Get media using a specific audio"""
    try:
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        star_service = create_star_api_service(api_key)
        media_data = star_service.get_audio_media(audio_id)
        
        if media_data:
            return jsonify({
                'success': True,
                'data': media_data
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to fetch audio media'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@star_api_bp.route('/star-api/search/audio', methods=['GET'])
def search_star_audio():
    """Search for audio"""
    try:
        query = request.args.get('query')
        if not query:
            return jsonify({'success': False, 'error': 'Query parameter is required'}), 400
        
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key not configured'}), 500
        
        star_service = create_star_api_service(api_key)
        search_data = star_service.search_audio(query)
        
        if search_data:
            return jsonify({
                'success': True,
                'data': search_data
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to search audio'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
