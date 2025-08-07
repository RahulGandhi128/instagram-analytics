/**
 * Chatbot API Service
 * Handles communication with the analytics chatbot backend
 */

const API_BASE_URL = 'http://localhost:5000/api';

export const chatbotAPI = {
  /**
   * Send a message to the chatbot
   * @param {string} message - The user's message
   * @param {string} sessionId - Session ID for conversation continuity
   * @param {string} username - Optional username filter for analytics
   * @param {number} days - Time period for analytics (default: 30)
   */
  sendMessage: async (message, sessionId, username = null, days = 30) => {
    const response = await fetch(`${API_BASE_URL}/chatbot/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        username,
        days
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  /**
   * Get conversation history for a session
   * @param {string} sessionId - Session ID
   */
  getHistory: async (sessionId) => {
    const response = await fetch(`${API_BASE_URL}/chatbot/history/${sessionId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  /**
   * Clear conversation history for a session
   * @param {string} sessionId - Session ID
   */
  clearHistory: async (sessionId) => {
    const response = await fetch(`${API_BASE_URL}/chatbot/clear/${sessionId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  /**
   * Get the analytics context that the chatbot uses
   * @param {string} username - Optional username filter
   * @param {number} days - Time period for analytics
   */
  getAnalyticsContext: async (username = null, days = 30) => {
    const params = new URLSearchParams();
    if (username) params.append('username', username);
    params.append('days', days.toString());

    const response = await fetch(`${API_BASE_URL}/chatbot/analytics-context?${params}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
};

export default chatbotAPI;
