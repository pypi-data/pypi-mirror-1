from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.recentcomments import RecentCommentsPortletMessageFactory as _

from Products.CMFCore.utils import getToolByName

import time as t


class IRecentCommentsPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    name = schema.TextLine(title=_(u"Titulo"),
                                      description=_(u"Titulo del portlet"),
                                      required=True)

    n_comment = schema.TextLine(title=_(u"Numero de comentarios"),
                                      description=_(u"Numero de comentarios recientes que apareceran"),
                                      required=True)

    n_caracter = schema.TextLine(title=_(u"Numero de caracteres"),
                                      description=_(u"Numero de caracteres que apareceran por comentario"),
                                      required=True)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IRecentCommentsPortlet)

    # TODO: Set default values for the configurable parameters here

    name = u""
    n_comment = u""
    n_caracter = u""

    # TODO: Add keyword parameters for configurable parameters here

    def __init__(self, name=u"", n_comment=u"", n_caracter=u""):
        self.name = name
        self.n_comment = n_comment
        self.n_caracter = n_caracter

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Recent Comments"


def get_key(element):
    return element["key"]


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('recentcommentsportlet.pt')

    def comments(self):
	number = int(self.data.n_comment)
	number_caracter = int(self.data.n_caracter)
	urltool = getToolByName(self.context, 'portal_url')
	portal  = urltool.getPortalObject()
	comment_sections = []
	comments = []
	catalog = getToolByName(portal, 'portal_catalog')
	news = catalog.searchResults(portal_type="News Item")
	for new in news:
	    path = new.getPath().replace('/b', '')
	    obj  = new.getObject()
	    title = obj.title
	    if hasattr(obj, 'talkback'):
	        comment_sections += [(path,title,obj.talkback)]
	for sect in comment_sections:
	    path, title, obj = sect
	    for time, c in obj.objectItems():
		ftime = t.strftime("%d/%b/%Y %H:%M:%S", t.localtime(int(time)))
		comments += [{'key':time, 'time':ftime,'comment':c,'url':path, 'title':title, 'text':c.text[:number_caracter]}]
	comments = sorted(comments, key=get_key, reverse=True)
	comments = comments[:number]
	return comments

    def name(self):
        return self.data.name

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IRecentCommentsPortlet)

    def create(self, data):
        return Assignment(**data)


# NOTE: If this portlet does not have any configurable parameters, you
# can use the next AddForm implementation instead of the previous.

# class AddForm(base.NullAddForm):
#     """Portlet add form.
#     """
#     def create(self):
#         return Assignment()


# NOTE: If this portlet does not have any configurable parameters, you
# can remove the EditForm class definition and delete the editview
# attribute from the <plone:portlet /> registration in configure.zcml


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IRecentCommentsPortlet)
