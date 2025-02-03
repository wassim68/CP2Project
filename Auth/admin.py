from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.User)
admin.site.register(models.Student)
admin.site.register(models.company)
admin.site.register(models.Skills)
admin.site.register(models.Notfications)
admin.site.register(models.MCF)