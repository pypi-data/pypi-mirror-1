from zope.interface import Interface

from zope.interface import implements
from zope.component import getMultiAdapter
from zope import schema
from zope.formlib import form

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from ely.portlets.image import ImagePortletMessageFactory as _
from ely.portlets.image.widget import ImageWidget

class IImagePortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    title = schema.TextLine(title=_(u"Title"),
                             description=_(u"Title for the image"),
                             required=False)

    caption = schema.TextLine(title=_(u"Caption"),
                              description=_(u"Caption for the image"),
                              required=False)

    internal_target = schema.Choice(title=_(u"Internal Target"),
                            description=_(u"Find an internal target for this image to link to"),
                            required=False,
                            source=SearchableTextSourceBinder({}))

    image = schema.Field(title=u'Image field',
                         description=u"Add or replace image for the portlet",
                         required=False)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IImagePortlet)

    title = u''
    caption = u''
    image = None
    assignment_context_path = None
    internal_target = None

    def __init__(self,
                 assignment_context_path=None,
                 image=None,
                 title=u'',
                 caption=u'',
                 internal_target=None):
        self.image = image
        self.assignment_context_path = assignment_context_path
        self.internal_target = internal_target
        self.title = title
        self.caption = caption


class Renderer(base.Renderer):
    """Portlet renderer.
    """

    render = ViewPageTemplateFile('imageportlet.pt')

    @property
    @memoize
    def image_tag(self):
        if self.data.image:
            state=getMultiAdapter((self.context, self.request),
                                  name="plone_portal_state")
            portal=state.portal()
            assignment_url = \
                    portal.unrestrictedTraverse(
                self.data.assignment_context_path).absolute_url()
            width = self.data.image.width
            height = self.data.image.height
            return "<img src='%s/%s/@@image' width='%s' height='%s'/>" % \
                   (assignment_url,
                    self.data.__name__,
                    str(width),
                    str(height))
        return None

    @property
    @memoize
    def linked_object(self):
        state=getMultiAdapter((self.context, self.request),
                              name="plone_portal_state")
        portal=state.portal()
        object_path = self.data.internal_target
        # it feels insane that i need to do manual strippping of the
        # first slash in this string. I must be doing something wrong
        # please make this bit more sane

        if object_path is None or len(object_path)==0:
            return None
        # The portal root is never a target

        if object_path[0]=='/':
            object_path = object_path[1:]
        return portal.restrictedTraverse(object_path, default=None)

    @property
    def link_url(self):
        linked_object = self.linked_object
        if linked_object:
            return linked_object.absolute_url()
        else:
            return None

class AddForm(base.AddForm):
    """Portlet add form.
    """
    form_fields = form.Fields(IImagePortlet)
    form_fields['image'].custom_widget = ImageWidget
    form_fields['internal_target'].custom_widget = UberSelectionWidget

    def create(self, data):
        assignment_context_path = \
                    '/'.join(self.context.__parent__.getPhysicalPath())
        return Assignment(assignment_context_path=assignment_context_path,
                          **data)

class EditForm(base.EditForm):
    """Portlet edit form.
    """
    form_fields = form.Fields(IImagePortlet)
    form_fields['image'].custom_widget = ImageWidget
    form_fields['internal_target'].custom_widget = UberSelectionWidget
