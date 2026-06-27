/**
 * src/routes/evidence.routes.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * Route mapping for evidence API endpoints.
 * ───────────────────────────────────────────────────────────────────────────
 */

import { Router } from 'express';
import { collectEvidenceController } from '../controllers/evidence.controller.js';

const router = Router();

// POST /collect (Resolves to: POST /api/v1/evidence/collect when mounted)
router.post('/collect', collectEvidenceController);

export default router;
