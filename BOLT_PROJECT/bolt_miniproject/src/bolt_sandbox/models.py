# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from autoslug import AutoSlugField
from django.core.urlresolvers import reverse

from django.db import models

# Create your models here.

class Section(models.Model):

    title = models.CharField(max_length=30, unique=True, null=True)
    slug = models.CharField(max_length=30, unique=True, null=True)

    def get_task(self):
        return Task.objects.filter(tags__in=[self])

    def get_absolute_url(self):
        return reverse('section', args=[str(self.slug)])

    def __str__(self):
        return self.title
    
class Task(models.Model): 
    title = models.TextField()
    section = models.ForeignKey(Section)
    function_name = models.CharField(max_length=100, null=True)

    class Meta:
        verbose_name = 'Task'

    def get_absolute_url(self):
        return reverse('task', args=[str(self.id)])

    def __str__(self):
        return self.title