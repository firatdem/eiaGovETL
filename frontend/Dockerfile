# Build step
FROM node:22-alpine@sha256:ce8d97f7cfc7c5386421eb932df20a29df99b1a7f469f6157d5c9956702ffadc AS build

WORKDIR /app

# Copy only the frontend folder into the container
COPY ./frontend/ /app/

# Install the audited dependency set without re-resolving it during the build.
RUN npm ci && npm run build

# Production image
FROM nginx:alpine@sha256:892bb2152464f0c5d8972593a5f5afaf8054552580b699d95f8ff4af08c2d33d

# Copy the built frontend from previous stage
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
