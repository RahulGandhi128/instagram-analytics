import React, { useState, useEffect } from 'react';
import { X, Info, AlertTriangle, CheckCircle, Clock, Database, Users, Image, MessageCircle, BookOpen, Star } from 'lucide-react';

const DataCollectionDialog = ({ isOpen, onClose, onStartCollection, username }) => {
  const [selectedDataTypes, setSelectedDataTypes] = useState({
    profile: true,
    media_posts: true,
    comments: true,
    stories: false,
    highlights: false,
    followers: false,
    following: false,
    similar_accounts: false
  });
  
  const [limits, setLimits] = useState({
    media_posts: 50,
    comments_per_post: 20,
    stories: 20,
    highlights: 10,
    followers: 100,
    following: 100
  });

  const [estimatedCalls, setEstimatedCalls] = useState(0);
  const [estimatedTime, setEstimatedTime] = useState(0);

  // Calculate API calls based on selections and limits
  useEffect(() => {
    let totalCalls = 0;
    let totalTime = 0;

    // Base calls
    if (selectedDataTypes.profile) {
      totalCalls += 1;
      totalTime += 2;
    }

    if (selectedDataTypes.media_posts) {
      totalCalls += 1; // One call for media posts
      totalTime += 3;
    }

    if (selectedDataTypes.comments && selectedDataTypes.media_posts) {
      // Comments require one call per post
      totalCalls += Math.min(limits.media_posts, 50); // Max 50 posts for comments
      totalTime += Math.min(limits.media_posts, 50) * 2; // 2 seconds per comment call
    }

    if (selectedDataTypes.stories) {
      totalCalls += 1;
      totalTime += 2;
    }

    if (selectedDataTypes.highlights) {
      totalCalls += 1;
      totalTime += 2;
    }

    if (selectedDataTypes.followers) {
      totalCalls += 1;
      totalTime += 3;
    }

    if (selectedDataTypes.following) {
      totalCalls += 1;
      totalTime += 3;
    }

    if (selectedDataTypes.similar_accounts) {
      totalCalls += 1;
      totalTime += 2;
    }

    setEstimatedCalls(totalCalls);
    setEstimatedTime(totalTime);
  }, [selectedDataTypes, limits]);

  const dataTypes = [
    {
      key: 'profile',
      label: 'Profile Information',
      description: 'Basic profile data (username, followers, bio, verification status)',
      icon: Users,
      defaultCalls: 1,
      color: 'bg-blue-50 text-blue-700'
    },
    {
      key: 'media_posts',
      label: 'Media Posts',
      description: `Instagram posts, reels, and carousels (up to ${limits.media_posts} posts)`,
      icon: Image,
      defaultCalls: 1,
      color: 'bg-green-50 text-green-700'
    },
    {
      key: 'comments',
      label: 'Post Comments',
      description: `Comments on posts (up to ${limits.comments_per_post} comments per post)`,
      icon: MessageCircle,
      defaultCalls: limits.media_posts,
      color: 'bg-purple-50 text-purple-700',
      dependsOn: 'media_posts'
    },
    {
      key: 'stories',
      label: 'Stories',
      description: `Recent stories (up to ${limits.stories} stories)`,
      icon: BookOpen,
      defaultCalls: 1,
      color: 'bg-orange-50 text-orange-700'
    },
    {
      key: 'highlights',
      label: 'Highlights',
      description: `Story highlights (up to ${limits.highlights} highlights)`,
      icon: Star,
      defaultCalls: 1,
      color: 'bg-yellow-50 text-yellow-700'
    },
    {
      key: 'followers',
      label: 'Followers Sample',
      description: `Sample of followers (up to ${limits.followers} followers)`,
      icon: Users,
      defaultCalls: 1,
      color: 'bg-indigo-50 text-indigo-700'
    },
    {
      key: 'following',
      label: 'Following Sample',
      description: `Sample of accounts they follow (up to ${limits.following} accounts)`,
      icon: Users,
      defaultCalls: 1,
      color: 'bg-pink-50 text-pink-700'
    },
    {
      key: 'similar_accounts',
      label: 'Similar Accounts',
      description: 'Accounts similar to this profile',
      icon: Star,
      defaultCalls: 1,
      color: 'bg-teal-50 text-teal-700'
    }
  ];

  const handleDataTypeToggle = (key) => {
    setSelectedDataTypes(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const handleLimitChange = (key, value) => {
    setLimits(prev => ({
      ...prev,
      [key]: parseInt(value) || 0
    }));
  };

  const handleStartCollection = () => {
    const collectionConfig = {
      username,
      dataTypes: selectedDataTypes,
      limits,
      estimatedCalls,
      estimatedTime
    };
    onStartCollection(collectionConfig);
    onClose();
  };

  const getRiskLevel = () => {
    if (estimatedCalls <= 10) return { level: 'low', color: 'text-green-600', bg: 'bg-green-50' };
    if (estimatedCalls <= 50) return { level: 'medium', color: 'text-yellow-600', bg: 'bg-yellow-50' };
    return { level: 'high', color: 'text-red-600', bg: 'bg-red-50' };
  };

  const riskLevel = getRiskLevel();

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Data Collection Configuration</h2>
            <p className="text-gray-600 mt-1">Configure what data to collect for @{username}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* API Call Estimation */}
        <div className="p-6 border-b border-gray-200">
          <div className={`p-4 rounded-lg ${riskLevel.bg}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <AlertTriangle className={`w-5 h-5 ${riskLevel.color}`} />
                <div>
                  <h3 className={`font-semibold ${riskLevel.color}`}>
                    API Call Estimation
                  </h3>
                  <p className="text-sm text-gray-600">
                    Risk Level: <span className={`font-medium ${riskLevel.color}`}>{riskLevel.level.toUpperCase()}</span>
                  </p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-gray-900">{estimatedCalls}</div>
                <div className="text-sm text-gray-600">API calls</div>
              </div>
            </div>
            
            <div className="mt-4 grid grid-cols-2 gap-4">
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-gray-500" />
                <span className="text-sm text-gray-600">
                  Estimated time: {Math.ceil(estimatedTime / 60)} minutes
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <Database className="w-4 h-4 text-gray-500" />
                <span className="text-sm text-gray-600">
                  Data size: ~{Math.round(estimatedCalls * 0.5)} MB
                </span>
              </div>
            </div>

            {estimatedCalls > 200 && (
              <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="w-4 h-4 text-red-600" />
                  <span className="text-sm text-red-700 font-medium">
                    High API usage detected. Consider reducing limits to stay within rate limits.
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Data Type Selection */}
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Data Types</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {dataTypes.map((dataType) => {
              const Icon = dataType.icon;
              const isDisabled = dataType.dependsOn && !selectedDataTypes[dataType.dependsOn];
              
              return (
                <div
                  key={dataType.key}
                  className={`p-4 border rounded-lg cursor-pointer transition-all ${
                    selectedDataTypes[dataType.key]
                      ? 'border-instagram-purple bg-instagram-purple/5'
                      : 'border-gray-200 hover:border-gray-300'
                  } ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''}`}
                  onClick={() => !isDisabled && handleDataTypeToggle(dataType.key)}
                >
                  <div className="flex items-start space-x-3">
                    <div className={`p-2 rounded-lg ${dataType.color}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium text-gray-900">{dataType.label}</h4>
                        <input
                          type="checkbox"
                          checked={selectedDataTypes[dataType.key]}
                          onChange={() => !isDisabled && handleDataTypeToggle(dataType.key)}
                          className="rounded border-gray-300 text-instagram-purple focus:ring-instagram-purple"
                          disabled={isDisabled}
                        />
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{dataType.description}</p>
                      <div className="flex items-center space-x-2 mt-2">
                        <span className="text-xs text-gray-500">API calls:</span>
                        <span className="text-xs font-medium text-gray-700">{dataType.defaultCalls}</span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Limits Configuration */}
        <div className="p-6 border-t border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Limits</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Media Posts
              </label>
              <select
                value={limits.media_posts}
                onChange={(e) => handleLimitChange('media_posts', e.target.value)}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
              >
                <option value={25}>25 posts</option>
                <option value={50}>50 posts</option>
                <option value={100}>100 posts</option>
                <option value={200}>200 posts</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Comments per Post
              </label>
              <select
                value={limits.comments_per_post}
                onChange={(e) => handleLimitChange('comments_per_post', e.target.value)}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
              >
                <option value={10}>10 comments</option>
                <option value={20}>20 comments</option>
                <option value={50}>50 comments</option>
                <option value={100}>100 comments</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Stories
              </label>
              <select
                value={limits.stories}
                onChange={(e) => handleLimitChange('stories', e.target.value)}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
              >
                <option value={10}>10 stories</option>
                <option value={20}>20 stories</option>
                <option value={50}>50 stories</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Highlights
              </label>
              <select
                value={limits.highlights}
                onChange={(e) => handleLimitChange('highlights', e.target.value)}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
              >
                <option value={5}>5 highlights</option>
                <option value={10}>10 highlights</option>
                <option value={20}>20 highlights</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Followers Sample
              </label>
              <select
                value={limits.followers}
                onChange={(e) => handleLimitChange('followers', e.target.value)}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
              >
                <option value={50}>50 followers</option>
                <option value={100}>100 followers</option>
                <option value={200}>200 followers</option>
                <option value={500}>500 followers</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Following Sample
              </label>
              <select
                value={limits.following}
                onChange={(e) => handleLimitChange('following', e.target.value)}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-instagram-purple focus:ring-instagram-purple"
              >
                <option value={50}>50 following</option>
                <option value={100}>100 following</option>
                <option value={200}>200 following</option>
                <option value={500}>500 following</option>
              </select>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Info className="w-4 h-4" />
            <span>Data collection may take several minutes depending on the amount selected.</span>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleStartCollection}
              disabled={estimatedCalls === 0}
              className="px-6 py-2 bg-instagram-purple text-white rounded-md hover:bg-instagram-pink transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              <CheckCircle className="w-4 h-4" />
              <span>Start Collection ({estimatedCalls} calls)</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataCollectionDialog;
