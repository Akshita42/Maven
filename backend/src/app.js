/**
 * src/app.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * Creates and configures the Express application.
 *
 * This file is intentionally SEPARATE from server.js.
 *
 * ─── Why separate app.js from server.js? ───────────────────────────────────
 * server.js creates an HTTP server and binds it to a port.
 * app.js configures the Express application.
 *
 * Separation allows:
 *   - Unit/integration tests to import `app` without binding to a port
 *   - Supertest (a testing library) can run requests against `app` directly
 *   - The same `app` could be served over HTTP and HTTPS simultaneously
 *
 * If everything was in one file, tests would try to bind port 4000, fail if
 * the port is already in use, and your CI pipeline would break.
 *
 * ─── Middleware order — why it matters ────────────────────────────────────
 * Express executes middleware in the ORDER it is registered.
 * Getting this wrong causes subtle bugs:
 *
 *   1. CORS must be FIRST
 *      → Browser sends OPTIONS preflight before the real request
 *      → If CORS runs after routes, the OPTIONS request hits a 404 first
 *      → Browser sees the 404 and blocks the real request
 *
 *   2. Body parser before routes
 *      → Routes read req.body — if parser hasn't run, req.body is undefined
 *
 *   3. Request logger after body parser
 *      → So we could log body size/content if needed in the future
 *
 *   4. Routes after all setup middleware
 *      → Routes assume CORS is set, body is parsed, etc.
 *
 *   5. 404 handler after all routes
 *      → Only reached if NO route matched
 *
 *   6. Error handler LAST
 *      → Must be registered after everything else
 *      → Catches errors from ALL middleware and routes above it
 * ───────────────────────────────────────────────────────────────────────────
 */

import express from 'express';
import corsMiddleware from './middleware/cors.middleware.js';
import requestLogger from './middleware/requestLogger.middleware.js';
import errorHandler from './middleware/errorHandler.middleware.js';
import router from './routes/index.js';
import { sendError } from './utils/response.js';
import { HTTP_STATUS } from './constants/httpStatus.js';
import { ERROR_CODES } from './constants/errorCodes.js';

const app = express();

// ── 1. CORS ────────────────────────────────────────────────────────────────
// Must be first. Handles preflight OPTIONS requests before they reach routes.
app.use(corsMiddleware);
app.options('*', corsMiddleware); // explicitly handle all OPTIONS preflight

// ── 2. Body Parsing ────────────────────────────────────────────────────────
// express.json() parses incoming requests with Content-Type: application/json
// limit: '1mb' prevents oversized payloads from exhausting memory
app.use(express.json({ limit: '1mb' }));

// express.urlencoded() parses form-encoded bodies (for completeness)
app.use(express.urlencoded({ extended: true }));

// ── 3. Request Logger ──────────────────────────────────────────────────────
app.use(requestLogger);

// ── 4. API Routes ──────────────────────────────────────────────────────────
// All routes are prefixed with /api to namespace them from potential
// static file serving or future non-API routes at the same server.
app.use('/api', router);

// ── 5. 404 Handler ─────────────────────────────────────────────────────────
// Any request that reaches here did not match any registered route.
// Uses the standardised Maven error contract with a machine-readable code.
// The message is intentionally generic — never echo back user-supplied
// path segments, as that can enable reflected injection in older browsers.
app.use((req, res) => {
  return sendError(res, {
    code:    ERROR_CODES.ROUTE_NOT_FOUND,
    message: 'The requested endpoint does not exist.',
  }, HTTP_STATUS.NOT_FOUND);
});

// ── 6. Centralised Error Handler ───────────────────────────────────────────
// MUST be last. Catches any error thrown or passed via next(err).
app.use(errorHandler);

export default app;
