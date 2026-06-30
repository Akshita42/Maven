/**
 * src/controllers/report.controller.js
 *
 * Handles HTTP mapping for report generation queries.
 */

import { buildReport } from '../services/ai/report.js';
import { sendSuccess, sendError } from '../utils/response.js';
import { HTTP_STATUS } from '../constants/httpStatus.js';
import { ERROR_CODES } from '../constants/errorCodes.js';

export const buildReportController = async (req, res, next) => {
  try {
    const payload = req.body;

    if (!payload || !payload.evidence || !payload.intelligence || !payload.thesis || !payload.committee || !payload.critique || !payload.recommendation) {
      return sendError(res, {
        code: ERROR_CODES.VALIDATION_ERROR,
        message: 'Request validation failed. Payload must contain evidence, intelligence, thesis, committee, critique, and recommendation objects.',
      }, HTTP_STATUS.UNPROCESSABLE_ENTITY);
    }

    const { data, meta } = await buildReport(payload);
    return sendSuccess(res, data, meta);
  } catch (err) {
    next(err);
  }
};
