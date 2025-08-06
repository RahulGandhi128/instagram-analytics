import React, { useState, useEffect, useCallback } from 'react';
import { Users, CheckCircle, Lock, ExternalLink, Verified, Plus, Trash2, AlertCircle } from 'lucide-react';
import { analyticsAPI } from '../services/api';

const Profiles = ({ showNotification }) => {
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newUsername, setNewUsername] = useState('');
  const [addingProfile, setAddingProfile] = useState(false);
  const [deletingProfile, setDeletingProfile] = useState(null);

  const fetchProfiles = useCallback(async () => {
    setLoading(true);
    try {
      const response = await analyticsAPI.getProfiles();
      setProfiles(response.data.data);
    } catch (error) {
      showNotification('Error loading profiles', 'error');
    } finally {
      setLoading(false);
    }
  }, [showNotification]);

  useEffect(() => {
    fetchProfiles();
  }, [fetchProfiles]);

  const fetchInstagramData = async () => {
    try {
      showNotification('Fetching Instagram data... This may take a few minutes', 'info');
      const response = await fetch('http://localhost:5000/api/fetch-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      
      if (data.success) {
        showNotification('Instagram data fetched successfully!', 'success');
        await fetchProfiles(); // Refresh profiles after fetching data
      } else {
        showNotification(`Error: ${data.error}`, 'error');
      }
    } catch (error) {
      showNotification('Error fetching Instagram data', 'error');
    }
  };

  const addProfile = async () => {
    if (!newUsername.trim()) {
      showNotification('Please enter a username', 'error');
      return;
    }

    setAddingProfile(true);
    try {
      const response = await fetch('http://localhost:5000/api/profiles', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: newUsername.trim()
        }),
      });
      const data = await response.json();
      
      if (data.success) {
        showNotification(data.message, 'success');
        setNewUsername('');
        setShowAddModal(false);
        await fetchProfiles(); // Refresh profiles after adding
      } else {
        showNotification(`Error: ${data.error}`, 'error');
      }
    } catch (error) {
      showNotification('Error adding profile', 'error');
    } finally {
      setAddingProfile(false);
    }
  };

  const deleteProfile = async (username) => {
    if (!window.confirm(`Are you sure you want to delete ${username} and all associated data? This action cannot be undone.`)) {
      return;
    }

    setDeletingProfile(username);
    try {
      const response = await fetch(`http://localhost:5000/api/profiles/${username}`, {
        method: 'DELETE',
      });
      const data = await response.json();
      
      if (data.success) {
        showNotification(data.message, 'success');
        await fetchProfiles(); // Refresh profiles after deleting
      } else {
        showNotification(`Error: ${data.error}`, 'error');
      }
    } catch (error) {
      showNotification('Error deleting profile', 'error');
    } finally {
      setDeletingProfile(null);
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    }
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toLocaleString();
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
            Profiles
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Overview of all tracked Instagram accounts
          </p>
        </div>
        <div className="mt-4 flex md:mt-0 md:ml-4 space-x-3">
          <button
            onClick={() => setShowAddModal(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Profile
          </button>
          <button
            onClick={fetchInstagramData}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-instagram-purple hover:bg-instagram-pink focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-instagram-purple"
          >
            <Users className="w-4 h-4 mr-2" />
            Fetch Instagram Data
          </button>
          <button
            onClick={fetchProfiles}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <Users className="w-4 h-4 mr-2" />
            Refresh Profiles
          </button>
        </div>
      </div>

      {/* Profiles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {profiles.map((profile) => (
          <div key={profile.username} className="bg-white rounded-lg shadow-md overflow-hidden">
            {/* Profile Header */}
            <div className="p-6 bg-gradient-to-r from-instagram-pink to-instagram-purple">
              <div className="flex items-center">
                {profile.profile_pic_url ? (
                  <img
                    src={profile.profile_pic_url}
                    alt={profile.full_name}
                    className="w-16 h-16 rounded-full border-2 border-white object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'flex';
                    }}
                  />
                ) : null}
                <div 
                  className={`w-16 h-16 rounded-full bg-white flex items-center justify-center ${profile.profile_pic_url ? 'hidden' : 'flex'}`}
                  style={{ display: profile.profile_pic_url ? 'none' : 'flex' }}
                >
                  <Users className="w-8 h-8 text-gray-400" />
                </div>
                <div className="ml-4 flex-1">
                  <div className="flex items-center">
                    <h3 className="text-lg font-semibold text-white truncate">
                      {profile.full_name || profile.username}
                    </h3>
                    {profile.is_verified && (
                      <Verified className="w-5 h-5 ml-2 text-blue-400" />
                    )}
                  </div>
                  <p className="text-sm text-white opacity-90">
                    @{profile.username}
                  </p>
                </div>
              </div>
            </div>

            {/* Profile Stats */}
            <div className="p-6">
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center">
                  <div className="text-lg font-semibold text-gray-900">
                    {formatNumber(profile.follower_count)}
                  </div>
                  <div className="text-xs text-gray-500">Followers</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-gray-900">
                    {formatNumber(profile.following_count)}
                  </div>
                  <div className="text-xs text-gray-500">Following</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-gray-900">
                    {formatNumber(profile.media_count)}
                  </div>
                  <div className="text-xs text-gray-500">Posts</div>
                </div>
              </div>

              {/* Biography */}
              {profile.biography && (
                <div className="mb-4">
                  <p className="text-sm text-gray-600 leading-relaxed">
                    {profile.biography.length > 100 
                      ? `${profile.biography.substring(0, 100)}...` 
                      : profile.biography
                    }
                  </p>
                </div>
              )}

              {/* Account Status */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  {profile.is_verified && (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Verified
                    </span>
                  )}
                  {profile.is_private && (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                      <Lock className="w-3 h-3 mr-1" />
                      Private
                    </span>
                  )}
                </div>
              </div>

              {/* Engagement Rate */}
              {profile.follower_count > 0 && (
                <div className="bg-gray-50 rounded-lg p-3 mb-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Engagement Rate</span>
                    <span className="text-sm font-medium text-instagram-purple">
                      {profile.engagement_rate !== undefined 
                        ? `${profile.engagement_rate}%` 
                        : 'Calculating...'
                      }
                    </span>
                  </div>
                  <div className="mt-1">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-instagram-pink to-instagram-purple h-2 rounded-full"
                        style={{ 
                          width: profile.engagement_rate ? `${Math.min(profile.engagement_rate * 10, 100)}%` : '0%' 
                        }}
                      ></div>
                    </div>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="space-y-3">
                <a
                  href={`https://instagram.com/${profile.username}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-instagram-purple hover:bg-instagram-pink focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-instagram-purple"
                >
                  View on Instagram
                  <ExternalLink className="w-4 h-4 ml-2" />
                </a>
                
                <button
                  onClick={() => deleteProfile(profile.username)}
                  disabled={deletingProfile === profile.username}
                  className="w-full inline-flex items-center justify-center px-4 py-2 border border-red-300 text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
                >
                  {deletingProfile === profile.username ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-700 mr-2"></div>
                      Deleting...
                    </>
                  ) : (
                    <>
                      <Trash2 className="w-4 h-4 mr-2" />
                      Delete Profile
                    </>
                  )}
                </button>
              </div>

              {/* Last Updated */}
              {profile.last_updated && (
                <div className="mt-3 text-xs text-gray-500 text-center">
                  Last updated: {new Date(profile.last_updated).toLocaleDateString('en-IN', { 
                    timeZone: 'Asia/Kolkata',
                    year: 'numeric',
                    month: 'short', 
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })} IST
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {profiles.length === 0 && (
        <div className="text-center py-12">
          <Users className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No profiles found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by fetching profile data from Instagram.
          </p>
          <div className="mt-6">
            <button
              onClick={fetchProfiles}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-instagram-purple hover:bg-instagram-pink focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-instagram-purple"
            >
              <Users className="w-4 h-4 mr-2" />
              Refresh Profiles
            </button>
          </div>
        </div>
      )}

      {/* Add Profile Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Add New Profile</h3>
                <button
                  onClick={() => setShowAddModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                </button>
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Instagram Username
                </label>
                <input
                  type="text"
                  value={newUsername}
                  onChange={(e) => setNewUsername(e.target.value)}
                  placeholder="Enter Instagram username (without @)"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-instagram-purple focus:border-instagram-purple"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      addProfile();
                    }
                  }}
                />
                <p className="mt-1 text-xs text-gray-500">
                  Example: naukridotcom, swiggyindia, zomato
                </p>
              </div>

              <div className="flex items-center space-x-3">
                <button
                  onClick={addProfile}
                  disabled={addingProfile || !newUsername.trim()}
                  className="flex-1 inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-instagram-purple hover:bg-instagram-pink focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-instagram-purple disabled:opacity-50"
                >
                  {addingProfile ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Adding...
                    </>
                  ) : (
                    <>
                      <Plus className="w-4 h-4 mr-2" />
                      Add Profile
                    </>
                  )}
                </button>
                <button
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-instagram-purple"
                >
                  Cancel
                </button>
              </div>

              <div className="mt-4 p-3 bg-blue-50 rounded-md">
                <div className="flex">
                  <AlertCircle className="w-5 h-5 text-blue-400 mr-2 mt-0.5" />
                  <div className="text-sm text-blue-800">
                    <p className="font-medium">Note:</p>
                    <p>Adding a profile will automatically fetch its data from Instagram. This may take a few moments.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profiles;
