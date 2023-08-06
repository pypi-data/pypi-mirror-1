"""Setup the Refaction application"""
import logging

import paste.deploy
from paste.deploy import appconfig
from pylons import config

from refaction.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
    """Place any commands to setup refaction here"""
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)
    paste.deploy.CONFIG.push_process_config({'app_conf':conf.local_conf,
                'global_conf':conf.global_conf})

    from refaction import model
    engine = config['pylons.g'].sa_engine
    print 'Creating database tables'
    model.meta.create_all(bind=engine)

    print 'Creating default entries'
    role = model.Role(name=u'admin')
    role.save()
    role = model.Role(name=u'manager')
    role.save()
    role = model.Role(name=u'subscriber')
    role.save()
    role = model.Role(name=u'member')
    role.save()
    try:
        from crypt import crypt
        password = unicode(crypt('admin', 'AA'))
    except ImportError:
        password = u'admin'
    user = model.User(name=u'admin', password=password, role=1)
    user.save()
    model.Session.commit()


