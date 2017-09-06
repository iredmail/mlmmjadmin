import requests
import tsettings

api_headers = {'X-MLMMJ-ADMIN-API-AUTH-TOKEN': tsettings.api_auth_token}

def GET(url, data=None):
    _url = tsettings.url + url
    r = requests.get(_url, data=data, headers=api_headers, verify=False)
    return r.json()

def POST(url, data=None):
    _url = tsettings.url + url
    r = requests.post(_url, data=data, headers=api_headers, verify=False)
    return r.json()

def PUT(url, data=None):
    _url = tsettings.url + url
    r = requests.put(_url, data=data, headers=api_headers, verify=False)
    return r.json()

def DELETE(url, data=None):
    _url = tsettings.url + url
    r = requests.delete(_url, data=data, headers=api_headers, verify=False)
    return r.json()

def DEBUG(*msg):
    print '[DEBUG]', msg
