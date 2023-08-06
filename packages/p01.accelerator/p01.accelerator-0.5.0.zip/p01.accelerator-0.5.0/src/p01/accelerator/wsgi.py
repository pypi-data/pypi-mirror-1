###############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id:$
"""

import zope.app.wsgi
from zope.app.appsetup.product import _configs as productConfigs

import p01.tmp.wsgi


def application_factory(global_conf, conf='zope.conf', **local_conf):
    p01.tmp.wsgi.configureTMPStorage(local_conf)
    configfile = os.path.join(global_conf['here'], conf)
    schemafile = os.path.join(
        os.path.dirname(zope.app.appsetup.__file__), 'schema', 'schema.xml')
    global APPLICATION
    APPLICATION = zope.app.wsgi.getWSGIApplication(configfile, schemafile)
    zope.event.notify(zope.app.appsetup.interfaces.ProcessStarting())
    return APPLICATION
