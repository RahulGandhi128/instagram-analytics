import React, { useState, useEffect } from 'react';
import { Heart, MessageCircle, Share, Play, ExternalLink, Calendar, Bookmark, Eye, MoreHorizontal, MapPin, Users } from 'lucide-react';
import { analyticsAPI } from '../services/api';
import { useUsernames } from '../hooks/useUsernames';

const MediaPosts = ({ showNotification }) => {
  const [posts, setPosts] = useState([]);
  const [profileInfo, setProfileInfo] = useState(null);
  const [summaryStats, setSummaryStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedPost, setSelectedPost] = useState(null);
  const [filters, setFilters] = useState({
    username: '',
    mediaType: '',
    sortBy: 'date',
    limit: 50
  });
  
  const { usernames } = useUsernames();

  useEffect(() => {
    // Only fetch posts if we have a username filter
    if (filters.username) {
      fetchPosts();
    } else {
      setPosts([]);
      setProfileInfo(null);
      setSummaryStats(null);
      setLoading(false);
    }
    
    // Listen for global data fetch events
    const handleDataFetched = () => {
      if (filters.username) {
        fetchPosts();
      }
    };
    
    window.addEventListener('dataFetched', handleDataFetched);
    
    return () => {
      window.removeEventListener('dataFetched', handleDataFetched);
    };
  }, [filters]);

  const fetchPosts = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filters.username) params.username = filters.username;
      if (filters.mediaType) params.media_type = filters.mediaType;
      if (filters.sortBy) params.sort_by = filters.sortBy;
      if (filters.limit) params.limit = filters.limit;

      const response = await analyticsAPI.getMedia(params);
      setPosts(response.data.data || []);
      setProfileInfo(response.data.profile_info || null);
      setSummaryStats(response.data.summary_stats || null);
    } catch (error) {
      console.error('Error loading media posts:', error);
      showNotification('Error loading media posts', 'error');
      setPosts([]);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getMediaTypeIcon = (post) => {
    if (post.is_video) return '🎥';
    if (post.media_type === 'reel') return '🎬';
    if (post.is_carousel) return '🖼️';
    return '📷';
  };

  const getMediaTypeColor = (type) => {
    switch (type) {
      case 'reel': return 'bg-red-100 text-red-800';
      case 'carousel': return 'bg-blue-100 text-blue-800';
      case 'post': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPerformanceColor = (score) => {
    if (score >= 150) return 'bg-green-100 text-green-800';
    if (score >= 100) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-instagram-purple"></div>
      </div>
    );
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between mb-6">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            Media Posts
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Browse and analyze Instagram posts with enhanced metrics
          </p>
        </div>
      </div>

      {/* Profile Header */}
      {profileInfo && (
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <div className="flex items-center space-x-4">
            {profileInfo.profile_pic_url && (
              <img 
                src={profileInfo.profile_pic_url} 
                alt={profileInfo.full_name}
                className="w-16 h-16 rounded-full"
              />
            )}
            <div className="flex-1">
              <div className="flex items-center space-x-2">
                <h3 className="text-xl font-bold text-gray-900">{profileInfo.full_name}</h3>
                {profileInfo.is_verified && (
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    Verified ✓
                  </span>
                )}
                {profileInfo.is_business_account && (
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                    Business
                  </span>
                )}
              </div>
              <p className="text-gray-600">@{profileInfo.username}</p>
              {profileInfo.biography && (
                <p className="mt-2 text-sm text-gray-700">{profileInfo.biography}</p>
              )}
              <div className="mt-3 flex items-center space-x-6 text-sm">
                <div><span className="font-semibold">{profileInfo.follower_count?.toLocaleString()}</span> followers</div>
                <div><span className="font-semibold">{profileInfo.following_count?.toLocaleString()}</span> following</div>
                {profileInfo.avg_engagement_rate && (
                  <div><span className="font-semibold">{profileInfo.avg_engagement_rate.toFixed(2)}%</span> avg engagement</div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Summary Stats */}
      {summaryStats && (
        <div className="bg-white p-4 rounded-lg shadow mb-6">
          <h4 className="text-lg font-medium text-gray-900 mb-3">Summary Statistics</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-instagram-purple">{summaryStats.total_posts_returned}</div>
              <div className="text-sm text-gray-600">Posts Shown</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{summaryStats.likes_formatted}</div>
              <div className="text-sm text-gray-600">Total Likes</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{summaryStats.comments_formatted}</div>
              <div className="text-sm text-gray-600">Total Comments</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{summaryStats.engagement_formatted}</div>
              <div className="text-sm text-gray-600">Total Engagement</div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Username
            </label>
            <select
              value={filters.username}
              onChange={(e) => setFilters({...filters, username: e.target.value})}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
            >
              <option value="">Select Account</option>
              {usernames.map(username => (
                <option key={username} value={username}>{username}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Media Type
            </label>
            <select
              value={filters.mediaType}
              onChange={(e) => setFilters({...filters, mediaType: e.target.value})}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
            >
              <option value="">All Types</option>
              <option value="post">Post</option>
              <option value="reel">Reel</option>
              <option value="carousel">Carousel</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Sort By
            </label>
            <select
              value={filters.sortBy}
              onChange={(e) => setFilters({...filters, sortBy: e.target.value})}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
            >
              <option value="date">Latest First</option>
              <option value="engagement">Most Engaging</option>
              <option value="likes">Most Liked</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Limit
            </label>
            <select
              value={filters.limit}
              onChange={(e) => setFilters({...filters, limit: parseInt(e.target.value)})}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
            >
              <option value={25}>25 posts</option>
              <option value={50}>50 posts</option>
              <option value={100}>100 posts</option>
            </select>
          </div>
        </div>
      </div>

      {/* Posts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {posts.map((post) => (
          <div key={post.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
            {/* Post Header */}
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{getMediaTypeIcon(post)}</span>
                  <div>
                    <h3 className="font-semibold text-gray-900">{post.full_name}</h3>
                    <p className="text-sm text-gray-600">@{post.username}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getMediaTypeColor(post.media_type)}`}>
                    {post.media_type}
                  </span>
                  {post.performance_score > 0 && (
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPerformanceColor(post.performance_score)}`}>
                      {post.performance_score.toFixed(0)}%
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Post Content */}
            <div className="p-4">
              {post.caption && (
                <p className="text-gray-900 mb-3 text-sm leading-relaxed">
                  {post.caption_preview || (post.caption.length > 100 
                    ? `${post.caption.substring(0, 100)}...` 
                    : post.caption)}
                </p>
              )}

              {/* Hashtags Preview */}
              {post.hashtags && post.hashtags.length > 0 && (
                <div className="mb-3">
                  <div className="flex flex-wrap gap-1">
                    {post.hashtags.slice(0, 3).map((tag, index) => (
                      <span key={index} className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-50 text-blue-700">
                        #{tag}
                      </span>
                    ))}
                    {post.hashtags.length > 3 && (
                      <span className="text-xs text-gray-500">+{post.hashtags.length - 3} more</span>
                    )}
                  </div>
                </div>
              )}

              {/* Enhanced Metrics */}
              <div className="grid grid-cols-2 gap-3 mb-3">
                <div className="flex items-center text-gray-600">
                  <Heart className="w-4 h-4 mr-1 text-red-500" />
                  <span className="text-sm font-medium">{post.like_count_formatted || post.like_count?.toLocaleString()}</span>
                </div>
                <div className="flex items-center text-gray-600">
                  <MessageCircle className="w-4 h-4 mr-1 text-blue-500" />
                  <span className="text-sm font-medium">{post.comment_count_formatted || post.comment_count?.toLocaleString()}</span>
                </div>
                {post.save_count > 0 && (
                  <div className="flex items-center text-gray-600">
                    <Bookmark className="w-4 h-4 mr-1 text-yellow-500" />
                    <span className="text-sm font-medium">{post.save_count_formatted || post.save_count?.toLocaleString()}</span>
                  </div>
                )}
                {post.share_count > 0 && (
                  <div className="flex items-center text-gray-600">
                    <Share className="w-4 h-4 mr-1 text-green-500" />
                    <span className="text-sm font-medium">{post.share_count_formatted || post.share_count?.toLocaleString()}</span>
                  </div>
                )}
                {post.video_view_count > 0 && (
                  <div className="flex items-center text-gray-600">
                    <Eye className="w-4 h-4 mr-1 text-purple-500" />
                    <span className="text-sm font-medium">{post.video_view_count?.toLocaleString()}</span>
                  </div>
                )}
              </div>

              {/* Total Engagement */}
              <div className="mb-3 p-2 bg-gray-50 rounded-md">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Total Engagement</span>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-instagram-purple">
                      {post.total_engagement_formatted || post.total_engagement?.toLocaleString()}
                    </div>
                    {post.engagement_rate > 0 && (
                      <div className="text-xs text-gray-500">{post.engagement_rate}% rate</div>
                    )}
                  </div>
                </div>
              </div>

              {/* Post Info */}
              <div className="space-y-2 text-xs text-gray-500">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Calendar className="w-3 h-3 mr-1" />
                    {post.post_time_ago || formatDate(post.post_datetime_ist)}
                  </div>
                  {post.instagram_url && (
                    <a
                      href={post.instagram_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center text-instagram-purple hover:text-instagram-pink"
                    >
                      View Post
                      <ExternalLink className="w-3 h-3 ml-1" />
                    </a>
                  )}
                </div>

                {/* Location */}
                {post.location_name && (
                  <div className="flex items-center">
                    <MapPin className="w-3 h-3 mr-1" />
                    {post.location_name}
                  </div>
                )}

                {/* Collaboration */}
                {post.is_collab && post.collab_with && (
                  <div className="flex items-center">
                    <Users className="w-3 h-3 mr-1" />
                    Collaboration with: {post.collab_with}
                  </div>
                )}

                {/* Carousel Info */}
                {post.is_carousel && (
                  <div className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700">
                    Carousel ({post.carousel_media_count} items)
                  </div>
                )}

                {/* Sponsored/Ad indicators */}
                <div className="flex space-x-2">
                  {post.is_sponsored && (
                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-orange-100 text-orange-800">
                      Sponsored
                    </span>
                  )}
                  {post.is_ad && (
                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-800">
                      Ad
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {posts.length === 0 && filters.username && (
        <div className="text-center py-12">
          <div className="text-gray-500">
            No posts found for this account. Try fetching data first or adjust your filters.
          </div>
        </div>
      )}

      {/* No Username Selected */}
      {!filters.username && (
        <div className="text-center py-12">
          <div className="text-gray-500">
            Please select a username to view posts.
          </div>
        </div>
      )}
    </div>
  );
};

export default MediaPosts;
