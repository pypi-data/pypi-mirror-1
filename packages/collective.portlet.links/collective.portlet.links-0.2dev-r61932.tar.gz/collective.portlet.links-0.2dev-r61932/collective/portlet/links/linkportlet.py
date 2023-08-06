from zope.interface import Interface

from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.links import LinkPortletMessageFactory as _

class ILinkPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form 
    # below.

    titles = schema.List(
        title=_(u"Title"),
        description=_(u"The text to click on, one each line. You need the"
                       " same amount links matching these titles."),
        required=True,
        value_type = schema.TextLine(),
    )
                             

    urls = schema.List(
        title=_(u"URLs"),
        description=_(u"URLs like http://www.test.de/, one each line, as the "
                      "link target for the text given above."),
        required=True,
        value_type = schema.TextLine(),
    )

    cssclass = schema.TextLine(
        title=_(u"Link CSS class"),
        description=_(u"An additional css class to apply to the <a href...> tag"),
        required=False
    )


class Assignment(base.Assignment):
    """Portlet assignment.
    
    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    
    implements(ILinkPortlet)

    cssclass = u"context"

    # TODO: Add keyword parameters for configurable parameters here
    # def __init__(self, some_field=u"):
    #    self.some_field = some_field
        
    def __init__(self,titles="",urls=""):
	self.titles=titles
	self.urls=urls
        
        
    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"Link Portlet")


class MyLink:
    """simple (possibly superfluos) class with link-data.
    """
    def __init__(self, title, url):
        self.title = title
        self.url = url

class Renderer(base.Renderer):
    """Portlet renderer.
    
    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('linkportlet.pt')
    
    def cssclass(self):
        return self.data.cssclass
    
    def listlinks(self):
        titles = self.data.titles
        links = self.data.urls        

        if len(titles) != len(links):
            return [MyLink('Error, number of links != number of titles.', '#')]
        result = []
        for idx in range(0, len(titles)):
            result.append(MyLink(titles[idx], links[idx]))
        return result

# NOTE: If this portlet does not have any configurable parameters, you can
# inherit from NullAddForm and remove the form_fields variable.

class AddForm(base.AddForm):
    """Portlet add form.
    
    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(ILinkPortlet)
    label=_(u"Add Link Portlet")
    description=_(u"This Portlet shows a list of Links as Buttons")

    def create(self, data):
	assignment=Assignment()
	form.applyChanges(assignment, self.form_fields, data)
	return assignment

# NOTE: IF this portlet does not have any configurable parameters, you can
# remove this class definition and delete the editview attribute from the
# <plone:portlet /> registration in configure.zcml

class EditForm(base.EditForm):
    """Portlet edit form.
    
    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(ILinkPortlet)
    label=_(u"Edit Link Portlet")
    description=_(u"This Portlet shows a list of Links as Buttons")

