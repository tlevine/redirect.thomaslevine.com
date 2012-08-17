server {
  listen 80;
  server_name redirect.thomaslevine.com;


  # Splash page
  index index.html index.htm;
  location / {
    autoindex on;
    alias /srv/splash/;
  }

  # In case people try to access the form from a to-be-redirected url
  add_header Access-Control-Allow-Origin *;
  # Version 1 of the API
  location /v1 {
    proxy_pass        http://localhost:9002;
    proxy_set_header  X-Real-IP  $remote_addr;
  }
}
