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
