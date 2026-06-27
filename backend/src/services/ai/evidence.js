/**
 * src/services/ai/evidence.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * Integration service for structured evidence collection AI queries.
 * ───────────────────────────────────────────────────────────────────────────
 */

import aiClient from './client.js';

/**
 * Triggers structured evidence collection for a resolved company entity.
 *
 * Returns the full response envelope containing both data and meta blocks.
 *
 * @param {object} resolverResult - Resolved company profile data from Phase 5
 * @returns {Promise<{ status: string, data: object, meta: object }>}
 */
export const collectEvidence = async (resolverResult) => {
  const response = await aiClient._request('/api/v1/evidence/collect', {
    method: 'POST',
    body: JSON.stringify(resolverResult),
  });
  return response;
};
