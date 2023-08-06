# -*- coding: utf-8 -*-
"""
affinitic.verifyinterface

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: __init__.py,v 41215ad6b84e 2009/12/18 15:58:56 jfroche $
"""

import os
from zope.interface import declarations
from zope.interface import exceptions
from zope.interface.verify import verifyClass
import logging
import sys

logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

packagesToVerifyInterfaces = os.environ.get('verifyinterface', [])
if packagesToVerifyInterfaces:
    packagesToVerifyInterfaces = packagesToVerifyInterfaces.split('\n')


def needVerify(cls):
    """
    Check if we need to check interface contract for a class
    """
    moduleName = str(cls.__module__)
    if 'affinitic.verifyinterface' in moduleName:
        return False
    if len(packagesToVerifyInterfaces) == 0:
        return True
    verify = False
    for packageToVerify in packagesToVerifyInterfaces:
        if str(moduleName).startswith(packageToVerify):
            verify = True
            break
    return verify

#PATCH START
zope_interface_declarations = declarations.classImplements


def classImplementsAndVerify(cls, *interfaces):
    zope_interface_declarations(cls, interfaces)
    if not needVerify(cls):
        return
    for interface in declarations.implementedBy(cls):
        try:
            verifyClass(interface, cls)
        except (exceptions.BrokenImplementation, exceptions.BrokenMethodImplementation), ex:
            print '%s failed implementing %s: %s' % (cls, interface, ex)

logger.debug('Patching classImplements, add automatic verify on classImplements/implements')
declarations.classImplements = classImplementsAndVerify
