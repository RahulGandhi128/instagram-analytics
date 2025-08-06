import { useState, useEffect } from 'react';
import { profileService } from '../services/profileService';

export const useUsernames = () => {
  const [usernames, setUsernames] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Initial load
    const loadUsernames = async () => {
      setLoading(true);
      const profiles = await profileService.fetchProfiles();
      setUsernames(profiles.map(profile => profile.username));
      setLoading(false);
    };

    loadUsernames();

    // Subscribe to profile updates
    const unsubscribe = profileService.subscribe((profiles) => {
      setUsernames(profiles.map(profile => profile.username));
    });

    return unsubscribe;
  }, []);

  return { usernames, loading };
};
