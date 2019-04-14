# import pytz
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
# import select2.fields
# from django.db.models import Q
from django.urls import reverse
# from django_extensions.db.models import TimeStampedModel
# import datetime

from empty import settings


class Information(models.Model):
    title = models.CharField(max_length=96, null=True, blank=True)
    text = models.CharField(max_length=4000, null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)

    def get_absolute_url(self):
        # return '/'
        # return reverse('/', kwargs={'pk': self.pk})
        return reverse('edit_information', kwargs={'pk': self.pk})

    def __str__(self):
        return "{}{}{}".format(self.title, ' mit Status ', self.status)


class Organization(models.Model):
    name = models.CharField(max_length=96)

    def __str__(self):
        return "{}".format(self.name)


class emptySetting(models.Model):
    """
    haelt Konfigurationen fuer die Anwendung.
    """
    key = models.CharField(max_length=255, null=True, blank=True)
    value = models.CharField(max_length=255, null=True, blank=True)
    datum = models.DateField(null=True, blank=True)

    def __str__(self):
        return "{} {}".format(self.value, self.datum)


#
# Django Signal, erstellt automatisch ein Mitarbeiter Objekt in der Datenbank wenn ein Django User erstellt wird.
#
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def build_profile_on_user_creation(sender, instance, created, **kwargs):
    if created:
        # profile = Mitarbeiter(owner=instance)
        # profile.is_dispo = False
        # profile.save()
        pass
