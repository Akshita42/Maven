/**
 * src/services/ai/intelligence.js
 *
 * Integration service for structured investment intelligence AI queries.
 */

import aiClient from './client.js';

/**
 * Triggers structured intelligence evaluation for a resolved company or evidence package.
 *
 * @param {object} payload - ResolverResult or EvidencePackage
 * @returns {Promise<{ status: string, data: object, meta: object }>}
 */
export const analyzeCompany = async (payload) => {
  const response = await aiClient._request('/api/v1/intelligence/analyze', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return response;
};
