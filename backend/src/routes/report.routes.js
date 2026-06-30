/**
 * src/routes/report.routes.js
 *
 * Defines report generation endpoints.
 */

import { Router } from 'express';
import { buildReportController } from '../controllers/report.controller.js';

const router = Router();

router.post('/build', buildReportController);

export default router;
