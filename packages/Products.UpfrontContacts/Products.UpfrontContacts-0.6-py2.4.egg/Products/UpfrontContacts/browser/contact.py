from zope.interface import implements
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _

class IContactToolsPortlet(IPortletDataProvider):
    """A portlet that renders tools for importing, exporting and
       searching contacts
    """

class Assignment(base.Assignment):
    implements(IContactToolsPortlet)

    title = _(u'label_contact_tools', default=u'Contact Tools')

class Renderer(base.Renderer):
    """ Renderer for contact tools portlet
    """
    render = ViewPageTemplateFile('contacttools.pt')

class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
