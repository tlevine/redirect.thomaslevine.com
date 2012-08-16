import re

def _validate_request_id(request_id):
    if '/' in request_id:
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

def _current_froms():
    return set()
