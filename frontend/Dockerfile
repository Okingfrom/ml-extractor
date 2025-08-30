# Frontend Dockerfile - build React app and serve via nginx
ARG REACT_APP_API_URL=http://localhost:8010
FROM node:18-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
COPY public ./public
COPY src ./src
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=${REACT_APP_API_URL}
RUN npm ci && npm run build

FROM nginx:stable-alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
