"""
Core API Endpoints - Health check, image proxy, downloads
"""
from flask import Blueprint, request, jsonify, Response
import requests
import base64

core_bp = Blueprint('core', __name__)

@core_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

@core_bp.route('/proxy/image', methods=['GET'])
def proxy_image():
    image_url = request.args.get('url')
    if not image_url:
        return jsonify({'error': 'URL parameter is required'}), 400

    try:
        # Fetch the image
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Get content type from response headers
        content_type = response.headers.get('Content-Type', 'image/jpeg')
        
        # Return the image with proper headers
        return Response(
            response.content,
            content_type=content_type,
            headers={
                'Cache-Control': 'public, max-age=3600',
                'Access-Control-Allow-Origin': '*'
            }
        )
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch image: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@core_bp.route('/download/image', methods=['GET'])
def download_image():
    """
    Download an image and return it as base64 encoded data
    """
    try:
        image_url = request.args.get('url')
        if not image_url:
            return jsonify({
                'success': False,
                'error': 'URL parameter is required'
            }), 400

        # Fetch the image
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Convert to base64
        image_data = base64.b64encode(response.content).decode('utf-8')
        content_type = response.headers.get('Content-Type', 'image/jpeg')
        
        return jsonify({
            'success': True,
            'data': {
                'image_data': image_data,
                'content_type': content_type
            }
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch image: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@core_bp.route('/fetch-data', methods=['POST'])
def fetch_data():
    """
    Trigger data collection from Star API
    This endpoint handles data fetching requests from the frontend
    """
    try:
        data = request.get_json() or {}
        username = data.get('username')
        dataTypes = data.get('dataTypes', {})
        limits = data.get('limits', {})
        
        # Import the Star API data service
        from services.star_api_data_service import create_star_api_data_service
        import os
        
        # Get API key from environment
        api_key = os.getenv('API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API_KEY not configured. Please set the API_KEY environment variable.'
            }), 500
        
        # Create the service
        star_api_service = create_star_api_data_service(api_key)
        
        # If username is provided, collect data for that specific profile
        if username:
            # Check if profile exists
            from models.database import Profile
            profile = Profile.query.filter_by(username=username).first()
            if not profile:
                return jsonify({
                    'success': False,
                    'error': f'Profile {username} not found. Please add the profile first.'
                }), 404
            
            # Collect data for the specific profile with configuration
            result = star_api_service.collect_comprehensive_data_with_config(username, dataTypes, limits)
            
            return jsonify({
                'success': True,
                'message': f'Data collection completed for {username}',
                'data': {
                    'username': username,
                    'status': 'completed',
                    'timestamp': result.get('timestamp', '2025-08-21T13:54:00Z'),
                    'collected_data': result
                }
            })
        else:
            # Collect data for all profiles
            from models.database import Profile
            profiles = Profile.query.all()
            
            if not profiles:
                return jsonify({
                    'success': False,
                    'error': 'No profiles found. Please add profiles first.'
                }), 404
            
            results = []
            for profile in profiles:
                try:
                    result = star_api_service.collect_comprehensive_data(profile.username)
                    results.append({
                        'username': profile.username,
                        'status': 'success',
                        'data': result
                    })
                except Exception as e:
                    results.append({
                        'username': profile.username,
                        'status': 'error',
                        'error': str(e)
                    })
            
            return jsonify({
                'success': True,
                'message': f'Data collection completed for {len(profiles)} profiles',
                'data': {
                    'profiles_processed': len(profiles),
                    'results': results,
                    'timestamp': '2025-08-21T13:54:00Z'
                }
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Data collection failed: {str(e)}'
        }), 500