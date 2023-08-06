Beaker Session Cleanup
======================

This is a beaker plugin which exposes a cleanup function. The cleanup function
cleans the old session data created by beaker database backend.

It uses a PasterCall plugin to expose the cleanup to the console.

Mercurial repository: bitbucket.org_.

.. _bitbucket.org: http://bitbucket.org/kaukas/beakercleanup

Installation
------------

easy_install:

    ``$ <env>/bin/easy_install BeakerCleanup``

pip:

    ``$ <env/bin/pip install BeakerCleanup``

General usage
-------------

    ``$ <environment>/bin/paster call beaker.scripts.cleanup:cleanup path/to/config.cfg 4h bkr.session``

    ``beaker.scripts.cleanup:cleanup`` is an entry point to the cleanup function

    ``path/to/config.cfg`` is a path to the WSGI config file containing beaker
    session parameters (usually .cfg or .ini)

    ``4h`` tells to clean up sessions which are older than (has ``accessed``
    before) 4 hours. You can give

        - 1m, 18m, 76m, etc - minutes
        - 1h, 4h, 25h, etc - hours
        - 1d, 2d, 32d, etc - days

    ``bkr.session`` (optional, default: ``'beaker.session'``) is a prefix which
    is needed to find the beaker session parameters in the config file. It
    allows you to choose which backend to clean up when you have more than one.
    E.g.::

        bkr.session.url = sqlite:///my.db
        bkr.session.table_name = sessions
        
Usage examples
--------------

If you are mostly using defaults your call could be similar to this:

    ``$ paster call beaker.scripts.cleanup:cleanup my/config.ini 5h``

If you are using a virtual environment <env> you'll call it like this

    ``$ <env>/bin/paster call beaker.scripts.cleanup:cleanup <env>/prod.ini 3d``
