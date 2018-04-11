import settings


def __get_dict_for_boolean_params(form, param):
    kv = {}

    if param in form:
        v = form.get(param, '')

        if v not in ['yes', 'no']:
            return kv

        kv = {settings.MLMMJ_BOOLEAN_WEB_PARAMS[param]: v}

    return kv


def __get_dict_for_list_params(mail, form, param):
    kv = {}

    mail = str(mail).lower()
    (listname, domain) = mail.split('@', 1)

    _separator = ','
    # customer_headers: Split multiple values by '\n'
    if param == 'custom_headers':
        _separator = '\n'

    _values = []

    _v = form.get(param, '')
    if _v:
        _values = _v.split(_separator)
        _values = [i.strip() for i in _values if i]
        _values.sort()

    if param == 'custom_headers':
        # Remove invalid header
        _values = [v for v in _values if ':' in v]

        # Add default custom headers
        _new = []
        _default_custom_header_names = [v.lower() for v in settings.MLMMJ_DEFAULT_CUSTOM_HEADERS.keys()]
        for v in _values:
            (_header, _v) = v.split(':')
            if _header.lower() not in _default_custom_header_names:
                _new.append(v)

        _default_custom_headers = dict(settings.MLMMJ_DEFAULT_CUSTOM_HEADERS)
        for (k, v) in _default_custom_headers.items():
            # for placeholder support
            v = v % {'mail': mail, 'domain': domain, 'listname': listname}
            _new.append('{0}: {1}'.format(k, v))

        _values = _new

    if param == 'remove_headers':
        # Make sure header ends with ':'
        for (_index, v) in enumerate(_values):
            if not v.endswith(':'):
                _values[_index] = v + ':'

        # Remove default headers
        _values_lower = [v.lower() for v in _values]
        _default_removed_headers = list(settings.MLMMJ_DEFAULT_REMOVED_HEADERS)
        for v in _default_removed_headers:
            if v.lower() not in _values_lower:
                _values.append(v)

    # Always return a dict even value is empty.
    kv = {settings.MLMMJ_LIST_WEB_PARAMS[param]: _values}

    return kv


def __get_dict_for_normal_params(form, param):
    kv = {}

    v = form.get(param, '')

    # Always return a dict even value is empty.
    kv = {settings.MLMMJ_NORMAL_WEB_PARAMS[param]: v}

    return kv


def __get_dict_for_text_params(form, param):
    kv = {}

    v = form.get(param, '')

    # Always return a dict even value is empty.
    kv = {settings.MLMMJ_TEXT_WEB_PARAMS[param]: v}

    return kv


def get_dict_for_form_param(mail, form, param):
    kv = {}

    if param in settings.MLMMJ_BOOLEAN_WEB_PARAMS:
        kv = __get_dict_for_boolean_params(form=form, param=param)
    elif param in settings.MLMMJ_LIST_WEB_PARAMS:
        kv = __get_dict_for_list_params(mail=mail, form=form, param=param)
    elif param in settings.MLMMJ_NORMAL_WEB_PARAMS:
        kv = __get_dict_for_normal_params(form=form, param=param)
    elif param in settings.MLMMJ_TEXT_WEB_PARAMS:
        kv = __get_dict_for_text_params(form=form, param=param)
    elif param in settings.MLMMJ_OTHER_WEB_PARAMS:
        kv = {param: form.get(param)}

    return kv


def get_max_message_size(form):
    """Get max message size (in bytes)."""
    size = form.get('max_message_size')
    try:
        size = int(size)
    except:
        size = 0

    return size
