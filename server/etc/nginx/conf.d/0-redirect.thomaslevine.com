wsgi_python_executable  /usr/bin/python;

server {
  listen 80;
  server_name redirect.thomaslevine.com;

  # This is fine because we don't use cookies or any statefulness.
  # But we also don't need it.
  # add_header Access-Control-Allow-Origin *;

# # Splash page
# index index.html index.htm;
# location / {
#   autoindex on;
#   alias /srv/splash/;
# }

  # Version 1 of the API
  root /srv/v1;
  include /etc/nginx/wsgi_vars;
  location / {
    wsgi_pass /srv/v1/app.py;
  }
}
