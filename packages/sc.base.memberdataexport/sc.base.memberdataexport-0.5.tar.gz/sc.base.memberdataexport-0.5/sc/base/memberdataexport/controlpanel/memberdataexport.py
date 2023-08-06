from zope import schema

from zope.component import adapts
from zope.interface import Interface
from zope.interface import implements

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase

from zope.formlib.form import FormFields
from plone.app.controlpanel.form import ControlPanelForm

from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from sc.base.memberdataexport import MessageFactory as _

LINETERMINATOR_CHOICES = {
    _(u"Windows"): u'win',
    _(u"Linux/MacOSX"): u'other',
}

LINETERMINATOR_VOCABULARY = SimpleVocabulary(
    [SimpleTerm(v, v, k) for k, v in LINETERMINATOR_CHOICES.items()]
    )

ENCODING_CHOICES = {
    _(u"UTF-8"): u'utf-8',
    _(u"ISO-8859-1"): u'iso-8859-1',
}

ENCODING_VOCABULARY = SimpleVocabulary(
    [SimpleTerm(v, v, k) for k, v in ENCODING_CHOICES.items()]
    )

class IExportSchema(Interface):
    
    
    filename = schema.TextLine(title=_(u'File name'),
                                     description=_(u'Filename used on export'),
                                     required=True,
                                     default=u'memberdata.csv')
    
    delimiter = schema.TextLine(title=_(u'Delimiter'),
                                description=_(u'Character to be used on \
                                                export'),
                                required=True,
                                default=u',')
    
    lineTerminator = schema.Choice(title=_(u'Line terminator'),
                                   description=_(u''),
                                   required=True,
                                   vocabulary=LINETERMINATOR_VOCABULARY)
    
    encoding = schema.Choice(title=_(u'Encoding'),
                                     description=_(u''),
                                     required=True,
                                     vocabulary=ENCODING_VOCABULARY)
    
    alwaysQuote = schema.Bool(title = _(u"Always quote fields?"),
                              description = _(u"Should we always use quotes to "
                                               "separate data."),
                              default = False,
                              required = True)
    
class ExportPanelAdapter(SchemaAdapterBase):
    
    adapts(IPloneSiteRoot)
    implements(IExportSchema)
    
    def __init__(self, context):
        super(ExportPanelAdapter, self).__init__(context)
        portal_properties = getToolByName(context, 'portal_properties')
        self.context = portal_properties.memberdataexport_properties
    
    delimiter = ProxyFieldProperty(IExportSchema['delimiter'])
    filename = ProxyFieldProperty(IExportSchema['filename'])
    
    def get_encoding(self):
        return self.context.encoding
    
    def set_encoding(self, value):
        self.context.manage_changeProperties(encoding=value)
    encoding = property(get_encoding,set_encoding)
    
    def get_lineTerminator(self):
        return self.context.lineTerminator
    
    def set_lineTerminator(self, value):
        self.context.manage_changeProperties(lineTerminator=value)
    lineTerminator = property(get_lineTerminator,set_lineTerminator)
    
    def get_alwaysQuote(self):
        return self.context.alwaysQuote
    
    def set_alwaysQuote(self, value):
        if value:
            self.context.manage_changeProperties(alwaysQuote=True)
        else:
            self.context.manage_changeProperties(alwaysQuote=False)
    
    alwaysQuote = property(get_alwaysQuote, set_alwaysQuote)

class ExportPanel(ControlPanelForm):

    form_fields = FormFields(IExportSchema)
    
    label = _(u'Member data export settings')
    description = _(u'Configure export settings for memberdata.')
    form_name = _(u'Export settings')
