# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import admin
# from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from empty import settings

from .views import HomePageView, HomePageNewView, BagView, BagEditView, logout_view, AjaxInfoUploadView, delete_info_file, get_pdf_content, deleteInformation, CreateInformation, ReadInformation

urlpatterns = [

    # url(r"^admin/$", admin.site.urls),

    # url(r"home/$", HomePageView.as_view(), name="home"),

    # url(r'^$', staff_member_required(BagView.as_view())),

    url(r"^start/$", HomePageView.as_view(), name="start"),

    url(r'^$', lambda r: HttpResponseRedirect('start')),

    url(r"loginnew/$", HomePageNewView.as_view(), name="loginnew"),

    url(r"bag/$", staff_member_required(BagView.as_view()), name="bag"),

    url(r"bagedit/(?P<pk>\d+)/$", staff_member_required(BagEditView.as_view()), name="bagedit"),

    url(r'^create_information/$', staff_member_required(CreateInformation.as_view()), name='create_information'),

    # url(r'^edit_information/(?P<pk>\d+)/$', staff_member_required(EditInformation.as_view()), name='edit_information'),

    url(r'^delete_information$', staff_member_required(deleteInformation), name='delete_information'),

    url(r'^info/$', ReadInformation.as_view(), name='info'),

    url(r'^i18n/', include('django.conf.urls.i18n')),

    url(
        regex=r'^ajax-infoupload/(?P<pk>\d+)/$', view=AjaxInfoUploadView.as_view(), name='ajax_info_upload_view',
    ),

    url(r'^delete_info_file$', delete_info_file, name='delete_info_file'),

    url(r'^get_pdf_content$', get_pdf_content, name='get_pdf_content'),

    url(r'^logout$', logout_view, name='logout'),

]
