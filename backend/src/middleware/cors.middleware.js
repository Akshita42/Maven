/**
 * src/middleware/cors.middleware.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * Configures Cross-Origin Resource Sharing (CORS) for the API.
 *
 * ─── What is CORS? ─────────────────────────────────────────────────────────
 * Browsers enforce the Same-Origin Policy: a page at localhost:3000 is not
 * allowed to make an XHR/fetch call to localhost:4000 by default, because
 * the PORT is different (origin = protocol + host + port).
 *
 * CORS is the mechanism by which the SERVER tells the browser:
 *   "I am OK receiving requests from that origin."
 *
 * The browser sends a preflight OPTIONS request first, then the real request.
 * If the server doesn't respond correctly to the preflight, the browser
 * blocks the request before it even leaves the client.
 *
 * ─── Why NOT allow all origins (*)? ───────────────────────────────────────
 * Wildcard (*) origin means ANY website can call this API.
 * - If we add authentication cookies later, `credentials: true` cannot be
 *   combined with origin: '*' (the browser rejects it).
 * - An attacker could build a phishing page that makes API calls on behalf
 *   of a logged-in user (CSRF-style attack).
 * - For Maven, we know exactly where the frontend runs.
 *
 * ─── allowedHeaders ────────────────────────────────────────────────────────
 * We explicitly list which request headers are permitted.
 * 'Authorization' will be needed when we add JWT auth in a future phase.
 * ───────────────────────────────────────────────────────────────────────────
 */

import cors from 'cors';
import config from '../config/index.js';

const corsOptions = {
  /** Only the React dev server (or deployed frontend URL) is allowed */
  origin: config.cors.origin,

  /** Standard HTTP methods for a REST API */
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],

  /** Headers the client is allowed to send */
  allowedHeaders: ['Content-Type', 'Authorization'],

  /**
   * Allow cookies / Authorization headers to be sent cross-origin.
   * Required when we implement session-based auth in a future phase.
   */
  credentials: true,

  /**
   * How long (in seconds) the browser should cache the preflight response.
   * 600 = 10 minutes — reduces preflight overhead for frequent callers.
   */
  maxAge: 600,
};

export default cors(corsOptions);
