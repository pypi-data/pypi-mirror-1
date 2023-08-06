###############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id:$
"""

from zope.app.appsetup.product import _configs as productConfigs


def configureFSStorage(local_conf):
    fsStorage = local_conf.get('fsStorage')
    if fsStorage is None:
        raise ValueError(
            "Missing p01.fsfile 'fsStorage' configuration in paste *.ini file")
    productConfigs.update({'p01.fsfile': {'fsStorage':fsStorage}})
