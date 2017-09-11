import requests
import settings
import tsettings

api_headers = {settings.API_AUTH_TOKEN_HEADER_NAME: tsettings.api_auth_token}


def get(url, data=None):
    _url = tsettings.url + url
    r = requests.get(_url, data=data, headers=api_headers, verify=False)
    return r.json()


def post(url, data=None):
    _url = tsettings.url + url
    r = requests.post(_url, data=data, headers=api_headers, verify=False)
    return r.json()


def put(url, data=None):
    _url = tsettings.url + url
    r = requests.put(_url, data=data, headers=api_headers, verify=False)
    return r.json()


def delete(url, data=None):
    _url = tsettings.url + url
    r = requests.delete(_url, data=data, headers=api_headers, verify=False)
    return r.json()


def debug(*msg):
    print '[DEBUG]', msg
