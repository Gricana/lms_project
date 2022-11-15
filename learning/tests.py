from django.test import TestCase


class LearningTestCase(TestCase):

    pass


cls.student_group = Group.objects.create(name='Ученик')
cls.student_perms = Permission.objects.filter(content_type__app_label='learning',
                                              codename__in=['view', 'add_tracking'])
cls.student_group.permissions.set(cls.student_perms)

# Создания нового пользователя с правами группы "Автор"

cls.author_group = Group.objects.create(name='Автор')
cls.author_perms = Permission.objects.filter(content_type__app_label='learning',
                                             codename__in=['view', 'add', 'change', 'delete'])
cls.author_group.permissions.set(cls.author_perms)