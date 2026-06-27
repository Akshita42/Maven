/**
 * src/services/health.service.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * Aggregates health diagnostics across the entire Maven ecosystem.
 *
 * This service queries the local backend metadata and triggers a health check
 * call to the downstream Python AI service. It combines the answers into a
 * single, structured system status payload.
 *
 * ─── Degraded State Policy ──────────────────────────────────────────────────
 * If a critical downstream dependency (like the AI service) is down, the
 * backend MUST NOT throw an HTTP error or crash. Instead, it degrades its own
 * system status to 'degraded', records the downstream component state as
 * 'unavailable', and returns a 200 OK.
 *
 * This allows the client UI to notify users which features are unavailable
 * without crashing or returning unstyled raw error codes.
 * ───────────────────────────────────────────────────────────────────────────
 */

import config from '../config/index.js';
import { API } from '../constants/api.js';
import aiClient from './ai/client.js';

/**
 * Asynchronously gathers and merges health statuses of the backend and AI service.
 *
 * @returns {Promise<{
 *   status: 'healthy' | 'degraded',
 *   services: {
 *     backend: { status: string, version: string, uptime: number, timestamp: string },
 *     aiService: { status: string, version?: string, uptime?: number, timestamp?: string, reason?: string }
 *   }
 * }>}
 */
export const getHealthStatus = async () => {
  const backendHealth = {
    status: API.HEALTH_STATUS.HEALTHY,
    version: config.version,
    uptime: parseFloat(process.uptime().toFixed(3)),
    timestamp: new Date().toISOString(),
  };

  const services = {
    backend: backendHealth,
  };

  let systemStatus = API.HEALTH_STATUS.HEALTHY;

  try {
    // Query Python service health via the AI client abstraction
    const aiHealth = await aiClient.getHealth();

    services.aiService = {
      status: aiHealth.status,
      version: aiHealth.version,
      uptime: aiHealth.uptime,
      timestamp: aiHealth.timestamp,
    };
  } catch (err) {
    // Graceful degradation when the Python AI service fails
    systemStatus = API.HEALTH_STATUS.DEGRADED;

    services.aiService = {
      status: 'unavailable',
      reason: err.message || 'Connection refused or timed out',
    };
  }

  return {
    status: systemStatus,
    services,
  };
};
