# -*- coding: utf-8 -*-

from django.template import Library

register = Library()


@register.simple_tag
def page_link(num_page, params, anchor):
    link = '?page=%s' % num_page
    if params:
        link = '%s&amp;%s' % (link, params.replace('&', '&amp;'))
    if anchor:
        link += '#%s' % anchor
    return link


@register.inclusion_tag('paginator.html')
def paginate(obj):
    return obj