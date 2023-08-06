from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from redturtle.portlet.lightreviewlist import LightReviewListMessageFactory as _


class ILightReviewList(IPortletDataProvider):
    """A lighter review list portlet; it only display a link to full_review_list
    as normal review list portlet is someway slow and inefficent.
    """

    # some_field = schema.TextLine(title=_(u"Some field"),
    #                              description=_(u"A field to use"),
    #                              required=True)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ILightReviewList)

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
        return "Light review list"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('lightreviewlist.pt')


    @property
    def available(self):
        """Don't show anything if anon user"""
        return not getToolByName(self.context, 'portal_membership').isAnonymousUser()

    @property
    def portal_url(self):
        return getToolByName(self.context, 'portal_url').getPortalObject().absolute_url()

#class AddForm(base.AddForm):
#    """Portlet add form.
#
#    This is registered in configure.zcml. The form_fields variable tells
#    zope.formlib which fields to display. The create() method actually
#    constructs the assignment that is being added.
#    """
#    form_fields = form.Fields(ILightReviewList)
#
#    def create(self, data):
#        return Assignment(**data)

class AddForm(base.NullAddForm):
    """Portlet add form"""
    def create(self):
        return Assignment()


#class EditForm(base.EditForm):
#    """Portlet edit form.
#
#    This is registered with configure.zcml. The form_fields variable tells
#    zope.formlib which fields to display.
#    """
#    form_fields = form.Fields(ILightReviewList)
