from django.contrib import admin
from reversion.admin import VersionAdmin
from demo.models import emptySetting




@admin.register(emptySetting)
class ClientModelAdmin(VersionAdmin):
    pass
