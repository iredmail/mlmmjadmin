# Roadmap

## 1.0: RESTful API

- rc/sysv script without uwsgi.
- API:
    - new parameter: `enable_newsletter_subscription`. Used to explictly enable it.
    - Add API endpoint to verify whether given email address is already a member

- Design SQL tables and LDAP schema used to store mailing list accounts and
  profiles.
    * LDAP: use existing `objectClass=mailList`?

- Better FreeBSD support:
    - rc scripts

---

Tasks already finished:

- Run as non-privileged user/group: `mlmmj:mlmmj`.
- Run as a daemon service, no web server required.
- Return JSON data to API client:
    - Operation succeeds: `{'_success': true}`
    - Operation succeeds with data returned: `{'_success': true, '_data': <data>}`
    - Operation failed: `{'_success': false, '_msg': <error reason>}`
- Supports hook to check whether domain, email address exist in SQL/LDAP/...
  backend.
- Log (part of) auth_token for troubleshooting purpose
- Add mapping for form parameters and mlmmj parameters
- Hide unsupported web/mlmmj parameters
- Add mailing list with some default settings
- Delete mailing list
- Update mailing list parameters
- Archive mailing list directory.
    - Able to archive account data to specified archive directory.
- Unit tests
- Add backend `bk_none` to handle mlmmj without SQL/LDAP/... databases.
- Correctly handle footer in both plain text and html formats.

- script `tools/maillist_admin.py` (interactive with API):
    * Add new account (must be able to handle all profile parameters)
    * Update profile parameters
    * Delete account
    * List subscribers in different subscription version

- script `samples/bin/mlmmj-amime-receive`: Call altermime for handling footer.

## 2.0

### API

- Rename a mailing list
- View or remove pending subscription subscribers
- Able to update parameter for ALL accounts under same domain.

### Web Interface

Since mlmmj supports management by sending emails to particular addresses
(e.g. `list+unsubscribe@domain.com`, `list+owner@domain.com`), web
interface is not so urgent.

- Allow moderators to manage mailing list profiles
- Allow end users to manage their own subscriptions
- Custom skel template files
- Deploy with Nginx with https support

## 3.0: Archive

- Write scripts to convert archived emails of public mailing list to web pages.
- Support multiple list addresses.
