This is simple set of tests to verify that this Python wrapper is working and
that WhatCounts is talking to us the way we're expecting.  Because we're making
a lot of somewhat rigid assumptions about the responses we're getting from WC,
we want to know for sure when those assumptions are failing.

CONFIGURATION
These tests require an active account with WhatCounts with the Web API enabled
(requires an email to WC support staff) and the appropriate API key, which you 
can get from their website (see the package's README).

Once that information is obtained, set up the appropriate values in the
config.py in this directory.  There is explanation contained in that module.

To run these tests:
1. Make sure that the PyWhatCounts package is somewhere in your PYTHONPATH.
2. Use either runalltests.py for the full suite or run any test singly. 
