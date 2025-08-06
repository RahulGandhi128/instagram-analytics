import React, { useState, useEffect } from 'react';
import { Users } from 'lucide-react';
import { getProxiedImageUrl } from '../utils/imageProxy';

const ProfilePicture = ({ profile, size = 'medium', className = '' }) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);
  const [currentViewport, setCurrentViewport] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const updateViewport = () => {
      setCurrentViewport({
        width: window.innerWidth,
        height: window.innerHeight
      });
    };
    
    updateViewport();
    window.addEventListener('resize', updateViewport);
    
    return () => window.removeEventListener('resize', updateViewport);
  }, []);

  // Reset states when profile changes
  useEffect(() => {
    setImageLoaded(false);
    setImageError(false);
  }, [profile.profile_pic_url]);

  const getSizeClasses = () => {
    switch (size) {
      case 'small':
        return 'w-10 h-10';
      case 'large':
        return 'w-20 h-20';
      case 'medium':
      default:
        return 'w-16 h-16';
    }
  };

  const getIconSize = () => {
    switch (size) {
      case 'small':
        return 'w-5 h-5';
      case 'large':
        return 'w-10 h-10';
      case 'medium':
      default:
        return 'w-8 h-8';
    }
  };

  const handleImageLoad = (e) => {
    console.log(`✅ ProfilePicture loaded for ${profile.username}`, {
      viewport: currentViewport,
      naturalSize: `${e.target.naturalWidth}x${e.target.naturalHeight}`,
      displaySize: size,
      src: e.target.src
    });
    setImageLoaded(true);
    setImageError(false);
  };

  const handleImageError = (e) => {
    console.error(`❌ ProfilePicture failed for ${profile.username}`, {
      viewport: currentViewport,
      src: e.target.src,
      error: e.nativeEvent
    });
    setImageLoaded(false);
    setImageError(true);
  };

  const baseClasses = `${getSizeClasses()} rounded-full border-2 border-white flex-shrink-0 ${className}`;

  if (!profile.profile_pic_url || imageError) {
    return (
      <div className={`${baseClasses} bg-white flex items-center justify-center relative`}>
        <Users className={`${getIconSize()} text-gray-400`} />
        <div className="absolute -bottom-1 -right-1 bg-yellow-500 text-white text-xs px-1 rounded">
          ?
        </div>
      </div>
    );
  }

  const proxiedUrl = getProxiedImageUrl(profile.profile_pic_url);

  return (
    <div className="relative">
      <img
        src={proxiedUrl}
        alt={profile.full_name || profile.username}
        className={`${baseClasses} object-cover`}
        onLoad={handleImageLoad}
        onError={handleImageError}
        style={{
          display: imageLoaded || !imageError ? 'block' : 'none'
        }}
      />
      
      {/* Fallback shown while loading or on error */}
      {(!imageLoaded && !imageError) && (
        <div className={`${baseClasses} bg-gray-200 flex items-center justify-center absolute top-0 left-0`}>
          <div className="animate-pulse">
            <Users className={`${getIconSize()} text-gray-400`} />
          </div>
        </div>
      )}

      {/* Error fallback */}
      {imageError && (
        <div className={`${baseClasses} bg-white flex items-center justify-center absolute top-0 left-0`}>
          <Users className={`${getIconSize()} text-gray-400`} />
          <div className="absolute -bottom-1 -right-1 bg-red-500 text-white text-xs px-1 rounded">
            !
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfilePicture;
