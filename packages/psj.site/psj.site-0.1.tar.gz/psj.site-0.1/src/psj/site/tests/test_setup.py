##
## test_setup.py
## Login : <uli@pu.smp.net>
## Started on  Tue Apr  8 13:09:43 2008 Uli Fouquet
## $Id$
## 
## Copyright (C) 2008 Uli Fouquet
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##

"""Test setup for psj.site.
"""
from Testing import ZopeTestCase as ztc
# Needed for Python tests, that must provide a Plone test.
from ulif.plone.testsetup import SimplePloneTestCase
# The replacement for (normally) two files of code with many, many
# lines:
from ulif.plone.testsetup import register_all_plone_tests
test_suite = register_all_plone_tests('psj.site',
                                      extra_packages=['psj.content',
                                                      'psj.policy'])
