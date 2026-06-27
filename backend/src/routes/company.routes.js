/**
 * src/routes/company.routes.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * Route mapping for company API endpoints.
 * ───────────────────────────────────────────────────────────────────────────
 */

import { Router } from 'express';
import { resolveCompanyController } from '../controllers/company.controller.js';

const router = Router();

// POST /resolve (Resolves to: POST /api/v1/company/resolve when mounted)
router.post('/resolve', resolveCompanyController);

export default router;
