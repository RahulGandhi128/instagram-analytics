/**
 * Image proxy utility to handle Instagram images through our backend proxy
 */

const API_BASE_URL = 'http://localhost:5000/api';

/**
 * Convert Instagram image URL to proxy URL to bypass CORS
 * @param {string} originalUrl - The original Instagram image URL
 * @returns {string} - The proxied image URL through our backend
 */
export const getProxiedImageUrl = (originalUrl) => {
  if (!originalUrl) return null;
  
  // Check if it's already a proxied URL
  if (originalUrl.includes('/api/proxy/image')) {
    return originalUrl;
  }
  
  // Only proxy Instagram URLs
  if (!originalUrl.includes('instagram.com') && !originalUrl.includes('cdninstagram.com')) {
    return originalUrl;
  }
  
  // Create the proxy URL
  const encodedUrl = encodeURIComponent(originalUrl);
  return `${API_BASE_URL}/proxy/image?url=${encodedUrl}`;
};

/**
 * Create a fallback image component with error handling
 * @param {object} props - Image component props
 * @returns {object} - Enhanced image props with error handling
 */
export const createImageWithFallback = (props) => {
  const { src, onError, onLoad, ...otherProps } = props;
  
  return {
    ...otherProps,
    src: getProxiedImageUrl(src),
    onError: (e) => {
      console.error('Image failed to load:', {
        originalSrc: src,
        proxiedSrc: getProxiedImageUrl(src),
        error: e
      });
      
      // Call the original onError handler if provided
      if (onError) {
        onError(e);
      }
    },
    onLoad: (e) => {
      console.log('Image loaded successfully:', {
        originalSrc: src,
        proxiedSrc: getProxiedImageUrl(src)
      });
      
      // Call the original onLoad handler if provided
      if (onLoad) {
        onLoad(e);
      }
    }
  };
};

export default {
  getProxiedImageUrl,
  createImageWithFallback
};
