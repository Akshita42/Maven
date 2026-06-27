/**
 * src/constants/api.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * Application-level constants that define Maven's API identity and conventions.
 *
 * These values appear throughout the codebase:
 *   - In response envelopes (status strings)
 *   - In health payloads (service name, health statuses)
 *   - In startup banners (version, service name)
 *   - In route prefixes (API version)
 *
 * Centralising them here means:
 *   - They are defined once, readable from one place
 *   - A rename (e.g., service name changes) is a one-file edit
 *   - No magic strings scattered across middleware, controllers, services
 *
 * ─── Why version the API? ──────────────────────────────────────────────────
 * /api/v1/health gives us the ability to introduce /api/v2/health later
 * without breaking existing consumers. This is standard REST API practice.
 * We are not using the version prefix in routes yet, but the constant is
 * established so future phases adopt it consistently from day one.
 * ───────────────────────────────────────────────────────────────────────────
 */

export const API = {
  /** Canonical name of this service. Used in health payloads and banners. */
  SERVICE_NAME: 'maven-backend',

  /** Current API version. Prepended to all versioned route groups. */
  VERSION: 'v1',

  /**
   * Top-level response status strings.
   * Used in every response envelope — never use raw strings in code.
   */
  RESPONSE_STATUS: {
    SUCCESS: 'success',
    ERROR: 'error',
  },

  /**
   * Possible health states for any Maven service.
   *
   *   HEALTHY   — all systems operational
   *   DEGRADED  — running but with reduced capability (e.g., AI slow)
   *   UNHEALTHY — a critical dependency is down
   */
  HEALTH_STATUS: {
    HEALTHY: 'healthy',
    DEGRADED: 'degraded',
    UNHEALTHY: 'unhealthy',
  },
};
