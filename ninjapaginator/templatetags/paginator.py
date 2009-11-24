# -*- coding: utf-8 -*-

from django.template import Library

register = Library()


@register.simple_tag
def page_link(num_page, params):
    link = '?page=%s' % num_page
    if params:
        return '%s&amp;%s' % (link, params.replace('&', '&amp;'))
    return link