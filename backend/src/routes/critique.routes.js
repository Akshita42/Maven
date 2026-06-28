/**
 * src/routes/critique.routes.js
 *
 * Route mapping for investment self-critique API endpoints.
 */

import { Router } from 'express';
import { evaluateCritiqueController } from '../controllers/critique.controller.js';

const router = Router();

// POST /evaluate (Resolves to: POST /api/v1/critique/evaluate when mounted)
router.post('/evaluate', evaluateCritiqueController);

export default router;
