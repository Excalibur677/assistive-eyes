from django.contrib import admin
from .models import Medicine, ScanHistory

admin.site.register(Medicine)
admin.site.register(ScanHistory)