/**
 * src/routes/intelligence.routes.js
 *
 * Route mapping for intelligence API endpoints.
 */

import { Router } from 'express';
import { analyzeCompanyController } from '../controllers/intelligence.controller.js';

const router = Router();

// POST /analyze (Resolves to: POST /api/v1/intelligence/analyze when mounted)
router.post('/analyze', analyzeCompanyController);

export default router;
