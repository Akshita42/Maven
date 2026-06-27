/**
 * src/routes/health.routes.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * Defines the URL-to-controller mapping for the /health group of endpoints.
 *
 * ─── What a route file does ────────────────────────────────────────────────
 * Route files have ONE job: map HTTP method + path to a controller function.
 * No logic. No data transformation. Just wiring.
 *
 * ─── Express Router ────────────────────────────────────────────────────────
 * Router() creates a mini Express application that can be mounted at any
 * prefix by the parent router (see routes/index.js).
 *
 * When mounted at /health (in index.js), router.get('/') becomes
 * GET /api/health in the full application because:
 *   app.use('/api', router)        →  prefix /api
 *   router.use('/health', health)  →  prefix /api/health
 *   health.get('/')                →  GET /api/health
 *
 * ─── Future health routes ──────────────────────────────────────────────────
 * When we add Python health checking in Phase 2, it will be added here:
 *   router.get('/ai-service', checkAiServiceHealth);
 * ───────────────────────────────────────────────────────────────────────────
 */

import { Router } from 'express';
import { getHealth } from '../controllers/health.controller.js';

const router = Router();

/**
 * GET /api/health
 * Returns backend service health status.
 * This endpoint is intentionally unauthenticated — it must always be reachable
 * by load balancers, Docker healthchecks, and monitoring tools.
 */
router.get('/', getHealth);

export default router;
