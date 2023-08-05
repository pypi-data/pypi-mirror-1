##########################################################
#
# Licensed under the terms of the GNU Public License
# (see docs/LICENSE.GPL)
#
# Copyright (c) 2005:
#   - The Open Planning Project (http://www.openplans.org/)
#   - Whit Morriss <whit at www.openplans.org>
#   - and contributors
#
##########################################################
from urllib import quote
from zope.interface import Interface
from zope.component import adapter, handle
from Products.Five import BrowserView
from wicked import utils
from wicked.normalize import titleToNormalizedId as normalize
from wicked.config import BACKLINK_RELATIONSHIP
from wicked.utils import getWicked
from wicked.link import WickedAdd, BasicLink
from wicked.interfaces import IWickedContentAddedEvent
from Products.Archetypes.interfaces import IBaseObject

_marker=object()

class ATWickedAdd(WickedAdd, BrowserView):

    def add_content(self, title=None, section=None, type_name=_marker):
        # make it possible to pass in container
        # pre-populate with backlinks?
        type_name = self.request.get('type_name', type_name)
        if type_name is _marker:
            type_name = self.context.portal_type
        title = self.request.get('Title', title)
        section = self.request.get('section', section)
        assert title, 'Must have a title to create content' 
        newcontentid = normalize(title)

        container = self.aq_parent.aq_parent
        container.invokeFactory(type_name, id=newcontentid,
                                   title=title)

        newcontent = getattr(self.context, newcontentid)
        self.notify_content_added(newcontent, title, section)

# channel on AT
@adapter(IBaseObject, IWickedContentAddedEvent)
def handle_at_newcontent(context, event):
    field = context.Schema()[event.section]
    wicked = getWicked(field, context, event)
    wicked.manageLink(context, event.title)
    portal_status_message='"%s" has been created' % event.title
    url = event.newcontent.absolute_url()
    restr = "%s/edit?portal_status_message=%s" %(url, quote(portal_status_message))
    event.request.RESPONSE.redirect(restr)

    
class BasicFiveLink(BasicLink, BrowserView):
    """
    Five prepared link implementation
    """
    __init__=BasicLink.__init__


def test_suite():
    import unittest
    from zope.testing import doctest
    optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS
    from Products.PloneTestCase.layer import PloneSite, ZCMLLayer
    from Testing.ZopeTestCase import ZopeDocFileSuite, FunctionalDocFileSuite
    from Products.PloneTestCase import ptc
    ptc.setupPloneSite()
    renderer = ZopeDocFileSuite('renderer.txt',
                                package='wicked.at',
                                optionflags=optionflags)
    setattr(renderer, 'layer', ZCMLLayer)
    add = FunctionalDocFileSuite('add.txt',
                           package='wicked.at',
                           test_class=ptc.FunctionalTestCase,                                   
                           optionflags=optionflags)
                 
    return unittest.TestSuite((add, renderer))


