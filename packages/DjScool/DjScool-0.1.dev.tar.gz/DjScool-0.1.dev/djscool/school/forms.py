from django import forms
from django.forms.models import modelform_factory
from django.forms.util import ErrorList
from django.contrib.auth.models import User

from djscool.school import models


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        exclude = ['user']

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None):
        super(ProfileForm, self).__init__(data, files, auto_id, prefix,
                                          initial, error_class, label_suffix,
                                          empty_permitted, instance)

        if instance and self.get_user():
            self.initial['first_name'] = self.user.first_name
            self.initial['last_name'] = self.user.last_name

    def get_user(self):
        try:
            return self.instance.user
        except User.DoesNotExist:
            return None

    def save_user(self):
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        username =  '%(last_name)s_%(first_name)s' %  self.cleaned_data
        username = username.replace(' ', '').lower()
        user = User(first_name=first_name, last_name=last_name,
                    username=username, is_active=False)
        user.save(force_insert=True)
        self.instance.user = user

    def save(self, commit=True):
        self.save_user()
        return super(ProfileForm, self).save(commit)

    @classmethod
    def factory(clss, model):
        return modelform_factory(model, form=clss)


class StudentForm(ProfileForm):
    role = forms.IntegerField(
               widget=forms.Select(choices=models.STUDENT_CHOICES))
    class Meta:
        model = models.Student

class TeacherForm(ProfileForm):
    role = forms.IntegerField(
               widget=forms.Select(choices=models.TEACHER_CHOICES))
    class Meta:
        model = models.Teacher

__all__ = ['ProfileForm', 'StudentForm', 'TeacherForm']
