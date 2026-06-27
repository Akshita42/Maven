/**
 * src/middleware/errorHandler.middleware.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * Centralised error handling. This is the last line of defence.
 *
 * Any error thrown inside a route handler, or passed via next(error),
 * ends up here. It is caught, logged, and converted into a clean JSON
 * response using the standardised Maven error contract.
 *
 * The server NEVER crashes because of an API exception.
 *
 * ─── How Express recognises an error handler ───────────────────────────────
 * Express identifies error-handling middleware by the NUMBER of arguments.
 * Normal middleware takes 3: (req, res, next)
 * Error middleware takes 4: (err, req, res, next)
 *
 * The 'err' parameter MUST be first. Even if 'next' is unused, omitting it
 * causes Express to treat this as normal middleware, silently breaking it.
 *
 * ─── How errors reach this handler ────────────────────────────────────────
 * Method 1 — async route with try/catch:
 *   app.get('/test', async (req, res, next) => {
 *     try { ... } catch (err) { next(err); }
 *   });
 *
 * Method 2 — synchronous throw (Express 4 catches automatically):
 *   app.get('/test', (req, res) => { throw new Error('Broke'); });
 *
 * ─── Custom error codes on Error objects ───────────────────────────────────
 * Future code can attach machine-readable codes to errors:
 *   const err = new Error('AI service is down');
 *   err.statusCode = 503;
 *   err.code = ERROR_CODES.AI_SERVICE_UNAVAILABLE;
 *   next(err);
 *
 * This handler reads those properties and includes them in the response.
 *
 * ─── Stack trace policy ────────────────────────────────────────────────────
 * Development: stack included in response.error.details for fast debugging.
 * Production:  stack EXCLUDED from response — never leak implementation to clients.
 *              Stack is still logged internally so ops teams can investigate.
 * ───────────────────────────────────────────────────────────────────────────
 */

import logger from '../utils/logger.js';
import { sendError } from '../utils/response.js';
import { HTTP_STATUS } from '../constants/httpStatus.js';
import { ERROR_CODES } from '../constants/errorCodes.js';

/**
 * Express 4 centralised error-handling middleware.
 * Must be registered LAST in app.js (after all routes).
 *
 * @param {Error & { statusCode?: number; status?: number; code?: string }} err
 * @param {import('express').Request}    req
 * @param {import('express').Response}   res
 * @param {import('express').NextFunction} next - Required even if unused
 */
// eslint-disable-next-line no-unused-vars
const errorHandler = (err, req, res, next) => {
  const statusCode = err.statusCode || err.status || HTTP_STATUS.INTERNAL_SERVER_ERROR;
  const message    = err.message || 'An unexpected error occurred.';
  const code       = err.code || ERROR_CODES.INTERNAL_SERVER_ERROR;
  const isDev      = process.env.NODE_ENV !== 'production';

  // Always log the full error internally (including stack) for diagnostics
  logger.error(`Unhandled error: ${req.method} ${req.originalUrl}`, {
    statusCode,
    code,
    message,
    ...(err.stack ? { stack: err.stack } : {}),
  });

  // Build the error response — stack only in development
  return sendError(res, {
    code,
    message,
    ...(isDev && err.stack ? { details: { stack: err.stack } } : {}),
  }, statusCode);
};

export default errorHandler;
