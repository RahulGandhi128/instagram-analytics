"""
Main API Routes - Import and register all endpoint blueprints
"""
from flask import Blueprint

# Import all endpoint blueprints for comprehensive functionality
from .endpoints_core import core_bp
from .endpoints_profiles_clean import profiles_bp
from .endpoints_analytics import analytics_bp
from .endpoints_star_api import star_api_bp

# Other endpoints available but not critical
# from .endpoints_chatbot import chatbot_bp  
# from .endpoints_content import content_bp

# Create main API blueprint
api_bp = Blueprint('api', __name__)

def register_blueprints(app):
    """
    Register comprehensive endpoint blueprints with the Flask app
    """
    # Register all working blueprints
    app.register_blueprint(core_bp, url_prefix='/api')
    app.register_blueprint(profiles_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api')
    app.register_blueprint(star_api_bp, url_prefix='/api')
    
    print("✅ Comprehensive API endpoint blueprints registered successfully!")
    print("📁 Active endpoints:")
    print("   - endpoints_core.py: Health check")
    print("   - endpoints_profiles_clean.py: Profile management & media")
    print("   - endpoints_analytics.py: Analytics, insights, dashboard")
    print("   - endpoints_star_api.py: Star API data collection")

# For backward compatibility, export the main blueprint
__all__ = ['api_bp', 'register_blueprints']
