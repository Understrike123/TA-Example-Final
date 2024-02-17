# Gunakan image NGINX resmi sebagai base image
FROM nginx:latest

# Salin konfigurasi NGINX ke dalam kontainer
COPY nginx.conf /etc/nginx/nginx.conf
