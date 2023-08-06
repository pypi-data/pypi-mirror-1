from datetime import datetime, timedelta
import os

from beaker.ext.database import DatabaseNamespaceManager
from paste.call.commands import CallEP
import sqlalchemy as sa

from beaker.tests import db_file

def test_cleanup():
    r"""Test session cleanup.

    The cleanup function takes 3 arguments:
    - config file - a full path to a WSGI config file where the beaker session
      parameters are described
    - older than - remove sessions that are older than the supplied timespan.
      Examples: 1m (minute), 20m, 80m, 1h (hour), 24h
    - prefix - the beaker session parameter prefix in the configuration file.
      Default - 'beaker.session'

    Let's first set the database session table up
    DatabaseNamespaceManager creates the session table

        >>> dnm = DatabaseNamespaceManager('abc', url='sqlite:///%s' % db_file,
        ...     table_name='session', lock_dir=os.getcwd())

    Load the table

        >>> engine = sa.create_engine('sqlite:///%s' % db_file)
        >>> md = sa.MetaData(bind=engine)
        >>> cache = sa.Table('session', md, autoload=True)

    Insert several sessions into it. The first one was accessed 50 minutes ago

        >>> now = datetime.now()
        >>> r = cache.insert().values(namespace='abc', created=now, data='',
        ...     accessed=now - timedelta(minutes=50)).execute()

    Another was accessed 70 minutes ago

        >>> r = cache.insert().values(namespace='bcd', created=now, data='',
        ...     accessed=now - timedelta(minutes=70)).execute()

    Then 3 hours ago

        >>> r = cache.insert().values(namespace='cde', created=now, data='',
        ...     accessed=now - timedelta(hours=3)).execute()

    And 1 day 15 minutes ago

        >>> r = cache.insert().values(namespace='def', created=now, data='',
        ...     accessed=now - timedelta(days=1, minutes=15)).execute()

    Now call the cleanup and ask it to clean the sessions older than 1 day

        >>> cfg_file = os.path.join(os.path.dirname(__file__), 'testapp.cfg')
        >>> cmd = CallEP('')
        >>> outcode = cmd.run(['beaker.scripts:cleanup', cfg_file, '1d'])

    We should only have the sessions newer than 1 day left in the db

        >>> for c in cache.select(order_by='namespace').execute():
        ...     print c.namespace
        abc
        bcd
        cde

    Now cleanup the sessions older than 2 hours and check

        >>> outcode = cmd.run(['beaker.scripts:cleanup', cfg_file, '2h'])
        >>> for c in cache.select(order_by='namespace').execute():
        ...     print c.namespace
        abc
        bcd

    Now cleanup the sessions older than 55 minutes and check

        >>> outcode = cmd.run(['beaker.scripts:cleanup', cfg_file, '55m'])
        >>> for c in cache.select(order_by='namespace').execute():
        ...     print c.namespace
        abc

    """
