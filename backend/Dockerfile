# ─────────────────────────────────────────────────────────────────
# Maven Backend — Dockerfile
# ─────────────────────────────────────────────────────────────────
#
# Uses the official Node.js LTS Alpine image.
# Alpine is a minimal Linux distro — the resulting image is ~180MB
# versus ~900MB for the full Debian-based node image.
#
# Layer ordering is deliberate:
#   1. Copy package files FIRST (rarely change)
#   2. npm ci  (cached by Docker if package-lock.json unchanged)
#   3. Copy source LAST (changes on every build)
#
# This means Docker only re-runs npm ci when dependencies change,
# not every time you edit a .js file — dramatically faster builds.
# ─────────────────────────────────────────────────────────────────

FROM node:20-alpine

# Set working directory inside the container
WORKDIR /app

# Copy dependency manifests first to exploit Docker layer caching
COPY package*.json ./

# npm ci is preferred over npm install in CI/CD:
# - Installs exactly the versions in package-lock.json
# - Never modifies package-lock.json
# - Faster in clean environments
# --omit=dev skips devDependencies (nodemon not needed in prod)
RUN npm ci --omit=dev

# Copy application source
COPY src/ ./src/

# Document the port this container will listen on.
# This is metadata — docker-compose still needs to publish the port.
EXPOSE 4000

# Healthcheck lets Docker/orchestrators know if the container is alive.
# Polls /api/health every 30s, fails after 3 consecutive failures.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:4000/api/health || exit 1

# Run the application (not npm start — avoids the npm process wrapper)
CMD ["node", "src/server.js"]
