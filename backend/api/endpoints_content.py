"""
Content Creation Endpoints - Content creation and brainstormer functionality
"""
from flask import Blueprint, request, jsonify
from services.brainstormer_service import brainstormer_service
import uuid
import asyncio

content_bp = Blueprint('content', __name__)

@content_bp.route('/content/create', methods=['POST'])
def create_content():
    """
    Create content using AI brainstormer
    """
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        session_id = data.get('session_id')
        username = data.get('username')  # Optional context
        content_type = data.get('content_type', 'post')  # post, story, reel
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Prompt is required'
            }), 400
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Generate content
        content = brainstormer_service.generate_content(
            prompt=prompt,
            session_id=session_id,
            username=username,
            content_type=content_type
        )
        
        return jsonify({
            'success': True,
            'data': {
                'content': content,
                'session_id': session_id,
                'content_type': content_type
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_bp.route('/content/conversation/<session_id>', methods=['GET'])
def get_content_conversation(session_id):
    """
    Get content creation conversation history
    """
    try:
        conversation = brainstormer_service.get_conversation_history(session_id)
        
        return jsonify({
            'success': True,
            'data': {
                'conversation': conversation,
                'session_id': session_id
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_bp.route('/content/analytics-context/<username>', methods=['GET'])
def get_content_analytics_context(username):
    """
    Get analytics context for content creation
    """
    try:
        context = brainstormer_service.get_analytics_context_for_content(username)
        
        return jsonify({
            'success': True,
            'data': context
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_bp.route('/brainstormer/chat', methods=['POST'])
def brainstormer_chat():
    """
    Chat with the brainstormer AI
    """
    try:
        data = request.get_json()
        message = data.get('message')
        session_id = data.get('session_id')
        username = data.get('username')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Get brainstormer response
        response = brainstormer_service.chat(
            message=message,
            session_id=session_id,
            username=username
        )
        
        return jsonify({
            'success': True,
            'data': {
                'response': response,
                'session_id': session_id
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
