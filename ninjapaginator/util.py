# -*- coding: utf-8 -*-

from django.utils.datastructures import MultiValueDictKeyError
from django.core.paginator import Paginator, EmptyPage
from django.http import Http404



class NinjaPaginator(object):
    """
    Pagination decorator with multiple types of pagination
    Should be used along with 'render_to' decorator
    from django-annoying application
    http://www.assembla.com/spaces/django-annoying
    """

    def __init__(self, object_list='object_list', style='digg', per_page=10, frame_size=8):
        """
        receive decorator parameters 
        """
        self.object_list = object_list
        self.style = style
        self.per_page = per_page
        self.frame_size = frame_size
        
    def __call__(self, function):
        """
        receive decorated function and return decorate method
        """
        self.function = function
        return self.decorate
    
    def decorate(self, request, *args, **kwargs):
        """
        style paginator according to 'style' parameter
        """
        self.output = self.function(request, *args, **kwargs)
        if not isinstance(self.output, dict):                       
            return self.output                  
        self.paginate_qs = self.output.pop(self.object_list) 
        try:                                                   
            self.page_num = int(request.GET['page'])                
        except (ValueError, MultiValueDictKeyError):           
            self.page_num = 1          
        self.paginator = Paginator(self.paginate_qs, self.per_page)
        try:
            self.page = self.paginator.page(self.page_num)
        except EmptyPage:
            raise  Http404()
        self.output['page_num'] = self.page_num
        self.output['per_page'] = self.per_page
        self.pages = self.paginator.num_pages
        self.output[self.object_list] = self.page.object_list
        self.output[self.style] = True
        run_style = getattr(self, "%s_style" % self.style)
        return run_style()
    
    def digg_style(self):
        if self.page_num > 1:
            self.output['PREVIOUS'] = self.page_num -1
        if self.page_num < self.paginator.num_pages:
            self.output['NEXT'] = self.page_num + 1
        if self.pages > self.frame_size and self.pages <= self.frame_size +2:
            self.output['left_page_numbers'] = range(1, self.pages + 1)
        elif self.pages < self.frame_size:
            self.output['left_page_numbers'] = range(1, self.pages + 1)
        elif self.pages > self.frame_size and self.page_num < self.frame_size - 1:
            self.output['left_page_numbers'] = range(1, self.frame_size + 1)
            self.output['right_page_numbers'] = range(self.pages -1, self.pages +1)
        elif self.pages > self.frame_size and self.page_num > self.frame_size - 2 and self.pages - (self.frame_size / 2) <= self.page_num + 1:
            self.output['left_page_numbers'] = range(1, 3)
            self.output['middle_page_numbers'] = range(self.pages - self.frame_size + 1, self.pages +1)
        elif self.pages > self.frame_size and self.page_num > self.frame_size - 2:
            self.output['left_page_numbers'] = range(1, 3)
            self.output['middle_page_numbers'] = range(self.page_num - (self.frame_size / 2) +1, self.page_num + (self.frame_size / 2))
            self.output['right_page_numbers'] = range(self.pages -1, self.pages +1)
        return self.output

    def filmfeed_style(self):
        if self.pages < self.frame_size:
            self.output['page_numbers'] = range(1, self.pages + 1)
        elif self.page_num < (self.frame_size / 2) + 1:
            self.output['page_numbers'] = range(1, self.frame_size + 1)
        elif self.page_num >= (self.frame_size / 2) + 1 and self.pages - (self.frame_size / 2) <= self.page_num:
            self.output['page_numbers'] = range(self.pages - self.frame_size + 1, self.pages + 1)
        elif self.page_num >= (self.frame_size / 2) + 1:
            start = self.page_num - (self.frame_size / 2)
            end = self.page_num + (self.frame_size / 2)
            self.output['page_numbers'] = range(start, end + 1)
        return self.output
