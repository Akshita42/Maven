/**
 * src/services/ai/committee.js
 *
 * Integration service for structured investment committee review AI queries.
 */

import aiClient from './client.js';

/**
 * Triggers structured committee review for a company profile, evidence, thesis or intelligence payload.
 *
 * @param {object} payload - ResolverResult, EvidencePackage, InvestmentIntelligence, or InvestmentThesis
 * @returns {Promise<{ status: string, data: object, meta: object }>}
 */
export const reviewThesis = async (payload) => {
  const response = await aiClient._request('/api/v1/committee/review', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return response;
};
