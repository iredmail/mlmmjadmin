# Regular expressions of email address, IP address, network.

import re

# Email address.
#
#   - `+`, `=` are used in SRS rewritten addresses.
#   - `/` is sub-folder. e.g. 'john+lists/abc/def@domain.com' will create
#     directory `lists` and its sub-folders `lists/abc/`, `lists/abc/def`.
email = r'''[\w\-\#][\w\-\.\+\=\/\&\#]*@[\w\-][\w\-\.]*\.[a-zA-Z0-9\-]{2,15}'''
cmp_email = re.compile(r'^' + email + r'$', re.IGNORECASE | re.DOTALL)

#
# Domain name
#
# Single domain name.
domain = r'''[\w\-][\w\-\.]*\.[a-z0-9\-]{2,25}'''
cmp_domain = re.compile(r'^' + domain + r'$', re.IGNORECASE | re.DOTALL)
