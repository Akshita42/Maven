/**
 * src/controllers/committee.controller.js
 *
 * Handles HTTP mapping for company investment committee review queries.
 * Validates request input and forwards queries to the Python AI service.
 */

import { reviewThesis } from '../services/ai/committee.js';
import { sendSuccess, sendError } from '../utils/response.js';
import { HTTP_STATUS } from '../constants/httpStatus.js';
import { ERROR_CODES } from '../constants/errorCodes.js';

/**
 * POST /api/v1/committee/review
 *
 * Gateway endpoint triggering investment committee review evaluation.
 *
 * @param {import('express').Request}    req
 * @param {import('express').Response}   res
 * @param {import('express').NextFunction} next
 */
export const reviewThesisController = async (req, res, next) => {
  try {
    const payload = req.body;

    // Gateway validation check: Ensure we have at least one identifier field
    if (!payload || (!payload.ticker && !payload.evidenceId && !payload.intelligenceId && !payload.thesisId)) {
      return sendError(res, {
        code: ERROR_CODES.VALIDATION_ERROR,
        message: 'Request validation failed. Either a ResolverResult (with ticker), EvidencePackage (with evidenceId), InvestmentIntelligence (with intelligenceId), or InvestmentThesis (with thesisId) is required.',
        details: {
          validation_errors: [
            {
              field: 'payload',
              message: 'Ticker, evidenceId, intelligenceId, and thesisId are all missing.'
            }
          ]
        }
      }, HTTP_STATUS.UNPROCESSABLE_ENTITY);
    }

    // Call the Python AI service
    const { data, meta } = await reviewThesis(payload);

    return sendSuccess(res, data, meta);
  } catch (err) {
    next(err);
  }
};
