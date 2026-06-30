/**
 * src/controllers/recommendation.controller.js
 *
 * Handles HTTP mapping for investment recommendation queries.
 */

import { buildRecommendation } from '../services/ai/recommendation.js';
import { sendSuccess, sendError } from '../utils/response.js';
import { HTTP_STATUS } from '../constants/httpStatus.js';
import { ERROR_CODES } from '../constants/errorCodes.js';

export const buildRecommendationController = async (req, res, next) => {
  try {
    const payload = req.body;

    if (!payload || !payload.thesis || !payload.review || !payload.critique) {
      return sendError(res, {
        code: ERROR_CODES.VALIDATION_ERROR,
        message: 'Request validation failed. Payload must contain thesis, review, and critique objects.',
      }, HTTP_STATUS.UNPROCESSABLE_ENTITY);
    }

    const { data, meta } = await buildRecommendation(payload);
    return sendSuccess(res, data, meta);
  } catch (err) {
    next(err);
  }
};
