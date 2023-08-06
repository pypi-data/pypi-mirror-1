# Because this integrates with a third party ASP requiring authentication
# we're pulling out sensitive user-specific info needed for testing into this single
# file.  In order to run tests, you'll have to fill this out.

# your WhatCounts realm
TEST_REALM = 'XXX'

# your WhatCounts API key, available, as of 1/8/2006, from
# http://whatcounts.com/bin/api_setup
TEST_KEY   = 'XXX'

# an email address for a user that you're TOTALLY confident doesn't exist
# it is subscribed and deleted frequently
TEST_DUMMY_USER = 'bogus_user@foobar.com'

# this is the id of a valid list in your realm.  it should probably be a sandbox list
TEST_LIST  = '77721'
