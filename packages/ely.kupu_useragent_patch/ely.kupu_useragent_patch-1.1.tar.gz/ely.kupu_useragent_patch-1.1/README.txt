Introduction
============

Both kupu and tinymce check the user-agent header in requests as part
of isKupuEnabled and isTinyMCEEnabled. If user-agent is empty then it
will return false. This is not so useful in those situations where it
is nice to clear out user agent, e.g. with nginx in front of squid.

This patch removes that check. So far it seems pretty stable to
inflict kupu and tinymce on people without the user-agent data.
