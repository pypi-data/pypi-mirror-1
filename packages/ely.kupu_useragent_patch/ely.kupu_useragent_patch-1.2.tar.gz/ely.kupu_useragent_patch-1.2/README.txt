Introduction
============

Kupu checks the user-agent header in requests as part of
isKupuEnabled. If user-agent is empty then it will return false. This
is not so useful in those situations where it is nice to clear out
user agent, e.g. with nginx in front of squid.

This patch removes that check. So far it seems pretty stable to
inflict kupu on people without the user-agent data.

(A similar patch has already been applied to Products.TinyMCE.)
