/**
 * Image proxy utility to handle Instagram images through our backend proxy
 */

const imageProxy = (url, width = 300, height = 300) => {
  if (!url) return null;
  
  // If it's already a placeholder, return as is
  if (url.includes('via.placeholder.com')) {
    return url;
  }
  
  // If it's a relative URL or local URL, return as is
  if (url.startsWith('/') || url.startsWith('http://localhost') || url.startsWith('https://localhost')) {
    return url;
  }
  
  // For external URLs, use placeholder service
  return `https://via.placeholder.com/${width}x${height}/1a1a1a/ffffff?text=Instagram+Post+${Math.random().toString(36).substring(7)}`;
};

export default imageProxy;
