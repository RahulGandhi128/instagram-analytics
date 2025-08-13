"""
Chatbot Endpoints - AI chatbot functionality for analytics insights
"""
from flask import Blueprint, request, jsonify
from services.chatbot_service import analytics_chatbot
import uuid

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/chatbot/chat', methods=['POST'])
def chat():
    """
    Handle chatbot conversation
    """
    try:
        data = request.get_json()
        message = data.get('message')
        session_id = data.get('session_id')
        username = data.get('username')  # Optional context
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Get chatbot response
        response = analytics_chatbot.chat(message, session_id, username)
        
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

@chatbot_bp.route('/chatbot/history/<session_id>', methods=['GET'])
def get_chat_history(session_id):
    """
    Get chat history for a session
    """
    try:
        history = analytics_chatbot.get_conversation_history(session_id)
        
        return jsonify({
            'success': True,
            'data': {
                'history': history,
                'session_id': session_id
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chatbot_bp.route('/chatbot/clear/<session_id>', methods=['DELETE'])
def clear_chat_history(session_id):
    """
    Clear chat history for a session
    """
    try:
        analytics_chatbot.clear_conversation(session_id)
        
        return jsonify({
            'success': True,
            'message': 'Chat history cleared'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chatbot_bp.route('/chatbot/analytics-context', methods=['GET'])
def get_analytics_context():
    """
    Get analytics context for chatbot
    """
    try:
        username = request.args.get('username')
        
        if not username:
            return jsonify({
                'success': False,
                'error': 'Username parameter is required'
            }), 400

        context = analytics_chatbot.get_analytics_context(username)
        
        return jsonify({
            'success': True,
            'data': context
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
