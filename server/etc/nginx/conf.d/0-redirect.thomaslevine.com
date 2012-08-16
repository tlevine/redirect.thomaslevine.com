server {
  listen 80;
  server_name redirect.thomaslevine.com;

  # This is fine because we don't use cookies or any statefulness.
  add_header Access-Control-Allow-Origin *;

  # Splash page
  index index.html index.htm;
  location / {
    autoindex on;
    alias /srv/splash/;
  }

  # Version 1 of the API
  rewrite ^\/v1\/([^\s/]+)\/?$  /v1/?id=$1;
  location /v1 {
    fastcgi_param DOCUMENT_ROOT /srv/v1;
    fastcgi_param SCRIPT_NAME app.py;
    fastcgi_param SCRIPT_FILENAME /srv/v1/app.py;

    # Fill in the gaps. This does not overwrite previous settings,
    # so it goes last
    include /etc/nginx/fastcgi_params;
    fastcgi_pass unix:/var/run/fcgiwrap.socket;
  }
}
