# Testing data
import settings

domain = 'api-test.com'
listname = 'test-list'
ml = listname + '@' + domain

# urls
url_ml = '/api/' + ml

# Not exist domain
domain_not_exist = 'not-exist-test-domain.com'
url_ml_in_not_exist_domain = '/api/ml@' + domain_not_exist

params_create_ml = {
    'close_list': 'no',
    'disable_subscription': 'no',
    'moderated': 'no',
    'disable_send_copy_to_sender': 'yes',
    'only_subscriber_can_post': 'yes',
    'only_moderator_can_post': 'no',
    'moderate_non_subscriber_post': 'no',
    'notify_owner_when_sub_unsub': 'no',
    'notify_sender_when_moderated': 'no',
    'subject_prefix': '[test-prefix] ',
    'disable_archive': 'no',
    'disable_digest_subscription': 'yes',
    'disable_digest_text': 'yes',
    'disable_nomail_subscription': 'yes',
    'disable_retrieving_old_posts': 'yes',
    'only_subscriber_can_get_old_posts': 'no',
    'disable_retrieving_subscribers': 'yes',
    'disable_notify_subscription_moderated': 'yes',
    'disable_notify_when_missing_listaddress': 'yes',
    'disable_notify_when_access_denied': 'yes',
    'disable_notify_when_subscriber_only': 'yes',
    'disable_notify_when_moderator_only': 'yes',
    'moderate_subscription': 'yes',
    'subscription_moderators': '1@z.io,2@z.io,3@z.io',  # conflict with 'moderate_subscription=yes',
    'moderators': '11@z.io,12@z.io,13@z.io',
    'custom_headers': 'X-Test-1: ABC\nX-Test-2: DEF\nX-Test-3: GHI',
    'remove_headers': 'X-Remove-1:,X-Remove-2:,X-Remove-3:',
    'owner': '1@x.io,2@x.io,3@x.io',
    'relay_host': '192.168.1.1',
    'smtp_helo': 'test.domain.com',
    'smtp_port': '2525',
    'footer_text': """Here is specified in bytes how big a mail can be and\n
still be prepared for sending in memory. It is greatly reducing the amount of\n
write system calls to prepare it in memory before sending it, but can also\n
lead to denial of service attacks. Default is 16k (16384 bytes).""",
    'footer_html': '<p>This is footer in html format.</p>',
}

params_create_verify = dict(params_create_ml)
params_create_verify['subscription_moderators'] = ['1@z.io', '2@z.io', '3@z.io']
params_create_verify['moderators'] = ['11@z.io', '12@z.io', '13@z.io']
params_create_verify['custom_headers'] = ['X-Test-1: ABC', 'X-Test-2: DEF', 'X-Test-3: GHI']
params_create_verify['remove_headers'] = ['X-Remove-1:', 'X-Remove-2:', 'X-Remove-3:']
params_create_verify['remove_headers'] += settings.MLMMJ_DEFAULT_REMOVED_HEADERS
params_create_verify['owner'] = ['1@x.io', '2@x.io', '3@x.io']

# Add default custom headers
_default_custom_headers = dict(settings.MLMMJ_DEFAULT_CUSTOM_HEADERS)
for (k, v) in _default_custom_headers.items():
    # for placeholder support
    v = v % {'mail': ml, 'listname': listname, 'domain': domain}
    params_create_verify['custom_headers'].append('{}: {}'.format(k, v))

params_update_ml = {
    'close_list': 'yes',
    'disable_subscription': 'yes',
    'moderated': 'yes',
    'disable_send_copy_to_sender': 'no',
    'only_subscriber_can_post': 'no',
    'only_moderator_can_post': 'yes',
    'moderate_non_subscriber_post': 'yes',
    'notify_owner_when_sub_unsub': 'yes',
    'notify_sender_when_moderated': 'yes',
    'subject_prefix': '[updated-prefix] ',
    'disable_archive': 'yes',
    'disable_digest_subscription': 'no',
    'disable_digest_text': 'no',
    'disable_nomail_subscription': 'no',
    'disable_retrieving_old_posts': 'no',
    'only_subscriber_can_get_old_posts': 'yes',
    'disable_retrieving_subscribers': 'no',
    'disable_notify_subscription_moderated': 'no',
    'disable_notify_when_missing_listaddress': 'no',
    'disable_notify_when_access_denied': 'no',
    'disable_notify_when_subscriber_only': 'no',
    'disable_notify_when_moderator_only': 'no',
    'moderate_subscription': 'no',
    'footer_text': 'This if updated footer in plain text.',
    'footer_html': """<p>This is updated footer in html format.</p>""",
}
