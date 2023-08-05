from tempfile import TemporaryFile
from reportlab.platypus import SimpleDocTemplate, Paragraph

from zope.interface import implementer
from zope.component import adapter
from zope.publisher.interfaces import IRequest
from zope.i18n import translate

from worldcookery.interfaces import IRecipe
from worldcookery.pdf.common import getStyleSheet, writeDocument
from worldcookery.pdf.interfaces import IPDFPresentation

@adapter(IRecipe, IRequest)
@implementer(IPDFPresentation)
def recipeToPDF(context, request):
    # this translates AND encodes to utf-8
    def _(msg, mapping=None):
        return translate(msg, domain='worldcookery', mapping=mapping,
                         context=request).encode('utf-8')

    title = ('<para spaceBefore="20" spaceAfter="40">%s</para>'
             % context.name.encode('utf-8'))
    description = ('<para spaceBefore="15">%s</para>'
                   % context.description.encode('utf-8'))
    ingr = [ingr.encode('utf-8') for ingr in context.ingredients]
    tools = [tool.encode('utf-8') for tool in context.tools]
    time_to_cook = _(u'${time_to_cook} mins',
                     mapping={'time_to_cook': context.time_to_cook})

    # create the document structure
    style = getStyleSheet()
    doc_structure = [
        Paragraph(title, style['title']),
        Paragraph(_(u"Name of the dish:"), style['h3']),
        Paragraph(context.name.encode('utf-8'), style['Normal']),
        Paragraph(_(u"Ingredients:"), style['h3']),
        Paragraph(', '.join(ingr), style['Normal']),
        Paragraph(_(u"Needed kitchen tools:"), style['h3']),
        Paragraph(', '.join(tools), style['Normal']),
        Paragraph(_(u"Time needed for preparation:"), style['h3']),
        Paragraph(time_to_cook, style['Normal']),
        Paragraph(description,  style['Normal']),
        ]

    tempfile = TemporaryFile()
    writeDocument(tempfile, doc_structure)
    return tempfile