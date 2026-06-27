/**
 * src/server.js
 *
 * ─── Purpose ───────────────────────────────────────────────────────────────
 * Application entry point.
 *
 * This file has ONE job: bind the Express app to a TCP port and handle
 * process-level lifecycle events.
 *
 * ─── What lives here vs app.js ─────────────────────────────────────────────
 *   app.js    → application configuration (routes, middleware)
 *   server.js → infrastructure (port binding, signals, process events)
 *
 * ─── Graceful Shutdown (SIGTERM) ───────────────────────────────────────────
 * When Docker stops a container, it sends SIGTERM to the main process.
 * If the process doesn't exit within a timeout (default 10s), Docker sends
 * SIGKILL — a hard kill that terminates immediately.
 *
 * Graceful shutdown:
 *   1. Stop accepting new connections
 *   2. Wait for in-flight requests to complete
 *   3. Then exit cleanly
 *
 * This matters in production: a user mid-way through a 20-second AI research
 * query should not have their request cut off by a deployment rollout.
 *
 * ─── Process safety nets ───────────────────────────────────────────────────
 * These are LAST-RESORT handlers. They exist to prevent the process from
 * silently continuing in an unknown state after a catastrophic failure.
 * Proper error handling (try/catch, next(err)) should always come first.
 * ───────────────────────────────────────────────────────────────────────────
 */

import app from './app.js';
import config from './config/index.js';
import logger from './utils/logger.js';
import { API } from './constants/api.js';

// ── Startup Banner ─────────────────────────────────────────────────────────
/**
 * Prints a formatted startup banner to the console.
 *
 * Why a banner?
 *   In development, the terminal accumulates output from multiple processes
 *   (frontend dev server, backend, database, AI service). A visible banner
 *   makes it immediately clear which service started, on which port, and
 *   in which environment — reducing the "which terminal is which?" problem.
 *
 * Why console.log and not logger.info?
 *   The banner is a display artefact, not a log entry. It should not carry
 *   a timestamp or severity level. It is purely for developer experience.
 *   We use console.log directly and exclusively here.
 */
const printBanner = () => {
  const C = {
    reset:  '\x1b[0m',
    bold:   '\x1b[1m',
    cyan:   '\x1b[36m',
    green:  '\x1b[32m',
    yellow: '\x1b[33m',
    dim:    '\x1b[2m',
  };

  const divider = `${C.cyan}${C.bold}${'═'.repeat(54)}${C.reset}`;
  const label   = (key, value, colour = C.reset) =>
    `  ${C.yellow}${key.padEnd(14)}${C.reset}${colour}${value}${C.reset}`;

  console.log(`\n${divider}`);
  console.log(`  ${C.green}${C.bold}◆  Maven AI Investment Copilot${C.reset}`);
  console.log(divider);
  console.log(label('Service',     API.SERVICE_NAME,   C.green));
  console.log(label('Version',     config.version));
  console.log(label('API',         API.VERSION));
  console.log(label('Environment', config.env,         config.env === 'production' ? C.yellow : C.reset));
  console.log(label('Port',        String(config.port)));
  console.log(label('Health',      `http://localhost:${config.port}/api/health`, C.cyan));
  console.log(`${divider}\n`);
};

// ── Server Bootstrap ───────────────────────────────────────────────────────
const server = app.listen(config.port, () => {
  printBanner();
  logger.info('Server is ready to accept connections.');
});

// ── Graceful Shutdown ──────────────────────────────────────────────────────
process.on('SIGTERM', () => {
  logger.info('SIGTERM received — shutting down gracefully...');

  // server.close() stops accepting new connections.
  // The callback fires once all in-flight requests are complete.
  server.close(() => {
    logger.info('All connections closed. Process exiting cleanly.');
    process.exit(0);
  });
});

// ── Process Safety Nets ────────────────────────────────────────────────────
process.on('unhandledRejection', (reason) => {
  logger.error('Unhandled Promise Rejection — process exiting', {
    reason: String(reason),
  });
  process.exit(1);
});

process.on('uncaughtException', (err) => {
  logger.error('Uncaught Exception — process exiting', {
    message: err.message,
    stack:   err.stack,
  });
  process.exit(1);
});

export default server;
