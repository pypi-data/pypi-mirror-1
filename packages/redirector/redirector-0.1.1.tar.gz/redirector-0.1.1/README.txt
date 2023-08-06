redirector
==========

*Control redirects through WSGI middleware.*

redirector is a piece of WSGI middleware that allows redirects to be
managed within the scope of a python web service.  Traditionally,
redirects are done via Apache or some other web server disparate from
the python application.  This leads to several undesirable
consequences:

 * there is no way of controlling redirects through the web
 * the web server must be restarted when redirects are changed

Because of this methodology of doing things, it discourages the
stake-holders (the people that actually care about the redirects) from
changing the redirects themselves.  Because the redirects are not, in
their mind, content, this leads to unmaintainable systems.  The goal
of redirector is to bring the power to create redirects to any
authorized user.


Status
------

Redirector is largely in the conceptual stage.  While what redirector
does now (regular expression redirects) is sufficient to reproduce
Apache's behavior, it is not enough to realize the vision of bringing
redirects to the people for WSGI apps.  

Even this documentation is thoroughly imcomplete.


TODO
----

redirector needs several pieces to become what it should be:

Types of Redirects
------------------

Currently, only regular expression redirects (a la Apache) are
implemented. Another possibility, probably more applicable, are
something like glob redirects.  The reason that these are useful is
that they, with a carefully constructed rule system, can be seen to
match each other.  In other words, you can see if the existing set of
redirects is contradictory and if there are superfluous redirects.  It
also better matches how non-experts think about redirects.
