-------------------
ABOUT PyWhatCounts
-------------------

This is a light wrapper for (the bulk emailer service) WhatCounts' Web Api.  The
use case that drove this wrapper means we're only supporting a limited part of
their API; we're approaching it from the standpoint of a single user who wants
to modify their settings (if this seems shortsighted, note that it's a deadline-
driven 0.1 release ;)

Specifically, that means that certain commands, such as updating user information,
is implemented for only a single person at a time, instead of in batches.  Also,
most of the list-centric commands (except for "show lists") are not implemented
at all.

The WC Web API has seemed at time a little fragile and it gets updated at times.
While I don't have any reason to believe they would make updates that would 
jeopardize backwards compatability, I've designed the package, esp tests, to be
very sensitive to changes so that users are aware as soon as possible and can
refactor as needed.  This wrapper attempts (for better or worse) to interpret
the responses from WC and raise exceptions accordingly:

WCUserError:   for normal user errors, such as trying to subscribe someone with a
               malfromed email address
WCAuthError:   solely for authentication errors (bad realm, bad key for realm,
               Web API not authorized for realm)
WCSystemError: Raised only for unexpected responses from WhatCounts.  Indicates
               either a change in their API or a case we haven't accounted for.
               Either way, not a good sign.  :)

-------------------
About tests
-------------------
There is a (hopefully thorough) suite of unittests to verify that this wrapper
is working and/or that WC is behaving as expected.  See the README in the 
tests/ for more.



-------------------
ABOUT Authentication Settings
-------------------

** Authentication Codes/"Keys"/Pwds **
In order to interact with WhatCounts using the Web API or the module, you will
need a Web API key.

From WC's API Web 1.7:
"Creating the Authentication Code 
To an authentication code, use your web browser and open the URL: 
http://whatcounts.com/bin/api_setup 
 
The lower part of the screen has a section labeled Web API. Press the 
button labeled "Generate Authentication Code." The screen will be refreshed
and your authentication code will appear. If you need to change it, revisit this 
page and perform the same step again. This code will be required when using 
the WhatCounts web API."

-------------------
Contact
-------------------
This product was developed by ONE/Northwest (to be integrated with the CMS 
Plone).  We'd love feedback:

Jon Baldivieso (jonb@onenw.org)
Andrew Burkhalter (andrewb@onenw.org)