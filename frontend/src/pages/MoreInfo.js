import React, { useState, useEffect } from 'react';
import { Code, Info, Calculator, TrendingUp, Hash, Clock, BarChart } from 'lucide-react';

const MoreInfo = () => {
  const [calculationMethods, setCalculationMethods] = useState({});
  const [loading, setLoading] = useState(true);

  // Fetch calculation methods from backend
  useEffect(() => {
    fetchCalculationMethods();
  }, []);

  const fetchCalculationMethods = async () => {
    try {
      const response = await fetch('/api/analytics/calculation-methods');
      if (response.ok) {
        const data = await response.json();
        setCalculationMethods(data.data || {});
      }
    } catch (error) {
      console.error('Error fetching calculation methods:', error);
    } finally {
      setLoading(false);
    }
  };

  // Static calculation information (fallback if API doesn't work)
  const staticCalculations = {
    performance_metrics: {
      title: "📊 Performance Metrics",
      icon: <TrendingUp className="h-6 w-6" />,
      metrics: {
        engagement_rate: {
          name: "Engagement Rate",
          formula: "(Total Engagement / Followers) × 100",
          description: "Measures audience interaction relative to follower count",
          pythonCode: `def calculate_engagement_rate(total_engagement, followers):
    if followers == 0:
        return 0.0
    return round((total_engagement / followers) * 100, 2)`
        },
        content_quality: {
          name: "Content Quality Score",
          formula: "Weighted average of (Caption Usage × 25% + Consistency × 25% + Diversity × 25% + Engagement Consistency × 25%)",
          description: "Comprehensive score based on content characteristics and performance patterns",
          pythonCode: `def calculate_content_quality(posts):
    factors = {
        'caption_usage': calculate_caption_usage(posts),
        'consistency': calculate_posting_consistency(posts),
        'diversity': calculate_content_diversity(posts),
        'engagement_consistency': calculate_engagement_consistency(posts)
    }
    
    weights = {'caption_usage': 0.25, 'consistency': 0.25, 
               'diversity': 0.25, 'engagement_consistency': 0.25}
    
    quality_score = sum(factors[key] * weights[key] for key in factors)
    return round(quality_score)`
        },
        performance_score: {
          name: "Performance Score",
          formula: "(Content Quality × 0.4) + (Engagement Rate × 30) + (Posting Consistency × 0.3)",
          description: "Overall performance combining quality, engagement, and consistency",
          pythonCode: `def calculate_performance_score(content_quality, engagement_rate, consistency):
    # Normalize engagement rate (cap at reasonable maximum)
    normalized_engagement = min(engagement_rate * 30, 100)
    
    score = (content_quality * 0.4 + 
             normalized_engagement * 0.3 + 
             consistency * 0.3)
    
    return round(min(score, 100))`
        }
      }
    },
    hashtag_analytics: {
      title: "🔥 Hashtag Analytics",
      icon: <Hash className="h-6 w-6" />,
      metrics: {
        hashtag_performance: {
          name: "Hashtag Performance",
          formula: "Total Engagement per Hashtag / Usage Count",
          description: "Average engagement generated per hashtag usage",
          pythonCode: `def calculate_hashtag_performance(posts):
    hashtag_data = {}
    
    for post in posts:
        if post.caption:
            hashtags = re.findall(r'#\\w+', post.caption.lower())
            post_engagement = (post.like_count or 0) + (post.comment_count or 0)
            
            for hashtag in hashtags:
                if hashtag not in hashtag_data:
                    hashtag_data[hashtag] = {'count': 0, 'total_engagement': 0}
                hashtag_data[hashtag]['count'] += 1
                hashtag_data[hashtag]['total_engagement'] += post_engagement
    
    # Calculate average engagement per hashtag
    for hashtag in hashtag_data:
        hashtag_data[hashtag]['avg_engagement'] = (
            hashtag_data[hashtag]['total_engagement'] / 
            hashtag_data[hashtag]['count']
        )
    
    return hashtag_data`
        },
        trending_analysis: {
          name: "Trending Hashtags",
          formula: "Ranked by Total Engagement × Usage Frequency",
          description: "Identifies hashtags with highest combined engagement and usage",
          pythonCode: `def get_trending_hashtags(hashtag_performance, limit=15):
    # Sort by total engagement (trending factor)
    trending = sorted(
        hashtag_performance.items(),
        key=lambda x: x[1]['total_engagement'],
        reverse=True
    )[:limit]
    
    return [
        {
            'hashtag': f"#{tag.replace('#', '')}", 
            'total_posts': data['count'],
            'total_engagement': data['total_engagement'],
            'avg_engagement': data['avg_engagement']
        } 
        for tag, data in trending
    ]`
        }
      }
    },
    media_type_analysis: {
      title: "🎯 Media Type Analysis",
      icon: <BarChart className="h-6 w-6" />,
      metrics: {
        content_type_performance: {
          name: "Content Type Performance",
          formula: "Average Engagement per Media Type",
          description: "Compares performance across carousel, reel, and post formats",
          pythonCode: `def calculate_media_type_performance(posts):
    media_stats = {}
    
    for post in posts:
        media_type = post.media_type or 'post'
        engagement = (post.like_count or 0) + (post.comment_count or 0)
        
        if media_type not in media_stats:
            media_stats[media_type] = {
                'count': 0, 'total_engagement': 0, 'engagements': []
            }
        
        media_stats[media_type]['count'] += 1
        media_stats[media_type]['total_engagement'] += engagement
        media_stats[media_type]['engagements'].append(engagement)
    
    # Calculate averages and best performing type
    for media_type in media_stats:
        count = media_stats[media_type]['count']
        total = media_stats[media_type]['total_engagement']
        media_stats[media_type]['avg_engagement'] = total / count if count > 0 else 0
    
    # Find best performing type (excluding 'post' generic type)
    valid_types = {k: v for k, v in media_stats.items() 
                   if k != 'post' and v['count'] > 0}
    
    best_type = max(valid_types.items(), 
                   key=lambda x: x[1]['avg_engagement'])[0] if valid_types else 'N/A'
    
    return media_stats, best_type`
        }
      }
    },
    posting_time_analysis: {
      title: "⏰ Posting Time Analysis",
      icon: <Clock className="h-6 w-6" />,
      metrics: {
        optimal_posting_times: {
          name: "Optimal Posting Times",
          formula: "Highest Average Engagement by Hour/Day",
          description: "Identifies best times and days based on historical engagement",
          pythonCode: `def calculate_optimal_posting_times(posts):
    hour_performance = {}
    day_performance = {}
    
    for post in posts:
        if not post.post_datetime_ist:
            continue
            
        hour = post.post_datetime_ist.hour
        day = post.post_datetime_ist.strftime('%A')
        engagement = (post.like_count or 0) + (post.comment_count or 0)
        
        # Hour analysis
        if str(hour) not in hour_performance:
            hour_performance[str(hour)] = {
                'count': 0, 'total_engagement': 0
            }
        hour_performance[str(hour)]['count'] += 1
        hour_performance[str(hour)]['total_engagement'] += engagement
        
        # Day analysis  
        if day not in day_performance:
            day_performance[day] = {
                'count': 0, 'total_engagement': 0
            }
        day_performance[day]['count'] += 1
        day_performance[day]['total_engagement'] += engagement
    
    # Calculate averages
    for hour_data in hour_performance.values():
        hour_data['avg_engagement'] = (
            hour_data['total_engagement'] / hour_data['count']
        )
    
    for day_data in day_performance.values():
        day_data['avg_engagement'] = (
            day_data['total_engagement'] / day_data['count']
        )
    
    return hour_performance, day_performance`
        },
        time_period_breakdown: {
          name: "Time Period Breakdown",
          formula: "Categorized by Morning (6-12), Afternoon (12-18), Evening (18-24), Night (0-6)",
          description: "Groups posting times into periods for pattern analysis",
          pythonCode: `def calculate_time_period_breakdown(posts):
    periods = {
        'morning': {'count': 0, 'total_engagement': 0},    # 6-12
        'afternoon': {'count': 0, 'total_engagement': 0},  # 12-18  
        'evening': {'count': 0, 'total_engagement': 0},    # 18-24
        'night': {'count': 0, 'total_engagement': 0}       # 0-6
    }
    
    for post in posts:
        if not post.post_datetime_ist:
            continue
            
        hour = post.post_datetime_ist.hour
        engagement = (post.like_count or 0) + (post.comment_count or 0)
        
        if 6 <= hour < 12:
            period = 'morning'
        elif 12 <= hour < 18:
            period = 'afternoon'
        elif 18 <= hour < 24:
            period = 'evening'
        else:
            period = 'night'
            
        periods[period]['count'] += 1
        periods[period]['total_engagement'] += engagement
    
    total_posts = sum(p['count'] for p in periods.values())
    
    # Calculate percentages and averages
    for period_data in periods.values():
        count = period_data['count']
        period_data['avg_engagement'] = (
            period_data['total_engagement'] / count if count > 0 else 0
        )
        period_data['percentage'] = (
            round(count / total_posts * 100, 1) if total_posts > 0 else 0
        )
    
    return periods`
        }
      }
    },
    engagement_trends: {
      title: "📈 Engagement Trends",
      icon: <TrendingUp className="h-6 w-6" />,
      metrics: {
        daily_engagement: {
          name: "Daily Engagement Calculation",
          formula: "Sum of (Likes + Comments + Shares) per Day",
          description: "Aggregates all engagement metrics by posting date",
          pythonCode: `def calculate_daily_engagement(posts, days=30):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    daily_metrics = {}
    
    # Initialize all days with zero
    current_date = start_date
    while current_date <= end_date:
        daily_metrics[current_date] = {
            'date': current_date.isoformat(),
            'posts_count': 0,
            'total_engagement': 0,
            'total_likes': 0,
            'total_comments': 0
        }
        current_date += timedelta(days=1)
    
    # Aggregate posts by date
    for post in posts:
        if not post.post_datetime_ist:
            continue
            
        post_date = post.post_datetime_ist.date()
        
        if start_date <= post_date <= end_date:
            likes = post.like_count or 0
            comments = post.comment_count or 0
            engagement = likes + comments
            
            daily_metrics[post_date]['posts_count'] += 1
            daily_metrics[post_date]['total_engagement'] += engagement
            daily_metrics[post_date]['total_likes'] += likes
            daily_metrics[post_date]['total_comments'] += comments
    
    # Calculate averages
    for day_data in daily_metrics.values():
        posts_count = day_data['posts_count']
        day_data['avg_engagement_per_post'] = (
            day_data['total_engagement'] / posts_count if posts_count > 0 else 0
        )
    
    return list(daily_metrics.values())`
        }
      }
    }
  };

  const renderMetricSection = (sectionKey, section) => (
    <div key={sectionKey} className="bg-white rounded-lg shadow p-6 mb-6">
      <div className="flex items-center mb-4">
        <div className="text-purple-500 mr-3">
          {section.icon}
        </div>
        <h2 className="text-xl font-bold text-gray-900">{section.title}</h2>
      </div>
      
      <div className="space-y-6">
        {Object.entries(section.metrics).map(([metricKey, metric]) => (
          <div key={metricKey} className="border-l-4 border-purple-500 pl-4">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">{metric.name}</h3>
            
            <div className="bg-blue-50 p-3 rounded-lg mb-3">
              <h4 className="font-medium text-blue-800 mb-1">📐 Formula:</h4>
              <code className="text-blue-700 text-sm">{metric.formula}</code>
            </div>
            
            <div className="bg-green-50 p-3 rounded-lg mb-3">
              <h4 className="font-medium text-green-800 mb-1">📝 Description:</h4>
              <p className="text-green-700 text-sm">{metric.description}</p>
            </div>
            
            <div className="bg-gray-50 p-3 rounded-lg">
              <h4 className="font-medium text-gray-800 mb-2 flex items-center">
                <Code className="h-4 w-4 mr-1" />
                Python Implementation:
              </h4>
              <pre className="text-xs text-gray-700 overflow-x-auto bg-gray-100 p-2 rounded border">
                <code>{metric.pythonCode}</code>
              </pre>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
            <p className="mt-2 text-gray-600">Loading calculation methods...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center mb-4">
            <Info className="h-8 w-8 text-purple-500 mr-3" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Analytics Calculation Methods</h1>
              <p className="text-gray-600">Transparent view of all metrics, formulas, and implementation code</p>
            </div>
          </div>
          
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-center">
              <Calculator className="h-5 w-5 text-yellow-600 mr-2" />
              <div>
                <h3 className="font-medium text-yellow-800">Transparency & Accuracy</h3>
                <p className="text-yellow-700 text-sm mt-1">
                  All calculations are derived from the actual analytics service code. 
                  This documentation stays synchronized with code changes to ensure accuracy.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Calculation Methods */}
        {Object.entries(calculationMethods).length > 0 
          ? Object.entries(calculationMethods).map(([key, section]) => renderMetricSection(key, section))
          : Object.entries(staticCalculations).map(([key, section]) => renderMetricSection(key, section))
        }

        {/* Footer */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">📋 Implementation Notes</h2>
          <div className="space-y-2 text-sm text-gray-600">
            <p>• All engagement calculations include likes, comments, and available interaction metrics</p>
            <p>• Time-based analysis uses IST (Indian Standard Time) for consistency</p>
            <p>• Content quality scores are normalized to 0-100 scale for easy comparison</p>
            <p>• Hashtag analysis uses case-insensitive pattern matching for accuracy</p>
            <p>• Media type classification follows Instagram's standard categories</p>
            <p>• Zero-division protection is implemented across all ratio calculations</p>
          </div>
          
          <div className="mt-4 p-3 bg-purple-50 rounded-lg">
            <p className="text-purple-700 text-sm">
              <strong>Data Source:</strong> Analytics Service (backend/services/analytics_service.py)
              <br />
              <strong>Last Updated:</strong> Synchronized with code deployment
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MoreInfo;
