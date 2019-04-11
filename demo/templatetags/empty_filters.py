import json
import time

from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def to_json(obj):
    return mark_safe(json.dumps(obj))


@register.filter
def get_timestamp():
   now = time.time()
   localtime = time.localtime(now)
   milliseconds = '%03d' % int((now - int(now)) * 1000)
   return time.strftime('%Y%m%d%H%M%S', localtime) + milliseconds


@register.filter(name='urlforheadtags')
@stringfilter
def urlforheadtags(str, kind):
    ontill = str.replace('/', 'r', 1).find('/')
    headtagurl = str[:ontill]
    if headtagurl == '/create_information':
        headtagurl = '/edit_information'
    return kind + '/per_page' + headtagurl + '.' + kind
