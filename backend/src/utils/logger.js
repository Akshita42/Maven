/**
 * src/utils/logger.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * A minimal, structured console logger.
 *
 * Why not console.log directly?
 *   - console.log has no levels (you can't filter by severity)
 *   - console.log has no timestamps
 *   - In production you want structured JSON logs (for log aggregators)
 *   - This wrapper gives us a consistent interface we can upgrade later
 *
 * Why not Winston or Pino right now?
 *   - Winston and Pino are excellent but add configuration complexity.
 *   - This phase needs to be simple and understandable.
 *   - The interface (logger.info, logger.warn, logger.error) is identical
 *     to what Winston/Pino expose, so swapping is a one-line change later.
 *
 * ─── Production upgrade path ───────────────────────────────────────────────
 *   Replace the implementation below with:
 *     import winston from 'winston';
 *     export default winston.createLogger({ ... });
 *   All call sites remain unchanged.
 * ───────────────────────────────────────────────────────────────────────────
 */

// ANSI escape codes for terminal colour output.
// These are ignored or stripped by log aggregators in production.
const COLOURS = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  cyan: '\x1b[36m',
};

const LEVEL_LABELS = {
  info:  `${COLOURS.green}INFO ${COLOURS.reset}`,
  warn:  `${COLOURS.yellow}WARN ${COLOURS.reset}`,
  error: `${COLOURS.red}ERROR${COLOURS.reset}`,
  debug: `${COLOURS.cyan}DEBUG${COLOURS.reset}`,
};

/**
 * Internal log function. Formats a structured log line and writes to stdout.
 *
 * @param {'info'|'warn'|'error'|'debug'} level - Severity level
 * @param {string} message                       - Human-readable description
 * @param {object} [meta={}]                     - Optional structured metadata
 */
const log = (level, message, meta = {}) => {
  const timestamp = new Date().toISOString();
  const label = LEVEL_LABELS[level] || level.toUpperCase();
  const metaStr = Object.keys(meta).length > 0 ? ` ${JSON.stringify(meta)}` : '';

  // Format: [LEVEL] 2026-06-27T12:00:00.000Z  Message  {meta}
  const line = `[${label}] ${COLOURS.cyan}${timestamp}${COLOURS.reset}  ${message}${metaStr}`;

  if (level === 'error') {
    console.error(line);
  } else {
    console.log(line);
  }
};

const logger = {
  /**
   * Log an informational message (normal operation).
   * @param {string} message
   * @param {object} [meta]
   */
  info: (message, meta) => log('info', message, meta),

  /**
   * Log a warning (something unexpected but non-fatal).
   * @param {string} message
   * @param {object} [meta]
   */
  warn: (message, meta) => log('warn', message, meta),

  /**
   * Log an error (something broke that needs attention).
   * @param {string} message
   * @param {object} [meta]
   */
  error: (message, meta) => log('error', message, meta),

  /**
   * Log a debug message (verbose tracing for development).
   * Suppressed in production — use for internal state tracing,
   * not for information users or operators need to act on.
   *
   * Why suppress in production?
   *   Debug logs are high-volume and contain internal implementation details.
   *   Shipping them to production log aggregators wastes storage and may
   *   accidentally expose sensitive data (request bodies, tokens, etc.).
   *
   * @param {string} message
   * @param {object} [meta]
   */
  debug: (message, meta) => {
    if (process.env.NODE_ENV !== 'production') {
      log('debug', message, meta);
    }
  },
};

export default logger;
