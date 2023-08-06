from zope import schema
from zope.interface import Interface

from Products.CMFPlone import PloneMessageFactory as _pmf

from quintagroup.doublecolumndocument import doublecolumndocumentMessageFactory as _

class IDoubleColumnDocument(Interface):

    title = schema.TextLine(title=_pmf(u"label_title", default=u"Product title"), required=True)
    description = schema.TextLine(title=_pmf(u"label_description", default=u"A brief description of the item."))

    body1 = schema.SourceText(title=_(u"label_body-1_text", default=u"Body 1 text"))
    body2 = schema.SourceText(title=_(u"label_body-2_text", default=u'Body 2 text'))