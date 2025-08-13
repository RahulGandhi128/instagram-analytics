"""
Profile Management Endpoints - Add, delete, get profiles and data fetching
"""
from flask import Blueprint, request, jsonify
from services.instagram_service import InstagramAnalyticsService
from models.database import db, Profile, MediaPost, Story
from sqlalchemy import func, desc
import os

profiles_bp = Blueprint('profiles', __name__)

# Initialize the service
instagram_service = InstagramAnalyticsService(os.getenv('API_KEY'))

@profiles_bp.route('/profiles', methods=['POST'])
def add_profile():
    """
    Add a new profile to track
    """
    try:
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({
                'success': False,
                'error': 'Username is required'
            }), 400

        # Check if profile already exists
        existing_profile = Profile.query.filter_by(username=username).first()
        if existing_profile:
            return jsonify({
                'success': False,
                'error': 'Profile already exists'
            }), 409

        # Create new profile
        profile = Profile(username=username)
        db.session.add(profile)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': {'username': username}
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profiles_bp.route('/profiles/<username>', methods=['DELETE'])
def delete_profile(username):
    """
    Delete a profile and all associated data
    """
    try:
        # Find the profile
        profile = Profile.query.filter_by(username=username).first()
        if not profile:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404

        # Delete associated data
        MediaPost.query.filter_by(profile_id=profile.id).delete()
        Story.query.filter_by(profile_id=profile.id).delete()
        
        # Delete the profile
        db.session.delete(profile)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Profile {username} deleted successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profiles_bp.route('/profiles', methods=['GET'])
def get_profiles():
    """
    Get all tracked profiles with their stats
    """
    try:
        profiles = Profile.query.all()
        
        profile_data = []
        for profile in profiles:
            media_count = MediaPost.query.filter_by(profile_id=profile.id).count()
            story_count = Story.query.filter_by(profile_id=profile.id).count()
            
            # Get latest media for thumbnail
            latest_media = MediaPost.query.filter_by(profile_id=profile.id)\
                                         .order_by(desc(MediaPost.id))\
                                         .first()
            
            profile_data.append({
                'id': profile.id,
                'username': profile.username,
                'bio': profile.bio,
                'follower_count': profile.follower_count,
                'following_count': profile.following_count,
                'media_count': media_count,
                'story_count': story_count,
                'profile_pic_url': profile.profile_pic_url,
                'latest_media_url': latest_media.display_url if latest_media else None,
                'created_at': profile.created_at.isoformat() if profile.created_at else None
            })
        
        return jsonify({
            'success': True,
            'data': profile_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profiles_bp.route('/fetch-data', methods=['POST'])
def fetch_data():
    """
    Fetch Instagram data for specified usernames
    """
    try:
        data = request.get_json()
        usernames = data.get('usernames', [])
        
        if not usernames:
            return jsonify({
                'success': False,
                'error': 'No usernames provided'
            }), 400

        results = []
        for username in usernames:
            try:
                result = instagram_service.fetch_instagram_data(username)
                results.append({
                    'username': username,
                    'success': True,
                    'data': result
                })
            except Exception as e:
                results.append({
                    'username': username,
                    'success': False,
                    'error': str(e)
                })

        return jsonify({
            'success': True,
            'results': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profiles_bp.route('/fetch-instagram-data', methods=['POST'])
def fetch_instagram_data():
    """
    Fetch Instagram data for all profiles or specified ones
    """
    try:
        data = request.get_json()
        usernames = data.get('usernames', [])
        
        if usernames:
            # Fetch data for specified usernames
            results = {}
            for username in usernames:
                try:
                    result = instagram_service.fetch_instagram_data(username)
                    results[username] = result
                except Exception as e:
                    results[username] = {'error': str(e)}
        else:
            # Fetch data for all profiles
            profiles = Profile.query.all()
            results = {}
            for profile in profiles:
                try:
                    result = instagram_service.fetch_instagram_data(profile.username)
                    results[profile.username] = result
                except Exception as e:
                    results[profile.username] = {'error': str(e)}

        return jsonify({
            'success': True,
            'data': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profiles_bp.route('/fetch-instagram-data/<username>', methods=['POST'])
def fetch_instagram_data_for_user(username):
    """
    Fetch Instagram data for a specific user
    """
    try:
        result = instagram_service.fetch_instagram_data(username)
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profiles_bp.route('/profiles/<username>', methods=['GET'])
def get_profile(username):
    """
    Get specific profile data
    """
    try:
        profile = Profile.query.filter_by(username=username).first()
        if not profile:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404

        return jsonify({
            'success': True,
            'data': {
                'username': profile.username,
                'bio': profile.bio,
                'follower_count': profile.follower_count,
                'following_count': profile.following_count,
                'profile_pic_url': profile.profile_pic_url
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profiles_bp.route('/media', methods=['GET'])
def get_media():
    """
    Get media posts with pagination
    """
    try:
        username = request.args.get('username')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = MediaPost.query
        
        if username:
            profile = Profile.query.filter_by(username=username).first()
            if not profile:
                return jsonify({
                    'success': False,
                    'error': 'Profile not found'
                }), 404
            query = query.filter_by(profile_id=profile.id)
        
        media_posts = query.order_by(desc(MediaPost.id)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'posts': [{
                    'id': post.id,
                    'shortcode': post.shortcode,
                    'display_url': post.display_url,
                    'like_count': post.like_count,
                    'comment_count': post.comment_count,
                    'caption': post.caption,
                    'created_at': post.created_at.isoformat() if post.created_at else None
                } for post in media_posts.items],
                'total': media_posts.total,
                'pages': media_posts.pages,
                'current_page': page
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profiles_bp.route('/stories', methods=['GET'])
def get_stories():
    """
    Get stories with pagination
    """
    try:
        username = request.args.get('username')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = Story.query
        
        if username:
            profile = Profile.query.filter_by(username=username).first()
            if not profile:
                return jsonify({
                    'success': False,
                    'error': 'Profile not found'
                }), 404
            query = query.filter_by(profile_id=profile.id)
        
        stories = query.order_by(desc(Story.id)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'stories': [{
                    'id': story.id,
                    'story_id': story.story_id,
                    'display_url': story.display_url,
                    'story_type': story.story_type,
                    'created_at': story.created_at.isoformat() if story.created_at else None
                } for story in stories.items],
                'total': stories.total,
                'pages': stories.pages,
                'current_page': page
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
