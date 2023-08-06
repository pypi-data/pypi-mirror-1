from zope.interface import Interface
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from zope import schema
from zope.formlib import form

from plone.memoize.instance import memoize
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFPlone import PloneMessageFactory as _

from collective.portlet.googleapps import portletMessageFactory as _

class IGoogleDocsPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    # some_field = schema.TextLine(title=_(u"Some field"),
    #                              description=_(u"A field to use"),
    #                              required=True)

    header = schema.TextLine(title=_(u"Portlet header"),
                             description=_(u"Title of the rendered portlet"),
                             required=True,
                             default=_(u"My Google Docs"))

    limit = schema.Int(title=_(u"Limit"),
                       description=_(u"Specify the maximum number of items to show in the portlet. "),
                       required=True,
                       default=5)

    hosted_domain = schema.TextLine(title=_(u"Hosted domain to access"),
                       description=_(u"If specified, this will be the domain account that will be accessed (for example, 'university.edu.au').  If not specifed, you will access a regular Google account."),
                       required=False,
                       default=_(u""))

    secure_connection = schema.Bool(title=_(u"Secure connection?"),
                       description=_(u"If enabled, use the HTTPS protocol (where possible)."),
                       required=True,
                       default=True)

    portlet_height = schema.TextLine(title=_(u"Portlet height"),
                       description=_(u"If specified, this will be the height of the portlet (in pixels or percent)."),
                       required=False,
                       default=_(u""))

    portlet_width = schema.TextLine(title=_(u"Portlet width"),
                       description=_(u"If specified, this will be the width of the portlet (in pixels or percent)."),
                       required=False,
                       default=_(u""))

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IGoogleDocsPortlet)

    # TODO: Set default values for the configurable parameters here

    header = u"My Google Docs"
    limit = 0 
    hosted_domain = u""
    secure_connection = True
    portlet_height = u"160"
    portlet_width = u"100%"

    # TODO: Add keyword parameters for configurable parameters here
    def __init__(self, header=u"My Google Docs", limit=0, hosted_domain=u"", secure_connection=True, portlet_height=u"160", portlet_width=u"100%"):
        self.header = header
        self.limit = limit
        self.hosted_domain = hosted_domain
	self.secure_connection = secure_connection
	self.portlet_height = portlet_height
	self.portlet_width = portlet_width

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return self.header


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('googledocsportlet.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    @memoize
    #need to make the url back to google 
    def google_docs_iframe_url(self):
       url = 'http'+(self.data.secure_connection and 's' or '')+'://docs.google.com'
 
       if self.data.hosted_domain:
           url += ('/a/'+self.data.hosted_domain)
       
       url += '/API/IGoogle?'
       
       if self.data.limit:
           url += ('up_numDocuments='+str(self.data.limit))

       return url

    def google_url(self):
        url = 'http'+(self.data.secure_connection and 's' or '')+'://docs.google.com'

	if self.data.hosted_domain:
           url += ('/a/'+self.data.hosted_domain)

	return url 

# NOTE: If this portlet does not have any configurable parameters, you can
# inherit from NullAddForm and remove the form_fields variable.

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IGoogleDocsPortlet)

    def create(self, data):
        return Assignment(**data)


# NOTE: IF this portlet does not have any configurable parameters, you can
# remove this class definition and delete the editview attribute from the
# <plone:portlet /> registration in configure.zcml

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IGoogleDocsPortlet)
    
    label = _(u"Edit Google Docs Portlet")
    description = _(u"A portlet which displays a listing of a user's Google Documents.")

