# Enable web.py debug mode.
DEBUG = False

# Syslog server address.
# use '/dev/log' if it logs locally.
SYSLOG_SERVER = '/dev/log'
SYSLOG_PORT = 514

# Syslog facility
SYSLOG_FACILITY = 'local5'

# Recipient delimiters. If you have multiple delimiters, please list them all.
RECIPIENT_DELIMITERS = ['+']

# The transport name defined in Postfix master.cf used to call 'mlmmj-receive'
# program.
MTA_TRANSPORT_NAME = 'mlmmj'

# HTTP header name used to store auth token.
API_AUTH_TOKEN_HEADER_NAME = 'X-MLMMJADMIN-API-AUTH-TOKEN'

#
# Access control
#
# Enable restriction
RESTRICT_ACCESS = False

# List all IP addresses of allowed client for http access.
ACCEPTED_CLIENTS = []

# Directory used to store mlmmj mailing list data.
MLMMJ_SPOOL_DIR = '/var/spool/mlmmj'

# Directory used to store data of removed but archived mailing list account.
# NOTE: This directory must be owned by daemon user/group.
#
# While removing account, it's optional to archive account data under
# MLMMJ_SPOOL_DIR, you can set a different archive directory to store archived
# data, to keep MLMMJ_SPOOL_DIR clean.
#
# If empty, account data will be simply renamed with timestamp appended under
# same directory (<listname> -> <listname>-<timestamp>).
MLMMJ_ARCHIVE_DIR = '/var/spool/mlmmj-archive'

# Directory which stores skel files (templates in different languages).
MLMMJ_SKEL_DIR = '/usr/share/mlmmj/text.skel'

# Default file permission for created files/directories
MLMMJ_FILE_PERMISSION = 0o700

#
# Absolute path to mlmmj commands. If empty, will try /usr/bin and
# /usr/local/bin automatically.
#
CMD_MLMMJ_SUB = ''

#
# Mapping of web form parameter names and mlmmj parameter names
#
# Mlmmj control mailing list profiles with multiple plain text files, for a
# full list of control options/files, please check official document:
# http://mlmmj.org/docs/tunables/
#
#   - A "boolean" parameter/file mean the contents of a file does not matter,
#     the mere presence of it, will set the variable to "true".
#   - A "normal" parameter/file, the first line will be used as value, leaving
#     line 2 and forward ready for commentary etc.
#   - A "list" parameter/file, means this parameter supports multiple values,
#     and one value per line.
#   - A "text" parameter/file, means entire content of file is used as value.
#
MLMMJ_BOOLEAN_WEB_PARAMS = {
    #'addtohdr': 'addtohdr',

    # Define the list is open or closed.
    # If it's closed, subscription and unsubscription via mail is disabled.
    'close_list': 'closedlist',

    'only_moderator_can_post': 'modonlypost',
    'only_subscriber_can_post': 'subonlypost',

    # Disable subscription. Unsubscription is possible.
    'disable_subscription': 'closedlistsub',

    # Disable mail confirmation to subscribe to the list.
    # WARNING: This should in principle never ever be used, but there are times
    # on local lists etc. where this is useful. HANDLE WITH CARE!
    'disable_subscription_confirm': 'nosubconfirm',

    # Disable subscription to the digest version of the mailing list.
    # Useful if you don't want to allow digests and notify users about it.
    'disable_digest_subscription': 'nodigestsub',

    # Digest mails won't have a text part with a thread summary.
    'disable_digest_text': 'nodigesttext',

    # Disable subscription to the 'nomail' version of the mailing list.
    # Useful if you don't want to allow 'nomail' and notify users about it.
    'disable_nomail_subscription': 'nonomailsub',

    # If this file is present, then mlmmj in case of moderation checks the
    # envelope from, to see if the sender is a moderator, and in that case
    # only send the moderation mails to that address. In practice this means that
    # a moderator sending mail to the list won't bother all the other moderators
    # with his mail.
    #'ifmodsendonlymodmoderate': 'ifmodsendonlymodmoderate',

    # Either parameter `owner` or `moderators` is required.
    # If both exists, `moderators` has higher priority.
    'moderated': 'moderated',
    'moderate_non_subscriber_post': 'modnonsubposts',

    # Disable retrieving old posts by sending email to address
    # `<listname>+get-N@domain.com`
    'disable_retrieving_old_posts': 'noget',

    # Only subscribers can retrieve old posts by sending LISTNAME+get-N@
    'only_subscriber_can_get_old_posts': 'subonlyget',

    # Disable retrieving subscribers by sending email to LISTNAME+list@
    # Note: only owner can send to such address.
    'disable_retrieving_subscribers': 'nolistsubsemail',

    'notify_sender_when_moderated': 'notifymod',
    'notify_owner_when_sub_unsub': 'notifysub',
    'disable_send_copy_to_sender': 'notmetoo',

    # Disable sending email to the person requesting subscription about his/her
    # subscription is moderated.
    'disable_notify_subscription_moderated': 'nosubmodmails',

    # Disable notifying sender that the email was rejected due to no
    # listaddress in To: or Cc: headers.
    'disable_notify_when_missing_listaddress': 'notoccdenymails',
    'disable_notify_when_access_denied': 'noaccessdenymails',
    'disable_notify_when_subscriber_only': 'nosubonlydenymails',
    'disable_notify_when_moderator_only': 'nomodonlydenymails',
    'disable_notify_when_exceeding_max_mail_size': 'nomaxmailsizedenymails',

    'disable_archive': 'noarchive',
    'tocc': 'tocc',
    #
    # Custom parameters which are not supported by mlmmj itself
    #
    'enable_newsletter_subscription': 'enable_newsletter_subscription',
}

MLMMJ_LIST_WEB_PARAMS = {
    #'access': 'access',
    'custom_headers': 'customheaders',
    'remove_headers': 'delheaders',
    'extra_addresses': 'listaddress',
    'owner': 'owner',
    'owners': 'owner',  # this is an alias to 'owner'
}

MLMMJ_NORMAL_WEB_PARAMS = {
    #'bouncelife': 'bouncelife',
    #'delimiter': 'delimiter',
    #'digestinterval': 'digestinterval',
    #'digestmaxmails': 'digestmaxmails',
    'max_message_size': 'maxmailsize',
    #'maxverprecips': 'maxverprecips',
    #'memorymailsize': 'memorymailsize',
    #'modreqlife': 'modreqlife',
    'subject_prefix': 'prefix',
    'relay_host': 'relayhost',
    'smtp_helo': 'smtphelo',
    'smtp_port': 'smtpport',
    #'staticbounceaddr': 'staticbounceaddr',
    #'verp': 'verp',
}

# mlmmj's built-in footer support is very bad, so we don't support parameter
# 'footer', see `footer_text` and `footer_html` below.
MLMMJ_TEXT_WEB_PARAMS = {}

# Define additional parameters used to manage mlmmj easier.
# Notes:
#   - these parameter names are not officially supported by mlmmj
#     (not listed on website: http://mlmmj.org/docs/tunables/)
#   - parameter name is same as value. We define the mapping in
#     MLMMJ_OTHER_PARAM_MAP below.
MLMMJ_OTHER_WEB_PARAMS = {
    'name': 'name',
    'moderate_subscription': 'moderate_subscription',
    'moderators': 'moderators',
    'subscription_moderators': 'subscription_moderators',
    'footer_text': 'footer_text',
    'footer_html': 'footer_html',
}

# Map web parameter name to mlmmj parameter name
MLMMJ_OTHER_PARAM_MAP = {
    'name': {'mlmmj_param': 'name',
             'type': 'normal'},
    'moderate_subscription': {'mlmmj_param': 'submod',
                              'type': 'boolean'},
    'subscription_moderators': {'mlmmj_param': 'submod',
                                'type': 'list',
                                'is_email': True},
    'moderators': {'mlmmj_param': 'moderators',
                   'type': 'list',
                   'is_email': True},
    # mlmmj's built-in footer support is very bad, we use 'altermime' to handle
    # the footer. And we will generate two files for this purpose:
    #   - control/footer_text: footer in plain text
    #   - control/footer_html: footer in html
    # FYI: http://mlmmj.org/docs/readme-footers/
    'footer_text': {'mlmmj_param': 'footer_text',
                    'type': 'text'},
    'footer_html': {'mlmmj_param': 'footer_html',
                    'type': 'text'},
}

# All web parameters
MLMMJ_WEB_PARAMS = {}
MLMMJ_WEB_PARAMS.update(MLMMJ_BOOLEAN_WEB_PARAMS)
MLMMJ_WEB_PARAMS.update(MLMMJ_LIST_WEB_PARAMS)
MLMMJ_WEB_PARAMS.update(MLMMJ_TEXT_WEB_PARAMS)
MLMMJ_WEB_PARAMS.update(MLMMJ_NORMAL_WEB_PARAMS)
MLMMJ_WEB_PARAMS.update(MLMMJ_OTHER_WEB_PARAMS)

# All mlmmj parameters
MLMMJ_PARAM_NAMES = list(MLMMJ_WEB_PARAMS.values())

MLMMJ_PARAM_TYPES = {
    'boolean': MLMMJ_BOOLEAN_WEB_PARAMS,
    'normal': MLMMJ_NORMAL_WEB_PARAMS,
    'list': MLMMJ_LIST_WEB_PARAMS,
    'text': MLMMJ_TEXT_WEB_PARAMS,
    'other': MLMMJ_OTHER_WEB_PARAMS,
}

# Add default settings for mailing list account if was not set in http request.
# For list type parameters, multiple values must be separated by comma. For
# example: {param: 'value1,value2,value3'}
#
# If you want to add (new) or remove (existing) settings, please add setting
# in config file like below (just Python dictionay operations):
#
#   *) Add a new one or replace existing one;
#
#       MLMMJ_DEFAULT_PROFILE_SETTINGS.update({key: value})
#
#   *) Remove an existing one:
#
#   MLMMJ_DEFAULT_PROFILE_SETTINGS.pop(key)             # Remove existing one
#
MLMMJ_DEFAULT_PROFILE_SETTINGS = {
    # With `tocc` enabled, the list address does not have to be in the To: or
    # Cc: header of the email to the list. This is useful when we have alias
    # domains and don't want to list all <listname>@<alias-domain> in the
    # `control/listaddress` file.
    'tocc': 'yes',
    #'disable_send_copy_to_sender': 'yes',
    'only_subscriber_can_post': 'yes',
    'only_moderator_can_post': 'no',
    'moderate_non_subscriber_post': 'no',
    'notify_owner_when_sub_unsub': 'no',
    'notify_sender_when_moderated': 'no',
    'disable_archive': 'no',
    # Retrieving old posts
    'disable_retrieving_old_posts': 'yes',
    'only_subscriber_can_get_old_posts': 'yes',
    # moderate subscription
    #'moderate_subscription': 'yes',
    # different subscription types
    #'disable_digest_subscription': 'yes',
    #'disable_nomail_subscription': 'yes',
    # notification about postings being denied
    #'disable_notify_when_missing_listaddress': 'yes',
    #'disable_notify_when_access_denied': 'yes',
    #'disable_notify_when_subscriber_only': 'yes',
    #'disable_notify_when_moderator_only': 'yes',
}

# Ignore values submitted from API client, always set certain parameters to
# given values.
MLMMJ_FORCED_PROFILE_SETTINGS = {}

# Sub-directories under mailing list directory for newly created account
MLMMJ_DEFAULT_SUB_DIRS = [
    'archive',
    'bounce',
    'control',
    'digesters.d',
    'incoming',
    'moderation',
    'nomailsubs.d',
    'queue',
    'queue/discarded',
    'requeue',
    'subconf',
    'subscribers.d',
    'text',
    'unsubconf',
]

# Headers we need to always add to every email.
# Available place holders:
#   - %(mail)s - will be replaced by full email address of mailing list
#   - %(domain)s - will be replaced by domain name of mailing list email address
#   - %(listname)s - will be replaced by username part of mailing list email address
#
# FYI: http://www.faqs.org/rfcs/rfc2369.html
MLMMJ_DEFAULT_CUSTOM_HEADERS = {
    'Precedence': 'list',
    'X-Mailing-List': '%(mail)s',
    #'Reply-To': '%(mail)s',
    'List-Subscribe': '<mailto:%(listname)s+subscribe@%(domain)s?subject=Subscribe>',
    'List-Unsubscribe': '<mailto:%(listname)s+unsubscribe@%(domain)s?subject=Unsubscribe>',
    #'List-Help': '<mailto:%(listname)s+help@%(domain)s?subject=help>',
    #'List-Owner': '<mailto:%(listname)s+owner@%(domain)s>',
}

# Headers we need to remove from received emails.
# Format:
#   - must be in title format like 'X-Abc-Def:' (first character is upper case)
#   - must end with ':'
MLMMJ_DEFAULT_REMOVED_HEADERS = [
    #'DKIM-Signature:',
    #'Authentication-Results:',
]
