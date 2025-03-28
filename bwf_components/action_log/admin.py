from django.contrib import admin

# Register your models here.

from .models import ActionLog

admin.site.register(ActionLog)