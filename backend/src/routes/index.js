/**
 * src/routes/index.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * The root API router. All route groups are mounted here.
 *
 * ─── Why a root router instead of registering routes directly in app.js? ──
 * As Maven grows, we will have:
 *   /api/health     → health check
 *   /api/research   → company research (Phase 2+)
 *   /api/portfolio  → portfolio management (future)
 *   /api/sessions   → session management (future)
 *
 * If we registered each of these in app.js, that file would grow to hundreds
 * of lines and become a maintenance problem.
 *
 * The root router keeps app.js clean. app.js does one thing:
 *   app.use('/api', router);
 *
 * All route organisation lives in this file.
 *
 * ─── Adding a new route group ──────────────────────────────────────────────
 * 1. Create src/routes/research.routes.js
 * 2. Import it here: import researchRoutes from './research.routes.js'
 * 3. Mount it: router.use('/research', researchRoutes)
 * 4. Result: GET /api/research/... automatically works
 * ───────────────────────────────────────────────────────────────────────────
 */

import { Router } from 'express';
import healthRoutes from './health.routes.js';
import companyRoutes from './company.routes.js';
import evidenceRoutes from './evidence.routes.js';

const router = Router();

/**
 * Mount all route groups under their respective prefixes.
 * The full path is constructed as: /api + prefix + route
 *
 * Example: router.use('/health', healthRoutes)
 *          + healthRoutes has router.get('/')
 *          = GET /api/health
 */
router.use('/health', healthRoutes);
router.use('/v1/company', companyRoutes);
router.use('/v1/evidence', evidenceRoutes);

// Future route groups will be added below as phases are implemented:
// router.use('/research', researchRoutes);

export default router;
