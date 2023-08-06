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

    # some_field = schema.TextLine(title=_(u"Some field"),
    #                              description=_(u"A field to use"),
    #                              required=True)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IRecentCommentsPortlet)

    # TODO: Set default values for the configurable parameters here

    # some_field = u""

    # TODO: Add keyword parameters for configurable parameters here
    # def __init__(self, some_field=u""):
    #    self.some_field = some_field

    def __init__(self):
        pass

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Recent Comments"


def get_key(element):
    return element["time"]


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('recentcommentsportlet.pt')

    def comments(self):
	number = 5
	urltool = getToolByName(self.context, 'portal_url')
	portal  = urltool.getPortalObject()
	comment_sections = []
	comments = []
	catalog = getToolByName(portal, 'portal_catalog')
	news = catalog.searchResults(portal_type="News Item")
	for new in news:
	    path = new.getPath()
	    obj  = new.getObject()
	    title = obj.title
	    if hasattr(obj, 'talkback'):
	        comment_sections += [(path,title,obj.talkback)]
	for sect in comment_sections:
	    path, title, obj = sect
	    for time, c in obj.objectItems():
		ftime = t.strftime("%d/%b/%Y %H:%M:%S", t.localtime(int(time)))
		#fitime = t.ctime(int(time))
	        comments += [{'time':ftime,'comment':c,'url':path, 'title':title}]
	comments = sorted(comments, key=get_key)
	comments = comments[:number]
	return comments


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
