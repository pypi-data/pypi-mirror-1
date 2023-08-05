# -*- coding: utf-8 -*-
#
# File: __init__.py
#
# Copyright (c) InQuant GmbH
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

__author__    = """Ramon Bartl <ramon.bartl@inquant.de>"""
__docformat__ = 'plaintext'
__revision__  = "$Revision: 2966 $"
__version__   = '$Revision: 2966 $'[11:-2]

from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from inquant.portlet.contextualrecentitems import contextualrecentitems

from inquant.portlet.contextualrecentitems.tests.base import TestCase


class TestPortlet(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def test_portlet_type_registered(self):
        portlet = getUtility(IPortletType, name='inquant.portlet.contextualrecentitems.ContextualRecentItems')
        self.assertEquals(portlet.addview, 'inquant.portlet.contextualrecentitems.ContextualRecentItems')

    def test_interfaces(self):
        portlet = contextualrecentitems.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_values(self):
        portlet = contextualrecentitems.Assignment(name="Recent Changed Sites", type="Document", count=5)
        self.assertEquals(portlet.data.name, 'Recent Changed Sites')
        self.assertEquals(portlet.data.type, 'Document')
        self.assertEquals(portlet.data.count, 5)

    def test_invoke_add_view(self):
        portlet = getUtility(IPortletType, name='inquant.portlet.contextualrecentitems.ContextualRecentItems')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={"name":"Recent Changed News", "type":"Topic", "count":5})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], contextualrecentitems.Assignment))

        assignment = mapping.values[0]

        self.assertEquals(assignment.name, 'Recent Changed News')
        self.assertEquals(assignment.type, 'Topic')
        self.assertEquals(assignment.count, 5)

    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = contextualrecentitems.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, contextualrecentitems.EditForm))

    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)

        assignment = contextualrecentitems.Assignment()

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, contextualrecentitems.Renderer))


class TestRenderer(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or contextualrecentitems.Assignment()
        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_render(self):
        r = self.renderer(context=self.portal, assignment=contextualrecentitems.Assignment(name="Recent Event changes", type="Event", count=5))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.failUnless("Recent Event changes" in output)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :
