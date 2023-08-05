This package provides the ``WSGIPublisherApplication`` class which
exposes the object publishing machinery in ``zope.publisher`` as a
WSGI application.  It also lets us bring up the Zope application
server (parsing ``zope.conf`` and ``site.zcml``) with a mere function
call::

    >>> db = zope.app.wsgi.config('zope.conf')

This is especially useful for debugging.

To bring up Zope and obtain the WSGI application object at the same,
use the ``getWSGIApplication`` function.  Here's an example of a
factory a la PasteDeploy_::

    def application_factory(global_conf):
        zope_conf = os.path.join(global_conf['here'], 'zope.conf')
        return zope.app.wsgi.getWSGIApplication(zope_conf)

.. _PasteDeploy: http://pythonpaste.org/deploy/


Changes
=======

3.4.0 (2007-09-14)
------------------

* Fixed the tests to run on Python 2.5 as well as Python 2.4.

* Split ``getApplication`` into ``config`` and ``getApplication`` so
  that ``config`` could be reused, for example for debugging.

3.4.0a1 (2007-04-22)
--------------------

Initial release as a separate project, corresponds to zope.app.wsgi
from Zope 3.4.0a1
