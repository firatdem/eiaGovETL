# Build step
FROM node:20-alpine as build

WORKDIR /app

# Copy only the frontend folder into the container
COPY ./frontend/ /app/

# Install required dependencies (including chart.js)
RUN npm install chart.js react-chartjs-2 && \
    npm install --save-dev @types/chart.js && \
    npm install && npm run build

# Production image
FROM nginx:alpine

# Copy the built frontend from previous stage
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
