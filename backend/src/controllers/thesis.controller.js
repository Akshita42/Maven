/**
 * src/controllers/thesis.controller.js
 *
 * Handles HTTP mapping for company investment thesis build queries.
 * Validates request input and forwards queries to the Python AI service.
 */

import { buildThesis } from '../services/ai/thesis.js';
import { sendSuccess, sendError } from '../utils/response.js';
import { HTTP_STATUS } from '../constants/httpStatus.js';
import { ERROR_CODES } from '../constants/errorCodes.js';

/**
 * POST /api/v1/thesis/build
 *
 * Gateway endpoint triggering investment thesis generation.
 *
 * @param {import('express').Request}    req
 * @param {import('express').Response}   res
 * @param {import('express').NextFunction} next
 */
export const buildThesisController = async (req, res, next) => {
  try {
    const payload = req.body;

    // Gateway validation check: Ensure we have at least one identifier field
    if (!payload || (!payload.ticker && !payload.evidenceId && !payload.intelligenceId)) {
      return sendError(res, {
        code: ERROR_CODES.VALIDATION_ERROR,
        message: 'Request validation failed. Either a ResolverResult (with ticker), EvidencePackage (with evidenceId), or InvestmentIntelligence (with intelligenceId) is required.',
        details: {
          validation_errors: [
            {
              field: 'payload',
              message: 'Ticker, evidenceId, and intelligenceId are all missing.'
            }
          ]
        }
      }, HTTP_STATUS.UNPROCESSABLE_ENTITY);
    }

    // Call the Python AI service
    const { data, meta } = await buildThesis(payload);

    return sendSuccess(res, data, meta);
  } catch (err) {
    next(err);
  }
};
