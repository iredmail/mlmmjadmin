from . import get, post, delete, debug
from . import data


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
    assert _json['_success'] is True

    _json = get(url=url)
    assert _json['_success'] is True

    # Verify mlmmj parameters
    _data = _json['_data']
    params = data.params_create_verify
    for _param in params:
        _expected = params[_param]
        _real = _data[_param]

        if isinstance(_expected, list):
            _expected.sort()

        if isinstance(_real, list):
            _real.sort()

        # For debug purpose, print related data for troubleshooting
        if _real != _expected:
            # debug(_data)
            debug('[{}] expected value: {}'.format(_param, _expected))
            debug('[{}]     real value: {}'.format(_param, _real))

        assert _real == _expected

    if _remove_ml:
        remove_ml()
