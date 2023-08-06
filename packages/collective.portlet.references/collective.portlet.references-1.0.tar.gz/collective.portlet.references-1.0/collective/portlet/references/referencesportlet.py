from zope.interface import implements
from zope.component import getMultiAdapter, queryMultiAdapter

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from collective.portlet.references import ReferencesPortletMessageFactory as _
from Products.CMFCore.WorkflowCore import WorkflowException


class IReferencesPortlet(IPortletDataProvider):
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

    implements(IReferencesPortlet)

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
        return _("References")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('referencesportlet.pt')

    def __init__(self, context, request, view, manager, data):
        super(Renderer, self).__init__(context, request, view, manager, data)
        self.visible_text_links = []
        self.invisible_text_links = []
        self.visible_related_items = []
        self.invisible_related_items = []

    def update(self):
        context = aq_inner(self.context)
        refs = self.refs
        if len(refs) == 0:
            return {}
        try:
            related = context.getRelatedItems()
        except AttributeError:
            related = []
        wf_tool = getToolByName(context, 'portal_workflow')
        for ref in refs:
            pcs = getMultiAdapter((ref, self.request),
                                  name='plone_context_state')
            visible_for_anonymous = False
            for perm in ref.permissionsOfRole('Anonymous'):
                if perm['name'] == 'View':
                    visible_for_anonymous = (perm['selected'] == 'SELECTED')
                    break

            try:
                review_state_id = wf_tool.getInfoFor(ref, 'review_state')
            except WorkflowException:
                review_state_id = ''
                # TODO: perhaps the next line needs to be smarter,
                # like check higher levels.
                visible_for_anonymous = True
            review_state_title = wf_tool.getTitleForStateOnType(
                review_state_id, ref.portal_type)
            info = dict(
                title = pcs.object_title(),
                url = pcs.view_url(),
                state_id = review_state_id,
                state_title = review_state_title,
                )
            if ref in related:
                if visible_for_anonymous:
                    self.visible_related_items.append(info)
                else:
                    self.invisible_related_items.append(info)
            else:
                if visible_for_anonymous:
                    self.visible_text_links.append(info)
                else:
                    self.invisible_text_links.append(info)

    @property
    def reference_sections(self):
        infos = []
        infos.append(dict(
                title = _(u'Invisible links in the text'),
                refs = self.invisible_text_links,
                ))
        infos.append(dict(
                title = _(u'Visible links in the text'),
                refs = self.visible_text_links,
                ))
        infos.append(dict(
                title = _(u'Invisible related items'),
                refs = self.invisible_related_items,
                ))
        infos.append(dict(
                title = _(u'Visible related items'),
                refs = self.visible_related_items,
                ))
        return infos

    @property
    def refs(self):
        context = aq_inner(self.context)
        try:
            # Check if this method exists.
            context.getRefs
        except AttributeError:
            # For example a Plone Site has no references field.
            return []

        # We are not interested in e.g. the 'translationOf' relation from
        # LinguaPlone.

        # Get the references from plone.app.linkintegrity for
        # references inside the text.
        refs = context.getRefs('isReferencing')
        # Add the related items.
        for ref in context.getRefs('relatesTo'):
            if ref not in refs:
                refs.append(ref)
        return refs
        
    @property
    def available(self):
        # XXX not for anonymous.  Well, probably only for Reviewers.
        context = aq_inner(self.context)
        pps = context.restrictedTraverse('@@plone_portal_state')
        if pps.anonymous():
            return False
        return len(self.refs) > 0


class AddForm(base.NullAddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """

    def create(self):
        return Assignment()
