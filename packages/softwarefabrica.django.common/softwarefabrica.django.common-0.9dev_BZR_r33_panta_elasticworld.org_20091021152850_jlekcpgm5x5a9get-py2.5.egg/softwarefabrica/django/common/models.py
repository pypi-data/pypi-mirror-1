# models.py
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
#from django.db.models.query import QuerySet
from django.db.models import Q
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes import generic
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from softwarefabrica.django.utils.managers import QuerySetManager
from softwarefabrica.django.utils.UUIDField import UUIDField
from softwarefabrica.django.common.managers import *
import datetime

# -- common model support ------------------------------------------------

class CommonModel(models.Model):
    uuid        = UUIDField(_("uuid"), primary_key=True, db_index=True)

    desc	= models.CharField(_("description"), max_length=200, blank=True)
    long_desc	= models.TextField(_("long description"), blank=True)

    active      = models.BooleanField(_("active"),      default=True, db_index=True, blank=True)
    active_from = models.DateTimeField(_("active from"), db_index=True, blank=True, null=True, editable=False)
    active_to   = models.DateTimeField(_("active to"),   db_index=True, blank=True, null=True, editable=False)

    createdby   = models.ForeignKey(User, db_index=True, verbose_name=_("created by"), related_name='createdby_%(class)s_set', blank = True, null = True, editable=False)
    modifiedby  = models.ForeignKey(User, db_index=True, verbose_name=_("modified by"), related_name='modifiedby_%(class)s_set', blank = True, null = True, editable=False)
    created     = models.DateTimeField(_("created"), db_index=True, editable=False)
    modified    = models.DateTimeField(_("modified"), db_index=True, editable=False)

    objects     = QuerySetManager()

    QuerySet = ActiveQuerySet

    class Meta:
        abstract = True

    class SFApp:
        exclude_fields = ('uuid',)
        detail_exclude_fields = ('uuid', 'desc', 'long_desc',)

    def is_active(self, when=None):
        return instance_is_active(self, when)
    is_active.verbose_name = "is active"

    def deactivate(self, when=None):
        return deactivate_instance(self, when)

    def save_specific(self, *args, **kwargs):
        user    = kwargs.pop('user', None)
        request = kwargs.pop('request', None)
        time_now = datetime.datetime.now()
        if (user is None) and (request is not None):
            from django.http import HttpRequest
            assert isinstance(request, HttpRequest)
            if request.user.is_authenticated():
                user = request.user
        if not self.uuid:
            if not self.active_from:
                self.active_from = time_now
            if not self.created:
                if user is not None:
                    self.createdby = user
                self.created = time_now
        if user is not None:
            self.modifiedby = user
        self.modified = time_now
        return self

    def save(self, *args, **kwargs):
        self.save_specific(*args, **kwargs)
        kwargs.pop('user', None)
        kwargs.pop('request', None)
        return models.Model.save(self, *args, **kwargs)

def get_sfapp_field(instance_or_model, fieldname, default=None):
    """
    Search for the field named ``fieldname`` in:
    
    - instance ``SFApp`` class (if an instance is passed)
    - model ``SFApp class``
    - instance/model bases ``SFApp`` (following the instance MRO)
    - instance (if an instance is passed)
    - model
    - instance/model bases (following the instance MRO)
    """
    if hasattr(instance_or_model, 'get_sfapp_field'):
        get_sfapp_field = getattr(instance_or_model, 'get_sfapp_field')
        return get_sfapp_field(instance_or_model, fieldname, default)
    places = []
    if isinstance(instance_or_model, CommonModel):
        places = [instance_or_model, instance_or_model.__class__]
        for b in instance_or_model.__class__.__mro__:
            if b not in places:
                places.append(b)
    elif isinstance(instance_or_model, type) and issubclass(instance_or_model, CommonModel):
        places = [instance_or_model,]
        for b in instance_or_model.__mro__:
            if b not in places:
                places.append(b)
    else:
        raise ValueError("instance_or_model must be a CommonInfo instance or subclass")
    n_places = places[:]
    sfapp_places = []
    for place in places:
        if hasattr(place, 'SFApp'):
            sfapp = getattr(place, 'SFApp')
            if sfapp not in sfapp_places:
                sfapp_places.append(sfapp)
    places = n_places
    places[0:0] = sfapp_places
    for place in places:
        if hasattr(place, fieldname):
            return getattr(place, fieldname)
    return default

class CommonOwnedModel(CommonModel):
    owner_user  = models.ForeignKey(User, db_index=True, verbose_name=_("owner user"), related_name="owner_user_%(class)s_set", blank=True, null=True, editable=False)
    owner_group = models.ForeignKey(Group, db_index=True, verbose_name=_("owner group"), related_name="owner_group_%(class)s_set", blank=True, null=True, editable=False)

    #class QuerySet(ActiveQuerySet, OwnedQuerySet):
    #    pass
    QuerySet = OwnedActiveQuerySet

    class Meta:
        abstract = True

    def save_specific(self, *args, **kwargs):
        owner = kwargs.pop('owner', None)
        owner_user  = kwargs.pop('owner_user', None)
        owner_group = kwargs.pop('owner_group', None)
        if not self.uuid:
            if (owner is not None) and ((owner_user is None) and (owner_group is None)):
                (owner_user, owner_group) = owner
            if (owner_user is not None) and (not self.owner_user):
                self.owner_user = owner_user
            if (owner_group is not None) and (not self.owner_group):
                self.owner_group = owner_group
        return super(CommonOwnedModel, self).save_specific(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.save_specific(*args, **kwargs)
        kwargs.pop('user', None)
        kwargs.pop('request', None)
        kwargs.pop('owner', None)
        kwargs.pop('owner_user', None)
        kwargs.pop('owner_group', None)
        return models.Model.save(self, *args, **kwargs)

# -- recursive models support --------------------------------------------

def instance_full_name(obj, separator):
    """
    Return the full name for the object, complete with pieces from its ancestors.
    For example: 'Recipes/Cookies'.

    The model must have ``parent`` and ``name`` fields.
    """
    if obj.parent is not None:
        return u"%s%s%s" % (obj.get_full_name(separator = separator), separator, obj.name)
    return obj.name

def instance_absolute_name(obj, master, master_separator, local_separator, master_local_separator):
    """
    Return the absolute name for the object, complete with pieces from its ancestors
    and the full name of its master object.
    For example: 'Softwarefabrica/Projects.Estimator'.

    The model must have ``parent`` and ``name`` fields.
    """
    return u"%s%s%s" % (master.get_full_name(separator = master_separator), master_local_separator, obj.get_full_name(separator = local_separator))

def ancestors(obj, include_obj=False):
    ancestors = []
    if include_self:
        ancestors.append(obj)
    p = obj.parent
    while p:
        ancestors.append(p)
        p = p.parent
    return ancestors

def ancestors_with_obj(obj):
    return ancestors(include_obj = True)

def is_leaf(obj):
    model = obj.__class__
    return (model._default_manager.filter(parent = self).count() == 0)

class RecursiveModel(models.Model):
    parent = models.ForeignKey('self', verbose_name=_("parent"), related_name='parent_%(class)s_set', blank=True, null=True, db_index=True)
    name   = models.CharField(_("name"), max_length=80, blank=False, db_index=True)

    fullname_cache = models.CharField(_("fullname_cache"), max_length=220, blank=False, db_index=True, editable=False)

    PARENT_SEPARATOR = u'/'

    class Meta:
        abstract = True
        unique_together = (('parent', 'name'), ('parent', 'fullname_cache'),)
        ordering = ('parent', 'name',)

    def __unicode__(self):
        return self.get_full_name()

    def save_specific(self, user=None, request=None, *args, **kwargs):
        fullname            = self.get_full_name()
        self.fullname_cache = fullname
        return self

    def save(self, *args, **kwargs):
        self.save_specific(*args, **kwargs)
        kwargs.pop('user', None)
        kwargs.pop('request', None)
        return models.Model.save(self, *args, **kwargs)

    def get_full_name(self, separator=None):
        """
        Return the full name for the object, complete with pieces from its ancestors.
        For example: 'Recipes/Cookies'.
        """
        separator = separator or self.PARENT_SEPARATOR

        if self.parent is not None:
            return u"%s%s%s" % (self.parent.get_full_name(separator = separator), separator, self.name)
        return self.name

    fullname = property(get_full_name, None, None, "full name")

    def ancestors(self, include_self=False):
        ancestors = []
        if include_self:
            ancestors.append(self)
        p = self.parent
        while p:
            ancestors.append(p)
            p = p.parent
        return ancestors

    def ancestors_with_self(self):
        return self.ancestors(include_self = True)

    def descendants(self, include_self=False):
        descendants = []
        model = self.__class__
        if include_self:
            descendants.append(self)
        direct = model.objects.filter(parent = self).all()
        for obj in direct:
            assert obj.parent == self
            descendants.append(obj)
            obj_descendants = obj.descendants(include_self = False)
            descendants.extend(obj_descendants)
        return descendants

    def is_leaf(self):
        model = self.__class__
        return (model._default_manager.filter(parent = self).count() == 0)
