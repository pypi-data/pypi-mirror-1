from django.contrib import admin
from models import *

class MemberImageInline(admin.TabularInline):
    model = MemberImage
    max_num = 1

class MemberAdmin(admin.ModelAdmin):
    model = Member
    inlines = [
        MemberImageInline,
    ]
    list_display = ('first_name', 'last_name', 'position', 'email', 'is_public',)
    search_fields = ('first_name', 'last_name',)
    list_filter = ('position', 'is_public')
    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'position', 'email', 'description',)
        }),
        ('Advanced options', {
            'fields': ('user', 'order', 'is_public',)
        }),
    )

class TeamAdmin(admin.ModelAdmin):
    model = Team
    list_display = ('name',)
    search_fields = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'description',)
        }),
        ('Advanced options', {
            'fields': ('members', 'order',)
        }),
    )

admin.site.register(Member, MemberAdmin)
admin.site.register(Team, TeamAdmin)