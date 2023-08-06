"""These are constants we're expecting from WhatCounts.

Since they might change the way their API responds, we're concentrating all of that
uncertainty here.

We're also keeping all of the messages we provide when we throw custom exceptions
here -- I'm assuming that users might ultimately see that, and we want that to
be customizable.
"""

import re



################
# WC RESPONSES
# these are the various responses we're expecting to see from WC
#

# generic errors that can come up in any command
ERROR_BAD_REALM = """FAILURE: Unable to determine customer account (realm)"""
ERROR_NO_API_FOR_REALM = """Unable to acquire API user credentials through API User Manager."""
ERROR_RE_BAD_KEY = re.compile("Password \(.*?\) doesn't match entry")
# found (only?) when using the change cmd with a non-existant user
ERROR_NO_SUCH_USER = """FAILURE: unable to find subscriber record"""

# (subscribe) - list id is not appropriate
ERROR_BAD_LIST = """FAILURE: Error looking up list ids, one or more list ids specified do not belong to your realm"""

RE_UNSUBSCRIBED = re.compile("(?P<unsubscribed>\d+) users? unsubscribed")
RE_UPDATED = re.compile("(?P<updated>\d+) users? updated")


################
# EXCEPTION MESSAGES
# these will probably get shown to not technical users so let's keep them friendly, ok?
#
EXC_INVALID_REALM       = """WhatCounts isn't recognizing the realm you supplied."""
EXC_API_NOT_AUTHORIZED  = """WhatCounts is reporting that the API hasn't been authorized for your "realm".  You'll need to email WhatCounts to turn that feature on."""
EXC_INVALID_KEY         = """WhatCounts is reporting that the api key (password) isn't correct for the realm you supplied."""
EXC_BAD_LIST            = """WhatCounts is reporting that the list you chose doesn't exist in your realm."""
EXC_MISSING_RESPONSE    = """Expected a reponse from WhatCounts but received nothing"""
EXC_UNEXPECTED_RESPONSE = """Received an unexpected response from WhatCounts: """
EXC_BAD_EMAIL           = """WhatCounts didn't accept the email address you supplied -- it might be invalid or that address had previoously opted out from this list."""
EXC_BAD_USER            = """WhatCounts didn't recognize the email address you supplied as an existing user in your realm."""
EXC_PROBLEM_UNSUB       = """There were problems unsubscribing."""
EXC_PROBLEM_UPDATE      = """There were problems updating the user's info."""
