import os
from empty import settings

from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import pdfminer.settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from subprocess import call
from Crypto.Cipher import AES

pdfminer.settings.STRICT = False

# converts pdf, returns its text content as a string


@csrf_exempt
def get_pdf_content(request):

    if request.method == 'POST':
        file_path = settings.MEDIA_ROOT + '/' + request.POST['file_path']

        output = StringIO()
        manager = PDFResourceManager()
        converter = TextConverter(manager, output, laparams=LAParams())
        interpreter = PDFPageInterpreter(manager, converter)

        # call('qpdf --password=%s --decrypt %s %s' %('', pdf_filename, pdf_filename_decr), shell=True)
        print('settings.PROJECT_ROOT: ', settings.PROJECT_ROOT)
        print('cwd: ', os.getcwd())
        tp = settings.PROJECT_ROOT + '/demo/temp.pdf'
        call('qpdf --password=%s --decrypt %s %s' % ('', file_path, tp), shell=True)
        fp = open(tp, mode='rb')

        password = ''
        maxpages = 0
        caching = False

        for page in PDFPage.get_pages(fp, [0], maxpages=maxpages, password=password, caching=caching):
            interpreter.process_page(page)
        fp.close()
        converter.close()
        text = output.getvalue()
        output.close

        return JsonResponse({'status': 'true', 'message': text, 'path': file_path}, status=200)

    else:

        return JsonResponse({'status': 'true', 'message': 'file not found!', 'path': file_path}, status=200)
