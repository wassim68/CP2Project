from django.contrib import admin
from . import models
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

admin.site.register(models.User)

class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'education', 'gendre', 'category', 'rating', 'cv', 'description', 'get_skills', 'get_saved_posts')

    def get_skills(self, obj):
        return ", ".join([skill.name for skill in obj.skills.all()])
    get_skills.short_description = 'Skills'

    def get_saved_posts(self, obj):
        return ", ".join([post.title for post in obj.savedposts.all()])
    get_saved_posts.short_description = 'Saved Posts'

admin.site.register(models.Student,StudentAdmin)
