/**
 * src/controllers/health.controller.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * Handles HTTP request mapping for health check routes.
 *
 * Asynchronously awaits health statuses and wraps them in the success envelope.
 * ───────────────────────────────────────────────────────────────────────────
 */

import { getHealthStatus } from '../services/health.service.js';
import { sendSuccess } from '../utils/response.js';

/**
 * GET /api/health
 *
 * Returns the combined health status of backend and downstream services.
 * Must be unauthenticated for monitoring tools and liveness checks.
 *
 * @param {import('express').Request}    req
 * @param {import('express').Response}   res
 * @param {import('express').NextFunction} next
 */
export const getHealth = async (req, res, next) => {
  try {
    const healthData = await getHealthStatus();
    
    // Send standard success envelope enclosing the service status mapping
    return sendSuccess(res, healthData);
  } catch (err) {
    // Forward unexpected exceptions to the centralized error middleware
    next(err);
  }
};
