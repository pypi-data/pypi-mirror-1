"""
This application contains only the basic school models.

"""
from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _


DAYS = (
    (0, _('Sunday')),
    (1, _('Monday')),
    (2, _('Tuesday')),
    (3, _('Wednesday')),
    (4, _('Thursday')),
    (5, _('Friday')),
    (6, _('Saturday'))
)

STUDENT = 0
CLASS_REP = 1
INSTITUTE_REP = 2
TEACHER = 3
VICE_PRINCIPAL = 4
PRINCIPAL = 5
CARETAKER = 6

STUDENT_CHOICES = (
    (STUDENT, _('Student')),
    (CLASS_REP, _('Class Rep')),
    (INSTITUTE_REP, _('Institute Rep')),
)
TEACHER_CHOICES = (
    (TEACHER, _('Teacher')),
    (VICE_PRINCIPAL, _('Vice Principal')),
)

ROLES = STUDENT_CHOICES + TEACHER_CHOICES + (
    (PRINCIPAL, _('Principal')),
    (CARETAKER, _('Caretaker')),
)

class UserProfile(models.Model):
    """
    An UserProfile is a model that keeps additional informations about an User.
    """

    user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
    phone = models.CharField(_('phone number'), max_length=20, blank=True, null=True)
    address = models.CharField(_('address'), max_length=20, blank=True, null=True)
    tax_code = models.CharField(_('tax code'), max_length=20, blank=True, null=True)
    web_site = models.URLField(_('web site'), blank=True, null=True)
    birth_date = models.DateField(_('birth date'), blank=True, null=True)
    role = models.IntegerField(_('role'), max_length=1, choices=ROLES)

    def is_student(self):
        if self.role in (STUDENT, CLASS_REP, INSTITUTE_REP):
            return True
        return False

    def is_teacher(self):
        if self.role in (TEACHER, VICE_PRINCIPAL):
            return True
        return False

    def __unicode__(self):
        return _('%(last_name)s %(first_name)s') % dict(vars(self),
                                                        **vars(self.user))


class Subject(models.Model):

    subject = models.CharField(_('subject'), max_length=50)

    class Meta:
        verbose_name = _('subject')
        verbose_name_plural = _('subjects')

    def __unicode__(self):
        return self.subject


class Classroom(models.Model):

    section = models.CharField(_('section'), max_length=1)
    year = models.IntegerField(_('year'), max_length=1)

    class Meta:
        verbose_name = _('classroom')
        verbose_name_plural = _('classrooms')

    def __unicode__(self):
        return '%s%s' % (self.year, self.section)


class Student(UserProfile):

    classroom = models.ForeignKey(Classroom, verbose_name=_('classroom'))

    class Meta:
        verbose_name = _('student')
        verbose_name_plural = _('students')


class Teacher(UserProfile):
    coordinate = models.ForeignKey(Classroom, verbose_name=_('coordinator of'), blank=True, null=True)
    subjects = models.ManyToManyField(Subject, verbose_name=_('subjects'), blank=True, null=True)
    free_day = models.IntegerField(_('free day'), max_length=1, choices=DAYS, blank=True, null=True)

    class Meta:
        verbose_name = _('teacher')
        verbose_name_plural = _('teachers')
