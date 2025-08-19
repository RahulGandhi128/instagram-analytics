import React, { useState, useEffect } from 'react';
import { Download, RefreshCw, Database, Zap } from 'lucide-react';
import { starApiService } from '../services/starApiService';

const StarApiDataManager = ({ selectedUsername, onDataUpdated, showNotification }) => {
  const [collectionStatus, setCollectionStatus] = useState(null);
  const [collecting, setCollecting] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (selectedUsername) {
      fetchCollectionStatus();
    }
  }, [selectedUsername]);

  const fetchCollectionStatus = async () => {
    if (!selectedUsername) return;
    
    setLoading(true);
    try {
      const status = await starApiService.getDataCollectionStatus(selectedUsername);
      setCollectionStatus(status.data);
    } catch (error) {
      console.error('Error fetching collection status:', error);
      setCollectionStatus({ status: 'error', last_updated: null });
    } finally {
      setLoading(false);
    }
  };

  const triggerDataCollection = async () => {
    if (!selectedUsername) {
      showNotification('Please select a username first', 'error');
      return;
    }

    setCollecting(true);
    try {
      showNotification('Starting comprehensive data collection...', 'info');
      
      const result = await starApiService.collectUserData(selectedUsername);
      
      if (result.success) {
        showNotification('Data collection completed successfully!', 'success');
        await fetchCollectionStatus();
        onDataUpdated && onDataUpdated();
      } else {
        showNotification(`Data collection failed: ${result.error}`, 'error');
      }
    } catch (error) {
      console.error('Error collecting data:', error);
      showNotification('Error during data collection', 'error');
    } finally {
      setCollecting(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'collected': return 'text-green-600 bg-green-100';
      case 'profile_only': return 'text-yellow-600 bg-yellow-100';
      case 'not_collected': return 'text-red-600 bg-red-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'collected': return 'Data Available';
      case 'profile_only': return 'Profile Only';
      case 'not_collected': return 'Not Collected';
      case 'error': return 'Error';
      default: return 'Unknown';
    }
  };

  if (!selectedUsername) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex items-center">
          <Database className="w-5 h-5 text-blue-500 mr-2" />
          <span className="text-blue-700">Select a username to manage Star API data collection</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <Zap className="w-5 h-5 text-purple-500 mr-2" />
          <h3 className="text-lg font-semibold text-gray-900">Star API Data Collection</h3>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={fetchCollectionStatus}
            disabled={loading}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
            title="Refresh status"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          
          <button
            onClick={triggerDataCollection}
            disabled={collecting || loading}
            className="flex items-center px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {collecting ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                Collecting...
              </>
            ) : (
              <>
                <Download className="w-4 h-4 mr-2" />
                Collect Data
              </>
            )}
          </button>
        </div>
      </div>

      {collectionStatus && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Status Card */}
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm text-gray-600 mb-1">Collection Status</div>
            <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(collectionStatus.status)}`}>
              {getStatusText(collectionStatus.status)}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Last Updated: {formatDate(collectionStatus.last_updated)}
            </div>
          </div>

          {/* Data Counts */}
          {collectionStatus.data_counts && (
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-sm text-gray-600 mb-2">Data Collected</div>
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span>Media Posts:</span>
                  <span className="font-medium">{collectionStatus.data_counts.media_posts}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span>Stories:</span>
                  <span className="font-medium">{collectionStatus.data_counts.stories}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span>Highlights:</span>
                  <span className="font-medium">{collectionStatus.data_counts.highlights}</span>
                </div>
              </div>
            </div>
          )}

          {/* Profile Info */}
          {collectionStatus.profile_info && (
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-sm text-gray-600 mb-2">Profile Stats</div>
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span>Followers:</span>
                  <span className="font-medium">{collectionStatus.profile_info.follower_count?.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span>Following:</span>
                  <span className="font-medium">{collectionStatus.profile_info.following_count?.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span>Posts:</span>
                  <span className="font-medium">{collectionStatus.profile_info.media_count?.toLocaleString()}</span>
                </div>
                {collectionStatus.profile_info.is_verified && (
                  <div className="text-xs text-blue-600 font-medium">✓ Verified</div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {collecting && (
        <div className="mt-4 bg-purple-50 border border-purple-200 rounded-lg p-3">
          <div className="text-sm text-purple-700">
            Collecting comprehensive data from Star API. This includes profile info, media posts, stories, highlights, and engagement metrics.
          </div>
        </div>
      )}
    </div>
  );
};

export default StarApiDataManager;
