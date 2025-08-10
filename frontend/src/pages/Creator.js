import React from 'react';
import ContentCreator from '../components/ContentCreator';

const Creator = ({ showNotification }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <h1 className="text-3xl font-bold text-gray-900">🎨 AI Content Creator</h1>
            <p className="mt-2 text-gray-600">
              Create engaging content with AI assistance. Generate posts, images, and videos with personalized analytics insights.
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-sm border min-h-[800px]">
          <ContentCreator showNotification={showNotification} />
        </div>
      </div>
    </div>
  );
};

export default Creator;
