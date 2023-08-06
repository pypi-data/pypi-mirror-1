from django.db import models
from django import template
from django.template.defaultfilters import slugify

import app_settings

class DynamicTemplate(models.Model):
    class Meta:
        ordering = ('title',)

    title = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, unique=True)
    group = models.SlugField(blank=True)
    content = models.TextField()

    def __unicode__(self):
        return self.title

    def render(self, context):
        return template.Template(self.content).render(template.Context(context))

class StaticFile(models.Model):
    file = models.FileField(upload_to=app_settings.STATIC_FILES_PATH)

    def __unicode__(self):
        return self.file.name

# SIGNALS AND LISTENERS
from django.db.models import signals

# DynamicTemplate
def dynamictemplate_pre_save(sender, instance, signal, *args, **kwargs):
    # Cria slug
    if not instance.slug:
        instance.slug = slugify(instance.title)

    if not instance.group:
        instance.group = slugify(instance.group)

signals.pre_save.connect(dynamictemplate_pre_save, sender=DynamicTemplate)

