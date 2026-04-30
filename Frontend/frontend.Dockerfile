FROM nginx:alpine

COPY index.html /usr/share/nginx/html/index.html

COPY floater.html /usr/share/nginx/html
COPY login.html /usr/share/nginx/html
COPY register.html /usr/share/nginx/html
COPY commandant.html /usr/share/nginx/html

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80