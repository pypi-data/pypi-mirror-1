from persistent import Persistent 
from OFS.SimpleItem import SimpleItem

from zope.interface import implements, Interface
from zope.component import adapts
from zope.formlib import form
from zope import schema
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName

from zope.component.interfaces import IObjectEvent

from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData

from plone.app.contentrules.browser.formhelper import AddForm, EditForm 

from Acquisition import aq_inner

from collective.action.twitter import MessageFactory as _

import twitter as TwitterApi

# imports for tiny url call
from urllib import urlencode
from urllib2 import urlopen, HTTPError, URLError

def getTinyURL(url):
    """ returns shotend url or None """  
    TINYURL = 'http://tinyurl.com/api-create.php'
    linkdata = urlencode(dict(url=url))
    try:
        link = urlopen( TINYURL, data=linkdata ).read().strip()
    except URLError:
        # there was an error
        link = None
    return link



class ITwitterPublishAction(Interface):
    """ Twitter Config """
    user = schema.TextLine(title=_(u'username'),
                         description=_(u'Username of your twitter account'),
                         required=True)
    password = schema.Password(title=_(u'password'),
                         description=_(u'Password of your twitter account'),
                         required=True)


class TwitterPublishAction(SimpleItem):
    """ """
    implements(ITwitterPublishAction, IRuleElementData)
    
    user = ""
    password = ""
    element = "collective.action.twitter.twitteraction"

    def summary(self):
        return _(u"Twitter account: ${user}", mapping=dict(user=self.user))


class TwitterPublishActionExecutor(object):
    """ """
    implements(IExecutable)
    adapts(Interface, ITwitterPublishAction, IObjectEvent)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        context = aq_inner(self.event.object)
        ploneutils = getToolByName(self.context, 'plone_utils')
        tw = TwitterApi.Api(self.element.user, self.element.password)
        obj = self.event.object
        title = obj.Title()
        url = getTinyURL(obj.absolute_url())
        if url is None:
            return False
        twittertext = "%s\n%s" % ( title[0:140-(len(url)+2)], url )

        try:
            status = tw.PostUpdate(twittertext)
            msg = _("Item published to twitter")
        except HTTPError, e:
            msg = _("Error while publishing to twitter %s" % str(e))
        ploneutils.addPortalMessage( msg )
        self.context.REQUEST.response.redirect(obj.absolute_url())
            
        return True

class TwitterPublishActionAddForm(AddForm):
    """An add form for portal type conditions.
    """
    form_fields = form.FormFields(ITwitterPublishAction)
    label = _(u"Add Twitter config")
    description = _(u"Your Twitter account information.")
    form_name = _(u"Configure element")

    def create(self, data):
        c = TwitterPublishAction()
        form.applyChanges(c, self.form_fields, data)
        return c

class TwitterPublishActionEditForm(EditForm):
    """An edit form for portal type conditions
    """
    form_fields = form.FormFields(ITwitterPublishAction)
    label = _(u"Edit Twitter Condition")
    description = _(u"Your Twitter account information.")
    form_name = _(u"Configure element")
