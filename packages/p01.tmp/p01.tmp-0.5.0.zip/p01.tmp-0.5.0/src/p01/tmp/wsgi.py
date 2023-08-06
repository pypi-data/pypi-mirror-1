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


def configureTMPStorage(local_conf):
    tmpStorage = local_conf.get('tmpStorage')
    if tmpStorage is None:
        raise ValueError(
            "Missing p01.tmp 'tmpStorage' configuration in paste *.ini file")
    productConfigs.update({'p01.tmp': {'tmpStorage':tmpStorage}})
