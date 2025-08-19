"""
Main API Routes - Import and register all endpoint blueprints
"""
from flask import Blueprint

# Import only working endpoint blueprints
from .endpoints_core import core_bp
from .endpoints_profiles_clean import profiles_bp

# Other endpoints disabled temporarily
# from .endpoints_analytics import analytics_bp
# from .endpoints_chatbot import chatbot_bp  
# from .endpoints_content import content_bp
# from .endpoints_star_api import star_api_bp

# Create main API blueprint
api_bp = Blueprint('api', __name__)

def register_blueprints(app):
    """
    Register working endpoint blueprints with the Flask app
    """
    # Register only working blueprints
    app.register_blueprint(core_bp, url_prefix='/api')
    app.register_blueprint(profiles_bp, url_prefix='/api')
    
    print("✅ Clean API endpoint blueprints registered successfully!")
    print("📁 Active endpoints:")
    print("   - endpoints_core.py: Health check")
    print("   - endpoints_profiles_clean.py: Clean profile management & media")

# For backward compatibility, export the main blueprint
__all__ = ['api_bp', 'register_blueprints']
