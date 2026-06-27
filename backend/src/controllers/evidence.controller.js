/**
 * src/controllers/evidence.controller.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * Handles HTTP mapping for company evidence collection queries.
 *
 * Validates request input and forwards queries to the Python AI service.
 * ───────────────────────────────────────────────────────────────────────────
 */

import { collectEvidence } from '../services/ai/evidence.js';
import { sendSuccess, sendError } from '../utils/response.js';
import { HTTP_STATUS } from '../constants/httpStatus.js';
import { ERROR_CODES } from '../constants/errorCodes.js';

/**
 * POST /api/v1/evidence/collect
 *
 * Gateway endpoint triggering evidence retrieval for a resolved company profile.
 *
 * @param {import('express').Request}    req
 * @param {import('express').Response}   res
 * @param {import('express').NextFunction} next
 */
export const collectEvidenceController = async (req, res, next) => {
  try {
    const resolverResult = req.body;

    // Gateway validation check: Ensure we have a resolved company ticker
    if (!resolverResult || !resolverResult.ticker || resolverResult.resolved !== true) {
      return sendError(res, {
        code: ERROR_CODES.VALIDATION_ERROR,
        message: 'Request validation failed. A valid, resolved company resolver profile (with ticker and resolved=true) is required.',
        details: {
          validation_errors: [
            {
              field: 'ticker',
              message: 'Ticker is missing or company profile is unresolved.'
            }
          ]
        }
      }, HTTP_STATUS.UNPROCESSABLE_ENTITY);
    }

    // Call the Python AI service
    const { data, meta } = await collectEvidence(resolverResult);

    return sendSuccess(res, data, meta);
  } catch (err) {
    // Forward unexpected network or backend exceptions to centralized handler
    next(err);
  }
};
