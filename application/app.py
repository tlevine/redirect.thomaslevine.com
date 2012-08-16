import os
import re
from copy import copy
import json
import web

from settings import ROOT
NGINX_SITES = os.path.join(ROOT, 'etc', 'nginx', 'conf.d')
try:
    os.makedirs(NGINX_SITES)
except OSError:
    pass

urls = (
    '/v1/(.+)/?', 'redirects'
)
app = web.application(urls, globals())

def api(api_request_func):
    'This stuff applies to all requests.'

    def wrapper(self, redirect_id):
        # JSON
        web.header('Content-Type', 'application/json; charset=utf-8')

        # Validate the redirect_id
        try:
            _validate_redirect_id(redirect_id)
        except ValueError, e:
        #   return {'error': e.message}
            raise BadRequest(e.message)

        data = api_request_func(self, redirect_id)
        if data and type(data) == dict:
            return json.dumps(data)
        else:
            return ''

    return wrapper

class redirects:
    @api
    def GET(self, redirect_id):
        try:
            data = _open_nginx_redirect(redirect_id)
        except OSError:
            raise NotFound()
        else:
            return data

    @api
    def PUT(self, redirect_id):
        params = web.input()
        if params['from'] in _current_froms(ROOT, redirect_id):
            raise Forbidden(
                "There's already a different redirect from %s. If you think"
                "there shouldn't be, contact Tom." % redirect_id
            )
        else:
            f = open(os.path.join(NGINX_SITES, '1-' + redirect_id), 'w')
            f.write(nginx_conf(params))
            f.close()
            return

    @api
    def POST(self, redirect_id):
        return {}

    @api
    def DELETE(self, redirect_id):
        return {}

def _validate_redirect_id(redirect_id):
    if '/' in redirect_id:
        raise ValueError('Request identifier contains a slash.')

def _validate_response_code(response_code):
    i = int(response_code)
    if i not in {301, 303}:
        raise ValueError( 'Response code must be 301 or 303.' )

def _validate_domain_name(domain_name):
    for char in ';{}':
        if char in domain_name:
            raise ValueError('Domain name may not contain "%s".' % char)

def _add_http(url):
    if re.match(r'^https?://.*', url):
        return url
    else:
        return 'http://' + url

def _remove_http(url):
    return re.sub(r'^https?://', '', url)

def _parse_nginx_redirect(conf):
    '''
    Parse the information of concern from an nginx redirect conf file.

    The configuration file looks like this
    server {
        listen       80;
        server_name  www.thomaslevine.org;
        return       303 http://www.thomaslevine.com$request_uri;
        # email occurrence@example.com;
    }
    '''

    # Regular expression matches
    lines = conf.split('\n')
    l2 = re.match(r'^\s+server_name\s+([^;]+);$', lines[2])
    l3 = re.match(r'^\s+return\s+(301|303)\s+([^$]+)\$request_uri;$', lines[3])
    l4 = re.match(r'^\s+# email\s+([^;]*);$', lines[4])
    url_from = l2.group(1)
    status_code = int(l3.group(1))
    url_to = l3.group(2)
    email = l4.group(1)
    
    return {
        'to': url_to,
        'from': url_from,
        'status_code': status_code,
        'email': email,
    }


def _open_nginx_redirect(redirect_id):
    filename = os.path.join(NGINX_SITES, '1-' + redirect_id)
    f = open(filename, 'r')
    data = _parse_nginx_conf(f.read())
    f.close()
    return data

def _current_froms(root, exclude):
    'Currently listed from addresses, excluding the one named $exclude'
    confdir = os.path.join(root, 'etc', 'nginx', 'conf.d')
    froms = set()
    for filename in os.listdir(confdir):
        if filename[0] == '0':
           continue
        elif filename == '1-' + exclude:
           continue
        f = open(os.path.join(confdir, filename), 'r')
        froms.add(_parse_nginx_redirect(f.read())['from'])
        f.close()
    return froms

def nginx_conf(orig_params):
    "Write the nginx configuration, validating and adding or removing the protocal."
    params = copy(orig_params)

    # Validation
    _validate_response_code(params['status_code'])
    _validate_domain_name(params['from'])
    _validate_domain_name(params['to'])

    params['from'] = _remove_http(params['from'])
    params['to'] = _add_http(params['to'])
    return '''server {
  listen      80;
  server_name %(from)s;
  return      %(status_code)d %(to)s$request_uri;
  # email     %(email)s;
}
''' % params

if __name__ == "__main__":
    app.run()
