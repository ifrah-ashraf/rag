# ── Stage 1: Install deps & build the production bundle ────────────
FROM node:22-alpine AS builder 

WORKDIR /app

# Copy only package manifests first → Docker caches the npm install
# layer as long as these files don't change.
COPY package.json package-lock.json* ./
RUN npm install

# Copy the rest of the source and build
COPY . .

# The API URL the browser will hit — defaults to host‑mapped Flask port.
# Override via docker-compose build args if your setup differs.
ARG VITE_API_URL=http://localhost:5000/ask
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build          
# outputs to /app/dist


# ── Stage 2: Serve the static build with nginx ────────────────────
FROM nginx:alpine

# Remove default nginx site
RUN rm /etc/nginx/conf.d/default.conf

# Add our own nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 5173

CMD ["nginx", "-g", "daemon off;"]
