from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import pdfminer.settings
pdfminer.settings.STRICT = False

# converts pdf, returns its text content as a string


def pconvert(fname):
    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    fp = open(fname, mode='rb')

    password = ''
    maxpages = 0
    caching = True

    for page in PDFPage.get_pages(fp, [0], maxpages=maxpages, password=password, caching=caching):
        interpreter.process_page(page)
    fp.close()
    converter.close()
    text = output.getvalue()
    output.close
    return text
