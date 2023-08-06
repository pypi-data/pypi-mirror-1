from ConfigParser import NoOptionError
from datetime import datetime, timedelta
import os

from paste.deploy.loadwsgi import NicerConfigParser
import sqlalchemy as sa


def cleanup(cfg_file, older_than, prefix='beaker.session'):
    cfg_file = os.path.abspath(cfg_file)
    cparser = NicerConfigParser(cfg_file, dict(
        here=os.path.dirname(cfg_file),
        __file__=cfg_file))
    cparser.read(cfg_file)
    dburi = cparser.get('app:main', '%s.url' % prefix)
    try:
        tab_name = cparser.get('app:main', '%s.table_name' % prefix)
    except NoOptionError:
        tab_name = 'beaker_cache'

    engine = sa.create_engine(dburi)
    md = sa.MetaData(bind=engine)
    cache = sa.Table(tab_name, md, autoload=True)

    older_dict = {}
    if older_than.endswith('m'):
        key = 'minutes'
    elif older_than.endswith('h'):
        key = 'hours'
    elif older_than.endswith('d'):
        key = 'days'
    older_dict[key] = int(older_than[:-1])
    older_than = datetime.now() - timedelta(**older_dict)

    cache.delete(cache.c.accessed < older_than).execute()
