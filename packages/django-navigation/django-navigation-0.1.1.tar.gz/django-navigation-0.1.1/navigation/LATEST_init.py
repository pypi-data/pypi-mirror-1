# -*- coding: utf-8 -*-
#
#  Copyright (c) 2008-2009 Andy Mikhailenko and contributors
#
#  Django Navigation is free software under terms of the GNU Lesser
#  General Public License version 3 (LGPLv3) as published by the Free
#  Software Foundation. See the file README for copying conditions.
#

" A breadcrumbs navigation application for Django framework. "

__author__  = 'Andy Mikhailenko'
__license__ = 'GNU Lesser General Public License (GPL), Version 3'
__url__     = 'http://bitbucket.org/neithere/django-navigation/'
__version__ = '0.1.0'


'''
Для специально написанных вьюх:

    Вариант 1:
    
        @render_to()
        def my_view(request, obj_id):
            object_list = SomeModel.objects.all()
            return {'obj': object_list}
        my_view.crumbs = 'Object List'

    Вариант 2:

        class CrumbsViews:
            def __init__(self, mode):
                assert hasattr(self, 'queryset') and \
                       isinstance(QuerySet, self.queryset)
                # FIXME user may want some other views like 'edit'
                assert mode in ('list', 'detail')
                self._handler = getattr(self, 'view_%s' % mode)

            def __call__(self, request, *args, **kwargs):
                self.request = request
                self.args    = args
                self.kwargs  = kwargs
                self.init()
                return self._handler()
            
            def init(self):
                pass

            def get_object(self):
                """Returns object or raises Http404. Query is constructed by adding
                ``detail_lookup`` to ``queryset`` (both are class attributes).

                ``detail_lookup`` must be a dictionary with query lookups mapped
                to view function keywords. The keywords should come from named
                regex groups in urlconf.
                """
                assert hasattr(self, 'detail_lookup') and \
                       isinstance(dict, self.detail_lookup)
                d = dict(k, self.kwargs[v] for k,v in self.detail_lookup)
                return get_object_or_404(self.queryset, **d)

            @render_to()
            def view_list(self):
                return {'object': self.get_object()}

            @render_to()
            def view_detail(self):
                return {'object_list': self.queryset}

        class ArticleViewer(CrumbsViewer):
            "Views for Article model"
            queryset = Article.objects.filter(published=True)
            facets = (
                (DateDrilldown, 'year', 'month', in_path=True),
                (Facet, 'category', in_path=True),    # from url regex group
                (Facet, 'author',   in_path=False),   # from request.GET
            )
            detail_lookup = {'slug__exact', 'slug'}
            crumbs_list = _('My objects')   # TODO: date drilldown
            crumbs_detail = lambda self: self.get_object().title

Для уже существующих приложений, чтобы не менять их код:

    Вариант 1:         XXX: HOW TO IMPLEMENT?

        crumbs.py

            crumbs = (
                ('pl-gallery', crumb_for_photologue_gallery),
            )
            def crumb_for_photologue_gallery(request, slug):
                return Gallery.objects.get(slug=slug)
'''
