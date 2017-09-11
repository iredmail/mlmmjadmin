from . import get, post, delete, debug
import data


def remove_ml(archive=False):
    url = data.url_ml
    if archive:
        url = url + '?archive=yes'
    else:
        url = url + '?archive=no'

    _json = delete(url=url)
    assert _json['_success'] is True

    _json = get(url=url)
    assert _json['_success'] is False
    assert _json['_msg'] == 'NO_SUCH_ACCOUNT'


def create_ml(_remove_ml=False):
    url = data.url_ml

    # Remove first.
    remove_ml()
    _json = get(url=url)
    assert _json['_success'] is False
    assert _json['_msg'] == 'NO_SUCH_ACCOUNT'

    # Create a new one
    params = data.params_create_ml
    _json = post(url=url, data=params)
    # print _json
    assert _json['_success'] is True

    _json = get(url=url)
    assert _json['_success'] is True

    # Verify mlmmj parameters
    _data = _json['_data']
    params = data.params_create_verify
    for _param in params:
        # For debug purpose, print related data for troubleshooting
        if _data[_param] != params[_param]:
            debug(_data)
            debug(_param, _data.get(_param), params.get(_param))

        assert _data[_param] == params[_param]

    if _remove_ml:
        remove_ml()
