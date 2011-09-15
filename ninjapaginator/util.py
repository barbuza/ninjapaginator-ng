# -*- coding: utf-8 -*-

from functools import partial, update_wrapper
from urllib import urlencode

from django.utils.datastructures import MultiValueDictKeyError
from django.core.paginator import Paginator, EmptyPage
from django.http import Http404
from django.conf import settings


def unicode_urlencode(params):
    """
    A unicode aware version of urllib.urlencode
    """

    if isinstance(params, dict):
        params = params.items()
    return urlencode([(k, isinstance(v, unicode) and v.encode('utf-8') or v) for k, v in params])


class NinjaPaginator(object):
    """
    Pagination decorator with multiple types of pagination
    Should be used along with 'render_to' decorator
    from django-annoying application
    http://bitbucket.org/offline/django-annoying/wiki/Home
    """

    def __init__(self, object_list='object_list', style=None, per_page=10, frame_size=8,
                 allow_user_per_page=False, fixed_user_per_page=None,
                 paginator_name=None, template=None, anchor=None):
        """
        receive decorator parameters 
        """
        self.object_list = object_list
        self.style = style or getattr(settings, "PAGINATION_STYLE", "digg")
        self.style_fn = getattr(self, '%s_style' % self.style)
        self._per_page = per_page
        self.frame_size = frame_size
        self.allow_user_per_page = allow_user_per_page
        self.paginator_name = paginator_name or '%s_paginator' % object_list
        self.template = template or 'paginator_%s.html' % self.style
        self.fixed_user_per_page = fixed_user_per_page
        self.anchor = anchor
    
    @property
    def per_page(self):
        if callable(self._per_page):
            return self._per_page()
        return self._per_page
    
    def __call__(self, function):
        """
        receive decorated function and return
        function decorated with decorate method
        """
        decorated = partial(self.decorate, function)
        return update_wrapper(decorated, self.decorate)
    
    def decorate(self, function, request, *args, **kwargs):
        """
        style pagination according to 'style' parameter
        """
        
        function_output = function(request, *args, **kwargs)
        
        if not isinstance(function_output, dict):
            return function_output
        
        output = {}
        params = request.GET.copy()
        
        page_num = 1
        try:
            page_num = int(params.pop('page')[0])
        except (ValueError, KeyError):
            pass
        
        per_page = self.per_page
        if self.allow_user_per_page and 'per_page' in params:
            try:
                user_per_page = int(params['per_page'])
                if not self.fixed_user_per_page or\
                        user_per_page not in self.fixed_user_per_page:
                    per_page = user_per_page
            except (ValueError, KeyError):
                params['per_page'] = self.per_page
        elif 'per_page' in params:
            params.pop('per_page')
        
        paginate_qs = function_output.pop(self.object_list)
        paginator = Paginator(paginate_qs, per_page)
        
        try:
            page = paginator.page(page_num)
        except EmptyPage:
            raise  Http404()
        
        output['page_num'] = page_num
        output['per_page'] = per_page
        output['params'] = unicode_urlencode(params)
        output['anchor'] = self.anchor
        pages = paginator.num_pages
        function_output[self.object_list] = page.object_list
        output['paginator_template'] = self.template
        output['allow_user_per_page'] = self.allow_user_per_page
        output.update(self.style_fn(pages, page_num))
        function_output[self.paginator_name] = output
        
        return function_output

    
    def digg_style(self, pages, page_num):
        output = {}
        if page_num > 1:
            output['PREVIOUS'] = page_num -1
        if page_num < pages:
            output['NEXT'] = page_num + 1
        if pages > self.frame_size and pages <= self.frame_size +2:
            output['left_page_numbers'] = range(1, pages + 1)
        elif pages <= self.frame_size:
            output['left_page_numbers'] = range(1, pages + 1)
        elif pages > self.frame_size and page_num < self.frame_size - 1:
            output['left_page_numbers'] = range(1, self.frame_size + 1)
            output['right_page_numbers'] = range(pages -1, pages +1)
        elif pages > self.frame_size and page_num > self.frame_size - 2 and pages - (self.frame_size / 2) <= page_num + 1:
            output['left_page_numbers'] = range(1, 3)
            output['middle_page_numbers'] = range(pages - self.frame_size + 1, pages +1)
        elif pages > self.frame_size and page_num > self.frame_size - 2:
            output['left_page_numbers'] = range(1, 3)
            output['middle_page_numbers'] = range(page_num - (self.frame_size / 2) +1, page_num + (self.frame_size / 2))
            output['right_page_numbers'] = range(pages -1, pages +1)
        return output
    
    
    def filmfeed_style(self, pages, page_num):
        output = {}
        if pages < self.frame_size:
            output['page_numbers'] = range(1, pages + 1)
        elif page_num < (self.frame_size / 2) + 1:
            output['page_numbers'] = range(1, self.frame_size + 1)
        elif page_num >= (self.frame_size / 2) + 1 and pages - (self.frame_size / 2) <= page_num:
            output['page_numbers'] = range(pages - self.frame_size + 1, pages + 1)
        elif page_num >= (self.frame_size / 2) + 1:
            start = page_num - (self.frame_size / 2)
            end = page_num + (self.frame_size / 2)
            output['page_numbers'] = range(start, end + 1)
        return output
    
    
    def muzx_style(self, pages, page_num):
        output = {}
        side_size = int(self.frame_size / 2.0)
        left_plus = max(0, side_size - (pages - page_num))
        right_plus = max(0, side_size - (page_num - 1))
        prev_pages = range(1, page_num)[-1 * (side_size + left_plus):]
        next_pages = range(page_num + 1, pages + 1)[:side_size + right_plus]
        output['page_numbers'] = prev_pages + [page_num] + next_pages
        return output
