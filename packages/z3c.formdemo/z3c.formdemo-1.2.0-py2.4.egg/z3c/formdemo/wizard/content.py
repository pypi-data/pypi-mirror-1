##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Hello Worl Message Implementation

$Id: content.py 75942 2007-05-24 14:53:46Z srichter $
"""
__docformat__ = "reStructuredText"
import zope.interface
from zope.schema.fieldproperty import FieldProperty
from z3c.formdemo.wizard import interfaces

class PersonalInfo(object):
    zope.interface.implements(interfaces.IPersonalInfo)

    lastName = FieldProperty(interfaces.IPersonalInfo['lastName'])
    firstName = FieldProperty(interfaces.IPersonalInfo['firstName'])
    email = FieldProperty(interfaces.IPersonalInfo['email'])
    phone = FieldProperty(interfaces.IPersonalInfo['phone'])
    street = FieldProperty(interfaces.IPersonalInfo['street'])
    city = FieldProperty(interfaces.IPersonalInfo['city'])
    zip = FieldProperty(interfaces.IPersonalInfo['zip'])

    def __repr__(self):
        return '<%s %s %s>' %(
            self.__class__.__name__, self.firstName, self.lastName)


class Employer(object):
    zope.interface.implements(interfaces.IEmployerInfo)

    name = FieldProperty(interfaces.IEmployerInfo['name'])
    street = FieldProperty(interfaces.IEmployerInfo['street'])
    city = FieldProperty(interfaces.IEmployerInfo['city'])
    zip = FieldProperty(interfaces.IEmployerInfo['zip'])

    def __repr__(self):
        return '<%s %s>' %(self.__class__.__name__, self.name)


class Person(PersonalInfo):

    def __init__(self):
        self.father = PersonalInfo()
        self.mother = PersonalInfo()
        self.employer = Employer()
