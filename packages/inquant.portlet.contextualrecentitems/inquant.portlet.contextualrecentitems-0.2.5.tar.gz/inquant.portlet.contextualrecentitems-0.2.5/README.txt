==========================
Context aware Recent Items
==========================

Overview
--------

A Plone Portlet which does an adapter lookup to fetch
the **portal type** to use in the query for recently changed
portlets.

Rationale
---------

This is scratching an itch of a customer, which wants to
display only recent "news" on a news page etc.
Instead of hard-coding the portal type, we do a adapter lookup.

Usage
-----

Users then can register adapters like::

    <adapter
        for=".interfaces.INewsArea
             zope.publisher.interfaces.browser.IBrowserRequest
             zope.publisher.interfaces.browser.IBrowserView
             "
        provides="inquant.portlet.contextualrecentitems.interfaces.ITypeNameProvider"
        factory=".adapters.FeedItemTypeProvider"
        />

    <five:implements
        class="Products.feedfeeder.content.folder.FeedfeederFolder"
        interface=".interfaces.INewsArea"
        />

And have the actual adapter look like::


    class FeedItemTypeProvider(object):
        def __init__(self, context, request, view):
            pass
        type = "FeedFeederItem"

The portlet renderer does a **queryMultiAdapter** on the context, the request
and the view. Thus, it's possible to have a different portlet for each view of
your content. This is useful for search pages registered on the site root::

    <adapter
        for="zope.interface.Interface
             zope.publisher.interfaces.browser.IBrowserRequest
             Products.BabpnProducts.browser.search.BabpnBOSearchView"
        provides="inquant.portlet.contextualrecentitems.interfaces.ITypeNameProvider"
        factory=".adapters.BizOpTypeProvider"
        />

    class BizOpTypeProvider(object):
        def __init__(self, context, request, view):
            pass
        type = "BusinessOpportunity"

That way, the **recent changes** portlet only shows items which match your search page.

Of course, if no adapter is found, the portlet falls back to its normal behavior like
the standard plone recently changed portlet.




