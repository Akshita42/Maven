/**
 * src/controllers/health.controller.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * Handles the HTTP layer for the health check endpoint.
 *
 * ─── Controller responsibilities ───────────────────────────────────────────
 *   ✓  Receive the HTTP request (req)
 *   ✓  Extract any needed params/body/query from the request
 *   ✓  Call the appropriate service
 *   ✓  Return the HTTP response (res)
 *
 *   ✗  No business logic
 *   ✗  No direct database calls
 *   ✗  No direct calls to external services
 *
 * ─── Why keep controllers thin? ────────────────────────────────────────────
 * The controller is the boundary between HTTP and your application logic.
 * Keeping it thin means:
 *   - Services are testable without an HTTP server running
 *   - Swapping Express for another framework (Fastify, Hapi) only
 *     requires rewriting controllers, not services
 *
 * ─── Error handling in controllers ─────────────────────────────────────────
 * For synchronous functions like this one, Express catches thrown errors.
 * For async controllers, always wrap in try/catch and call next(err).
 * We demonstrate the async pattern here even though this handler is sync,
 * as a template for future controllers.
 * ───────────────────────────────────────────────────────────────────────────
 */

import { getHealthStatus } from '../services/health.service.js';
import { sendSuccess } from '../utils/response.js';

/**
 * GET /api/health
 *
 * Returns the health status of the backend service.
 * This endpoint must always respond — it should never be behind auth.
 *
 * @param {import('express').Request}  req
 * @param {import('express').Response} res
 * @param {import('express').NextFunction} next
 */
export const getHealth = (req, res, next) => {
  try {
    const healthData = getHealthStatus();
    return sendSuccess(res, healthData);
  } catch (err) {
    // Forward unexpected errors to the centralised error handler
    next(err);
  }
};
