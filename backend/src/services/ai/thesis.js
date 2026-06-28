/**
 * src/services/ai/thesis.js
 *
 * Integration service for structured investment thesis AI queries.
 */

import aiClient from './client.js';

/**
 * Triggers structured thesis generation for a company profile, evidence, or intelligence payload.
 *
 * @param {object} payload - ResolverResult, EvidencePackage, or InvestmentIntelligence
 * @returns {Promise<{ status: string, data: object, meta: object }>}
 */
export const buildThesis = async (payload) => {
  const response = await aiClient._request('/api/v1/thesis/build', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return response;
};
