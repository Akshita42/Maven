/**
 * src/config/index.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * Central configuration registry with startup validation.
 *
 * Every environment variable is read ONCE, here, and exported as a typed
 * config object. The rest of the application NEVER reads process.env directly.
 *
 *   1. Auditability  — one file to review every configuration key
 *   2. Defaults      — fallback values co-located with variable names
 *   3. Testability   — tests can override this object cleanly
 *   4. Fail Fast     — invalid config crashes the process immediately
 *                      with a clear, actionable error message
 *
 * ─── Why Fail Fast? ────────────────────────────────────────────────────────
 * A server that starts with a missing CORS_ORIGIN silently blocks all
 * frontend requests. A server that starts with an invalid AI_SERVICE_URL
 * fails mysteriously on the first research request — not at startup.
 *
 * Crashing at startup with a clear message is always preferable to a
 * mysterious runtime failure hours later under production load.
 *
 * ─── dotenv ────────────────────────────────────────────────────────────────
 * `import 'dotenv/config'` is the ES Module equivalent of:
 *   require('dotenv').config()
 * It reads the nearest .env file and populates process.env before any
 * other module code runs. Must be the first import in this file.
 * ───────────────────────────────────────────────────────────────────────────
 */

import 'dotenv/config';

const config = {
  /** Runtime environment: 'development' | 'production' | 'test' */
  env: process.env.NODE_ENV || 'development',

  /** TCP port the HTTP server will bind to */
  port: parseInt(process.env.PORT || '4000', 10),

  /**
   * Application version — injected by npm from package.json at runtime.
   * npm_package_version is set automatically when running via npm scripts.
   * Falls back to '1.0.0' when running with `node src/server.js` directly.
   */
  version: process.env.npm_package_version || '1.0.0',

  cors: {
    /**
     * Exact origin of the React frontend.
     * Must be protocol + host + port, no trailing slash.
     * Example: 'http://localhost:3000'
     */
    origin: process.env.CORS_ORIGIN || 'http://localhost:3000',
  },

  aiService: {
    /**
     * Base URL of the Python FastAPI service.
     * Not used in Phase 1. Required from Phase 2 onward.
     */
    baseUrl: process.env.AI_SERVICE_URL || 'http://localhost:8000',

    /**
     * Maximum milliseconds to wait for a Python AI response.
     * 30 seconds is intentionally generous — AI inference takes time.
     */
    timeoutMs: parseInt(process.env.AI_SERVICE_TIMEOUT || '30000', 10),
  },
};

// ─── Configuration Validation ─────────────────────────────────────────────
/**
 * Validates the assembled config object against known rules.
 * Crashes the process immediately if any required value is missing or invalid.
 *
 * ─── Design choice: validate at import time ────────────────────────────────
 * This function is called at the bottom of this module, which means it runs
 * the moment config/index.js is first imported by server.js.
 * The process exits before any HTTP server is created if validation fails.
 *
 * ─── Why not throw? ────────────────────────────────────────────────────────
 * Throwing an Error would produce a stack trace pointing at this file,
 * not at the .env variable that caused the problem. A direct process.exit()
 * with a targeted message is a better developer experience.
 *
 * ─── Extending this validator ──────────────────────────────────────────────
 * When future phases add API keys (OPENAI_API_KEY, etc.), add a check:
 *   if (!process.env.OPENAI_API_KEY) {
 *     errors.push('OPENAI_API_KEY is required from Phase 3 onward.');
 *   }
 *
 * @param {typeof config} cfg - The assembled config object
 */
const validateConfig = (cfg) => {
  const errors = [];

  // ── PORT ────────────────────────────────────────────────────────────────
  if (!Number.isInteger(cfg.port) || cfg.port < 1 || cfg.port > 65535) {
    errors.push(
      `PORT must be a valid port number (1–65535).\n` +
      `     Current value: "${process.env.PORT || '(not set)'}" → parsed as: ${cfg.port}`
    );
  }

  // ── NODE_ENV ────────────────────────────────────────────────────────────
  const allowedEnvs = ['development', 'production', 'test'];
  if (!allowedEnvs.includes(cfg.env)) {
    errors.push(
      `NODE_ENV must be one of: ${allowedEnvs.join(', ')}.\n` +
      `     Current value: "${cfg.env}"`
    );
  }

  // ── CORS_ORIGIN ─────────────────────────────────────────────────────────
  if (!cfg.cors.origin || cfg.cors.origin.trim() === '') {
    errors.push(
      `CORS_ORIGIN must not be empty.\n` +
      `     Set it to your React frontend URL, e.g.: http://localhost:3000`
    );
  } else {
    try {
      new URL(cfg.cors.origin);
    } catch {
      errors.push(
        `CORS_ORIGIN must be a valid URL (include protocol and port).\n` +
        `     Current value: "${cfg.cors.origin}"`
      );
    }
  }

  // ── AI_SERVICE_URL ──────────────────────────────────────────────────────
  try {
    new URL(cfg.aiService.baseUrl);
  } catch {
    errors.push(
      `AI_SERVICE_URL must be a valid URL.\n` +
      `     Current value: "${cfg.aiService.baseUrl}"`
    );
  }

  // ── AI_SERVICE_TIMEOUT ──────────────────────────────────────────────────
  if (!Number.isInteger(cfg.aiService.timeoutMs) || cfg.aiService.timeoutMs < 1000) {
    errors.push(
      `AI_SERVICE_TIMEOUT must be at least 1000 milliseconds.\n` +
      `     Current value: "${process.env.AI_SERVICE_TIMEOUT || '(not set)'}"`
    );
  }

  // ── Exit if any validation failed ────────────────────────────────────────
  if (errors.length > 0) {
    // Use ANSI red for the header — this is a fatal error
    console.error('\n\x1b[31m╔══════════════════════════════════════════════════════╗\x1b[0m');
    console.error('\x1b[31m║  FATAL: Maven backend cannot start                   ║\x1b[0m');
    console.error('\x1b[31m║  Invalid or missing environment configuration.        ║\x1b[0m');
    console.error('\x1b[31m╚══════════════════════════════════════════════════════╝\x1b[0m\n');

    errors.forEach((err, index) => {
      console.error(`\x1b[31m  ${index + 1}.\x1b[0m ${err}\n`);
    });

    console.error('\x1b[33m  → Check your .env file (copy from .env.example if missing)\x1b[0m\n');

    process.exit(1);
  }
};

// Run validation immediately — before any HTTP server is created
validateConfig(config);

export default config;
