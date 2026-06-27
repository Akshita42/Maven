/**
 * src/constants/httpStatus.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * Named constants for HTTP status codes used throughout the Maven backend.
 *
 * Why not use raw numbers like `res.status(404)`?
 *
 *   res.status(404).json(...)        ← what does 404 mean here? Reader must know
 *   res.status(HTTP_STATUS.NOT_FOUND) ← self-documenting, searchable, refactorable
 *
 * If we ever need to change a status code (e.g., from 500 to 503 for
 * AI service unavailability), we change it in ONE place, not across 20 files.
 *
 * ─── Coverage ──────────────────────────────────────────────────────────────
 * We only include codes Maven actually uses or will use.
 * A complete list of 70+ codes would add noise without value.
 * ───────────────────────────────────────────────────────────────────────────
 */

export const HTTP_STATUS = {
  // ── 2xx Success ────────────────────────────────────────────────────────
  /** Request succeeded. Standard response for GET, POST that returns data. */
  OK: 200,

  /** Resource created. Used for POST that creates a new entity. */
  CREATED: 201,

  // ── 4xx Client Errors ──────────────────────────────────────────────────
  /** Malformed request syntax or invalid parameters. */
  BAD_REQUEST: 400,

  /** Authentication is required and has failed or not been provided. */
  UNAUTHORIZED: 401,

  /** Authenticated but not authorised to access this resource. */
  FORBIDDEN: 403,

  /** The resource or route does not exist. */
  NOT_FOUND: 404,

  /** Request is well-formed but semantically invalid (e.g., validation error). */
  UNPROCESSABLE_ENTITY: 422,

  /** Too many requests in a given time window. */
  TOO_MANY_REQUESTS: 429,

  // ── 5xx Server Errors ──────────────────────────────────────────────────
  /** Generic server error. Should be avoided in favour of specific codes. */
  INTERNAL_SERVER_ERROR: 500,

  /** The upstream service (Python AI Service) returned an invalid response. */
  BAD_GATEWAY: 502,

  /** The server is temporarily unavailable (overload or maintenance). */
  SERVICE_UNAVAILABLE: 503,

  /** The upstream service (Python AI Service) did not respond in time. */
  GATEWAY_TIMEOUT: 504,
};
