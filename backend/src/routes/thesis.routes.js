/**
 * src/routes/thesis.routes.js
 *
 * Route mapping for investment thesis API endpoints.
 */

import { Router } from 'express';
import { buildThesisController } from '../controllers/thesis.controller.js';

const router = Router();

// POST /build (Resolves to: POST /api/v1/thesis/build when mounted)
router.post('/build', buildThesisController);

export default router;
