from zope.interface import implements

from Products.Archetypes.atapi import *
from Products.ATContentTypes.atct import *
from Products.ATContentTypes.configuration import zconf

from Products.CMFPlone import PloneMessageFactory as _pmf

from quintagroup.doublecolumndocument import doublecolumndocumentMessageFactory as _
from quintagroup.doublecolumndocument import config
from interfaces import IDoubleColumnDocument

DoubleColumnDocumentSchema = ATContentTypeSchema.copy() + Schema((

    # overrides ExtensibleMetadataSchema "description" field
    TextField("description",
        default="",
        searchable=True,
        storage=AnnotationStorage(),
        widget=TextAreaWidget(
            label=_pmf(u"label_description", default=u"Description"),
            description=_pmf(u"help_description", default=u"A brief description of the item."),
            rows = 3
        ),
    ),

    TextField("body1",
        schemata=_(u"Columns"),
        default="",
        searchable=True,
        validators=("isTidyHtmlWithCleanup",),
        default_output_type="text/x-html-safe",
        allowable_content_types=zconf.ATDocument.allowed_content_types,
        storage=AnnotationStorage(),
        widget=RichWidget(
            label=_(u"label_body-1_text", default=u"Body 1 text"),
            description=_(u"help_body-1_text", default=u"The body 1 text of the document."),
            rows=25
        ),
    ),

    TextField("body2",
        schemata=_(u"Columns"),
        default="",
        searchable=True,
        validators=("isTidyHtmlWithCleanup",),
        default_output_type="text/x-html-safe",
        allowable_content_types=zconf.ATDocument.allowed_content_types,
        storage=AnnotationStorage(),
        widget=RichWidget(
            label = _(u"label_body-2_text", default=u"Body 2 text"),
            description = _(u"help_body-2_text", u"The body 2 text of the document."),
            rows = 25
        ),
    )

))


DoubleColumnDocumentSchema["title"].storage = AnnotationStorage()

class DoubleColumnDocument(ATCTContent):
    """Double Column Document"""

    implements(IDoubleColumnDocument)

    portal_type = "DoubleColumnDocument"

    #_at_rename_after_creation = True

    schema = DoubleColumnDocumentSchema

    title = ATFieldProperty("title")
    description = ATFieldProperty("description")

    body1 = ATFieldProperty("body1")
    body2 = ATFieldProperty("body2")


registerType(DoubleColumnDocument, config.PROJECTNAME)
