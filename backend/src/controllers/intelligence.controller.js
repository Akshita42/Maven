/**
 * src/controllers/intelligence.controller.js
 *
 * Handles HTTP mapping for company intelligence analysis queries.
 * Validates request input and forwards queries to the Python AI service.
 */

import { analyzeCompany } from '../services/ai/intelligence.js';
import { sendSuccess, sendError } from '../utils/response.js';
import { HTTP_STATUS } from '../constants/httpStatus.js';
import { ERROR_CODES } from '../constants/errorCodes.js';

/**
 * POST /api/v1/intelligence/analyze
 *
 * Gateway endpoint triggering intelligence evaluation.
 *
 * @param {import('express').Request}    req
 * @param {import('express').Response}   res
 * @param {import('express').NextFunction} next
 */
export const analyzeCompanyController = async (req, res, next) => {
  try {
    const payload = req.body;

    // Gateway validation check: Ensure we have either a resolved ticker or a direct evidenceId
    if (!payload || (!payload.ticker && !payload.evidenceId)) {
      return sendError(res, {
        code: ERROR_CODES.VALIDATION_ERROR,
        message: 'Request validation failed. Either a ResolverResult (with ticker) or an EvidencePackage (with evidenceId) is required.',
        details: {
          validation_errors: [
            {
              field: 'payload',
              message: 'Ticker and evidenceId are both missing.'
            }
          ]
        }
      }, HTTP_STATUS.UNPROCESSABLE_ENTITY);
    }

    // Call the Python AI service
    const { data, meta } = await analyzeCompany(payload);

    return sendSuccess(res, data, meta);
  } catch (err) {
    next(err);
  }
};
