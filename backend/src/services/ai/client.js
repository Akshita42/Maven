/**
 * src/services/ai/client.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * Low-level HTTP client for communicating with the Python AI Service.
 *
 * This file acts as the base gateway client. It manages timeouts,
 * request encapsulation, network headers, and error handling policies.
 *
 * ─── Why client.js? ────────────────────────────────────────────────────────
 * In a distributed microservice architecture, the Node.js backend acts as a
 * client of the Python service. Naming it "client" accurately reflects its
 * role: it handles standard HTTP transport concerns.
 *
 * This is different from the high-level orchestrator services (like
 * health.service.js) which handle application features.
 * ───────────────────────────────────────────────────────────────────────────
 */

import config from '../../config/index.js';
import { ERROR_CODES } from '../../constants/errorCodes.js';

class AiClient {
  constructor() {
    this.baseUrl = config.aiService.baseUrl;
    this.timeoutMs = config.aiService.timeoutMs;
  }

  /**
   * Internal helper to execute timed-out HTTP requests to the Python service.
   *
   * Uses native fetch and AbortController to enforce network timeouts.
   *
   * @param {string} path         - Route path (e.g. '/api/v1/health')
   * @param {object} [options={}] - Standard fetch options
   * @returns {Promise<any>}      - Parsed JSON response
   */
  async _request(path, options = {}) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeoutMs);

    const url = `${this.baseUrl}${path}`;
    const fetchOptions = {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, fetchOptions);
      clearTimeout(timeoutId);

      let payload;
      try {
        payload = await response.json();
      } catch (parseErr) {
        throw new Error('Invalid JSON payload returned from Python service.');
      }

      if (!response.ok) {
        const errMsg = payload?.error?.message || `HTTP error ${response.status}`;
        const errCode = payload?.error?.code || ERROR_CODES.INTERNAL_SERVER_ERROR;
        const err = new Error(errMsg);
        err.code = errCode;
        err.status = response.status;
        throw err;
      }

      return payload;
    } catch (err) {
      clearTimeout(timeoutId);

      if (err.name === 'AbortError') {
        const timeoutError = new Error('Connection to AI service timed out.');
        timeoutError.code = ERROR_CODES.AI_SERVICE_TIMEOUT;
        timeoutError.status = 504;
        throw timeoutError;
      }

      if (err.code) {
        throw err;
      }

      const connError = new Error('The Python AI service is unreachable or down.');
      connError.code = ERROR_CODES.AI_SERVICE_UNAVAILABLE;
      connError.status = 502;
      throw connError;
    }
  }

  /**
   * Fetches the health status of the Python AI service.
   *
   * Resolves to the data payload if healthy, or throws an error.
   *
   * @returns {Promise<{ service: string, version: string, status: string, uptime: number, timestamp: string }>}
   */
  async getHealth() {
    const response = await this._request('/api/v1/health');
    return response.data;
  }
}

export default new AiClient();
