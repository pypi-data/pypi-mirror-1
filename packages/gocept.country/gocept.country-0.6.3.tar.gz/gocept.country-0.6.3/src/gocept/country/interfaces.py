# -*- coding: latin-1 -*-
# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: interfaces.py 6599 2008-09-12 11:31:37Z mac $

import zope.interface

class ICountry(zope.interface.Interface):
    """A Country (ISO 3166)."""

    name = zope.interface.Attribute("Name of the country.")
    alpha2 = zope.interface.Attribute("Alpha2 code of the country.")
