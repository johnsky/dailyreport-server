# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User


class HistoryModel(models.Model):
    """
    
    """
    created = models.DateTimeField(u'Дата создания', auto_now_add = True)
    creator = models.ForeignKey(User,
                        verbose_name=u'Кто создал',
                        blank=True, null=True,
                        related_name = "+",)
    
    edited = models.DateTimeField(u'Дата редактирования', auto_now = True)
    editor = models.ForeignKey(User,
                        verbose_name=u'Кто редактировал',
                        blank=True, null=True,
                        related_name = "+")
    
    class Meta:
        abstract = True   

    #def save(self, *args, **kwargs):
    #    super(HistoryModel, self).save( *args, **kwargs)