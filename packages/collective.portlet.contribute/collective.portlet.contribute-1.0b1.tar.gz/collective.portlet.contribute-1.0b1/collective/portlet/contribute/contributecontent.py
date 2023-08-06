from zope.interface import implements
from zope.component import getUtility, getMultiAdapter

from zope import schema
from zope.formlib import form

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from plone.memoize.instance import memoize

from plone.i18n.normalizer.interfaces import IIDNormalizer

from plone.app.vocabularies.catalog import SearchableTextSourceBinder

from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget

from Acquisition import aq_inner, aq_parent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.CMFCore.interfaces import IFolderish

from collective.portlet.contribute import ContributeContentMessageFactory as _

class IContributeContent(IPortletDataProvider):
    """Portlet schema.
    """

    header = schema.TextLine(title=_(u"Portlet header"),
                             description=_(u"Title of the rendered portlet"),
                             required=True)
    
    text = schema.Text(title=_(u"Text"),
                       description=_(u"Lead-in text before the add-content button."),
                       required=False)

    footer = schema.TextLine(title=_(u"Portlet footer"),
                             description=_(u"Text to be shown in the footer"),
                             required=False)
    
    omit_border = schema.Bool(title=_(u"Omit portlet border"),
                              description=_(u"Tick this box if you want to render the portlet "
                                             "without the standard header, border or footer."),
                              required=True,
                              default=False)

    current_folder = schema.Bool(title=_(u"Add to current folder"),
                                 description=_(u"If true, add content to the current folder always. "
                                                "Otherwise, the path below will be used."),
                                 required=True,
                                 default=False)
    
    folder = schema.Choice(title=_(u"Folder"),
                           description=_(u"Folder where the content should be added. "
                                          "Has no effect if 'Add to current folder' is selected."),
                           required=False,
                           source=SearchableTextSourceBinder({'is_folderish': True}, default_query='path:'))

    types = schema.Tuple(title=_(u"Type(s)"),
                         description=_(u"Select one or more types to allow uses to add. "
                                        "Each type will be represented by a button."),
                         required=True,
                         value_type=schema.Choice(title=_(u"Type"),
                                                  vocabulary="plone.app.vocabularies.PortalTypes"))

class Assignment(base.Assignment):
    """Persistent assignment class
    """

    implements(IContributeContent)

    header = u""
    text = u""
    footer = u""
    omit_border = False
    current_folder = False
    folder = None
    types = ()
    
    def __init__(self, header=u"", text=u"", footer=u"", omit_border=False,
                    current_folder=False, folder=None, types=()):
        self.header = header
        self.text = text
        self.footer = footer
        self.omit_border = omit_border
        self.current_folder = current_folder
        self.folder = folder
        self.types = types

    @property
    def title(self):
        return self.header

class Renderer(base.Renderer):
    """Portlet renderer.
    """

    render = ViewPageTemplateFile('contributecontent.pt')

    def css_class(self):
        """Generate a CSS class from the portlet header
        """
        header = self.data.header
        normalizer = getUtility(IIDNormalizer)
        return "portlet-static-%s" % normalizer.normalize(header)

    def has_footer(self):
        return bool(self.data.footer)

    @property
    def available(self):
        return len(self.addable_types()) > 0
    
    @memoize
    def add_context(self):
        
        if self.data.current_folder:
            if INonStructuralFolder.providedBy(self.context) or not IFolderish.providedBy(self.context):
                return aq_parent(aq_inner(self.context))
            else:
                return aq_inner(self.context)
        else:
            path = self.data.folder
            if not path:
                return None

            if path.startswith('/'):
                path = path[1:]
        
            if not path:
                return None

            portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
            portal = portal_state.portal()
            return portal.restrictedTraverse(path, default=None)
    
    @memoize
    def addable_types(self):
        """Get a list of dicts with keys 'id', 'title', 'description',
        'action' and 'icon'.
        """
        
        context = self.add_context()
        if context is None:
            return ()
        
        factories_view = getMultiAdapter((context, self.request), name='folder_factories')
        addable_types = factories_view.addable_types(include=self.data.types)
        
        return addable_types
        

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IContributeContent)
    form_fields['text'].custom_widget = WYSIWYGWidget
    form_fields['folder'].custom_widget = UberSelectionWidget
    
    label = _(u"Add contribute content portlet")
    description = _(u"A portlet which lets a user add content of a particular type")
    
    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IContributeContent)
    form_fields['text'].custom_widget = WYSIWYGWidget
    form_fields['folder'].custom_widget = UberSelectionWidget
    
    label = _(u"Edit contribute content portlet")
    description = _(u"A portlet which lets a user add content of a particular type")
