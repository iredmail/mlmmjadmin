import web

from controllers.decorators import api_acl
from libs.utils import api_render
from libs import mlmmj
import settings

# Load mailing list backend.
backend = __import__(settings.backend_api)


class Profile(object):
    @api_acl
    def GET(self, mail):
        """Get mailing list profiles."""
        # Make sure mailing list account exists
        if not backend.is_maillist_exists(mail=mail):
            return api_render((False, 'NO_SUCH_ACCOUNT'))

        if not mlmmj.is_maillist_exists(mail):
            return api_render((False, 'NO_SUCH_ACCOUNT'))

        # Get specified profile parameters.
        # If parameters are given, get values of them instead of all profile
        # parameters.
        form = web.input()
        _web_params = form.get('params', '').lower().strip().replace(' ', '').split(',')
        _web_params = [p for p in _web_params if p in settings.MLMMJ_WEB_PARAMS]

        if _web_params:
            web_params = _web_params
        else:
            web_params = settings.MLMMJ_WEB_PARAMS

        kvs = {}
        for _param in web_params:
            qr = mlmmj.get_web_param_value(mail=mail, param=_param)
            if qr[0]:
                kvs[_param] = qr[1]['value']

        return api_render((True, kvs))

    @api_acl
    def POST(self, mail):
        """Create a new mailing list account."""
        mail = str(mail).lower()
        form = web.input()

        # Create account in backend
        qr = backend.add_maillist(mail=mail, form=form)
        if not qr[0]:
            return api_render(qr)

        # Create account in mlmmj
        qr = mlmmj.add_maillist_from_web_form(mail=mail, form=form)

        return api_render(qr)

    @api_acl
    def DELETE(self, mail):
        """Delete a mailing list account.

        curl -X DELETE ... https://<server>/api/mail    # same as `archive=yes`
        curl -X DELETE ... https://<server>/api/mail?archive=yes
        curl -X DELETE ... https://<server>/api/mail?archive=no

        Optional parameters (appended to URL):

        @archive - If set to `yes` (or no such parameter appended in URL), only
                   account in (SQL/LDAP/...) backend will be removed (so that
                   MTA won't accept new emails for this email address), but
                   data on file system will be kept (by renaming the mailing
                   list directory to `<listname>-<timestamp>`.

                   If set to `no`, account in (SQL/LDAP/...) backend AND all
                   data of this account on file system will be removed.
        """
        form = web.input()
        qr = backend.remove_maillist(mail=mail)

        if not qr[0]:
            return api_render(qr)

        _archive = form.get('archive')
        if _archive not in ['yes', 'no']:
            _archive = 'yes'

        qr = mlmmj.delete_ml(mail=mail, archive=_archive)
        return api_render(qr)

    @api_acl
    def PUT(self, mail):
        """
        Update a mailing list account.

        curl -X PUT -d "name='new name'&disable_subscription=yes" https://<server>/api/mail
        """
        form = web.input()
        qr = backend.update_maillist(mail=mail, form=form)
        if not qr[0]:
            return api_render(qr)

        qr = mlmmj.update_web_form_params(mail=mail, form=form)
        return api_render(qr)


class Owners(object):
    @api_acl
    def GET(self, mail):
        if not mlmmj.is_maillist_exists(mail):
            return api_render((False, 'NO_SUCH_ACCOUNT'))

        owners = mlmmj.get_owners(mail=mail)

        return api_render((True, owners))

    @api_acl
    def PUT(self, mail):
        """
        Available parameters:

        `add_owners`: Add one or multiple owners. Multiple owners must be separated by comma.
                      Conflict with `owners` parameter.
        `remove_owners`: Remove one or multiple owners. Multiple owners must be separated by comma.
                         Conflict with `owners` parameter.
        `owners`: Reset owners to given list. Multiple owners must be separated by comma.
                  Conflict with `add_owners` and `remove_owners` parameters.
        """
        form = web.input()

        if "owners" in form:
            reset_owners = form.get('owners', '').replace(' ', '').split(',')
            qr = mlmmj.reset_owners(mail=mail, owners=reset_owners)
            if not qr[0]:
                return api_render(qr)
        else:
            if "add_owners" in form:
                add_owners = form.get('add_owners', '').replace(' ', '').split(',')
                if add_owners:
                    qr = mlmmj.add_owners(mail=mail, owners=add_owners)
                    if not qr[0]:
                        return api_render(qr)

            if "remove_owners" in form:
                remove_owners = form.get('remove_owners', '').replace(' ', '').split(',')
                if remove_owners:
                    qr = mlmmj.remove_owners(mail=mail, owners=remove_owners)
                    if not qr[0]:
                        return api_render(qr)

        return api_render(True)


class Moderators(object):
    @api_acl
    def GET(self, mail):
        if not mlmmj.is_maillist_exists(mail):
            return api_render((False, 'NO_SUCH_ACCOUNT'))

        moderators = mlmmj.get_moderators(mail=mail)

        return api_render((True, moderators))

    @api_acl
    def PUT(self, mail):
        """
        Available parameters:

        `add_moderators`: Add one or multiple moderators. Multiple moderators must be separated by comma.
                          Conflict with `moderators` parameter.
        `remove_moderators`: Remove one or multiple moderators. Multiple moderators must be separated by comma.
                             Conflict with `moderators` parameter.
        `moderators`: Reset moderators to given list. Multiple moderators must be separated by comma.
                      Conflict with `add_moderators` and `remove_moderators` parameters.
        """
        form = web.input()

        if "moderators" in form:
            reset_moderators = form.get('moderators', '').replace(' ', '').split(',')
            qr = mlmmj.reset_moderators(mail=mail, moderators=reset_moderators)
            if not qr[0]:
                return api_render(qr)
        else:
            if "add_moderators" in form:
                add_moderators = form.get('add_moderators', '').replace(' ', '').split(',')
                if add_moderators:
                    qr = mlmmj.add_moderators(mail=mail, moderators=add_moderators)
                    if not qr[0]:
                        return api_render(qr)

            if "remove_moderators" in form:
                remove_moderators = form.get('remove_moderators', '').replace(' ', '').split(',')
                if remove_moderators:
                    qr = mlmmj.remove_moderators(mail=mail, moderators=remove_moderators)
                    if not qr[0]:
                        return api_render(qr)

        return api_render(True)
