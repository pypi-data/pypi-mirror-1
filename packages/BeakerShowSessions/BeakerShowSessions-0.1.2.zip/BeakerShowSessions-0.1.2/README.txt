BeakerShowSessions
==================

BeakerShowSessions is a Beaker_ extension that shows the active sessions
according to the given WSGI configuration file. Currently the plugin only works
with ext:database session storage backend.

You could call get_sessions in order to get a list of active sessions (dicts)::

    >>> from beaker.scripts import get_sessions
    >>> get_sessions('cfg/production.ini')

BeakerShowSessions expects to find these keys in the `[app:main]` section of
your configuration file

    - ``beaker.session.type = ext:database`` - the only supported backend (yet)
    - ``beaker.session.url`` - an `SQLAlchemy engine URL`_
    - ``beaker.session.timeout`` - session timeout in seconds
    - ``beaker.session.table_name`` - (optional) session storage table. Defaults
      to `beaker_cache`.

If your beaker configuration directive prefix is not `beaker.session` (or you
have multiple beaker instances) you can provide the correct prefix as a second
option::

    >>> get_sessions('cfg/prod.ini', 'bkr.sess')

If you are going to use BeakerShowSessions separately you could choose to call
`show_sessions` instead. It takes the same parameters but returns a pretty ASCII
table with results, like this::


    >>> print show_sessions('cfg/prod.ini')
    --------------------------------------------------------
         _accessed_time |      _creation_time |    user_name
    --------------------------------------------------------
    2001-02-03 10:11:12 | 2001-02-03 10:11:12 | john@doe.com

PasteCall_ provides a convenient method to call `show_sessions` from the
console::

    $ paster call beaker.scripts:show_sessions 'cfg/prod.ini' 'bkr.ses'
    --------------------------------------------------------
         _accessed_time |      _creation_time |    user_name
    --------------------------------------------------------
    2001-02-03 10:11:12 | 2001-02-03 10:11:12 | john@doe.com

You can find the Mercurial repository at bitbucket.org_

.. _Beaker: http://beaker.groovie.org
.. _SQLAlchemy engine URL: http://www.sqlalchemy.org/docs/05/dbengine.html#create-engine-url-arguments
.. _PasteCall: http://pypi.python.org/pypi/PasteCall
.. _bitbucket.org: http://bitbucket.org/kaukas/beakershowsessions
