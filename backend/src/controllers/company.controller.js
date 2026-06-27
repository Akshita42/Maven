/**
 * src/controllers/company.controller.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * Handles HTTP mapping for company entity resolution queries.
 *
 * Validates request input and forwards queries to the Python AI service.
 * ───────────────────────────────────────────────────────────────────────────
 */

import { resolveCompany } from '../services/ai/company.js';
import { sendSuccess, sendError } from '../utils/response.js';
import { HTTP_STATUS } from '../constants/httpStatus.js';
import { ERROR_CODES } from '../constants/errorCodes.js';

/**
 * POST /api/v1/company/resolve
 *
 * Gateway endpoint resolving query input to a canonical company profile.
 *
 * @param {import('express').Request}    req
 * @param {import('express').Response}   res
 * @param {import('express').NextFunction} next
 */
export const resolveCompanyController = async (req, res, next) => {
  try {
    const { company } = req.body;

    // Fail-fast validation check on Gateway layer
    if (company === undefined || company === null || String(company).trim() === '') {
      return sendError(res, {
        code: ERROR_CODES.VALIDATION_ERROR,
        message: 'Request validation failed. The field "company" is required and must not be empty.',
        details: {
          validation_errors: [
            {
              field: 'company',
              message: 'Input string is empty or missing.'
            }
          ]
        }
      }, HTTP_STATUS.UNPROCESSABLE_ENTITY);
    }

    // Call the Python AI service and retrieve the full envelope
    const { data, meta } = await resolveCompany(String(company).trim());

    // Forward both data and metadata block (e.g. processingTimeMs) directly
    return sendSuccess(res, data, meta);
  } catch (err) {
    // Forward unexpected network or backend exceptions to centralized handler
    next(err);
  }
};
