/**
 * src/services/health.service.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * Contains the business logic for the health check.
 *
 * For Phase 1, the health check is simple — it just returns that this
 * service is alive. But this file demonstrates the Service Layer pattern
 * that will be used throughout Maven for all future features.
 *
 * ─── Why have a service for something this simple? ─────────────────────────
 * The Controller-Service separation is an architectural pattern, not a
 * feature of the health endpoint specifically.
 *
 * In future phases:
 *   - The research service will call the Python AI service
 *   - The session service will query the database
 *   - The health service itself may check Python connectivity
 *
 * Establishing the pattern now means:
 *   1. All future services follow the same shape
 *   2. The controller stays thin (no logic, just orchestration)
 *   3. Services are independently testable (mock the service, test controller)
 *
 * ─── What goes in a service vs a controller? ────────────────────────────────
 *   Controller → receives HTTP request, calls service, sends HTTP response
 *   Service    → contains business logic, calls external systems if needed
 *
 * The controller knows about HTTP. The service does not.
 * ───────────────────────────────────────────────────────────────────────────
 */

import config from '../config/index.js';
import { API } from '../constants/api.js';

/**
 * Gathers and returns the current health status of the backend service.
 *
 * ─── Fields ────────────────────────────────────────────────────────────────
 *   service   — canonical service identifier (from API constants)
 *   version   — application version from package.json
 *   status    — health state: 'healthy' | 'degraded' | 'unhealthy'
 *   uptime    — seconds since the Node.js process started.
 *               process.uptime() is more precise than Date.now() arithmetic
 *               because it uses high-resolution timing and is immune to
 *               system clock changes (NTP adjustments, DST, etc.).
 *   timestamp — ISO 8601 UTC timestamp of this health check response.
 *               Useful for debugging caching issues and time-skew.
 *
 * ─── Future extension ──────────────────────────────────────────────────────
 * In a later phase this function will also check Python AI service health
 * and return a combined status. The status field would become 'degraded'
 * if Python is slow, or 'unhealthy' if Python is unreachable.
 * ───────────────────────────────────────────────────────────────────────────
 *
 * @returns {{ service: string, version: string, status: string, uptime: number, timestamp: string }}
 */
export const getHealthStatus = () => {
  return {
    service:   API.SERVICE_NAME,
    version:   config.version,
    status:    API.HEALTH_STATUS.HEALTHY,
    uptime:    parseFloat(process.uptime().toFixed(3)),
    timestamp: new Date().toISOString(),
  };
};
