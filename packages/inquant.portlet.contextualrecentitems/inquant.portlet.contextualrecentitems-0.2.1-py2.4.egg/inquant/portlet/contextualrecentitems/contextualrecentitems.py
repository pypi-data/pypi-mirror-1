# -*- coding: utf-8 -*-
#
# File: contextualrecentitems.py
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
__revision__  = "$Revision: 58889 $"
__version__   = '$Revision: 58889 $'[11:-2]

from zope import schema
from zope.formlib import form
from zope.interface import implements
from zope.component import getMultiAdapter, queryAdapter

from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider

from plone.app.portlets.portlets import base
from plone.app.portlets.cache import render_cachekey

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Acquisition import aq_inner

from inquant.portlet.contextualrecentitems import ContextualRecentItemsMessageFactory as _
from inquant.portlet.contextualrecentitems.interfaces import ITypeNameProvider


class IContextualRecentItems(IPortletDataProvider):
    """A portlet which displays recent items of a custom type
    """

    name = schema.TextLine(title=_(u"label_contextualrecentitems_portlet", default=u"Title"),
                           description=_(u"help_contextualrecentitems_portlet",
                           default=u"The title of the Portlet. This will appear in the header of the Portlet"),
                           default=u"Recent Changes",
                           required=False,)

    count = schema.Int(title=_(u'Number of items to display'),
                       description=_(u'How many items to list.'),
                       required=True,
                       default=5)


class Assignment(base.Assignment):
    implements(IContextualRecentItems)

    def __init__(self, name="", type="", count=5):
        self.count = count
        self.type = type
        self.name = name

    @property
    def title(self):
        return u"Contextual Recent Items Portlet"


def _render_cachekey(fun, self):
    if self.anonymous:
        raise ram.DontCache()
    return render_cachekey(fun, self)


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('contextualrecentitems.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.anonymous = portal_state.anonymous()
        self.portal_url = portal_state.portal_url()
        plone_tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.catalog = plone_tools.catalog()
        self.type = None

    @ram.cache(_render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return not self.anonymous and len(self._data())

    @property
    def name(self):
        return self.data.name

    def recent_items(self):
        return self._data()

    def recently_modified_link(self):
        if self.type:
            return '%s/@@recent_modified' % self.portal_url
        else:
            return '%s/@@contextual_recent_modified?type=%s' % (self.portal_url, self.type)

    @memoize
    def _data(self):
        limit = self.data.count

        query = dict( sort_on='modified',
                      sort_order='reverse',
                      sort_limit=limit)

        # XXX: maybe do a multi adapter query here?
        adapter = queryAdapter( #(self.context, self.request, self.view),
                self.view,
                ITypeNameProvider )

        if adapter:
            type = adapter.type
            query["portal_type"] = type
            self.type = type

        return self.catalog(**query)[:limit]


class AddForm(base.AddForm):
    form_fields = form.Fields(IContextualRecentItems)
    label = _(u"Add Contextual Recent Items Portlet")
    description = _(u"This portlet displays recently modified content of a custom Type.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(IContextualRecentItems)
    label = _(u"Edit Contextual Recent Items Portlet")
    description = _(u"This portlet displays recently modified content of a custom Type.")

# vim: set ft=python ts=4 sw=4 expandtab :
