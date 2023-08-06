# views.py
#
# Copyright (C) 2008-2009 Marco Pantaleoni. All rights reserved
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from django.shortcuts import get_object_or_404
from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.conf import settings

from softwarefabrica.django.crud import crud

from softwarefabrica.django.common.models import *

# -- generic views for CommonModel instances -----------------------------

class CreateObjectView(crud.CreateObjectView):
    """
    ``CreateObjectView`` generic view version for CommonModel instances.
    """
    def __init__(self, *args, **kwargs):
        super(CreateObjectView, self).__init__(*args, **kwargs)
        self._set_form_fields(*args, **kwargs)

    def _set_form_fields(self, *args, **kwargs):
        model           = kwargs.pop('model', self.model) or self.model
        args_fields     = kwargs.pop('fields', self.fields) or self.fields
        args_exclude    = kwargs.pop('exclude', self.exclude) or self.exclude
        args_fieldorder = kwargs.pop('fieldorder', self.fieldorder) or self.fieldorder
        if model:
            edit_fields = get_sfapp_field(model, 'edit_fields',
                                          get_sfapp_field(model, 'fields', args_fields))
            if edit_fields is not None:
                self.fields = edit_fields
                #if args_fieldorder is None:
                #    self.fieldorder = list(edit_fields)
            edit_exclude_fields = get_sfapp_field(model, 'edit_exclude_fields',
                                                  get_sfapp_field(model, 'exclude_fields', args_exclude))
            if (edit_exclude_fields is not None) and (args_exclude is None):
                self.exclude = edit_exclude_fields
        return self

    def pre_call(self, request, *args, **kwargs):
        self._set_form_fields(*args, **kwargs)
        return super(CreateObjectView, self).pre_call(request, *args, **kwargs)

# this is an example of how we could set the owner
#    def pre_save_instance(self, obj, form, request):
#        from django.http import HttpRequest
#        assert isinstance(request, HttpRequest)
#        assert isinstance(obj, CommonModel)
#        if not obj.uuid:
#            if (obj.owner_user is None) and request.user.is_authenticated():
#                obj.owner_user = request.user
#        return super(CreateObjectView, self).pre_save_instance(obj, form, request)

    def instance_save_args(self, obj, form, request):
        from django.http import HttpRequest
        assert isinstance(request, HttpRequest)
        assert isinstance(obj, CommonModel)
        s_kwargs = {}
        if request.user.is_authenticated():
            s_kwargs['user'] = request.user
        s_kwargs['request'] = request
        return ((), s_kwargs)

class UpdateObjectView(crud.UpdateObjectView):
    """
    ``UpdateObjectView`` generic view version for CommonModel instances.
    """
    def __init__(self, *args, **kwargs):
        super(UpdateObjectView, self).__init__(*args, **kwargs)
        self._set_form_fields(*args, **kwargs)

    def _set_form_fields(self, *args, **kwargs):
        model           = kwargs.pop('model', self.model) or self.model
        args_fields     = kwargs.pop('fields', self.fields) or self.fields
        args_exclude    = kwargs.pop('exclude', self.exclude) or self.exclude
        args_fieldorder = kwargs.pop('fieldorder', self.fieldorder) or self.fieldorder
        if model:
            edit_fields = get_sfapp_field(model, 'edit_fields',
                                          get_sfapp_field(model, 'fields', args_fields))
            if edit_fields is not None:
                self.fields = edit_fields
                #if args_fieldorder is None:
                #    self.fieldorder = list(edit_fields)
            edit_exclude_fields = get_sfapp_field(model, 'edit_exclude_fields',
                                                  get_sfapp_field(model, 'exclude_fields', args_exclude))
            if (edit_exclude_fields is not None) and (args_exclude is None):
                self.exclude = edit_exclude_fields
        return self

    def pre_call(self, request, *args, **kwargs):
        self._set_form_fields(*args, **kwargs)
        return super(UpdateObjectView, self).pre_call(request, *args, **kwargs)

    def instance_save_args(self, obj, form, request):
        from django.http import HttpRequest
        assert isinstance(request, HttpRequest)
        assert isinstance(obj, CommonModel)
        s_kwargs = {}
        if request.user.is_authenticated():
            s_kwargs['user'] = request.user
        s_kwargs['request'] = request
        return ((), s_kwargs)

class ListObjectView(crud.ListObjectView):
    """
    ``ListObjectView`` generic view version for CommonModel instances.

    Select only active instances.
    If the model supports the ``owner_XXX`` property (thus having an
    ``OwnedQuerySet``), select only instances owned by ``owner_user`` or public.

    If the ``dont_filter_owner`` parameter is passed and True, no filtering is
    applied on ``owner_XXX``.

    If the ``dont_filter_active`` parameter is passed and True, no filtering is
    performed on active/inactive instances.
    """
    def __init__(self, *args, **kwargs):
        self.dont_filter_owner  = kwargs.pop('dont_filter_owner', False)
        self.dont_filter_active = kwargs.pop('dont_filter_active', False)
        super(ListObjectView, self).__init__(*args, **kwargs)

    def populate_context(self, context, request, model, obj = None, template_object_name = 'object'):
        if ('q' in request.GET) and request.GET['q'].strip():
            q = request.GET['q']
            context['q'] = q
        return super(ListObjectView, self).populate_context(context, request, model, obj, template_object_name)

    def __call__(self, request, queryset = None, **kwargs):
        from softwarefabrica.django.common.search import search_queryset
        from django import db

        dont_filter_owner  = kwargs.pop('dont_filter_owner', self.dont_filter_owner)
        dont_filter_active = kwargs.pop('dont_filter_active', self.dont_filter_active)

        queryset = queryset or self.queryset
        from django.http import HttpRequest
        assert isinstance(request, HttpRequest)
        assert issubclass(queryset.model, CommonModel)
        if not dont_filter_owner:
            if isinstance(queryset, OwnedQuerySet):
                assert isinstance(queryset, OwnedQuerySet)
                if request.user.is_authenticated():
                    queryset = queryset.owned_or_public(user = request.user)
        if not dont_filter_active:
            if isinstance(queryset, ActiveQuerySet):
                assert isinstance(queryset, ActiveQuerySet)
                queryset = queryset.active()

        if ('q' in request.GET) and request.GET['q'].strip():
            q = request.GET['q']
            model = kwargs.get('model', None) or queryset.model
            assert issubclass(model, db.models.Model)
            fields = search_fields(model)
            queryset = search_queryset(queryset, q, fields)

        return super(ListObjectView, self).__call__(request, queryset = queryset, **kwargs)

class DetailObjectView(crud.DetailObjectView):
    EMPTY_VALUE = '--'

    def populate_context(self, context, request, model, obj = None, template_object_name = 'object'):
        from django.db import models
        from django.db.models.options import Options
        from django.db.models.fields import FieldDoesNotExist
        from django.utils import dateformat
        from django.utils.datastructures import SortedDict
        from django.utils.text import capfirst
        from django.utils.translation import get_date_formats
        from django.utils.html import escape, conditional_escape
        from django.utils.safestring import mark_safe
        from django.utils.encoding import smart_unicode, smart_str, force_unicode
    
        assert issubclass(model, models.Model)
        opts = model._meta
        assert isinstance(opts, Options)

        class SintheticField(object):
            def __init__(self, name, verbose_name):
                self.name = name
                self.verbose_name = verbose_name

        empty_value           = get_sfapp_field(obj, 'empty_value', self.EMPTY_VALUE)
        detail_fields         = get_sfapp_field(obj, 'detail_fields',
                                                get_sfapp_field(obj, 'fields', None))
        detail_exclude_fields = get_sfapp_field(obj, 'detail_exclude_fields',
                                                get_sfapp_field(obj, 'exclude_fields', ()))
        if detail_fields is None:
            detail_fields = []
            for field in opts.fields + opts.many_to_many:
                detail_fields.append(field.name)

        obj_field_values = []
        for fieldname in detail_fields:
            if fieldname in detail_exclude_fields:
                continue
            field_sinthetic = False
            field     = None
            raw_value = None
            try:
                field = opts.get_field(fieldname)
                raw_value = getattr(obj, field.name)
            except FieldDoesNotExist, e:
                if hasattr(obj, fieldname):
                    f = getattr(obj, fieldname)
                    verbose_name = fieldname
                    if hasattr(f, 'verbose_name'):
                        verbose_name = getattr(f, 'verbose_name')
                    field = SintheticField(fieldname,  verbose_name)
                    field_sinthetic = True
                    if callable(f):
                        raw_value = f()
                    else:
                        raw_value = f
            #print "FIELD %s raw:%s" % (field.name, raw_value)
            fmt_value = raw_value
            if (field is not None) and (not field_sinthetic):
                if field.rel:
                    if isinstance(field.rel, models.ManyToOneRel):
                        objs = getattr(obj, field.name)
                        if objs is not None:
                            if hasattr(objs, 'get_absolute_url'):
                                fmt_value = u'<a href="%s">%s</a>' % (objs.get_absolute_url(),
                                                                      objs)
                            else:
                                fmt_value = u'%s' % objs
                        else:
                            fmt_value = empty_value
                        fmt_value = mark_safe(fmt_value)
                    elif isinstance(field.rel, models.ManyToManyRel): # ManyToManyRel
                        objs = list(getattr(obj, field.name).all())
                        #print "rel: %s" % repr(objs)
                        fmt_value = objs
                elif field.choices:
                    objs = dict(field.choices).get(raw_value, empty_value)
                    fmt_value = objs
                elif isinstance(field, models.DateField) or isinstance(field, models.TimeField):
                    if raw_value:
                        date_format, datetime_format, time_format = get_date_formats()
                        if isinstance(field, models.DateTimeField):
                            objs = capfirst(dateformat.format(raw_value, datetime_format))
                        elif isinstance(field, models.TimeField):
                            objs = capfirst(dateformat.time_format(raw_value, time_format))
                        else:
                            objs = capfirst(dateformat.format(raw_value, date_format))
                    else:
                        objs = empty_value
                    fmt_value = objs
                elif isinstance(field, models.BooleanField) or isinstance(field, models.NullBooleanField):
                    objs = {True: _('Yes'), False: _('No'), None: _('Unknown')}[raw_value]
                    fmt_value = objs
                else:
                    fmt_value = raw_value
            if fmt_value is None:
                fmt_value = empty_value
            field_dict = dict(field = field, value = fmt_value)
            if field is not None:
                field_dict['name'] = field.name
            obj_field_values.append(field_dict)
        context['fieldvals'] = obj_field_values

        # many to many fields
        obj_field_values = []
        m2m_fields = []
        for field in opts.many_to_many:
            assert isinstance(field.rel, models.ManyToManyRel)
            m2m_fields.append(field)
        for field in m2m_fields:
            assert isinstance(field.rel, models.ManyToManyRel)
            fieldname = field.name
            if fieldname in detail_exclude_fields:
                continue
            raw_value = None
            raw_value = getattr(obj, field.name)
            fmt_value = raw_value
            assert isinstance(field.rel, models.ManyToManyRel)
            related_objs = getattr(obj, field.name).all()
            field_dict = dict(field = field,
                              name = field.name,
                              value = related_objs)
            obj_field_values.append(field_dict)
        context['m2m'] = obj_field_values

        ##
        ## related objects
        ## (reverse many to many and many to one relations)
        ##

        class RelatedItem(object):
            def __init__(self, instance, rel_object):
                from django.db.models.related import RelatedObject
                from django.db.models.fields.related import ManyToManyRel, ManyToOneRel
                assert isinstance(instance, CommonModel)
                assert isinstance(rel_object, RelatedObject)
                self.instance      = instance
                self.related       = rel_object
                self.field         = self.related.field
                self.fieldname     = self.field.verbose_name,
                self.rel           = self.field.rel
                assert (isinstance(self.rel, ManyToManyRel) or
                        isinstance(self.rel, ManyToOneRel))
                self.model         = self.related.model
                self.opts          = self.model._meta
                self.through_model = None
                self.through_opts  = None
                if hasattr(self.rel, 'through_model'):
                    self.through_model = getattr(self.rel, 'through_model')
                    self.through_opts  = self.through_model._meta
                rev_verbose_names  = get_sfapp_field(self.model,
                                                     'reverse_verbose_names', {})
                r_verbose_name, r_verbose_name_plural = (self.opts.verbose_name,
                                                         self.opts.verbose_name_plural)
                if self.field.name in rev_verbose_names:
                    r_verbose_name, r_verbose_name_plural = rev_verbose_names[self.field.name]
                self.r_verbose_name = r_verbose_name
                self.r_verbose_name_plural = r_verbose_name_plural

                self.object_list = []
                if self.related.get_accessor_name():
                    self.object_list = [i for i in getattr(self.instance,
                                                           self.related.get_accessor_name()).all()]
            def __str__(self):
                return '%r for instance:%r field:%s' % (self.related,
                                                        self.instance,
                                                        self.fieldname)
        # reverse many to many
        # all instances (and models) that have this model as a ManyToManyField
        # group by rel_object.field.verbose_name
        #rev_verbose_names  = get_sfapp_field(obj, 'reverse_verbose_names', {})
        m2m_referrers = []
        m2m_referrers_by_field = {}
        for rel_object in opts.get_all_related_many_to_many_objects():
            relitem = RelatedItem(obj, rel_object)
            if relitem.fieldname not in m2m_referrers_by_field:
                m2m_referrers_by_field[relitem.fieldname] = relitem
            else:
                o_relitem = m2m_referrers_by_field[relitem.fieldname]
                assert relitem.related == o_relitem.related
                assert relitem.model == o_relitem.model
                assert relitem.fieldname == o_relitem.fieldname
                assert relitem.field == o_relitem.field
                o_relitem.object_list.extend(relitem.object_list)
        m2m_related = []
        for fieldname in m2m_referrers_by_field.keys():
            m2m_related.append(m2m_referrers_by_field[fieldname])
        context['m2m_related'] = m2m_related

        # reverse many to one (foreign keys)
        # all instances (and models) that have this model as a ForeignKey
        # group by rel_object.field.verbose_name
        #rev_verbose_names  = get_sfapp_field(obj, 'reverse_verbose_names', {})
        fk_referrers = []
        fk_referrers_by_field = {}
        for rel_object in opts.get_all_related_objects():
            relitem = RelatedItem(obj, rel_object)
            if relitem.fieldname not in fk_referrers_by_field:
                fk_referrers_by_field[relitem.fieldname] = relitem
            else:
                o_relitem = fk_referrers_by_field[relitem.fieldname]
                assert relitem.related == o_relitem.related
                assert relitem.model == o_relitem.model
                assert relitem.fieldname == o_relitem.fieldname
                assert relitem.field == o_relitem.field
                o_referrer['object_list'].extend(referrer['object_list'])
                o_relitem.object_list.extend(relitem.object_list)
        fk_related = []
        for fieldname in fk_referrers_by_field.keys():
            fk_related.append(fk_referrers_by_field[fieldname])
        context['fk_related'] = fk_related

        return super(DetailObjectView, self).populate_context(context, request, model, obj, template_object_name)

DeleteObjectView = crud.DeleteObjectView
#DetailObjectView = crud.DetailObjectView

create_object = CreateObjectView()
update_object = UpdateObjectView()
delete_object = DeleteObjectView()
object_detail = DetailObjectView()
object_list   = ListObjectView()

def search_fields(model):
    from django import db
    assert issubclass(model, db.models.Model)
    search_fields = get_sfapp_field(model, 'search_fields',
                                    get_sfapp_field(model, 'fields', None))
    search_exclude_fields = get_sfapp_field(model, 'search_exclude_fields',
                                            get_sfapp_field(model, 'exclude_fields', ()))
    fields = []
    if search_fields is not None:
        for field in search_fields:
            if field not in search_exclude_fields:
                fields.append(field)
    return fields

def search(request, models, template_name='common/object_search.html'):
    """
    Search view.
    Receives a list of models in ``models``.
    """

    from django import db
    from softwarefabrica.django.common.search import search_models
    from softwarefabrica.django.utils.viewshelpers import render_to_response

    models_and_fields = []
    for model in models:
        assert issubclass(model, db.models.Model)
        fields = search_fields(model)
        models_and_fields.append((model, tuple(fields)))

    q = ''
    if ('q' in request.GET) and request.GET['q'].strip():
        q = request.GET['q']

        found_objects = search_models(q, models_and_fields)

    return render_to_response(request, template_name,
                              { 'query_string': q,
                                'found': found_objects,
                                })
