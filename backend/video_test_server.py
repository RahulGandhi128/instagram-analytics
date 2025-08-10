#!/usr/bin/env python3
"""
Simple Flask test server for video generation
Tests the frontend integration without requiring full backend
"""

from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import asyncio
import sys
import os

# Add the current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_creation import ContentCreationService, ContentRequest
from dataclasses import asdict

app = Flask(__name__)
CORS(app)

# Initialize content service
content_service = ContentCreationService()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'video_test_server'})

@app.route('/api/content/create', methods=['POST'])
def create_content():
    """Create content using AI/LLM services"""
    try:
        data = request.get_json()
        
        # Create content request
        request_obj = ContentRequest(
            user_id=data.get('user_id', 'anonymous'),
            prompt=data.get('prompt', ''),
            content_type=data.get('content_type', 'text'),
            analytics_context=data.get('analytics_context'),
            style_preferences=data.get('style_preferences'),
            session_id=data.get('session_id'),
            # Video-specific parameters
            video_include_audio=data.get('video_include_audio', False),
            video_quality=data.get('video_quality', 'standard'),
            video_generate_actual=data.get('video_generate_actual', False)
        )
        
        # Create async event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(content_service.create_content(request_obj))
            return jsonify(asdict(result))
        finally:
            loop.close()
            
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            'content_id': '',
            'content_type': data.get('content_type', 'unknown') if 'data' in locals() else 'unknown',
            'error': str(e),
            'debug_info': {'test_server_error': str(e)}
        }), 500

if __name__ == '__main__':
    print("🧪 Starting Video Generation Test Server")
    print("🎬 Google Veo 3 Fast integration ready")
    print("🌐 Server running on http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
