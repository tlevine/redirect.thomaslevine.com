server {
  listen 80;
  server_name redirect.thomaslevine.com;

  # Splash page
  index index.html index.htm;
  location / {
    autoindex on;
    alias /srv/splash/;
  }

  # Version 1 of the API
  location / {
    proxy_pass        http://localhost:9002;
    proxy_set_header  X-Real-IP  $remote_addr;
  }
}
