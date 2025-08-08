"""
Calculation Methods Extractor
Dynamically extracts calculation methods from analytics service for transparency
"""
import inspect
import ast
import re
from datetime import datetime
from services.analytics_service import AnalyticsService

class CalculationMethodsExtractor:
    def __init__(self):
        self.analytics_service = AnalyticsService()
        
    def extract_calculation_methods(self):
        """Extract all calculation methods with their code and formulas"""
        
        # Get source code of analytics service
        source_code = inspect.getsource(AnalyticsService)
        
        # Parse into AST for better analysis
        tree = ast.parse(source_code)
        
        calculation_methods = {
            'performance_metrics': {
                'title': '📊 Performance Metrics',
                'icon': 'TrendingUp',
                'metrics': {
                    'engagement_rate': {
                        'name': 'Engagement Rate',
                        'formula': '(Total Engagement / Followers) × 100',
                        'description': 'Measures audience interaction relative to follower count',
                        'pythonCode': self._extract_method_code('calculate_engagement_rate', source_code)
                    },
                    'content_quality': {
                        'name': 'Content Quality Score',
                        'formula': 'Weighted average of (Caption Usage × 25% + Consistency × 25% + Diversity × 25% + Engagement Consistency × 25%)',
                        'description': 'Comprehensive score based on content characteristics and performance patterns',
                        'pythonCode': self._extract_method_code('calculate_content_quality', source_code)
                    },
                    'performance_score': {
                        'name': 'Performance Score',
                        'formula': '(Content Quality × 0.4) + (Engagement Rate × 30) + (Posting Consistency × 0.3)',
                        'description': 'Overall performance combining quality, engagement, and consistency',
                        'pythonCode': self._extract_method_code('calculate_performance_score', source_code)
                    }
                }
            },
            'hashtag_analytics': {
                'title': '🔥 Hashtag Analytics',
                'icon': 'Hash',
                'metrics': {
                    'hashtag_performance': {
                        'name': 'Hashtag Performance',
                        'formula': 'Total Engagement per Hashtag / Usage Count',
                        'description': 'Average engagement generated per hashtag usage',
                        'pythonCode': self._extract_method_code('_calculate_hashtag_performance', source_code)
                    },
                    'trending_analysis': {
                        'name': 'Trending Hashtags',
                        'formula': 'Ranked by Total Engagement × Usage Frequency',
                        'description': 'Identifies hashtags with highest combined engagement and usage',
                        'pythonCode': self._extract_method_code('get_trending_hashtags', source_code)
                    }
                }
            },
            'media_type_analysis': {
                'title': '🎯 Media Type Analysis',
                'icon': 'BarChart',
                'metrics': {
                    'content_type_performance': {
                        'name': 'Content Type Performance',
                        'formula': 'Average Engagement per Media Type',
                        'description': 'Compares performance across carousel, reel, and post formats',
                        'pythonCode': self._extract_method_code('_calculate_media_type_analytics', source_code)
                    }
                }
            },
            'posting_time_analysis': {
                'title': '⏰ Posting Time Analysis',
                'icon': 'Clock',
                'metrics': {
                    'optimal_posting_times': {
                        'name': 'Optimal Posting Times',
                        'formula': 'Highest Average Engagement by Hour/Day',
                        'description': 'Identifies best times and days based on historical engagement',
                        'pythonCode': self._extract_method_code('_calculate_posting_time_analytics', source_code)
                    },
                    'time_period_breakdown': {
                        'name': 'Time Period Breakdown',
                        'formula': 'Categorized by Morning (6-12), Afternoon (12-18), Evening (18-24), Night (0-6)',
                        'description': 'Groups posting times into periods for pattern analysis',
                        'pythonCode': self._extract_method_code('_get_time_period_breakdown', source_code)
                    }
                }
            },
            'engagement_trends': {
                'title': '📈 Engagement Trends',
                'icon': 'TrendingUp',
                'metrics': {
                    'daily_engagement': {
                        'name': 'Daily Engagement Calculation',
                        'formula': 'Sum of (Likes + Comments + Shares) per Day',
                        'description': 'Aggregates all engagement metrics by posting date',
                        'pythonCode': self._extract_method_code('calculate_daily_metrics', source_code)
                    }
                }
            }
        }
        
        return calculation_methods
    
    def _extract_method_code(self, method_name, source_code):
        """Extract specific method code from source"""
        try:
            # Find method definition
            pattern = rf'def {method_name}\(.*?\):(.*?)(?=\n    def|\nclass|\n\n|\Z)'
            match = re.search(pattern, source_code, re.DOTALL)
            
            if match:
                method_body = match.group(1)
                # Clean up indentation
                lines = method_body.split('\n')
                cleaned_lines = []
                for line in lines:
                    if line.strip():  # Skip empty lines
                        # Remove 8 spaces (2 levels of indentation)
                        cleaned_line = line[8:] if line.startswith('        ') else line.strip()
                        cleaned_lines.append(cleaned_line)
                
                return f"def {method_name}(...):\n" + '\n'.join(cleaned_lines)
            else:
                return f"# Method {method_name} not found in source code"
                
        except Exception as e:
            return f"# Error extracting {method_name}: {str(e)}"
    
    def get_analytics_documentation(self):
        """Get comprehensive documentation of all analytics methods"""
        try:
            calculation_methods = self.extract_calculation_methods()
            
            # Add metadata
            documentation = {
                'metadata': {
                    'extracted_at': datetime.now().isoformat(),
                    'source_file': 'services/analytics_service.py',
                    'total_sections': len(calculation_methods),
                    'sync_status': 'live_extraction'
                },
                'data': calculation_methods
            }
            
            return documentation
            
        except Exception as e:
            return {
                'error': f'Failed to extract calculation methods: {str(e)}',
                'metadata': {
                    'extracted_at': datetime.now().isoformat(),
                    'sync_status': 'failed'
                },
                'data': {}
            }

# Global instance
calculation_extractor = CalculationMethodsExtractor()
