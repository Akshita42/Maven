/**
 * src/utils/response.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * Standardised HTTP response helpers.
 *
 * Every Maven API response follows this frozen contract:
 *
 *   Success:
 *   {
 *     "status": "success",
 *     "data":   { ... },      ← the actual payload
 *     "meta":   { ... }       ← pagination, timestamps, confidence scores, etc.
 *   }
 *
 *   Error:
 *   {
 *     "status": "error",
 *     "error": {
 *       "code":    "ROUTE_NOT_FOUND",    ← machine-readable, stable identifier
 *       "message": "...",                ← human-readable explanation
 *       "details": { ... }               ← optional debug info (dev only)
 *     }
 *   }
 *
 * ─── Why status string instead of boolean? ─────────────────────────────────
 * The previous version used `"success": true/false`.
 * A boolean can only represent two states.
 * A string can represent "success", "error", or future states like "partial"
 * (e.g., AI returns a partial recommendation when some evidence is missing).
 *
 * ─── Why a meta field? ─────────────────────────────────────────────────────
 * Future endpoints will return pagination info, generation timestamps,
 * confidence scores, and evidence counts alongside the core payload.
 * These are response metadata — they describe the response, not the content.
 * Mixing them into `data` would pollute the payload contract.
 *
 * ─── Why machine-readable error codes? ────────────────────────────────────
 * Error messages can change. Error codes must not.
 * The React frontend uses codes to decide which UI state to show.
 * If codes change, the frontend logic breaks silently.
 * ───────────────────────────────────────────────────────────────────────────
 */

import { API } from '../constants/api.js';

/**
 * Send a standardised success response.
 *
 * @param {import('express').Response} res         - Express response object
 * @param {object}  [data={}]                      - The response payload
 * @param {object}  [meta={}]                      - Response metadata (pagination, scores, etc.)
 * @param {number}  [statusCode=200]               - HTTP status code
 * @returns {import('express').Response}
 *
 * @example
 * // Minimal usage
 * sendSuccess(res, { service: 'backend', status: 'healthy' });
 *
 * // With metadata
 * sendSuccess(res, { items: [...] }, { total: 42, page: 1 });
 */
export const sendSuccess = (res, data = {}, meta = {}, statusCode = 200) => {
  return res.status(statusCode).json({
    status: API.RESPONSE_STATUS.SUCCESS,
    data,
    meta,
  });
};

/**
 * Send a standardised error response.
 *
 * @param {import('express').Response} res         - Express response object
 * @param {object}  errorPayload                   - Error descriptor object
 * @param {string}  errorPayload.code              - Machine-readable error code (from ERROR_CODES)
 * @param {string}  errorPayload.message           - Human-readable description
 * @param {object}  [errorPayload.details=null]    - Optional debug details (stack trace, etc.)
 * @param {number}  [statusCode=500]               - HTTP status code
 * @returns {import('express').Response}
 *
 * @example
 * sendError(res, {
 *   code: ERROR_CODES.ROUTE_NOT_FOUND,
 *   message: 'The requested endpoint does not exist.',
 * }, HTTP_STATUS.NOT_FOUND);
 */
export const sendError = (res, { code, message, details = null }, statusCode = 500) => {
  return res.status(statusCode).json({
    status: API.RESPONSE_STATUS.ERROR,
    error: {
      code,
      message,
      ...(details !== null ? { details } : {}),
    },
  });
};
