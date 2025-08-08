"""
Analytics Service Configuration
Defines which analytics sections to include for different use cases
"""

# Analytics sections configuration for different consumers
ANALYTICS_SECTIONS = {
    'dashboard': ['profiles', 'posts', 'performance'],
    'analytics_page': ['hashtags', 'media_types', 'posting_times', 'engagement_trends'],
    'chatbot': ['profiles', 'posts', 'hashtags', 'media_types', 'posting_times', 'engagement_trends', 'performance'],
    'api_summary': ['profiles', 'posts', 'stories'],
    'insights': ['posts', 'media_types', 'posting_times', 'performance'],
    'weekly_comparison': [],  # Uses dedicated method
    'full': ['profiles', 'posts', 'hashtags', 'media_types', 'posting_times', 'engagement_trends', 'performance', 'stories']
}

# Cache settings (for future implementation)
CACHE_SETTINGS = {
    'enabled': False,  # Disabled for now, can be enabled with Redis
    'ttl': 300,  # 5 minutes
    'redis_url': 'redis://localhost:6379'
}

# Performance thresholds for scoring and recommendations
PERFORMANCE_THRESHOLDS = {
    'high_engagement': 1000,
    'medium_engagement': 500,
    'low_engagement': 100,
    'min_posts_for_analysis': 5,
    'hashtag_min_usage': 2
}

# Time zone settings
TIMEZONE_SETTINGS = {
    'default_timezone': 'Asia/Kolkata',  # IST
    'display_format': '%Y-%m-%d %H:%M:%S'
}

# Limits for data processing
DATA_LIMITS = {
    'max_posts_per_query': 1000,
    'max_hashtags_to_analyze': 50,
    'max_top_results': 15,
    'default_days': 30
}

# Compatibility settings for legacy code
LEGACY_COMPATIBILITY = {
    'maintain_old_field_names': True,
    'include_deprecated_fields': True,
    'transform_for_frontend': True
}
