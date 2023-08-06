# -*- coding: utf-8 -*-
from harness.middleware import get_current_user

def record_user(field_name='user'):
    """
    A signal handler for any model. Sets currently logged in user
    to a given field of the instance.

    Requires 'harness.middleware.ThreadUserMiddleware' to be loaded.

    Usage:

    >>> from django.db import models
    >>> from django.db.models.signals import pre_save
    >>> from django.contrib.auth.models import User
    >>> from harness.signals import set_user
    >>>
    >>> class Entry(models.Model):
    ...     text   = models.TextField()
    ...     author = models.ForeignKey(User, editable=False)
    >>>
    >>> pre_save.connect(set_user('author'), sender=Entry)
    """
    def f(sender, instance, **kw):
        if not field_name in instance._meta.get_all_field_names():
            raise AttributeError, 'Cannot set current user: no such field "%s" '\
                                  'in %s' % (field_name, instance._meta.object_name)
        if not getattr(instance, '%s_id' % field_name):
            assert get_current_user(), 'get_current_user() must return User instance. '\
                                       'Check if middleware is connected'
            setattr(instance, field_name, get_current_user())
    return f
