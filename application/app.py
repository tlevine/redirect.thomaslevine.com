import os
import re
from copy import copy
import json
import shutil

from bottle import Bottle, run, request, response

PORT = 9002
try:
    from dev_settings import ROOT
except:
    ROOT = '/'
    DEV = False
else:
    DEV = True

NGINX_SITES = os.path.join(ROOT, 'etc', 'nginx', 'conf.d')

if DEV:
    try:
        shutil.rmtree(NGINX_SITES)
    except OSError:
        pass

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
            response.status = 404
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
            response.status = 400
            return {'error': e.message}

        data = api_request_func(redirect_id)
        if data:
            return json.dumps(data)
        else:
            return ''

    return wrapper

@b.get('/v1/')
@b.post('/v1/')
@b.put('/v1/')
@b.delete('/v1/')
@b.get('/v1')
@b.post('/v1')
@b.put('/v1')
@b.delete('/v1')
def v1():
    response.set_header('Content-Language', 'en')
    response.set_header('Content-Type', 'application/json; charset=utf-8')
    response.status = 400
    return json.dumps({
        'error': 'You must specify a redirect name after /v1/'
    })

@b.get('/v1/<redirect_id>')
@b.get('/v1/<redirect_id>/')
@redirect_must_exist
@api
def get(redirect_id):
    data = _open_nginx_redirect(redirect_id)
    return data

@b.post('/v1/<redirect_id>')
@b.post('/v1/<redirect_id>/')
@redirect_must_exist
@api
def post(redirect_id):
    params = _open_nginx_redirect(redirect_id)

    if 'from' in request.params:
        params['from'] = request.params['from']
    if 'to' in request.params:
        params['to'] = request.params['to']
    if 'status_code' in request.params:
        params['status_code'] = int(request.params.get('status_code', 303))
    if 'email' in request.params:
        params['email'] = request.params.get('email', '')

    if 'from' in params and params['from'] in _current_froms(ROOT, redirect_id):
        response.status = 403
        return { 'error':
            u"There's already a different redirect from %s. If you think "
            u"there shouldn't be, contact Tom." % params['from']
        }
    else:
        f = open(os.path.join(NGINX_SITES, '1-' + redirect_id), 'w')
        f.write(nginx_conf(params))
        f.close()
        response.status = 204

@b.put('/v1/<redirect_id>')
@b.put('/v1/<redirect_id>/')
@api
def put(redirect_id):
    missing_keys = {'from', 'to'}.difference(request.params.keys())
    if missing_keys != set():
        response.status = 400
        return {'error': 'You must specify the following addresses: "%s"' % '","'.join(missing_keys)}

    params = {
        'from': request.params['from'],
        'to': request.params['to'],
        'status_code': int(request.params.get('status_code', 303)),
        'email': request.params.get('email', ''),
    }
        
    if params['from'] in _current_froms(ROOT, redirect_id):
        response.status = 403
        return { 'error':
            u"There's already a different redirect from %s. If you think "
            u"there shouldn't be, contact Tom." % params['from']
        }
    else:
        f = open(os.path.join(NGINX_SITES, '1-' + redirect_id), 'w')
        f.write(nginx_conf(params))
        f.close()
        response.status = 204

@b.delete('/v1/<redirect_id>')
@b.delete('/v1/<redirect_id>/')
@redirect_must_exist
@api
def delete(redirect_id):
    os.remove(redirect_filename(redirect_id))
    response.status = 204

def _validate_redirect_id(redirect_id):
    if '/' in redirect_id:
        raise ValueError('Request identifier contains a slash.')

def _validate_response_code(response_code):
    i = int(response_code)
    if i not in {301, 303}:
        raise ValueError( 'Response code must be 301 or 303.' )

def _validate_domain_name(domain_name):
    for char in ';{} ':
        if char in domain_name:
            raise ValueError('Domain name may not contain "%s".' % char)

    if not domain_name:
        raise ValueError('Domain name may not be empty.')

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
    if len(lines) <= 2:
        # Empty file
        return {}

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
    "Open the redirect file and convert the data to a dictionary."
    f = open(redirect_filename(redirect_id), 'r')
    data = _parse_nginx_redirect(f.read())
    data['to'] = _add_http(data['to'])
    data['from'] = _add_http(data['from'])
    f.close()
    return data

def _current_froms(root, exclude):
    'Currently listed from addresses, excluding the one named $exclude'
    nginx_sites = os.path.join(root, 'etc', 'nginx', 'conf.d')
    froms = set()
    for filename in os.listdir(nginx_sites):
        if filename[0] == '0':
           continue
        elif filename == '1-' + exclude:
           continue
        f = open(os.path.join(nginx_sites, filename), 'r')
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
    run(b, host='localhost', port=PORT)

if __name__ == "__main__":
    main()
