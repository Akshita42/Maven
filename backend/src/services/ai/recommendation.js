/**
 * src/services/ai/recommendation.js
 *
 * Integration service for the final recommendation synthesis layer.
 */

import aiClient from './client.js';

/**
 * Triggers recommendation synthesis from upstream components.
 *
 * @param {object} payload - Must contain { thesis, review, critique }
 * @returns {Promise<{ status: string, data: object }>}
 */
export const buildRecommendation = async (payload) => {
  const response = await aiClient._request('/api/v1/recommendation/build', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return response;
};
