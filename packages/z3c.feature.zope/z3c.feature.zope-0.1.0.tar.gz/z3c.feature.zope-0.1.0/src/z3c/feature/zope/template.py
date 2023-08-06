##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Zope Project Template

$Id: template.py 98395 2009-03-27 08:54:36Z pcardune $
"""
import os
from z3c.feature.core import template

ZopeProjectTemplate = template.FileBasedTemplate(
    os.path.join(os.path.dirname(__file__),"zope-project.xml"),
    u"Zope 3 Web Application",
    u"Includes all the features you would want for a Zope 3 Web Application.")
