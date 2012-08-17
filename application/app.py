import os
import re
from copy import copy
import json
from bottle import Bottle, run, request, response

import settings
if __name__ == "__main__":
    ROOT = settings.ROOT_PRODUCTION
else:
    ROOT = settings.ROOT_TEST

NGINX_SITES = os.path.join(ROOT, 'etc', 'nginx', 'conf.d')
try:
    os.makedirs(NGINX_SITES)
except OSError:
    pass
def redirect_filename(redirect_id):
    return os.path.join(NGINX_SITES, '1-' + redirect_id)


b = Bottle()

def redirect_must_exist(api_request_func):
    'Return an HTTP error if the redirect doesn\'t exist.'

    def wrapper(redirect_id):
        if os.path.isfile(redirect_filename(redirect_id)):
            return api_request_func(redirect_id)
        else:
            # The redirect file doesn't exist
            return { "error": "That redirect doesn't exist. Use PUT to create it." }

    return wrapper

def api(api_request_func):
    'This stuff applies to all requests.'

    def wrapper(redirect_id):
        # Standard response header
        response.set_header('Content-Language', 'en')
        response.set_header('Content-Type', 'application/json; charset=utf-8')

        # Validate the redirect_id
        try:
            _validate_redirect_id(redirect_id)
        except ValueError, e:
            raise BadRequest(e.message)

        data = api_request_func(redirect_id)
        if data:
            return json.dumps(data)
        else:
            return ''

    return wrapper

@b.get('/v1/<redirect_id>')
@redirect_must_exist
@api
def get(redirect_id):
    data = _open_nginx_redirect(redirect_id)
    return data

@b.post('/v1/<redirect_id>')
@redirect_must_exist
@api
def post(redirect_id):
    data = _open_nginx_redirect(redirect_id)
    return data

@b.put('/v1/<redirect_id>')
@api
def put(redirect_id):
    missing_keys = {'from', 'to'}.difference(request.query.keys())
    if len(missing_keys) != 0:
        response.status = 400
        return {'error': 'You must specify the following addresses: "%s"' % '","'.join(missing_keys)}

    params = {
        'from': request.query['from'].encode('utf-8'),
        'to': request.query['to'].encode('utf-8'),
        'status_code': int(request.query.get('status_code', 303)),
        'email': request.query.get('email', '').encode('utf-8'),
    }
        
    if params['from'] in _current_froms(ROOT, redirect_id):
        response.status = 403
        return { 'error':
            "There's already a different redirect from %s. If you think"
            "there shouldn't be, contact Tom." % redirect_id
        }
    else:
        f = open(os.path.join(NGINX_SITES, '1-' + redirect_id), 'w')
        f.write(nginx_conf(params))
        f.close()
        response.status = 204
        return

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
    f = open(redirect_filename(redirect_id), 'r')
    data = _parse_nginx_redirect(f.read())
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

def main():
    run(b, host='localhost', port=9002)

if __name__ == "__main__":
    main()
