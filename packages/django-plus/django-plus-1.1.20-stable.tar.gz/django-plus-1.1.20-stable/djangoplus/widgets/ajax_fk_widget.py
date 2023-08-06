# -*- coding: utf-8 -*-
import operator

from django.forms.widgets import TextInput
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.db import models
from django.http import HttpResponse
from django.contrib import admin
from django.shortcuts import render_to_response
from django.template import RequestContext

from djangoplus.utils import path_to_object

registered_models = {}

class AjaxFKWidget(TextInput):
    class Media:
        js = (settings.MEDIA_URL+'js/ajax_fk_widget.js',)
        css = {'all': (settings.MEDIA_URL+'css/ajax_fk_widget.css',)}

    fill_left_zeros = 0
    rel = None
    model = None
    related_field = None
    filter_dict = {}

    window_url = None
    load_url = None
    add_url = None

    def __init__(self, *args, **kwargs):
        if 'rel' in kwargs:
            self.rel = kwargs.pop('rel')
            self.get_from_rel()
        else:
            self.model = kwargs.pop('model', None)
            self.related_field = kwargs.pop('related_field', 'pk')

        if 'fill_left_zeros' in kwargs:
            self.fill_left_zeros = kwargs.pop('fill_left_zeros')

        self.window_url = kwargs.pop('window_url', self.window_url)
        if self.window_url is None:
            self.window_url = reverse('ajax-fk-window-url', kwargs={
                'app': self.model.__module__.split('.')[0],
                'model': self.model.__name__,
                })

        self.load_url = kwargs.pop('load_url', self.load_url)
        if self.load_url is None:
            self.load_url = reverse('ajax-fk-load-url', kwargs={
                'app': self.model.__module__.split('.')[0],
                'model': self.model.__name__,
                })

        self.add_url = kwargs.pop('add_url', self.add_url)
        if self.add_url is None:
            self.add_url = '%s%s/%s/add/'%(
                    admin.site.root_path,
                    self.model.__module__.split('.')[0],
                    self.model.__name__.lower(),
                    )

        super(AjaxFKWidget, self).__init__(*args, **kwargs)

    def get_from_rel(self):
        self.model = self.rel.to
        self.related_field = self.rel.get_related_field().name

    def render(self, name, value, attrs=None):
        attrs = attrs or {}
        attrs['class'] = attrs.get('class', '') + ' ajax-fk'

        ret = super(AjaxFKWidget, self).render(name, value, attrs)
        class_path = '.'.join([self.model.__module__, self.model.__name__])

        display = self.make_display(attrs, value)

        script = self.make_script(name)

        return mark_safe(' '.join([ret, display, script]))

    def make_display(self, attrs, value):
        return '<span id="%s_display" class="ajax-fk-display">%s</span>'%(
                attrs['id'],
                value and self.label_for_value(value) or '(nenhum selecionado)',
                )

    def make_script(self, name):
        sc_params = {
                "model": '.'.join([self.model.__module__,self.model.__name__]),
                "filter": self.filter_dict or {},
                "window-url": self.window_url,
                "load-url": self.load_url,
                "add-url": self.add_url,
                "fill-left-zeros": self.fill_left_zeros,
                }
        script = """<script type="text/javascript">fk_widgets['%s'] = %s;%s</script>"""%(
                name,
                simplejson.dumps(sc_params),
                self.get_additional_script(name)
                )
        return script

    def get_additional_script(self, name):
        """To be used to extend script functions"""
        return ''

    def label_for_value(self, value):
        obj = self.model._default_manager.get(**{self.related_field: value})
        return unicode(obj)

    @classmethod
    def register(cls, driver_class):
        """Register a model class with its driver class
        Example: AjaxFKWidget.register(MyModelClass, AjaxFKMyModelClass)"""
        global registered_models

        registered_models[driver_class.model] = driver_class

class AjaxFKDriver(object):
    model = None
    list_display = None
    search_fields = None
    list_filter = None
    ordering = None

    def __init__(self, request, cls=None):
        self.request = request
        self.cls = cls

    def get_columns(self):
        return [self.model._meta.get_field_by_name(f)[0].verbose_name.capitalize() for f in self.list_display]

    def get_results(self):
        qs = self.get_query_set()

        # Keyword search
        qs = self.search_by_fields(qs)

        # Filters
        for k,v in self.request.GET.items():
            if not k.startswith('ajax-fk-filter-'):
                continue

            f_name = k[15:]

            qs = qs.filter(**{str(f_name): v})

        return qs

    def search_by_fields(self, qs):
        # Apply keyword searches.
        def construct_search(field_name):
            if field_name.startswith('^'):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith('='):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith('@'):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name

        if self.search_fields and self.request.GET.get('ajax_fk_search', ''):
            for bit in self.request.GET['ajax_fk_search'].split():
                or_queries = [models.Q(**{construct_search(str(field_name)): bit}) for field_name in self.search_fields]
                qs = qs.filter(reduce(operator.or_, or_queries))
            for field_name in self.search_fields:
                if '__' in field_name:
                    qs = qs.distinct()
                    break

        return qs

    def get_by_pk(self):
        try:
            obj = self.model.objects.get(pk=self.request.GET['pk'])

            ret = {
                'res': settings.RESULT_OK,
                'pk': obj.pk,
                'display': unicode(obj),
            }
        except self.model.DoesNotExist:
            ret = {
                'res': settings.RESULT_ERROR,
                'msg': u'%s não encontrado!'%self.model._meta.verbose_name,
            }

        return ret

    def get_query_set(self):
        qs = self.model.objects.all()

        # Ordering
        if self.ordering:
            qs = qs.order_by(*self.ordering)

        return qs

def window_view(request, app, model):
    cls = path_to_object('%s.models.%s'%(app, model))
    driver = registered_models[cls](request, cls)

    columns = driver.get_columns()
    results = driver.get_results()
    list_display = driver.list_display

    return render_to_response(
            'ajax_fk/window.html',
            locals(),
            context_instance=RequestContext(request),
            )

def load_view(request, app, model):
    cls = path_to_object('%s.models.%s'%(app, model))
    driver = registered_models[cls](request, cls)

    ret = driver.get_by_pk()

    return HttpResponse(simplejson.dumps(ret), mimetype='text/javascript')

