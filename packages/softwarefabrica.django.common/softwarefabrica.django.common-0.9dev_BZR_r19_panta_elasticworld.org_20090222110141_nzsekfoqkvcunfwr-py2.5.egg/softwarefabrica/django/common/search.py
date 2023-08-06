# search.py
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

from django.db import models
from django.db.models.options import Options

from softwarefabrica.django.utils import usearch

def search_model(query_string, model, fields):
    """
    Perform the requested search (terms in ``query_string``) in the
    specified ``model`` using the specified ``fields``.
    """
    assert issubclass(model, models.Model)
    opts = model._meta
    assert isinstance(opts, Options)
    query = usearch.get_query(query_string, fields)
    if query is not None:
        return model._default_manager.filter(query)
    return model._default_manager.all()

def search_models(query_string, models_and_fields):
    """
    Perform the requested search (terms in ``query_string``) in the models and
    fields specified in ``models_and_fields``.
    ``models_and_fields`` is a list of tuples (MODEL, FIELDS).
    """
    found_objects = []
    found = {}

    for model_fields in models_and_fields:
        (model, fields) = model_fields
        assert issubclass(model, models.Model)
        opts = model._meta
        assert isinstance(opts, Options)
        query = usearch.get_query(query_string, fields)
        found_for_model = []
        if query is not None:
            found_for_model = model._default_manager.filter(query)
        else:
            found_for_model = model._default_manager.all()
        found[opts.verbose_name] = found_for_model
        found_objects.append(dict(model        = model,
                                  name         = opts.verbose_name,
                                  name_plural  = opts.verbose_name_plural,
                                  opts         = opts,
                                  objects      = found_for_model,
                                  query_string = query_string))
    return found_objects

def search_queryset(queryset, query_string, fields, model=None):
    """
    Perform the requested search (terms in ``query_string``) filtering the
    specified ``queryset`` using the specified ``fields``.

    Returns the filtered queryset.
    """
    from django.db.models.query import QuerySet
    assert isinstance(queryset, QuerySet)

    queryset = queryset._clone()
    model    = model or queryset.model

    assert issubclass(model, models.Model)
    opts = model._meta
    assert isinstance(opts, Options)
    query = usearch.get_query(query_string, fields)
    if query is not None:
        return queryset.filter(query)
    return queryset
