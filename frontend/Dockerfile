
FROM node:20-alpine as build

WORKDIR /app

# Install dependencies using npm
# We copy package files first to leverage Docker cache
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code
COPY . .

# Declare build args
ARG VITE_API_URL
ARG VITE_WS_URL

# Set as env vars so Vite pick them up during build
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_WS_URL=$VITE_WS_URL

# Build the app
RUN npm run build

# Production serve stage using a simple HTTP server or Nginx
# Using a lightweight static server for simplicity in this MVP context
FROM node:20-alpine

WORKDIR /app

# Install 'serve' package globally
RUN npm install -g serve

# Copy built assets from builder stage
COPY --from=build /app/dist ./dist

# Expose port (default for 'serve' is 3000)
EXPOSE 3000

# Start server
CMD ["serve", "-s", "dist", "-l", "3000"]
