// Shared service for managing profile data across components
import { analyticsAPI } from './api';

class ProfileService {
  constructor() {
    this.profiles = [];
    this.listeners = new Set();
    this.isLoading = false;
    this.lastFetchTime = 0;
  }

  // Get all profiles
  async fetchProfiles() {
    // Prevent excessive API calls and multiple simultaneous calls
    const now = Date.now();
    if (this.isLoading) {
      return this.profiles;
    }
    if (this.lastFetchTime && now - this.lastFetchTime < 5000) {
      return this.profiles;
    }
    
    this.isLoading = true;
    this.lastFetchTime = now;
    
    try {
      const response = await analyticsAPI.getProfiles();
      this.profiles = response.data.data;
      this.notifyListeners();
      return this.profiles;
    } catch (error) {
      console.error('Error fetching profiles:', error);
      return [];
    } finally {
      this.isLoading = false;
    }
  }

  // Get cached profiles or fetch if empty
  getProfiles() {
    if (this.profiles.length === 0) {
      this.fetchProfiles();
    }
    return this.profiles;
  }

  // Get profile usernames for dropdowns
  getUsernames() {
    return this.profiles.map(profile => profile.username);
  }

  // Subscribe to profile updates
  subscribe(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  // Notify all listeners of profile updates
  notifyListeners() {
    this.listeners.forEach(callback => callback(this.profiles));
  }

  // Update profiles after add/delete operations
  async updateProfiles() {
    await this.fetchProfiles();
  }
}

// Create singleton instance
export const profileService = new ProfileService();

// Listen for global profile updates
window.addEventListener('profilesUpdated', () => {
  profileService.updateProfiles();
});

window.addEventListener('dataFetched', () => {
  profileService.updateProfiles();
});
