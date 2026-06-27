/**
 * src/middleware/requestLogger.middleware.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * Logs every HTTP request that passes through the server, including:
 *   - HTTP method (GET, POST, etc.)
 *   - URL path
 *   - HTTP response status code
 *   - Total request duration in milliseconds
 *   - Caller IP address
 *
 * ─── How duration is measured ──────────────────────────────────────────────
 * We record Date.now() when the request ENTERS this middleware.
 * Then we attach a listener to the response 'finish' event.
 * 'finish' fires AFTER the response body has been fully sent to the client.
 * Duration = finish_time - start_time.
 *
 * We cannot log duration at the point we call next() because the request
 * hasn't been processed yet at that point — we haven't even reached the
 * controller. The response event listener solves this.
 *
 * ─── Log levels by status code ─────────────────────────────────────────────
 *   5xx → error  (server broke)
 *   4xx → warn   (client made a bad request)
 *   2xx/3xx → info (normal operation)
 *
 * ─── Why not use 'morgan'? ─────────────────────────────────────────────────
 * Morgan is a popular alternative (one-liner setup). The custom implementation
 * here is intentional for two reasons:
 *   1. Teaching — you can see exactly how request logging works
 *   2. Integration — it uses our own logger so all output is consistent
 * ───────────────────────────────────────────────────────────────────────────
 */

import logger from '../utils/logger.js';

/**
 * Express middleware that logs all incoming requests with response metadata.
 *
 * @param {import('express').Request}  req
 * @param {import('express').Response} res
 * @param {import('express').NextFunction} next
 */
const requestLogger = (req, res, next) => {
  // Record the exact time this request arrived
  const startTime = Date.now();

  // Attach a listener that fires after the response is fully sent.
  // We use 'finish' (not 'close') because 'finish' means the response
  // was sent successfully; 'close' fires even if the connection dropped.
  res.on('finish', () => {
    const durationMs = Date.now() - startTime;
    const status = res.statusCode;

    // Choose log level based on HTTP status code
    const level = status >= 500 ? 'error' : status >= 400 ? 'warn' : 'info';

    logger[level](`${req.method} ${req.originalUrl}`, {
      status,
      duration: `${durationMs}ms`,
      ip: req.ip || req.socket.remoteAddress,
    });
  });

  // Pass control to the next middleware / route handler
  next();
};

export default requestLogger;
