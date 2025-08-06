// Shared service for managing profile data across components
import { analyticsAPI } from './api';

class ProfileService {
  constructor() {
    this.profiles = [];
    this.listeners = new Set();
  }

  // Get all profiles
  async fetchProfiles() {
    try {
      const response = await analyticsAPI.getProfiles();
      this.profiles = response.data.data;
      this.notifyListeners();
      return this.profiles;
    } catch (error) {
      console.error('Error fetching profiles:', error);
      return [];
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

// Initialize profiles on service creation
profileService.fetchProfiles();

// Listen for global profile updates
window.addEventListener('profilesUpdated', () => {
  profileService.updateProfiles();
});

window.addEventListener('dataFetched', () => {
  profileService.updateProfiles();
});
