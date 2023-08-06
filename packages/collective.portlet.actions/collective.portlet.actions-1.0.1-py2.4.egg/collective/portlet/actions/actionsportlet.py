# -*- coding: utf-8 -*-
# $Id: actionsportlet.py 86466 2009-05-20 09:33:08Z piv $
"""Actions portlet"""

from Acquisition import aq_inner
from zope.interface import implements
from zope import schema
from zope.formlib import form
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from zope.component import getMultiAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.memoize import view as pm_view


from collective.portlet.actions import ActionsPortletMessageFactory as _


class IActionsPortlet(IPortletDataProvider):
    """A portlet that shows an action category"""

    ptitle = schema.TextLine(
        title=_(u'label_title',
                default=u"Portlet Title"),
        description=_(u'help_title',
                      default=u"Displayed title of this portlet"),
        default=u"",
        required=True)

    category = schema.Choice(
        title=_(u'label_actions_category',
                default=u"Actions category"),
        description=_(u'help_actions_category',
                      default=u"Select an action category"),
        required=True,
        vocabulary='Modulo.vocabularies.actioncategories')

    show_icons = schema.Bool(
        title=_(u'label_show_icons',
                default=u"Show icons"),
        description=_(u'help_show_icons',
                      default=u"Show icons or default icon for actions without icon."),
        required=True,
        default=True)

    default_icon = schema.ASCIILine(
        title=_(u'label_default_icon',
                default=u"Default icon"),
        description=_(u'help_default_icon',
                      default=u"What icon we should use for actions with no specific icons. A 16*16 pixels image."),
        required=False,
        default='action_icon.gif')


class Assignment(base.Assignment):
    """Portlet assignment.
    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IActionsPortlet)

    ptitle = u""
    category = u""
    show_icons = True
    default_icon = 'action_icon.gif'

    def __init__(self, ptitle=u"", category=u"", show_icons=True, default_icon='action_icon.gif'):
        self.ptitle = ptitle
        self.category = category
        self.show_icons = show_icons
        self.default_icon = default_icon
        return

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"Actions portlet") + ' "%s"' % self.ptitle


class Renderer(base.Renderer):
    """Actions portlet renderer."""

    render = ViewPageTemplateFile('actionsportlet.pt')

    @property
    def available(self):
        """Override base class"""

        return bool(self.actionLinks())


    @property
    def title(self):
        """Portlet title"""

        return self.data.ptitle

    def actionLinks(self):
        """Features of action links"""
        return self.cachedLinks(self.data.category, self.data.default_icon,
                                self.data.show_icons)

    @pm_view.memoize
    def cachedLinks(self, actions_category, default_icon, show_icons):
        context_state = getMultiAdapter((aq_inner(self.context), self.request),
                                        name=u'plone_context_state')
        actions = context_state.actions().get(actions_category, [])

        # Finding method for icons
        if show_icons:
            portal_actionicons = getToolByName(self.context, 'portal_actionicons')
            def render_icon(category, action, default):
                if action['icon']:
                    # We have an icon *in* this action
                    return action['icon']
                # Otherwise we look for an icon in portal_actionicons
                return portal_actionicons.renderActionIcon(category, action['id'], default)
        else:
            def render_icon(category, action_id, default):
                # We don't show icons whatever
                return None

        # Building the result as list of dicts
        result = []
        for action in actions:
            if not (action['available']
                    and action['visible']
                    and action['allowed']
                    and action['url']):
                continue
            link = {
                'url': action['url'],
                'title': action['title'],
                'icon': render_icon(
                    actions_category,
                    action,
                    default=default_icon)
                }
            result.append(link)
        return result


class AddForm(base.AddForm):
    """Portlet add form.
    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IActionsPortlet)
    label = _(u'heading_add_actions_portlet',
              default=u'Add actions portlet')
    description= _(u'help_add_actions_portlet',
                   default=u'An action portlet displays actions from a category')

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IActionsPortlet)


class ActionCategoriesVocabulary(object):
    """Provides an actions categories vocabulary"""

    implements(IVocabularyFactory)

    def __call__(self, context):
        portal_actions = getToolByName(context, 'portal_actions')

        # Building the list of action categories
        categories = portal_actions.listFilteredActionsFor(context).keys()
        categories.sort()
        return SimpleVocabulary([SimpleTerm(cat, title=cat) for cat in categories])


ActionCategoriesVocabularyFactory = ActionCategoriesVocabulary()
