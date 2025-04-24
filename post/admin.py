from django.contrib import admin
from . import models

@admin.register(models.Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'Type', 'category', 'status',  'created_at')
    list_filter = ('worktype', 'Type', 'category', 'status', 'created_at')
    search_fields = ('title', 'description', 'company__email')
    filter_horizontal = ('skills', 'applications')
    #autocomplete_fields = ('company',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

admin.site.register(models.Application)
admin.site.register(models.Team)
@admin.register(models.TeamInvite)
class TeamInviteAdmin(admin.ModelAdmin):
    list_display = ('createdate', 'inviter', 'receiver', 'status') 
    list_filter = ('status',)  
    search_fields = ('inviter__username', 'receiver__username') 
    ordering = ('-createdate',)  