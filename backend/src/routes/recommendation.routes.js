/**
 * src/routes/recommendation.routes.js
 *
 * Defines recommendation generation endpoints.
 */

import { Router } from 'express';
import { buildRecommendationController } from '../controllers/recommendation.controller.js';

const router = Router();

router.post('/build', buildRecommendationController);

export default router;
