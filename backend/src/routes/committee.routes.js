/**
 * src/routes/committee.routes.js
 *
 * Route mapping for investment committee API endpoints.
 */

import { Router } from 'express';
import { reviewThesisController } from '../controllers/committee.controller.js';

const router = Router();

// POST /review (Resolves to: POST /api/v1/committee/review when mounted)
router.post('/review', reviewThesisController);

export default router;
