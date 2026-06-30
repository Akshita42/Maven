/**
 * src/services/ai/report.js
 *
 * Integration service for the final report compiler.
 */

import aiClient from './client.js';

/**
 * Triggers report compilation from all upstream components.
 *
 * @param {object} payload - Must contain { evidence, intelligence, thesis, committee, critique, recommendation }
 * @returns {Promise<{ status: string, data: object }>}
 */
export const buildReport = async (payload) => {
  const response = await aiClient._request('/api/v1/report/build', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return response;
};
