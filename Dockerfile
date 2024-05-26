FROM nginx:alpine

COPY apiparingud.js /usr/share/nginx/html/apiparingud.js
COPY index.html /usr/share/nginx/html/index.html

EXPOSE 80