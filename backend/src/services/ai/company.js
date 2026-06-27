/**
 * src/services/ai/company.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * Integration service for company-related AI Service queries.
 *
 * Exposes functions to communicate with Python's company resolver endpoints.
 * ───────────────────────────────────────────────────────────────────────────
 */

import aiClient from './client.js';

/**
 * Resolves a raw search input to a canonical company profile via Python.
 *
 * Returns the full response envelope containing both data and meta blocks.
 *
 * @param {string} companyName - User search query or ticker symbol
 * @returns {Promise<{ status: string, data: object, meta: object }>}
 */
export const resolveCompany = async (companyName) => {
  const response = await aiClient._request('/api/v1/company/resolve', {
    method: 'POST',
    body: JSON.stringify({ company: companyName }),
  });
  return response;
};
