# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django.forms.formsets import BaseFormSet, formset_factory

from bootstrap3.tests import TestForm
from invitations.models import Invitation

from demo.models import Mitarbeiter, Team, Kunde, SPESEN_TYP, emptySetting, KALENDER_VIEWS
#from demo.widgets import RelatedFieldWidgetCanAdd, CustomBootrapTextInputWidget, LeafletMapWidget
from demo.widgets import LeafletMapWidget, MonthYearWidget
from django.utils.translation import gettext_lazy as _


RADIO_CHOICES = (("1", "Radio 1"), ("2", "Radio 2"))

MEDIA_CHOICES = (
    ("Audio", (("vinyl", "Vinyl"), ("cd", "CD"))),
    ("Video", (("vhs", "VHS Tape"), ("dvd", "DVD"))),
    ("unknown", "Unknown"),
)


class ReportSelectForm(forms.Form):
    """
    month = forms.DateField(
        help_text='choose your month',
        label='Bitte wählen:',
        required=True,
        widget=MonthYearWidget()
    )
    """
    # forms.fields['month_month'].widget = forms.HiddenInput()
    # forms.fields['month_year'].widget = forms.HiddenInput()
    month_month = forms.CharField(widget=forms.HiddenInput(), initial='')
    month_year = forms.CharField(widget=forms.HiddenInput(), initial='')


class ReportSelectAbrechnenForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ReportSelectAbrechnenForm, self).__init__(*args, **kwargs)
        # self.fields['mitarbeiter'] = forms.MultipleChoiceField(
        #     label='',
        #     choices=[(o.id, str(o)) for o in Mitarbeiter.objects.all()]
        # )
        self.fields['kalender'] = forms.ChoiceField(
            label='',
            #choices=[(o.id, str(o)) for o in Kunde.objects.all()]
            choices=KALENDER_VIEWS
        )
        # self.fields['spesentype'] = forms.MultipleChoiceField(
        #     label='',
        #     choices=SPESEN_TYP
        # )
        #self.fields['spesentype'].required = False
        # self.fields['reporttype'] = forms.ChoiceField(
        #     label='',
        #     #choices=[('arbeitsrapport', 'Arbeitsrapport'), ('invoiceintern', 'Rechnung Intern'), ('invoiceextern', 'Rechnung Extern'), ('spesenreport', 'Spesen Report')]
        #     choices=[('invoiceintern', 'Rechnung Intern'),
        #              ('invoiceextern', 'Rechnung Kunde')]
        #
        # )

    month = forms.DateField(
        help_text='choose your month',
        label='',
        widget=MonthYearWidget()
    )

    # reporttype = forms.ChoiceField(
    #     widget=forms.Select()
    # )

    # mitarbeiter = forms.MultipleChoiceField(
    #     widget=forms.SelectMultiple()
    # )

    # spesentype = forms.MultipleChoiceField(
    #     widget=forms.SelectMultiple()
    # )

    kalender = forms.ChoiceField(
        widget=forms.Select()
    )

    # pdf = forms.BooleanField(
    #     required=False
    # )

    # pdf = forms.CharField(  # A hidden input for internal use
    #     widget=forms.HiddenInput()
    # )


class PlanningForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PlanningForm, self).__init__(*args, **kwargs)
        self.fields['mitarbeiter'] = forms.MultipleChoiceField(
            choices=[(o.id, str(o)) for o in Mitarbeiter.objects.all()]
        )
        self.fields['teams'] = forms.MultipleChoiceField(
            choices=[(o.id, str(o)) for o in Team.objects.all()]
        )

    von = forms.DateField(
        help_text='start date planning?',
        required=True,
        widget=DatePickerInput(format='%d.%m.%Y')
    )
    bis = forms.DateField(
        help_text='end date planning?',
        required=True,
        widget=DatePickerInput(format='%d.%m.%Y')
    )
    kamera = forms.BooleanField(
        required=False,
        label='Kamera?',
    )
    kamera_auf_anfrage = forms.BooleanField(
        required=False,
        label='Kamera auf Anfrage?',
    )
    ton = forms.BooleanField(
        required=False,
        label='Ton?',
    )
    ton_auf_anfrage = forms.BooleanField(
        required=False,
        label='Ton auf Anfrage?',
    )
    cut = forms.BooleanField(
        required=False,
        label='Cut?',
    )
    cut_auf_anfrage = forms.BooleanField(
        required=False,
        label='Cut auf Anfrage?',
    )
    teams = forms.MultipleChoiceField(
        widget=forms.Select(),
        required=True,
        label='Team',
    )
    mitarbeiter = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(),
        required=True,
        label='Mitarbeiter',
    )


class UnplanningForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(UnplanningForm, self).__init__(*args, **kwargs)
        self.fields['mitarbeiter'] = forms.MultipleChoiceField(
            choices=[(o.id, str(o)) for o in Mitarbeiter.objects.all()]
        )

    von = forms.DateField(
        help_text='start date planning?',
        required=True,
        widget=DatePickerInput(format='%d.%m.%Y')
    )
    bis = forms.DateField(
        help_text='end date planning?',
        required=True,
        widget=DatePickerInput(format='%d.%m.%Y')
    )
    mitarbeiter = forms.MultipleChoiceField(
        widget=forms.Select(),
        required=True,
        label='Mitarbeiter',
    )


class AbwesenheitFromToForm(forms.Form):
    von = forms.DateField(
        help_text='start date planning?',
        required=True,
        widget=DatePickerInput(format='%d.%m.%Y')
    )
    bis = forms.DateField(
        help_text='end date planning?',
        required=True,
        widget=DatePickerInput(format='%d.%m.%Y')
    )


class LockUntilForm(forms.Form):
    sperren = forms.DateField(
        help_text='Sperre Eintragungen bis',
        required=True,
        widget=DatePickerInput(format='%d.%m.%Y')
    )


# class ContactForm(TestForm):
#     pass


# class CheckOutForm(forms.ModelForm):
#     class Meta:
#         model = Transport
#         exclude = ['status', 'trip', 'sender', 'x', 'y', 'z', 'weight', 'from_airport', 'to_airport', 'description',
#                    'offer', 'street_from', 'city_from', 'country_from', 'street_to', 'city_to', 'country_to',
#                    'zip_from', 'zip_to', 'width', 'length', 'height']


class InvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        exclude = ['email_template', 'created', 'key', 'sent', 'inviter', 'accepted']


class PersonalAccountForm(forms.ModelForm):
    class Meta:
        model = Mitarbeiter
        fields = ['owner', 'mobile', 'mwstnr']
