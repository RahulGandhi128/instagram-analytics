"""
Main API Routes - Import and register all endpoint blueprints
"""
from flask import Blueprint

# Import all endpoint blueprints
from .endpoints_core import core_bp
from .endpoints_profiles import profiles_bp
from .endpoints_analytics import analytics_bp
from .endpoints_chatbot import chatbot_bp
from .endpoints_content import content_bp
from .endpoints_star_api import star_api_bp

# Create main API blueprint
api_bp = Blueprint('api', __name__)

def register_blueprints(app):
    """
    Register all endpoint blueprints with the Flask app
    """
    # Register each blueprint with appropriate URL prefix
    app.register_blueprint(core_bp, url_prefix='/api')
    app.register_blueprint(profiles_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api')
    app.register_blueprint(chatbot_bp, url_prefix='/api')
    app.register_blueprint(content_bp, url_prefix='/api')
    app.register_blueprint(star_api_bp, url_prefix='/api')
    
    print("✅ All API endpoint blueprints registered successfully!")
    print("📁 Endpoint files organized:")
    print("   - endpoints_core.py: Health check, image proxy")
    print("   - endpoints_profiles.py: Profile management")
    print("   - endpoints_analytics.py: Analytics & insights")
    print("   - endpoints_chatbot.py: AI chatbot functionality")
    print("   - endpoints_content.py: Content creation & brainstormer")
    print("   - endpoints_star_api.py: Star API integration")

# For backward compatibility, export the main blueprint
__all__ = ['api_bp', 'register_blueprints']
