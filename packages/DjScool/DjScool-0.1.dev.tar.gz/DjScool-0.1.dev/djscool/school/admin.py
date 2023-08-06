from django.contrib import admin
from djscool.school import forms, models

for model in (models.Subject, models.Classroom):
    admin.site.register(model)

class ProfileAdmin(admin.ModelAdmin):
    PROFILE_FIELDS = (
        ('Personal Informations', {'classes': ['collapse'], 'fields':
            ['phone', 'address', 'tax_code', 'web_site', 'birth_date']}),
    )

    def first_name(self, profile):
        return profile.user.first_name

    def last_name(self, profile):
        return profile.user.last_name

class StudentAdmin(ProfileAdmin):
    form = forms.StudentForm
    list_display = ('last_name', 'first_name', 'classroom')
    fieldsets = (
        (None, {'fields': ['first_name', 'last_name', 'role', 'classroom']}),
    ) + ProfileAdmin.PROFILE_FIELDS

class TeacherAdmin(ProfileAdmin):
    form = forms.TeacherForm
    list_display = ('last_name', 'first_name')
    fieldsets = (
        (None, {'fields': ['first_name', 'last_name', 'role']}),
        ('Other Informations', {'fields':
            ['coordinate', 'free_day', 'subjects']}),
    ) + ProfileAdmin.PROFILE_FIELDS


admin.site.register(models.Student, StudentAdmin)
admin.site.register(models.Teacher, TeacherAdmin)
