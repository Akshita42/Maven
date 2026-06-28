/**
 * src/services/ai/critique.js
 *
 * Integration service for structured investment self-critique AI queries.
 */

import aiClient from './client.js';

/**
 * Triggers structured self-critique review for a thesis, committee review, or resolution payload.
 *
 * @param {object} payload - ResolverResult, EvidencePackage, InvestmentIntelligence, InvestmentThesis, or InvestmentCommitteeReview
 * @returns {Promise<{ status: string, data: object, meta: object }>}
 */
export const evaluateCritique = async (payload) => {
  const response = await aiClient._request('/api/v1/critique/evaluate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return response;
};
