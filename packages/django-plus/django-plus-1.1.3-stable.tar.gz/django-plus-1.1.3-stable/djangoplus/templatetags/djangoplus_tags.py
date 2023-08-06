import base64, types, urllib
from datetime import datetime, timedelta

from django import template
from django.template import Library, Node
from django.utils.translation import ugettext as _
from django.utils.safestring import SafeUnicode, mark_safe
from django.conf import settings
from django.template.defaultfilters import slugify
from django.core.cache import cache

from djangoplus.utils import path_to_object
from djangoplus import app_settings

register = Library()

"""
Boolean general utilities
"""

@register.filter
def multiple_of(value,arg):
    return value % arg == 0

@register.filter
def in_list(value,arg):
    if not value:
        return False

    if type(arg) in (types.StringType, SafeUnicode):
        arg = arg.split(',')
    
    return value in arg

@register.filter
def is_equal(value,arg):
    return value == arg

@register.filter
def as_string(value):
    # Returns unicode convertion of value
    return unicode(value)

@register.filter
def is_not_equal(value,arg):
    # O inverso do is_equal
    return value != arg

@register.filter
def is_lt(value,arg):
    return int(value) < int(arg)

@register.filter
def is_lte(value,arg):
    return int(value) <= int(arg)

@register.filter
def is_gt(value,arg):
    return int(value) > int(arg)

@register.filter
def is_gte(value,arg):
    return int(value) >= int(arg)

@register.filter
def replace(value,arg):
    arg, arg2 = arg.split(':')
    return value.replace(arg, arg2)

"""
Date/time util template filters
"""

@register.filter
def is_day_of(value,arg):
    return (arg and value) and arg.day == int(value)

@register.filter
def is_month_of(value,arg):
    return (arg and value) and arg.month == int(value)

@register.filter
def is_year_of(value,arg):
    return (arg and value) and arg.year == int(value)

@register.filter
def is_hour_of(value,arg):
    return (arg and value) and arg.hour == int(value)

@register.filter
def is_minute_of(value,arg):
    return (arg and value) and arg.minute == int(value)

@register.filter
def dec_year(value,arg):
    delta = type(arg) != types.IntType and int(arg) or arg
    return value - timedelta(365 * delta)

@register.filter
def dec_month(value,arg):
    delta = type(arg) != types.IntType and int(arg) or arg
    return value - timedelta(30 * delta)

@register.filter
def inc_year(value,arg):
    delta = type(arg) != types.IntType and int(arg) or arg
    return value + timedelta(365 * delta)

@register.filter
def inc_month(value,arg):
    delta = type(arg) != types.IntType and int(arg) or arg
    return value + timedelta(30 * delta)

@register.filter
def list_as_text(value, field=None):
    if field:
        def get_value(obj, attr):
            attr = getattr(obj, attr)

            if type(attr) == types.MethodType:
                return attr()

            return attr or ''

        return ', '.join([get_value(i, field) for i in value])
    else:
        return ', '.join([unicode(i) for i in value])

@register.filter
def list_as_links(value):
    return ', '.join(['<a href="%s">%s</a>'%(i.get_absolute_url(), unicode(i)) for i in value])

"""
reStructuredText
"""

@register.filter
def rest(value, arg):
    from docutils.core import publish_parts

    arg = arg or 'html'
    parts = publish_parts(value, writer_name=arg)
    return parts['html_body']

"""
Strings
"""

@register.filter
def startswith(value,arg):
    return value.startswith(arg)

@register.filter
def endswith(value,arg):
    return value.endswith(arg)

"""
Miscelanea
"""

def multifind(s, q):
    # Retorna uma lista de posicoes de uma string em outra - utilizado pelo highlight
    ret = []
    sl = s.lower()
    q = q.lower()
    i = 0

    while i < len(sl):
        aux = sl[i:]
        if aux.find(q) == 0:
            ret.append(i)
            i += len(q)
        else:
            i += 1

    return ret

@register.filter
def highlight(s, q):
    # Destaca uma string dentro de outra em case insensitive, respeitando valor original
    pos = multifind(s, q)

    if not pos: return s

    anterior = 0
    ret = ''
    
    for p in pos:
        if anterior:
            ret += s[anterior+len(q):p]
        else:
            ret += s[anterior:p]

        ret += '<span class="highlight">' + s[p:p+len(q)] + '</span>'
        anterior = p

    ret += s[p+len(q):]

    return ret

@register.filter_function
def attr(obj, arg1):
    """Sets an HTML attribute to a form widget"""
    att, value = arg1.split("=")
    obj.field.widget.attrs[att] = value
    return obj

@register.filter_function
def order_by(queryset, args):
    """Returns a queryset filtered ordered by the field informed"""
    args = [x.strip() for x in args.split(',')]
    return queryset.order_by(*args)

@register.filter_function
def make_cloud(object_list, count_attribute, steps=5):
    """Make a cloud on the given list, using counter attribute informed"""
    def get_count(obj):
        if not hasattr(obj, '__cloud_counter'):
            cur = obj
            for attr in count_attribute.split('.'):
                cur = getattr(cur, attr)

            if type(cur) == types.MethodType:
                setattr(obj, '__cloud_counter', cur())
            else:
                setattr(obj, '__cloud_counter', cur)

        return obj.__cloud_counter

    def get_font_size(obj, steps_counts):
        for i, step in enumerate(steps_counts):
            if get_count(obj) < step:
                return i

        return steps

    def steps_between_to_numbers(first, second):
        div = float(second - first) / (steps-1)
        return [first+int(round(div * i)) for i in range(steps)]

    min_count = min([get_count(obj) for obj in object_list])
    max_count = max([get_count(obj) for obj in object_list])
    steps_counts = steps_between_to_numbers(min_count, max_count)

    return [(obj, get_font_size(obj, steps_counts)) for obj in object_list]

@register.filter_function
def moneyformat(value, decimal_places=2):
    """Returns a float value in monetary format, using MONETARY_LOCALE
    setting and locale functions"""
    import locale

    if app_settings.MONETARY_LOCALE:
        locale.setlocale(locale.LC_NUMERIC, app_settings.MONETARY_LOCALE)

    format = r"%0.0"+str(decimal_places)+'f'

    value = value or 0.0

    return locale.format(format, float(value), grouping=True)

@register.filter_function
def has_module_perm(user, app_label):
    """Checks if that user has some permission on that application and returns
    True or False for this."""
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return user.has_module_perms(app_label)

"""
TAMPLATE TAGS
"""

class ProtectAntiRobotsNode(Node):
    phrase = ''
    nodelist = ''

    def __init__(self, nodelist, phrase=None):
        super(ProtectAntiRobotsNode, self).__init__()

        self.nodelist = nodelist
        self.phrase = phrase or _('Let us know if you are human')

    def __repr__(self):
        return "<ProtectAntiRobotsNode>"

    def render(self, context):
        request = context['request']
        path = slugify(request.get_full_path())
        if 'protectantirobots_sec_'+path in request.COOKIES and \
           'protectantirobots_key_'+path in request.COOKIES:
            if request.COOKIES['protectantirobots_sec_'+path] == base64.b64decode(request.COOKIES['protectantirobots_key_'+path]):
                output = self.nodelist.render(context)
                return output
        
        sec = base64.b64encode(datetime.now().strftime("%H%m%S"))
        return '<a href="%s">%s</a>' %(self.get_url(sec, path), self.phrase)

    def get_url(self, sec, path):
        return "/protectantirobots/?k=%s&path=%s"%(sec, path)

def do_protectantirobots(parser, token):
    nodelist = parser.parse(('endprotectantirobots',))
    parser.delete_first_token()

    parts = token.split_contents()
    phrase = len(parts) > 1 and parts[1][1:-1] or None

    return ProtectAntiRobotsNode(nodelist, phrase)
do_protectantirobots= register.tag('protectantirobots', do_protectantirobots)

"""
{% dynamic_template [group] "name" %}
"""

from djangoplus.models import DynamicTemplate

class DynamicTemplateRender(template.Node):
    slug = None
    is_group = False

    def __init__(self, slug, is_group=False):
        self.slug = slug
        self.is_group = is_group

    def render(self, context):
        ret = ''

        if self.is_group:
            templates = DynamicTemplate.objects.filter(group=self.slug)
        else:
            templates = DynamicTemplate.objects.filter(slug=self.slug)

        for tpl in templates:
            ret += tpl.render(context)

        return ret

def do_dynamic_template(parser, token):
    try:
        parts = token.split_contents()
        tag_name = parts[0]
        slug = parts[-1]

        if len(parts) > 3:
            raise ValueError('Many arguments')
        elif len(parts) > 2 and parts[1] == 'group':
            is_group = True
        else:
            is_group = False
    except ValueError, e:
        raise template.TemplateSyntaxError, "%s requires 1 or 2 arguments" \
                % token.contents.split()[0]

    return DynamicTemplateRender(slugify(slug), is_group)

register.tag('dynamic_template', do_dynamic_template)

class RaiseRender(template.Node):
    vobj = None
    vadditional = None

    def __init__(self, vobj, vadditional=None):
        self.vobj = template.Variable(vobj)
        self.vadditional = vadditional

    def render(self, context):
        obj = self.vobj.resolve(context)

        if self.vadditional:
            obj = getattr(obj, self.vadditional)

        raise Exception(obj.__dict__)

def do_raise(parser, token):
    try:
        parts = token.split_contents()
        tag_name = parts[0]
        vobj = parts[1]
        vadditional = len(parts) == 3 and parts[2] or None
    except ValueError, e:
        raise template.TemplateSyntaxError, "%s requires 1 or 2 arguments" \
                % token.contents.split()[0]

    return RaiseRender(vobj, vadditional)

register.tag('raise', do_raise)

class ChangeGetParamsNode(template.Node):
    param = None
    new_value = None

    def __init__(self, param, new_value):
        self.param = template.Variable(param)
        self.new_value = template.Variable(new_value)

    def render(self, context):
        from urllib import urlencode
        # Resolve variables
        param = self.param.resolve(context)
        new_value = self.new_value.resolve(context)

        # Change current params
        cur_params = dict([(k,v) for k,v in context['request'].GET.items()])
        cur_params[param] = new_value

        return urlencode(cur_params)

def do_change_get_params(parser, token):
    try:
        parts = token.split_contents()
        param = parts[1]
        new_value = parts[2]
    except ValueError:
        raise template.TemplateSyntaxError, "%s requires 2 arguments"\
                % token.split_contents()[0]

    return ChangeGetParamsNode(param, new_value)

register.tag('change_get_params', do_change_get_params)

class RemoveFromGetParamsNode(template.Node):
    param = None

    def __init__(self, param):
        self.param = template.Variable(param)

    def render(self, context):
        from urllib import urlencode
        # Resolve variables
        param = self.param.resolve(context)

        # Change current params
        cur_params = dict([(k,v) for k,v in context['request'].GET.items() if k != param])

        return urlencode(cur_params)

def do_remove_from_get_params(parser, token):
    try:
        parts = token.split_contents()
        param = parts[1]
    except ValueError:
        raise template.TemplateSyntaxError, "%s requires 1 argument"\
                % token.split_contents()[0]

    return RemoveFromGetParamsNode(param)

register.tag('remove_from_get_params', do_remove_from_get_params)

# Model info

#@register.simple_tag
#def model_info_for_object(class_path, object):
#    cls = path_to_object(class_path)
#    return cls(object)

class ModelInfoForObjectNode(template.Node):
    class_path = None
    obj = None
    as_part = None
    as_varname = None

    def __init__(self, class_path, obj, as_part=None, as_varname=None):
        self.class_path = template.Variable(class_path)
        self.obj = template.Variable(obj)
        self.as_part = as_part
        self.as_varname = as_varname

    def render(self, context):
        class_path = self.class_path.resolve(context)
        obj = self.obj.resolve(context)

        cls = path_to_object(class_path)
        model_info = cls(obj, request=context.get('request', None))

        if not self.as_part:
            return model_info

        context[self.as_varname] = model_info
        return ''

def do_model_info_for_object(parser, token):
    try:
        parts = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "You must inform class path and object"

    return ModelInfoForObjectNode(*parts[1:])

register.tag('model_info_for_object', do_model_info_for_object)


#@register.simple_tag
#def model_info_for_list(class_path, list):
#    cls = path_to_object(class_path)
#    return cls(list)

class ModelInfoForListNode(template.Node):
    class_path = None
    list_obj = None
    as_part = None
    as_varname = None

    def __init__(self, class_path, list_obj, as_part=None, as_varname=None):
        self.class_path = template.Variable(class_path)
        self.list_obj = template.Variable(list_obj)
        self.as_part = as_part
        self.as_varname = as_varname

    def render(self, context):
        class_path = self.class_path.resolve(context)
        list_obj = self.list_obj.resolve(context)

        cls = path_to_object(class_path)
        model_list = cls(list_obj, request=context.get('request', None))

        if not self.as_part:
            return model_list

        context[self.as_varname] = model_list
        return ''

def do_model_info_for_list(parser, token):
    try:
        parts = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "You must inform class path and list object"

    return ModelInfoForListNode(*parts[1:])

register.tag('model_info_for_list', do_model_info_for_list)

class IncludeFromURLRender(template.Node):
    vurl = None
    vcache = None

    def __init__(self, vurl, vcache=None):
        self.vurl = template.Variable(vurl)
        self.vcache = vcache

    def render(self, context):
        url = self.vurl.resolve(context)
        url_key = 'includefromurl_'+slugify(url)

        # Load from cache?
        if self.vcache:
            cont = cache.get(url_key, '')
        else:
            cont = ''

        # If there is no content from cache, get from URL
        if not cont:
            fp = urllib.urlopen(url)
            cont = fp.read()
            fp.close()

        # Save on cache
        if self.vcache:
            cache.set(url_key, cont, int(self.vcache))

        return mark_safe(cont)

def do_includefromurl(parser, token):
    try:
        parts = token.split_contents()
        vurl = parts[1]
        vcache = len(parts) == 3 and parts[2] or None
    except ValueError, e:
        raise template.TemplateSyntaxError, "%s requires 1 or 2 arguments" \
                % token.contents.split()[0]

    return IncludeFromURLRender(vurl, vcache)

register.tag('includefromurl', do_includefromurl)

