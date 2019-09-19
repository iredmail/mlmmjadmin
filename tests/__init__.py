import requests
import settings

# Use first api token defined in `settings.py`.
base_url = 'http://127.0.0.1:7790'
api_auth_token = settings.api_auth_tokens[0]
api_headers = {settings.API_AUTH_TOKEN_HEADER_NAME: api_auth_token}


def get(url, data=None):
    _url = base_url + url
    r = requests.get(_url, data=data, headers=api_headers, verify=False)
    return r.json()


def post(url, data=None):
    _url = base_url + url
    r = requests.post(_url, data=data, headers=api_headers, verify=False)
    return r.json()


def put(url, data=None):
    _url = base_url + url
    r = requests.put(_url, data=data, headers=api_headers, verify=False)
    return r.json()


def delete(url, data=None):
    _url = base_url + url
    r = requests.delete(_url, data=data, headers=api_headers, verify=False)
    return r.json()


def debug(*msg):
    print(('[DEBUG] {}'.format(msg)))
