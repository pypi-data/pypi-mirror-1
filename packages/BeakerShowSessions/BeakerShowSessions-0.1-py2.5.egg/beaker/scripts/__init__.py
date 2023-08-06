# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)

from ConfigParser import NoOptionError
from datetime import datetime, timedelta
import os
from paste.deploy.loadwsgi import NicerConfigParser
import pickle
import sqlalchemy as sa


def get_sessions(cfg_file, prefix='beaker.session'):
    cfg_file = os.path.abspath(cfg_file)
    cparser = NicerConfigParser(cfg_file, dict(
        here=os.path.dirname(cfg_file),
        __file__=cfg_file))
    cparser.read(cfg_file)

    dburi = cparser.get('app:main', '%s.url' % prefix)
    timeout = cparser.getint('app:main', '%s.timeout' % prefix)
    try:
        tab_name = cparser.get('app:main', '%s.table_name' % prefix)
    except NoOptionError:
        tab_name = 'beaker_session'
    md = sa.MetaData(dburi)
    session = sa.Table(tab_name, md, autoload=True)

    sdata = []

    active_sessions = session.select(session.c.accessed >= datetime.now() - \
        timedelta(seconds=timeout), order_by=session.c.accessed)
    for s in active_sessions.execute():
        ses = pickle.loads(s.data).get('session', {})
        for key, value in ses.iteritems():
            if key in ('_accessed_time', '_creation_time'):
                value = datetime.fromtimestamp(value)
            elif value is None:
                value = 'N/A'
            else:
                value = unicode(value)
            ses[key] = value
        sdata.append(ses)

    return sdata


def show_sessions(*args, **kargs):
    sdata = get_sessions(*args, **kargs)
    if not sdata:
        return 'No sessions found'

    output = []

    columns = {}

    for d in sdata:
        for key, value in d.iteritems():
            if isinstance(value, datetime):
                value = d[key] = value.strftime('%Y-%m-%d %H:%M:%S')
            column = columns.get(key)
            if column is None:
                column = columns[key] = dict(title=key, width=len(key))
            if column['width'] < len(value):
                column['width'] = len(value)

    keys = sorted(columns.keys())

    header = []
    for key in keys:
        fmt = '%%%ss' % columns[key]['width']
        header.append(fmt % key)
    header = ' | '.join(header)
    dashes = '-' * len(header)
    output.append(dashes)
    output.append(header)
    output.append(dashes)

    for d in sdata:
        row = []
        for key in keys:
            fmt = '%%%ss' % columns[key]['width']
            value = d.get(key)
            row.append(fmt % value)
        output.append(' | '.join(row))

    output.append(dashes)

    return '\n'.join(output)
