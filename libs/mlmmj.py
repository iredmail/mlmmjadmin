import os
import shutil
import time
import glob
import subprocess
import web

from libs import utils, form_utils
from libs.logger import logger
import settings


subscription_versions = ['normal', 'nomail', 'digest']

def __get_ml_dir(mail):
    """Get absolute path of the root directory of mailing list account."""
    if not utils.is_email(mail):
        return None

    mail = str(mail).lower()
    (_username, _domain) = mail.split('@', 1)

    return os.path.join(settings.MLMMJ_SPOOL_DIR, _domain, _username)


def __get_ml_subscribers_dir(mail, subscription):
    """
    Get absolute path of the directory used to store subscribers which
    subscribed to given subscription version.

    @mail -- mail address of mailing list account
    @subscription -- subscription version: normal, nomail, digest.
    """
    if subscription == 'digest':
        return os.path.join(__get_ml_dir(mail=mail), 'digesters.d')
    elif subscription == 'nomail':
        return os.path.join(__get_ml_dir(mail=mail), 'nomailsubs.d')
    else:
        # subscription == 'normal'
        return os.path.join(__get_ml_dir(mail=mail), 'subscribers.d')


def __remove_ml_sub_dir(mail, dirname):
    if not dirname:
        return (True, )

    _ml_dir = __get_ml_dir(mail=mail)
    _sub_dir = os.path.join(_ml_dir, dirname)

    if os.path.exists(_sub_dir):
        try:
            shutil.rmtree(_sub_dir)
            logger.debug("[{}] {}, removed sub-directory: {}".format(web.ctx.ip, mail, _sub_dir))
        except Exception, e:
            logger.error("[{}] {}, error while removing sub-directory: {}".format(web.ctx.ip, mail, _sub_dir))
            return (False, repr(e))

    return (True, )


def __set_file_permission(path):
    _uid = os.getuid()
    _gid = os.getgid()

    try:
        os.chown(path, _uid, _gid)
        return (True, )
    except Exception, e:
        return (False, repr(e))


def __copy_dir_files(src, dest, create_dest=True):
    """Copy all regular files under source directory to dest directory."""
    if create_dest:
        if not os.path.exists(dest):
            try:
                os.makedirs(dest, mode=settings.MLMMJ_FILE_PERMISSION)
            except Exception, e:
                return (False, repr(e))

    for fn in os.listdir(src):
        _src_file = os.path.join(src, fn)
        if os.path.isfile(_src_file):
            shutil.copy(_src_file, dest)

    return (True, )


def __has_ml_dir(mail, path=None):
    if path:
        _ml_dir = path
    else:
        _ml_dir = __get_ml_dir(mail=mail)

    if os.path.exists(_ml_dir):
        return True
    else:
        return False


def __has_param_file(f):
    if os.path.exists(f):
        return True
    else:
        return False


def __get_param_file(mail, param):
    """Get path to the file used to control parameter setting.

    Sample value: /var/spool/mlmmj/<domain>/<username>/control/<param>
    """
    if not utils.is_email(mail):
        return None

    (_username, _domain) = mail.split('@', 1)

    return os.path.join(settings.MLMMJ_SPOOL_DIR,
                        _domain,
                        _username,
                        'control',
                        param)


def __remove_file(path):
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception, e:
            logger.error("[{}] error while removing parameter file: {}, {}".format(web.ctx.ip, path, e))
            return (False, repr(e))

    return (True, )


def __get_param_type(param):
    """Get parameter type.

    Possible param type must be one of: boolean, list, normal, text, or None (no such
    param).
    """
    for (_type, _param_dict) in settings.MLMMJ_PARAM_TYPES.items():
        if param in _param_dict.values():
            return _type

    return None


def __get_boolean_param_value(mail, param):
    _param_file = __get_param_file(mail=mail, param=param)

    if __has_param_file(_param_file):
        return 'yes'
    else:
        return 'no'


def __get_list_param_value(mail, param, is_email=False):
    _param_file = __get_param_file(mail=mail, param=param)

    _values = []
    if __has_param_file(_param_file):
        try:
            with open(_param_file, 'r') as f:
                _lines = f.readlines()
                _lines = [_line.strip() for _line in _lines]  # remove line breaks
                _values = [_line for _line in _lines if _line]  # remove empty values

                if is_email:
                    _values = [str(i).lower() for i in _values]
        except IOError:
            # No such file.
            pass
        except Exception, e:
            logger.error('Error while getting (list) parameter value: {} -> {}'.format(param, e))

    _values.sort()
    return _values


def __get_normal_param_value(mail, param, param_file=None):
    # Only first line is used by mlmmj.
    if not param_file:
        param_file = __get_param_file(mail=mail, param=param)

    try:
        with open(param_file, 'r') as f:
            value = f.readline()
            return value
    except IOError:
        # No such file.
        return ''
    except Exception, e:
        logger.error("[{}] {}, error while getting parameter value: {}, {}".format(web.ctx.ip, mail, param, e))
        return ''

    return ''


def __get_text_param_value(mail, param, param_file=None):
    # Full content is used by mlmmj.
    if not param_file:
        param_file = __get_param_file(mail=mail, param=param)

    try:
        with open(param_file, 'r') as f:
            value = f.read()
            return value
    except IOError:
        # No such file.
        return ''
    except Exception, e:
        logger.error("[{}] {}, error while getting parameter value: {}, {}".format(web.ctx.ip, mail, param, e))
        return ''

    return ''


def __get_other_param_value(mail, param):
    if param in settings.MLMMJ_OTHER_PARAM_MAP:
        _v = settings.MLMMJ_OTHER_PARAM_MAP[param]
        _param_type = _v['type']
        _mlmmj_param = _v['mlmmj_param']
        _is_email = _v.get('is_email', False)

        if _param_type == 'boolean':
            return __get_boolean_param_value(mail=mail, param=_mlmmj_param)
        elif _param_type == 'list':
            return __get_list_param_value(mail, param=_mlmmj_param, is_email=_is_email)
        elif _param_type == 'normal':
            return __get_normal_param_value(mail, param=_mlmmj_param)
        elif _param_type == 'text':
            return __get_text_param_value(mail, param=_mlmmj_param)

    return 'INVALID_PARAM'


def __get_param_value(mail, param):
    """Get value of given mailing list parameter.

    Possible returned values:

    - (False, <error_reason>)
    - (True, {'type': 'boolean', 'value': 'yes|no'})
    - (True, {'type': 'list', 'value': [...]})
    - (True, {'type': 'normal', 'value': '...'})
    - (True, {'type': 'text', 'value': '...'})
    - None: no such param.
    """
    if param in settings.MLMMJ_OTHER_WEB_PARAMS:
        _v = settings.MLMMJ_OTHER_PARAM_MAP[param]
        _param_type = _v['type']
        _value = __get_other_param_value(mail=mail, param=param)

        return (True, {'type': _param_type, 'value': _value})

    if param not in settings.MLMMJ_PARAMS:
        logger.error("[{}] {}, unknown parameter: {}".format(web.ctx.ip, mail, param))
        return (False, 'INVALID_PARAM')

    _param_file = __get_param_file(mail=mail, param=param)
    _param_type = __get_param_type(param=param)
    _ret = {'type': _param_type, 'value': None}

    # control file doesn't exist
    if not __has_param_file(_param_file):
        if _param_type == 'list':
            _ret['value'] = []
        elif _param_type == 'boolean':
            _ret['value'] = 'no'
        else:
            _ret['value'] = ''

        return (True, _ret)

    if _param_type == 'boolean':
        _ret['value'] = 'yes'
    else:
        with open(_param_file) as f:
            if _param_type == 'normal':
                _line = f.readline()
                _ret['value'] = _line
            elif _param_type == 'text':
                _text = f.read()
                _ret['value'] = _text
            elif _param_type == 'list':
                # Get all lines
                _lines = [_line.strip() for _line in f]

                # Remove empty values
                _lines = [_line for _line in _lines if _line]

                _ret['value'] = _lines

    return (True, _ret)


def __update_boolean_param(mail, param, value, param_file=None, touch_instead_of_create=False):
    """Create or remove parameter file for boolean type parameter.

    @touch_instead_of_create - touch parameter file instead of re-create it.
    """
    if not param_file:
        param_file = __get_param_file(mail=mail, param=param)

    if value == 'yes':
        try:
            if touch_instead_of_create:
                open(param_file, 'a').close()
            else:
                open(param_file, 'w').close()

            if param in ['modonlypost']:
                # Create 'control/moderated' also
                _f = __get_param_file(mail=mail, param='moderated')
                open(_f, 'a').close()

        except Exception, e:
            logger.error("[{}] {}, error while updating (boolean) parameter: {} -> {}, {}".format(
                web.ctx.ip, mail, param, value, e))
            return (False, repr(e))
    else:
        qr = __remove_file(path=param_file)
        if not qr[0]:
            return qr

    logger.info("[{}] {}, updated (boolean) parameter: {} -> {}".format(web.ctx.ip, mail, param, value))
    return (True, )


def __update_normal_param(mail, param, value, param_file=None, is_email=False):
    # Although we write all given value, but only first line is used by mlmmj.
    if not param_file:
        param_file = __get_param_file(mail=mail, param=param)

    if param == 'maxmailsize':
        try:
            value = int(value)
        except:
            value = 0

        if not value:
            # Remove param file.
            qr = __remove_file(path=param_file)
            return qr

    if value:
        if is_email:
            value = str(value).lower()
            if not utils.is_email(value):
                return (False, 'INVALID_EMAIL')

        try:
            if isinstance(value, int):
                value = str(value)

            value = value.encode('utf-8')

            with open(param_file, 'w') as f:
                f.write(value)
        except Exception, e:
            logger.error("[{}] {}, error while updating (normal) parameter: {} -> {}, {}".format(
                web.ctx.ip, mail, param, value, e))
            return (False, repr(e))
    else:
        qr = __remove_file(path=param_file)
        if not qr[0]:
            return qr

    logger.info("[{}] {}, updated (normal) parameter: {} -> {}".format(web.ctx.ip, mail, param, value))
    return (True, )


def __update_list_param(mail, param, value, param_file=None, is_email=False):
    if not param_file:
        param_file = __get_param_file(mail=mail, param=param)

    if isinstance(value, (str, unicode)):
        _values = __convert_web_param_value_to_list(value=value, is_email=is_email)
    else:
        _values = value

    if _values:
        try:
            param_file = __get_param_file(mail=mail, param=param)
            with open(param_file, 'w') as f:
                f.write('\n'.join(_values) + '\n')

            logger.info("[{}] {}, updated: {} -> {}".format(web.ctx.ip, mail, param, ', '.join(_values)))
        except Exception, e:
            logger.error("[{}] {}, error while updating (list) parameter: {} -> {}, {}".format(
                web.ctx.ip, mail, param, value, e))
            return (False, repr(e))
    else:
        qr = __remove_file(path=param_file)
        if not qr[0]:
            return qr

    logger.info("[{}] {}, updated (list) parameter: {} -> {}".format(web.ctx.ip, mail, param, value))
    return (True, )


def __update_text_param(mail, param, value, param_file=None):
    if not param_file:
        param_file = __get_param_file(mail=mail, param=param)

    if value:
        try:
            if isinstance(value, int):
                value = str(value)
            else:
                value = value.strip()

            value = value.encode('utf-8')

            # Footer text/html must ends with an empty line, otherwise
            # the characters will be a mess.
            with open(param_file, 'w') as f:
                f.write(value + '\n')
        except Exception, e:
            logger.error("[{}] {}, error while updating (normal) parameter: {} -> {}, {}".format(
                web.ctx.ip, mail, param, value, e))
            return (False, repr(e))
    else:
        qr = __remove_file(path=param_file)
        if not qr[0]:
            return qr

    logger.info("[{}] {}, updated (text) parameter: {} -> {}".format(web.ctx.ip, mail, param, value))
    return (True, )


def __update_other_param(mail, param, value):
    """Update parameters which cannot be simply mapped to a mlmmj parameter."""
    if param in settings.MLMMJ_OTHER_PARAM_MAP:
        _v = settings.MLMMJ_OTHER_PARAM_MAP[param]
        _param_type = _v['type']
        _mlmmj_param = _v['mlmmj_param']
        _is_email = _v.get('is_email', False)
        _param_file = __get_param_file(mail=mail, param=_mlmmj_param)

        if _param_type == 'boolean':
            return __update_boolean_param(mail=mail,
                                          param=_mlmmj_param,
                                          param_file=_param_file,
                                          value=value,
                                          touch_instead_of_create=True)
        elif _param_type == 'list':
            return __update_list_param(mail=mail,
                                       param=_mlmmj_param,
                                       param_file=_param_file,
                                       value=value,
                                       is_email=_is_email)
        elif _param_type == 'normal':
            return __update_normal_param(mail=mail,
                                         param=_mlmmj_param,
                                         param_file=_param_file,
                                         value=value,
                                         is_email=_is_email)
        elif _param_type == 'text':
            return __update_text_param(mail=mail,
                                       param=_mlmmj_param,
                                       param_file=_param_file,
                                       value=value)

    return (True, )


def __update_mlmmj_param(mail, param, value):
    """Update individual parameter of mailing list account."""
    _param_type = __get_param_type(param)

    if _param_type == 'boolean':
        _update_func = __update_boolean_param
    elif _param_type == 'normal':
        _update_func = __update_normal_param
    elif _param_type == 'list':
        _update_func = __update_list_param
    elif _param_type == 'text':
        _update_func = __update_text_param
    elif _param_type == 'other':
        _update_func = __update_other_param
    else:
        logger.error("[{}] {}, unknown parameter: {}".format(web.ctx.ip, mail, param))
        return (False, 'INVALID_PARAM_TYPE')

    qr = _update_func(mail=mail, param=param, value=value)
    return qr


def __update_mlmmj_params(mail, **kwargs):
    """Update multiple parameters of mailing list account. Abort if failed to
    update any parameter.

    Parameters must be used by mlmmj directly, not the ones used by web form.
    """
    if kwargs:
        for (k, v) in kwargs.items():
            qr = __update_mlmmj_param(mail=mail, param=k, value=v)
            if not qr[0]:
                return qr

    return (True, )


def __convert_web_param_value_to_list(value, is_email=False):
    try:
        # Split by ',' and remove empty values
        v = [i for i in value.replace(' ', '').split(',') if i]
    except:
        v = []

    if v and is_email:
        v = [str(i).lower() for i in v if utils.is_email(i)]

    return v


def __convert_form_to_mlmmj_params(mail, form):
    """Convert variables in web form to (a dict of) mlmmj parameters."""
    # Both 'moderate_subscription' and 'subscription_moderators' use same
    # mlmmj parameter name 'submod'
    if 'moderate_subscription' in form and 'subscription_moderators' in form:
        _mod = form.get('moderate_subscription')
        _moderators = form.get('subscription_moderators')

        if _mod == 'yes':
            if _moderators:
                # If there's some moderators, it will create 'submod' file
                # with emails of moderators. If file 'submod' presents, it
                # means moderation subscription is enabled. So we should remove
                # 'moderate_subscription' parameter here to avoid improper
                # file removal or re-creation (with empty content)
                form.pop('moderate_subscription')
            else:
                # If no subscription moderators, use an empty 'submod' file
                # and use mailing list owners as subscription moderators.
                form.pop('subscription_moderators')
        else:
            # remove 'subscription_moderators' and let mlmmj-admin remove
            # 'submod' directly.
            form.pop('subscription_moderators')

    # solve conflict of 'only_moderator_can_post' and 'only_subscriber_can_post'
    # 'only_moderator_can_post' should has higher priority
    if 'only_moderator_can_post' in form and 'only_subscriber_can_post' in form:
        if form.get('only_moderator_can_post') == 'yes':
            form['only_subscriber_can_post'] = 'no'

    # Store key:value of mlmmj parameters
    kvs = {}

    # Convert form variable names to mlmmj parameter names
    for param in form:
        kv = form_utils.get_dict_for_form_param(mail=mail, form=form, param=param)
        kvs.update(kv)

    return kvs


def __archive_ml(mail):
    _dir = __get_ml_dir(mail=mail)

    if __has_ml_dir(mail=mail, path=_dir):
        _timestamp = time.strftime('-%Y%m%d%H%M%S', time.gmtime())
        _new_dir = _dir + _timestamp

        if settings.MLMMJ_ARCHIVE_DIR:
            # Move to archive directory.
            __base_dir = _new_dir.replace(settings.MLMMJ_SPOOL_DIR, settings.MLMMJ_ARCHIVE_DIR)
            _new_dir = os.path.join(settings.MLMMJ_ARCHIVE_DIR, __base_dir)

            # Create parent directory
            if _new_dir.endswith('/'):
                _new_dir = os.path.dirname(_new_dir)

        # If new directory exists, append one more timestamp
        if os.path.exists(_new_dir):
            _new_dir = _new_dir + _timestamp

        # Create archive directory
        try:
            os.makedirs(_new_dir, mode=settings.MLMMJ_FILE_PERMISSION)
        except Exception, e:
            _msg = "error while creating directory under archive directory ({}), {}".format(_new_dir, repr(e))
            logger.error("[{}] {}, {}".format(web.ctx.ip, mail, _msg))
            return (False, _msg)

        try:
            os.rename(_dir, _new_dir)
            logger.info("[{}] {}, archived: {} -> {}".format(web.ctx.ip, mail, _dir, _new_dir))

            # Return new directory path
            return (True, _new_dir)
        except Exception, e:
            logger.error("[{}] {}, error while archiving: {} ({} -> {})".format(web.ctx.ip, mail, e, _dir, _new_dir))
            return (False, repr(e))

    return (True, )


def __remove_lines_in_file(f, lines):
    """
    Remove line from given file.

    @f -- path to file
    @lines -- a list/dict/tuple of lines you want to remove
    """
    if not lines:
        return (True, )

    if not os.path.exists(f):
        return (True, )

    try:
        with open(f, 'r') as _f:
            file_lines = _f.readlines()

        if len(lines) == 1:
            for l in file_lines:
                _l = l.strip()
                for line in lines:
                    if _l == line:
                        file_lines.remove(l)
                        if file_lines:
                            with open(f, 'w') as nf:
                                nf.write(''.join(file_lines))
                        else:
                            # Remove file
                            qr = __remove_file(path=f)
                            if not qr[0]:
                                return qr

                        break
        else:
            stripped_file_lines = [l.strip().lower() for l in file_lines]
            given_lines = [l.strip().lower() for l in lines]

            filtered_lines = set(stripped_file_lines) - set(given_lines)
            if filtered_lines:
                with open(f, 'w') as nf:
                    nf.write(''.join(filtered_lines))
            else:
                # Remove file
                __remove_file(path=f)
                if not qr[0]:
                    return qr

        return (True, )
    except Exception, e:
        return (False, repr(e))


def __add_lines_in_file(f, lines, sort_before_saving=True):
    """
    Add lines to given file.

    @f -- path to file
    @lines -- a list/dict/tuple of lines you want to remove
    @sort_before_saving -- A switch to sort lines before saving.
    """
    if not lines:
        return (True, )

    file_lines = []
    try:
        if os.path.exists(f):
            with open(f, 'r') as _f:
                file_lines = _f.readlines()

        lines = [i + '\n' for i in lines]
        file_lines += lines

        if sort_before_saving:
            file_lines.sort()

        with open(f, 'w') as nf:
            nf.write(''.join(file_lines))

        return (True, )
    except Exception, e:
        return (False, repr(e))


def __add_subscribers_with_confirm(mail,
                                   subscribers,
                                   subscription='normal'):
    """
    Add subscribers with confirm.

    @mail -- mail address of mailing list
    @subscribers -- a list/tuple/set of subscribers' mail addresses
    @subscription -- subscription version (normal, digest, nomail)
    """
    _dir = __get_ml_dir(mail)

    # Get absolute path of command `mlmmj-sub`
    _cmd_mlmmj_sub = settings.CMD_MLMMJ_SUB
    if not _cmd_mlmmj_sub:
        if os.path.exists('/usr/bin/mlmmj-sub'):
            _cmd_mlmmj_sub = '/usr/bin/mlmmj-sub'
        elif os.path.exists('/usr/local/bin/mlmmj-sub'):
            _cmd_mlmmj_sub = '/usr/local/bin/mlmmj-sub'
        else:
            return (False, 'SUB_COMMAND_NOT_FOUND')

    # mlmmj-sub arguments
    #
    # -L: Full path to list directory
    # -a: Email address to subscribe
    # -C: Request mail confirmation
    # -d: Subscribe to `digest` version of the list
    # -n: Subscribe to nomail version of the list
    _cmd = [_cmd_mlmmj_sub, '-L', _dir, '-C']

    if subscription == 'digest':
        _cmd.append('-d')
    elif subscription == 'nomail':
        _cmd.append('-n')

    # Directory used to store subscription confirm notifications
    _subconf_dir = os.path.join(_dir, 'subconf')

    _error = {}
    for addr in subscribers:
        try:
            # Remove confirm file generated before this request
            _old_conf_files = glob.glob(os.path.join(_subconf_dir, '????????????????-' + addr.replace('@', '=')))
            for _f in _old_conf_files:
                qr = __remove_file(path=_f)
                if not qr[0]:
                    return qr

            # Send new confirm
            _new_cmd = _cmd[:] + ['-a', addr]
            subprocess.Popen(_new_cmd, stdout=subprocess.PIPE)
        except Exception, e:
            _error[addr] = repr(e)

    if not _error:
        return (True, )
    else:
        return (False, repr(_error))


def is_maillist_exists(mail):
    if __has_ml_dir(mail):
        return True
    else:
        return False


def get_web_param_value(mail, param):
    """Get mlmmj parameter value of given web parameter name."""
    if param in settings.MLMMJ_WEB_PARAMS:
        _mlmmj_param = settings.MLMMJ_WEB_PARAMS[param]
        return __get_param_value(mail=mail, param=_mlmmj_param)
    else:
        return (False, 'INVALID_PARAM')


def add_maillist_from_web_form(mail, form):
    """Add a mailing list based on data submited from web form.

    @mail - mail address of mailing list account
    @form - a dict of web form input
    """
    domain = mail.split('@', 1)[-1]

    # Store mlmmj parameters
    kvs = {}

    # Add empty values for 'remove_headers', 'custom_headers'. This will
    # trigger form process functions to add pre-defined default values.
    if 'remove_headers' not in form:
        form['remove_headers'] = ''

    if 'custom_headers' not in form:
        form['custom_headers'] = ''

    # Set 'owner' to 'postmaster@<domain>'
    if 'owner' not in form:
        form['owner'] = 'postmaster@' + domain

    # Set 'owner' to 'postmaster@<domain>'
    if 'moderators' not in form:
        form['moderators'] = 'postmaster@' + domain

    kvs.update(__convert_form_to_mlmmj_params(mail=mail, form=form))

    # Add (missing) default settings
    _form = settings.MLMMJ_DEFAULT_PROFILE_SETTINGS
    for param in _form:
        if param not in form:
            kv = form_utils.get_dict_for_form_param(mail=mail, form=_form, param=param)
            kvs.update(kv)

    # Always set values
    _form = settings.MLMMJ_FORCED_PROFILE_SETTINGS
    for param in _form:
        kv = form_utils.get_dict_for_form_param(mail=mail, form=_form, param=param)
        kvs.update(kv)

    qr = create_ml(mail=mail, **kvs)
    return qr


def create_ml(mail, **kwargs):
    """Create required directories/files for a new mailing list on file system.

    WARNING: it doesn't check whether account already exists in backend.

    @mail - full email address of new mailing list you're going to create
    @kwargs - dict of parameter/value pairs used to set account profile
    """
    if not utils.is_email(mail):
        return (False, 'INVALID_EMAIL')

    mail = str(mail).lower()

    _ml_dir = __get_ml_dir(mail=mail)
    if not os.path.exists(_ml_dir):
        try:
            os.makedirs(_ml_dir, mode=settings.MLMMJ_FILE_PERMISSION)
        except Exception, e:
            _msg = "error while creating base directory ({}), {}".format(_ml_dir, repr(e))
            logger.error("[{}] {}, {}".format(web.ctx.ip, mail, _msg))
            return (False, _msg)

    # Create required sub-directories
    for _dir in settings.MLMMJ_DEFAULT_SUB_DIRS:
        _sub_dir = os.path.join(_ml_dir, _dir)
        if not os.path.exists(_sub_dir):
            try:
                os.makedirs(_sub_dir, mode=settings.MLMMJ_FILE_PERMISSION)
            except Exception, e:
                _msg = "error while creating sub-directory ({}), {}".format(_sub_dir, repr(e))
                logger.error("[{}] {}, {}".format(web.ctx.ip, mail, _msg))
                return (False, _msg)
        else:
            qr = __set_file_permission(_sub_dir)
            if not qr[0]:
                return qr

    # Create file `control/listaddress` with primary address
    _f = os.path.join(_ml_dir, 'control/listaddress')
    with open(_f, 'w') as f:
        f.write('{}\n'.format(mail))

    # Create extra control file
    index_path = os.path.join(_ml_dir, 'index')
    open(index_path, 'w').close()

    # Copy skel/language template files
    _sub_dir_text = os.path.join(_ml_dir, 'text')
    _language = kwargs.get('language', 'en')
    _src_dir = os.path.join(settings.MLMMJ_SKEL_DIR, _language)
    if not os.path.exists(_src_dir):
        logger.error("Skel directory doesn't exist: {}".format(_src_dir))
        return (False, 'SKEL_DIR_NOT_EXIST')

    qr = __copy_dir_files(_src_dir, _sub_dir_text)
    if not qr[0]:
        return qr

    qr = __update_mlmmj_params(mail=mail, **kwargs)
    if not qr[0]:
        return qr

    return (True, )


def delete_ml(mail, archive=True):
    """Delete a mailing list account. If archive is True or 'yes', account is
    'removed' by renaming its data directory.
    """
    _ml_dir = __get_ml_dir(mail=mail)

    if os.path.exists(_ml_dir):
        if archive in [True, 'yes']:
            qr = __archive_ml(mail=mail)
            return qr
        else:
            try:
                shutil.rmtree(_ml_dir)
                logger.info("[{}] {}, removed.".format(web.ctx.ip, mail))
            except Exception, e:
                return (False, repr(e))
    else:
        logger.info("[{}] {}, removed (no data on file system).".format(web.ctx.ip, mail))

    return (True, )


def update_web_form_params(mail, form):
    """Update mailing list profile with web form."""
    kvs = {}
    kvs.update(__convert_form_to_mlmmj_params(mail=mail, form=form))
    return __update_mlmmj_params(mail=mail, **kvs)


def get_subscribers(mail, subscription=None, combined=False):
    """Get subscribers of given subscription version.

    @mail -- mail address of mailing list account
    @subscription -- subscription version: normal, nomail, digest.
    @combined -- combine all subscribers into a list. Defaults to a dict with
                 beginning letter as key.
    """
    _dir = __get_ml_subscribers_dir(mail=mail, subscription=subscription)

    # Make sure directory exists
    try:
        fns = os.listdir(_dir)
    except Exception, e:
        return (False, repr(e))

    if combined:
        subscribers = set()
        for fn in fns:
            _addresses = [str(i).lower().strip() for i in open(os.path.join(_dir, fn)).readlines()]
            subscribers.update(_addresses)

        subscribers = list(subscribers)
        subscribers.sort()
    else:
        subscribers = {}
        for fn in fns:
            _addresses = [str(i).lower().strip() for i in open(os.path.join(_dir, fn)).readlines()]
            subscribers[fn] = list(set(_addresses))
            subscribers[fn].sort()

    return (True, subscribers)


def remove_subscriber(mail, subscriber, subscription='normal'):
    """Remove single subscriber from given subscription version.

    @mail -- mail address of mailing list account
    @subscriber -- mail address of subscriber
    @subscription -- subscription version: normal, nomail, digest.
    """
    mail = mail.lower()
    subscriber = subscriber.lower()

    _dir = __get_ml_subscribers_dir(mail=mail, subscription=subscription)

    # Get file stores the subscriber.
    path = os.path.join(_dir, subscriber[0])

    return __remove_lines_in_file(f=path, lines=[subscriber])


def remove_subscribers(mail, subscribers, subscription='normal'):
    """Remove multiple subscribers from given subscription version.

    @mail -- mail address of mailing list account
    @subscribers -- a list/tuple/set of subscribers' email addresses
    @subscription -- subscription version: normal, nomail, digest.
    """
    mail = mail.lower()
    subscribers = [str(i).lower() for i in subscribers if utils.is_email(i)]

    if not subscribers:
        return (True, )

    grouped_subscribers = {}
    for i in subscribers:
        letter = i[0]

        if letter in grouped_subscribers:
            grouped_subscribers[letter].append(i)
        else:
            grouped_subscribers[letter] = [i]

    _dir = __get_ml_subscribers_dir(mail=mail, subscription=subscription)
    for letter in grouped_subscribers:
        # Get file stores the subscriber.
        path = os.path.join(_dir, letter)

        qr = __remove_lines_in_file(f=path, lines=grouped_subscribers[letter])
        if not qr[0]:
            return qr

    return (True, )


def remove_all_subscribers(mail):
    """
    Remove all subscribers.

    :param mail: mail address of mailing list account
    """
    mail = mail.lower()

    _dirs = [__get_ml_subscribers_dir(mail=mail, subscription=i) for i in subscription_versions]
    try:
        for _dir in _dirs:
            for fn in os.listdir(_dir):
                _path = os.path.join(_dir, fn)
                qr = __remove_file(path=_path)
                if not qr[0]:
                    return qr
    except Exception, e:
        return (False, repr(e))

    return (True, )


def add_subscribers(mail, subscribers, subscription='normal', require_confirm=True):
    """
    Add subscribers to given subscription version.

    @mail -- mail address of mailing list account
    @subscribers -- a list/tuple/set of subscribers' email addresses
    @subscription -- subscription version: normal, nomail, digest.
    """
    mail = mail.lower()
    subscribers = [str(i).lower() for i in subscribers if utils.is_email(i)]

    if not subscribers:
        return (True, )

    if require_confirm:
        qr = __add_subscribers_with_confirm(mail=mail,
                                            subscribers=subscribers,
                                            subscription=subscription)
        if not qr[0]:
            return qr
    else:
        grouped_subscribers = {}
        for i in subscribers:
            letter = i[0]

            if letter in grouped_subscribers:
                grouped_subscribers[letter].append(i)
            else:
                grouped_subscribers[letter] = [i]

        _dir = __get_ml_subscribers_dir(mail=mail, subscription=subscription)
        for letter in grouped_subscribers:
            # Get file stores the subscriber.
            path = os.path.join(_dir, letter)

            qr = __add_lines_in_file(f=path, lines=grouped_subscribers[letter])
            if not qr[0]:
                return qr

    return (True, )
