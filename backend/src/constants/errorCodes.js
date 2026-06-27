/**
 * src/constants/errorCodes.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * Machine-readable error codes that form the error contract between the
 * backend and every consumer (React frontend, monitoring tools, logs).
 *
 * ─── Why machine-readable codes? ───────────────────────────────────────────
 * Error messages are for humans and can change (typos fixed, wording improved).
 * Error codes are for machines and must NEVER change once published.
 *
 * The React frontend can do:
 *   if (error.code === 'AI_SERVICE_UNAVAILABLE') showRetryButton();
 *   if (error.code === 'EVIDENCE_INSUFFICIENT') showMissingDataMessage();
 *
 * If we used raw messages instead, any rephrasing of a message would break
 * frontend conditional logic silently.
 *
 * ─── Naming convention ─────────────────────────────────────────────────────
 * SCREAMING_SNAKE_CASE — industry standard for error codes and constants.
 * Grouped by domain for discoverability.
 * ───────────────────────────────────────────────────────────────────────────
 */

export const ERROR_CODES = {
  // ── Generic ────────────────────────────────────────────────────────────
  /** Catch-all for unexpected server-side failures. */
  INTERNAL_SERVER_ERROR: 'INTERNAL_SERVER_ERROR',

  /** The requested URL path does not match any registered route. */
  ROUTE_NOT_FOUND: 'ROUTE_NOT_FOUND',

  /** Request data failed schema or business-rule validation. */
  VALIDATION_ERROR: 'VALIDATION_ERROR',

  // ── Configuration ──────────────────────────────────────────────────────
  /** The server started with invalid or missing environment configuration. */
  CONFIG_INVALID: 'CONFIG_INVALID',

  // ── AI Service (Python) ────────────────────────────────────────────────
  /** The Python AI Service is unreachable or down. */
  AI_SERVICE_UNAVAILABLE: 'AI_SERVICE_UNAVAILABLE',

  /** The Python AI Service did not respond within the configured timeout. */
  AI_SERVICE_TIMEOUT: 'AI_SERVICE_TIMEOUT',

  /** The AI Service returned a response that could not be parsed. */
  AI_SERVICE_BAD_RESPONSE: 'AI_SERVICE_BAD_RESPONSE',

  // ── Research Domain (Phase 2+) ─────────────────────────────────────────
  /** The research pipeline failed to complete. */
  RESEARCH_FAILED: 'RESEARCH_FAILED',

  /**
   * Evidence collected was insufficient to produce a recommendation.
   * Per the Decision Playbook: explain what is missing, do not refuse silently.
   */
  EVIDENCE_INSUFFICIENT: 'EVIDENCE_INSUFFICIENT',
};
