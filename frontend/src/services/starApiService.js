/**
 * Star API Data Service - Frontend Integration
 * Handles integration with enhanced Star API data collection service
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

class StarApiService {
  /**
   * Trigger comprehensive data collection for a username
   */
  async collectUserData(username) {
    try {
      const response = await api.post(`/star-api/collect-user-data/${username}`);
      return response.data;
    } catch (error) {
      console.error('Error collecting user data:', error);
      throw error;
    }
  }

  /**
   * Get enhanced analytics using Star API collected data
   */
  async getEnhancedAnalytics(username, days = 30) {
    try {
      const params = { username, days };
      
      // Get all analytics data in parallel
      const [
        profileRes,
        mediaRes,
        insightsRes,
        dailyChartRes,
        comprehensiveRes
      ] = await Promise.all([
        api.get(`/profiles?username=${username}`),
        api.get('/media', { params }),
        api.get('/analytics/insights', { params }),
        api.get('/analytics/daily-chart', { params }),
        api.get('/analytics/comprehensive', { params })
      ]);

      return {
        profile: profileRes.data.data?.[0] || null,
        media: mediaRes.data.data || [],
        insights: insightsRes.data.data || {},
        dailyMetrics: dailyChartRes.data.data || [],
        comprehensive: comprehensiveRes.data.data || {}
      };
    } catch (error) {
      console.error('Error fetching enhanced analytics:', error);
      throw error;
    }
  }

  /**
   * Get comprehensive media data with enhanced metrics
   */
  async getEnhancedMedia(username, options = {}) {
    try {
      const params = {
        username,
        limit: options.limit || 50,
        media_type: options.mediaType,
        ...options
      };

      const response = await api.get('/media', { params });
      return this.enhanceMediaData(response.data.data);
    } catch (error) {
      console.error('Error fetching enhanced media:', error);
      throw error;
    }
  }

  /**
   * Enhance media data with calculated metrics
   */
  enhanceMediaData(mediaData) {
    return mediaData.map(post => ({
      ...post,
      // Enhanced engagement metrics
      totalEngagement: (post.like_count || 0) + (post.comment_count || 0) + 
                      (post.save_count || 0) + (post.share_count || 0),
      
      // Video-specific metrics
      videoMetrics: post.is_video ? {
        playCount: post.play_count || 0,
        videoViewCount: post.video_view_count || 0,
        viewToEngagementRatio: post.video_view_count > 0 ? 
          ((post.like_count || 0) + (post.comment_count || 0)) / post.video_view_count : 0
      } : null,

      // Content type classification
      contentType: this.classifyContent(post),
      
      // Performance metrics
      performance: this.calculatePerformance(post),
      
      // Collaboration metrics
      collaborationMetrics: post.is_collab ? {
        isCollaboration: true,
        collaboratorInfo: post.collab_with,
        collaborationType: this.getCollaborationType(post)
      } : null
    }));
  }

  /**
   * Classify content type based on post data
   */
  classifyContent(post) {
    if (post.is_video && post.media_type === 'reel') return 'reel';
    if (post.carousel_media_count > 1) return 'carousel';
    if (post.is_video) return 'video';
    return 'image';
  }

  /**
   * Calculate performance metrics for a post
   */
  calculatePerformance(post) {
    const engagement = (post.like_count || 0) + (post.comment_count || 0);
    const totalReach = Math.max(post.video_view_count || 0, engagement);
    
    return {
      engagementScore: engagement,
      reachScore: totalReach,
      qualityScore: this.calculateQualityScore(post),
      viralityScore: this.calculateViralityScore(post)
    };
  }

  /**
   * Calculate quality score based on multiple factors
   */
  calculateQualityScore(post) {
    let score = 0;
    
    // Base engagement
    const engagement = (post.like_count || 0) + (post.comment_count || 0);
    score += Math.min(engagement / 100, 10); // Max 10 points for engagement
    
    // Content completeness
    if (post.caption && post.caption.length > 50) score += 2;
    if (post.hashtags && post.hashtags.length > 0) score += 1;
    if (post.location_name) score += 1;
    
    // Save ratio (indicates content value)
    if (post.save_count && engagement > 0) {
      score += Math.min((post.save_count / engagement) * 10, 3);
    }
    
    return Math.min(score, 20); // Max score of 20
  }

  /**
   * Calculate virality score
   */
  calculateViralityScore(post) {
    const shares = post.share_count || 0;
    const reshares = post.reshare_count || 0;
    const comments = post.comment_count || 0;
    const likes = post.like_count || 0;
    
    // Higher comment-to-like ratio indicates discussion/virality
    const discussionRatio = likes > 0 ? comments / likes : 0;
    
    // Share metrics
    const shareScore = (shares + reshares) * 2;
    
    // Discussion score
    const discussionScore = discussionRatio * 5;
    
    return shareScore + discussionScore;
  }

  /**
   * Get collaboration type
   */
  getCollaborationType(post) {
    if (post.is_sponsored) return 'sponsored';
    if (post.is_ad) return 'advertisement';
    if (post.collab_with) return 'collaboration';
    return 'organic';
  }

  /**
   * Get data collection status for a username
   */
  async getDataCollectionStatus(username) {
    try {
      const response = await api.get(`/star-api/collection-status/${username}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching collection status:', error);
      return { status: 'unknown', last_updated: null };
    }
  }

  /**
   * Generate insights from Star API data
   */
  generateInsights(analyticsData) {
    const { media, comprehensive, profile } = analyticsData;
    
    return {
      contentStrategy: this.analyzeContentStrategy(media),
      engagementPatterns: this.analyzeEngagementPatterns(media),
      growthOpportunities: this.identifyGrowthOpportunities(media, profile),
      performanceRecommendations: this.generateRecommendations(comprehensive)
    };
  }

  /**
   * Analyze content strategy from media data
   */
  analyzeContentStrategy(media) {
    const contentTypes = {};
    const performanceByType = {};
    
    media.forEach(post => {
      const type = this.classifyContent(post);
      contentTypes[type] = (contentTypes[type] || 0) + 1;
      
      if (!performanceByType[type]) {
        performanceByType[type] = { totalEngagement: 0, count: 0 };
      }
      
      performanceByType[type].totalEngagement += post.totalEngagement;
      performanceByType[type].count += 1;
    });

    // Calculate average performance by type
    Object.keys(performanceByType).forEach(type => {
      performanceByType[type].avgEngagement = 
        performanceByType[type].totalEngagement / performanceByType[type].count;
    });

    return {
      contentDistribution: contentTypes,
      performanceByType,
      recommendedContentMix: this.recommendContentMix(performanceByType)
    };
  }

  /**
   * Analyze engagement patterns
   */
  analyzeEngagementPatterns(media) {
    // Analyze timing, hashtags, content features that drive engagement
    return {
      bestPerformingFeatures: this.findBestFeatures(media),
      engagementTrends: this.analyzeEngagementTrends(media),
      audiencePreferences: this.analyzeAudiencePreferences(media)
    };
  }

  /**
   * Identify growth opportunities
   */
  identifyGrowthOpportunities(media, profile) {
    return {
      underperformingContent: media.filter(post => post.performance.engagementScore < 100),
      viralPotential: media.filter(post => post.performance.viralityScore > 5),
      collaborationOpportunities: media.filter(post => post.collaborationMetrics),
      contentGaps: this.identifyContentGaps(media)
    };
  }

  // Helper methods for analysis
  recommendContentMix(performanceByType) {
    // Implementation for content mix recommendations
    return {};
  }

  findBestFeatures(media) {
    // Implementation for finding best performing features
    return {};
  }

  analyzeEngagementTrends(media) {
    // Implementation for engagement trend analysis
    return {};
  }

  analyzeAudiencePreferences(media) {
    // Implementation for audience preference analysis
    return {};
  }

  identifyContentGaps(media) {
    // Implementation for content gap analysis
    return [];
  }

  generateRecommendations(comprehensive) {
    // Implementation for generating recommendations
    return [];
  }
}

export const starApiService = new StarApiService();
export default starApiService;
