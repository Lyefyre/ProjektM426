# -*- coding: utf-8 -*-
# from __future__ import unicode_literals
import calendar
import locale
from django.db.models.functions import Concat
import json
import datetime
import pytz

from django.utils.translation import ugettext_lazy as _

from django.core import serializers
from django import forms
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View, FormView, UpdateView, ListView, CreateView, DeleteView
from django.views.generic.base import TemplateView
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django_hashedfilenamestorage.storage import HashedFilenameFileSystemStorage
from django.db.models import CharField, Value as V

from empty import settings
from demo.models import Information, Organization

from django.views.decorators.csrf import csrf_exempt

from django.db.models.signals import post_save
from django.dispatch import receiver
import os
import shutil

from braces.views import (AjaxResponseMixin, JSONResponseMixin, LoginRequiredMixin, SuperuserRequiredMixin)

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import render_to_string

from demo.get_image_size import get_image_size, UnknownImageFormat
import xlrd
from demo.lazypdf import get_pdf_content

import docx2txt
from odf import text, teletype
from odf.opendocument import load

from demo.ODSReader import ODSReader
from PIL import Image, ExifTags


class FileslistAndLasteditInfoFunctions():
    """
    liefert die dateien eines ordners als liste
    und setzt oder liest last_edited (variabel des zuletzt geänderten datensatzes) um (wenn superuser) nach dem bearbeiten dorthin zu scrollen
    """

    def addtolist(self, path, list, textlist):
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for filename in files:
                    pathandname = root + filename

                    try:
                        width, height = get_image_size(pathandname)
                        wh = str(width / height) + '_'
                    except UnknownImageFormat:
                        wh = 'noimage_'

                    if textlist is not None:
                        tx = ''
                        if wh == 'noimage_':
                            print('path: ', pathandname)
                            try:
                                if '.pdf' in filename:
                                    # tx = pconvert(pathandname)
                                    pass  # handled with lazypdf

                                elif '.txt' in filename:
                                    txf = open(pathandname, encoding='utf-8')
                                    tx = txf.read()
                                    txf.close()

                                elif '.docx' in filename:
                                    tx = docx2txt.process(pathandname)

                                elif '.odt' in filename:
                                    textdoc = load(pathandname)
                                    tx = teletype.extractText(textdoc.body)

                                elif '.xlsx' in filename:
                                    wb = xlrd.open_workbook(pathandname)  # xls file to read from
                                    sh1 = wb.sheet_by_index(0)  # first sheet in workbook
                                    for rownum in range(sh1.nrows):
                                        onerow = ' '.join(sh1.row_values(rownum))
                                        tx = tx + onerow + '\n'

                                elif '.ods' in filename:
                                    doc = ODSReader(pathandname, clonespannedcolumns=True)
                                    table = doc.getSheet(u'Sheet1')
                                    for i in range(len(table)):
                                        for j in range(len(table[i])):
                                            tx = tx + ' ' + table[i][j]

                            except Exception:
                                pass

                        textlist.append(tx)

                    list.append(wh + pathandname)

        if textlist is not None:
            return list, textlist
        else:
            return list

    last_edited = 0

    def speaklastedited(self):

        return FileslistAndLasteditInfoFunctions.last_edited

    def setlastedited(self, pk):
        FileslistAndLasteditInfoFunctions.last_edited = pk


class EditAndCreateInfoFunctions():
    """
    formatiert formularfelder welche beim erstellen und beim bearbeiten einer information verwendet werden
    und setzt alle andern statuse auf AKTIV wenn einer information der status NEW zugewiesen wird
    """

    INFO_STATUS = (
        ('NEW', _('New (on top)')),
        ('ACTIV', _('Normal (by creation date)')),
        ('ARCHIV', _('Archive (invisible)')),
    )

    def formatcommonfields(self, form):
        form.fields['title'].widget = forms.TextInput(attrs={'title': _('Write the text of the headline in this field'), 'placeholder': _('Write the headline of the info in this field')})
        form.fields['text'].widget = forms.Textarea(attrs={'rows': 10, 'title': _('Write the text of the info in this field'), 'placeholder': _('Write the text of the info in this field')})
        form.fields['title'].label = form.fields['text'].label = ''
        form.fields['status'] = forms.ChoiceField(choices=self.INFO_STATUS)

        return form

    def speakspecifictranslations(self):
        return {
            'ClickDownload': '{}'.format(_('Click to download')),
            'Download': '{}'.format(_('Download')),
            'RemoveFile': '{}'.format(_('Remove File')),
            'Confirm': '{}'.format(_('Confirm')),
            'WantDeleteInfo': '{}'.format(_('Do you want to delete the entire Information')),
            'WantDeleteFile': '{}'.format(_('Do you want to delete the File')),
            'FileDeleted': '{}'.format(_('File deleted')),
            'BtnConfirm': '{}'.format(_('ok')),
            'BtnCancel': '{}'.format(_('Cancel')),
            'FileSize': '{}'.format(_('Your File has a size of:')),
            'MaxFileSize': '{}'.format(_('But the maximum possible size is:')),
            'InvalidFileType': '{}'.format(_('You can\'t upload files of this type.')),
            'OkFileTypeMsg': '{}'.format(_('You can upload the following types of Files:')),
            'AddNewInfo': '{}'.format(_('add a new information'))
        }

    def revertstatuses(self, ps, pk):
        if ps == 'NEW':
            ms = self.model.objects.filter(status='NEW')
            for m in ms:
                if m.pk != pk:
                    m.status = 'ACTIV'
                    m.save()


class HomePageView(TemplateView):
    template_name = "demo/start.html"

    def post(self, request, *args, **kwargs):

        user = authenticate(request, username=request.POST['email'], password=request.POST['password'])

        if user is not None:
            login(request, user)

            return redirect('bag')

        else:

            return redirect('start')


class HomePageNewView(TemplateView):
    model = Organization
    template_name = "demo/loginnew.html"

    def post(self, request, *args, **kwargs):

        user = authenticate(request, username=request.POST['email'], password=request.POST['password'])

        print('hallo product owner DS, somebody requested an account for organization nr. ', request.POST['organization'])
        print('')
        is_Org = len(self.model.objects.filter(pk=request.POST['organization']))
        print('try org2: ', is_Org)

        if is_Org == 1:
            if user is not None:
                login(request, user)

                print('')
                print('hallo product owner DS, you are logged in')
                print('')

                return redirect('bag')

            else:

                print('')
                print('hallo product owner DS, you are rejected by wrong organization')
                print('')

                return redirect('start')

        else:

            print('')
            print('hallo product owner DS, you are rejected')
            print('')

            return redirect('start')


class BagEditView(UpdateView, EditAndCreateInfoFunctions, FileslistAndLasteditInfoFunctions):
    model = Information
    fields = ['title', 'text', 'status']
    success_url = reverse_lazy('bag')
    template_name = "demo/bagedit.html"

    def get_form(self, form_class=None):
        self.setlastedited(self.kwargs['pk'])

        form = self.formatcommonfields(super(BagEditView, self).get_form(form_class))

        form.fields['infopk'] = forms.CharField(max_length=250, initial=self.kwargs['pk'])
        form.fields['infopk'].widget = forms.HiddenInput()

        return form

    def get_context_data(self, **kwargs):
        context = super(BagEditView, self).get_context_data(**kwargs)
        context['image_urls_path'] = 'infophotos/' + str(self.kwargs['pk']) + '/'
        path = settings.MEDIA_ROOT + '/infophotos/' + str(self.kwargs['pk']) + '/'
        context['image_urls'] = self.addtolist(path, [], None)
        context['specificTranslations'] = self.speakspecifictranslations()
        # print('z 240 - specificTranslations: ', context['specificTranslations'])
        return context

    def post(self, request, *args, **kwargs):
        self.revertstatuses(request.POST['status'], self.kwargs['pk'])

        return super(BagEditView, self).post(request, *args, **kwargs)


class CreateInformation(CreateView, EditAndCreateInfoFunctions):
    model = Information
    fields = ['title', 'text', 'status']

    def get_form(self, form_class=None):
        form = self.formatcommonfields(super(CreateInformation, self).get_form(form_class))

        form.fields['status'].initial = ['NEW']
        form.fields['listorimages'] = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

        return form

    def get_context_data(self, **kwargs):
        context = super(CreateInformation, self).get_context_data(**kwargs)
        context['specificTranslations'] = self.speakspecifictranslations()
        return context

    def post(self, request, *args, **kwargs):
        self.revertstatuses(request.POST['status'], None)
        if request.POST['listorimages'] == '0':
            self.success_url = reverse_lazy('info')

        return super(CreateInformation, self).post(request, *args, **kwargs)


#
# Django Signal, erstellt automatisch ein Ordner innerhalb von infophotos für die Mediendateien mit dem pk des neu erstellten Informationsdatensatzes als Name.
# Der Bearbeitungsmodus wird aufgerufen um Mediendateien hinzuzufügen.
#
@receiver(post_save, sender=Information)
def make_directory_on_information_creation(sender, instance, created, **kwargs):
    if created:
        new_info = str(instance.pk)
        mediapath = settings.MEDIA_ROOT + '/infophotos/' + new_info + '/'
        if not os.path.exists(mediapath):
            print("mediapath doesn't exist. trying to make", mediapath)
            os.makedirs(mediapath)


@csrf_exempt
def deleteInformation(request):

    if str.isnumeric(request.POST['pk']):

        todel = request.POST['pk']

        filedir = settings.MEDIA_ROOT + '/infophotos/' + todel
        print('path to directory to delete: ', filedir)

        """
        todo: dont remove if this is the last object
        (small security via frontend)
        """

        Information.objects.filter(pk=todel).delete()

        try:
            shutil.rmtree(filedir)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))

        return JsonResponse({'status': 'true', 'message': 'record and files directory removed!', 'gone': todel}, status=200)


class ReadInformation(ListView, FileslistAndLasteditInfoFunctions):
    model = Information
    ordering = ['-status', '-id']

    def get_context_data(self, **kwargs):
        context = super(ReadInformation, self).get_context_data(**kwargs)
        filedir = settings.MEDIA_ROOT + '/infophotos/'
        context['specificTranslations'] = EditAndCreateInfoFunctions.speakspecifictranslations(self)
        context['last_edited'] = 'pos_' + str(self.speaklastedited())
        context['image_urls_path'] = filedir
        context['image_urls_dict'] = {}
        context['text_dict'] = {}
        for x in self.object_list:
            path = filedir + str(x.pk) + '/'
            context['image_urls_dict'][str(x.pk)], context['text_dict'][str(x.pk)] = self.addtolist(path, [], [])
        return context


class BagView(TemplateView, FileslistAndLasteditInfoFunctions):
    model = Information
    ordering = ['-status', '-id']
    template_name = "demo/bag.html"

    def get_queryset(self):
        qs = self.model.objects.all()
        return qs

    def get_context_data(self, **kwargs):
        context = super(BagView, self).get_context_data(**kwargs)
        self.object_list = self.get_queryset()
        filedir = settings.MEDIA_ROOT + '/infophotos/'
        context['specificTranslations'] = EditAndCreateInfoFunctions.speakspecifictranslations(self)
        # context['last_edited'] = 'pos_' + str(self.speaklastedited())
        context['image_urls_path'] = filedir
        context['image_urls_dict'] = {}
        context['text_dict'] = {}

        for x in self.object_list:
            path = filedir + str(x.pk) + '/'
            context['image_urls_dict'][str(x.pk)], context['text_dict'][str(x.pk)] = self.addtolist(path, [], [])

        return context


@csrf_exempt
def delete_info_file(request):

    if request.method == 'POST':
        file_name = request.POST['file_name']
        file_dir = request.POST['file_dir']

        if '/' not in file_name and str.isnumeric(file_dir):
            file_dir_name = settings.MEDIA_ROOT + '/infophotos/' + file_dir + '/' + file_name
            path_exists = 'oh no'
            if os.path.exists(file_dir_name):
                path_exists = 'oh yess'
                os.remove(file_dir_name)

            return JsonResponse({'status': 'true', 'message': 'file removed!', 'fn': file_dir_name, 'pe': path_exists}, status=200)

        else:

            return JsonResponse({'message': 'file not removed!', 'fd': file_dir,  'fn': file_name}, status=200)


class AjaxInfoUploadView(LoginRequiredMixin, JSONResponseMixin, AjaxResponseMixin, View):
    """
    View for uploading info photos via AJAX.
    """

    def post_ajax(self, request, *args, **kwargs):

        uploaded_file = request.FILES['file']
        filedir = settings.MEDIA_ROOT + '/infophotos/'

        dl_path = filedir + kwargs.get('pk') + '/'
        if not os.path.exists(dl_path):
            print("path doesn't exist. trying to make")
            os.makedirs(dl_path)

        filepath = '{}{}{}{}'.format(filedir, kwargs.get('pk'), '/', uploaded_file.name)
        fout = open(filedir + kwargs.get('pk') + '/' + uploaded_file.name, 'wb')
        fout.write(uploaded_file.file.read())
        fout.close()

        if '.jpg' in filepath or '.JPG' in filepath or '.jpeg' in filepath or '.JPEG' in filepath or '.png' in filepath or '.PNG' in filepath:
            try:
                image = Image.open(filepath)
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break
                exif = dict(image._getexif().items())

                if exif[orientation] == 3:
                    image = image.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    image = image.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    image = image.rotate(90, expand=True)
                image.save(filepath)
                image.close()
                print('rotated', filepath)

            except (AttributeError, KeyError, IndexError):
                # cases: image don't have getexif
                print('not rotated', filepath)
                # pass

        print('uploaded_file', uploaded_file)

        response_dict = {
            'message': 'File uploaded successfully!',
        }

        return self.render_json_response(response_dict, status=200)


def logout_view(request):
    logout(request)
    return redirect('start')
