from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.User)
admin.site.register(models.company)
admin.site.register(models.Skills)
admin.site.register(models.Notfications)
admin.site.register(models.MCF)

class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'education', 'gendre', 'category', 'rating', 'cv', 'description', 'get_skills', 'get_saved_posts')

    def get_skills(self, obj):
        return ", ".join([skill.name for skill in obj.skills.all()])
    get_skills.short_description = 'Skills'

    def get_saved_posts(self, obj):
        return ", ".join([post.title for post in obj.savedposts.all()])
    get_saved_posts.short_description = 'Saved Posts'

admin.site.register(models.Student,StudentAdmin)
