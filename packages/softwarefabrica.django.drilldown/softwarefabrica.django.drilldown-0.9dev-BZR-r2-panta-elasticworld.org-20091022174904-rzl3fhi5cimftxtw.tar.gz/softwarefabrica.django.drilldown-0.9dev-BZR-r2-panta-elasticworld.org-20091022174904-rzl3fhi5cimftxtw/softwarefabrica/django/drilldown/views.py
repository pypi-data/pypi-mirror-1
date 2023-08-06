"""
Drilldown views.

Copyright (C) 2009 Marco Pantaleoni. All rights reserved.

@author: Marco Pantaleoni
@copyright: Copyright (C) 2009 Marco Pantaleoni
"""

__author__    = "Marco Pantaleoni"
__copyright__ = "Copyright (C) 2009 Marco Pantaleoni"
__license__   = "GPL v2"

from django.shortcuts import get_object_or_404
from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.encoding import force_unicode, smart_str
from django.utils.safestring import mark_safe
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.views.generic import GenericViewError
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.conf import settings
from django.db import transaction

from softwarefabrica.django.crud.crud import GenericView, POPUP_VARIABLE, CONTEXT_POPUP_VARIABLE
from softwarefabrica.django.common.views import *

from softwarefabrica.django.utils.viewshelpers import render_to_response

import datetime
import logging

NONE_REPR   = u'__none__'
FALSE_REPR  = u'__false__'
TRUE_REPR   = u'__true__'
EMPTY_REPR  = u'__empty__'

DATETIME_FORMAT = '%Y%m%d%H%M%S'
DATE_FORMAT     = '%Y%m%d'
TIME_FORMAT     = '%H%M%S'

def _make_link(obj, url=None, default_value=None):
    link_text = u''
    if obj:
        if hasattr(obj, 'get_absolute_url'):
            url = url or obj.get_absolute_url()
        link_text = u'%s' % obj
    if not link_text:
        link_text = u'%s' % default_value
    if not link_text:
        link_text = u'%s' % url
    link = u'<a href="%s">%s</a>' % (url, link_text)
    return link

def _db_python_to_text(db_field, value):
    from django.utils.encoding import smart_unicode, force_unicode
    import datetime
    import time
    assert isinstance(db_field, models.fields.Field)
    #logging.debug("_db_python_to_text(field:%s, value:%s)" % (db_field, value))
    #return db_field.value_to_string(value)
    if value is None:
        return force_unicode(NONE_REPR)
    elif value is False:
        return force_unicode(FALSE_REPR)
    elif value is True:
        return force_unicode(TRUE_REPR)
    elif value == u'':
        return force_unicode(EMPTY_REPR)
    elif isinstance(db_field, models.ForeignKey):
        if isinstance(value, models.Model):
            assert isinstance(value, models.Model)
            return u'%s' % value.pk
        return u'%s' % value
    elif isinstance(db_field, models.ManyToManyField):
        if isinstance(value, models.Model):
            assert isinstance(value, models.Model)
            return u'%s' % value.pk
        return u'%s' % value
    elif isinstance(db_field, models.DateTimeField) or \
         isinstance(db_field, models.DateField) or \
         isinstance(db_field, models.TimeField):
        if isinstance(value, datetime.datetime):
            return force_unicode(value.strftime(DATETIME_FORMAT))
        elif isinstance(value, datetime.date):
            return force_unicode(value.strftime(DATE_FORMAT))
        elif isinstance(value, datetime.time):
            return force_unicode(value.strftime(TIME_FORMAT))
        else:
            return force_unicode(value)
    elif isinstance(db_field, models.IntegerField):
        return force_unicode(u'%s' % value)
    return force_unicode(value)

def _db_text_to_python(db_field, text):
    import datetime
    import time
    assert isinstance(db_field, models.fields.Field)
    #logging.debug("_db_text_to_python(field:%s, text:%s)" % (db_field, text))
    if (text == NONE_REPR) or (text is None):
        return None
    elif (text == FALSE_REPR) or (text is False):
        return False
    elif (text == TRUE_REPR) or (text is True):
        return True
    elif (text == EMPTY_REPR) or (text == ''):
        return u''
    elif isinstance(text, models.Model):
        return text
    elif isinstance(db_field, models.ForeignKey) or \
         isinstance(db_field, models.ManyToManyField):
        if isinstance(text, models.Model):
            return text
        fk_model = db_field.rel.to
        fk_pk = fk_model._meta.pk
        pk_val = text
        if pk_val is None:
            return None
        if isinstance(fk_pk, models.fields.IntegerField):
            pk_val = int(text)
        try:
            return fk_model.objects.get(pk = pk_val)
        except ObjectDoesNotExist:
            return None
    elif isinstance(db_field, models.DateTimeField):
        if isinstance(text, datetime.datetime):
            return text
        return datetime.datetime.strptime(text, DATETIME_FORMAT)
    elif isinstance(db_field, models.DateField):
        if isinstance(text, datetime.date):
            return text
        return datetime.datetime.strptime(text, DATE_FORMAT).date()
    elif isinstance(db_field, models.TimeField):
        if isinstance(text, datetime.time):
            return text
        return datetime.datetime.strptime(text, TIME_FORMAT).time()
    elif isinstance(db_field, models.IntegerField):
        return int(text)
    return db_field.to_python(text)

class DrillDownField(object):
    EMPTY_VALUE = '--'

    def __init__(self, ddinfo, db_field, raw_value, url=None, auto_url=False,
                 empty_value=None, use_value=True):
        if empty_value is None:
            empty_value = self.EMPTY_VALUE

        assert isinstance(ddinfo, DrillDownInfo)
        assert isinstance(db_field, models.fields.Field)
        self.ddinfo        = ddinfo
        self.use_value     = use_value
        self.field         = db_field
        self.name          = db_field.name
        self.verbose_name  = db_field.verbose_name
        self.raw_value_str = raw_value
        self.raw_value     = raw_value
        self.value         = u'%s' % raw_value
        self.url           = url
        self.auto_url      = auto_url
        self.count         = None
        self.empty_value   = empty_value

        if self.use_value:
            self.raw_value = _db_text_to_python(db_field, raw_value)
            self._setup()

    def __str__(self):
        return "%s" % unicode(self.value).encode('ascii', 'ignore')

    def __repr__(self):
        rv_repr = unicode(self.raw_value).encode('ascii', 'ignore')
        v_repr  = unicode(self.value).encode('ascii', 'ignore')
        return "<DrillDownField field:%s %s value:%s (%s)>" % (self.name, self.field, rv_repr, v_repr)

    def construct_search(self):
        from django.db import models
        from django.db.models.fields.related import RelatedField
        assert isinstance(self.field, models.fields.Field)
        field_name = str(self.name)

        query_kw = "%s" % field_name
        if isinstance(self.field, RelatedField):
            query_kw = "%s" % field_name
        elif isinstance(self.field, models.BooleanField):
            query_kw = "%s" % field_name
        elif isinstance(self.field, models.DateTimeField) or \
             isinstance(self.field, models.DateField) or \
             isinstance(self.field, models.TimeField):
            query_kw = "%s" % field_name
        elif isinstance(self.field, models.IntegerField):
            query_kw = "%s" % field_name
        elif field_name.startswith('^'):
            query_kw = "%s__istartswith" % field_name[1:]
        elif field_name.startswith('='):
            query_kw = "%s__iexact" % field_name[1:]
        elif field_name.startswith('@'):
            query_kw = "%s__search" % field_name[1:]
        elif isinstance(self.field, models.CharField):
            #query_kw = "%s__icontains" % field_name
            query_kw = "%s" % field_name
        else:
            query_kw = "%s" % field_name
        return {query_kw: self.raw_value}

    def _setup(self):
        from django.utils.safestring import mark_safe
        from django.utils.encoding import smart_unicode, smart_str, force_unicode
        from django.utils.translation import get_date_formats
        from django.utils import dateformat
        from django.utils.text import capfirst
        from django.core.exceptions import ObjectDoesNotExist
    
        #logging.debug("DrillDownField::_setup(field:%s, raw_value:%s, url:%s)" % (self.field, self.raw_value, self.url))

        assert self.field is not None

        fmt_value = u'%s' % self.raw_value
        if self.field.rel:
            if isinstance(self.field.rel, models.ManyToOneRel):
                if self.field.rel.to:
                    try:
                        if isinstance(self.raw_value, models.Model):
                            pk_val = self.raw_value.pk
                        else:
                            pk_val = self.raw_value
                        obj_value = self.field.rel.to._default_manager.get(**{self.field.rel.field_name: pk_val})
                    except ObjectDoesNotExist:
                        obj_value = None
                    if obj_value is None:
                        fmt_value = self.empty_value
                    else:
                        if self.url:
                            fmt_value = _make_link(obj_value, self.url)
                        elif self.auto_url:
                            auto_url = None
                            if hasattr(obj_value, 'get_absolute_url'):
                                auto_url = obj_value.get_absolute_url()
                            if auto_url:
                                fmt_value = _make_link(obj_value, auto_url)
                            else:
                                fmt_value = u'%s' % obj_value
                        else:
                            fmt_value = u'%s' % obj_value
            elif isinstance(self.field.rel, models.ManyToManyRel): # ManyToManyRel
                # TODO
                if self.field.rel.to:
                    pass
        elif self.field.choices:
            fmt_value = dict(self.field.choices).get(self.raw_value, self.empty_value)
        elif isinstance(self.field, models.DateField) or isinstance(self.field, models.TimeField):
            if self.raw_value:
                date_format, datetime_format, time_format = get_date_formats()
                if isinstance(self.field, models.DateTimeField):
                    value = capfirst(dateformat.format(self.raw_value, datetime_format))
                elif isinstance(self.field, models.TimeField):
                    value = capfirst(dateformat.time_format(self.raw_value, time_format))
                else:
                    value = capfirst(dateformat.format(self.raw_value, date_format))
            else:
                value = self.empty_value
            fmt_value = value
        elif isinstance(self.field, models.BooleanField) or isinstance(self.field, models.NullBooleanField):
            value = {True: _('Yes'), False: _('No'), None: _('Unknown')}[self.raw_value]
            fmt_value = value
        else:
            fmt_value = self.raw_value
        if fmt_value is None:
            fmt_value = self.empty_value
        fmt_value = mark_safe(fmt_value)
        self.value = fmt_value
        return fmt_value

class DrillDownInfo(object):
    def __init__(self, request, url, queryset, drilldown_fields, view_name,
                 view_args, view_kwargs,
                 ddfield_class=None):
        from django.db.models.query import QuerySet
        from django.utils.datastructures import MultiValueDict
        assert isinstance(queryset, QuerySet)
        self.request  = request
        self.url      = url
        self.queryset = queryset
        self.model    = queryset.model
        self.opts     = self.model._meta
        self.drilldown_fields = drilldown_fields
        self.view_name = view_name
        self.ddfield_class = ddfield_class or DrillDownField
        self.view_args   = view_args
        self.view_kwargs = view_kwargs

        # ``field_values`` is a dictionary indexed by field name, obtained from
        # the drill down fields (from URL or POST), where each value is
        # a ``DrillDownField``
        #
        # ``pivot_field_values`` is an array of ``DrillDownField``, each for the
        # pivot field with a different value and url pointing to a new, further
        # "drilled-down" view.
        self.url_components   = None
        self.field_values     = MultiValueDict()     # field name -> DrillDownField
        self.pivot_field_name = None
        self.pivot_field      = None
        self.pivot_field_values = []
        self.filtered_queryset = None

        self.used_fields           = []
        self.remaining_field_names = []
        self.remaining_fields      = []
        self.bread_crumbs          = []
        self.bread_crumbs_root     = None

    def __repr__(self):
        return "<DrillDownInfo url:%s pivot:%s values:%s>" % (self.url, self.pivot_field_name, self.field_values)

    def get_field(self, field_name):
        dd_field = self.field_values[field_name]
        assert isinstance(dd_field, DrillDownField)
        return dd_field

    def get_fields(self, field_name):
        return self.field_values.getlist(field_name)

    def add_field(self, field_name, field_value):
        self.field_values.appendlist(field_name, field_value)
        return self

    def get_dbfield(self, field_name):
        dd_field = self.get_field(field_name)
        assert isinstance(dd_field, DrillDownField)
        assert isinstance(dd_field.field, models.fields.Field)
        return dd_field.field

class DrilldownParamEncoder(object):
    B64_PREFIX = u':base64:'

    def __init__(self, param=None):
        self.param = param

    def encode(self):
        import urllib
        import base64
    
        param_str = u'%s' % self.param
        if '/' in param_str:
            b64pfx_param_str = u':base64:' + param_str
            b64pfx_param_str_utf8 = b64pfx_param_str.encode('utf-8')
            encoded = urllib.quote_plus(base64.urlsafe_b64encode(b64pfx_param_str_utf8))
        else:
            param_str_utf8 = param_str.encode('utf-8')
            encoded = urllib.quote_plus(param_str_utf8)
        return encoded

    def decode(self, encoded):
        import urllib
        import base64
        from django.utils.encoding import force_unicode

        #logging.debug("DDParamEncode.decode(%s)" % repr(encoded))
        unquoted  = urllib.unquote_plus(encoded)
        param_str = unquoted
        #logging.debug("unquoted:%s" % repr(unquoted))
        try:
            unquoted_str = str(unquoted)
            b64pfx_param_str = None
            b64pfx_param_str_utf8 = base64.urlsafe_b64decode(unquoted_str)
            #logging.debug("b64pfx_param_str_utf8:%s" % repr(b64pfx_param_str_utf8))
            if b64pfx_param_str_utf8:
                b64pfx_param_str = force_unicode(b64pfx_param_str_utf8, 'utf-8')
            #logging.debug("b64pfx_param_str:%s" % repr(b64pfx_param_str))
            if b64pfx_param_str and b64pfx_param_str.startswith(u':base64:'):
                param_str = b64pfx_param_str[len(self.B64_PREFIX):]
            #logging.debug("param_str:%s" % repr(param_str))
        except Exception, e:
            #logging.debug("exception %s" % repr(e))
            if isinstance(unquoted, unicode):
                param_str = unquoted
            else:
                param_str_utf8 = unquoted
                param_str      = force_unicode(param_str_utf8, 'utf-8')
        self.param = param_str
        return param_str

    @classmethod
    def Encode(cls, param):
        e_obj = cls(param)
        return e_obj.encode()

    @classmethod
    def Decode(cls, encoded):
        e_obj = cls()
        return e_obj.decode(encoded)

class DrillDownView(GenericView):
    """
    Generic view to handle drilldown navigation.

    Templates: ``<app_label>/<model_name>_drilldown.html``
               ``<app_label>/<model_name>_browse.html``
               ``<app_label>/object_drilldown.html``
               ``<app_label>/object_browse.html``
               ``<model_name>_drilldown.html``
               ``<model_name>_browse.html``
               ``object_drilldown.html``
               ``object_browse.html``
    """

    QUERYSET             = None
    PAGINATE_BY          = 5
    MODEL                = None
    APP_LABEL            = None
    MODEL_NAME           = None
    MIMETYPE             = None
    LOOKUP_KWARGS        = None
    FIELDS               = None
    DDINFO_CLASS         = DrillDownInfo
    DDFIELD_CLASS        = DrillDownField
    ALLOW_EMPTY          = True
    TEMPLATE_OBJECT_NAME = 'object'
    VIEW_NAME            = None

    __name__ = 'DrillDownView'

    def __init__(self, queryset = None, paginate_by = None,
                 model = None,
                 app_label = None, model_name = None,
                 fields   = None,
                 mimetype = None,
                 lookup_kwargs = None,
                 ddinfo_class = None,
                 ddfield_class = None,
                 allow_empty = None,
                 template_object_name = None,
                 view_name = None,
                 *args, **kwargs):
        super(DrillDownView, self).__init__(*args, **kwargs)
        if queryset is not None:
            self.queryset = queryset
        else:
            self.queryset = self.QUERYSET
        self.paginate_by   = paginate_by or self.PAGINATE_BY
        self.model         = model or self.MODEL
        self.app_label     = app_label or self.APP_LABEL
        self.model_name    = model_name or self.MODEL_NAME
        self.fields        = fields or self.FIELDS
        self.mimetype      = mimetype or self.MIMETYPE
        self.lookup_kwargs = lookup_kwargs or self.LOOKUP_KWARGS
        self.ddinfo_class  = ddinfo_class or self.DDINFO_CLASS
        self.ddfield_class = ddfield_class or self.DDFIELD_CLASS
        if allow_empty is not None:
            self.allow_empty = allow_empty
        else:
            self.allow_empty = self.ALLOW_EMPTY
        self.template_object_name = template_object_name or self.TEMPLATE_OBJECT_NAME
        self.view_name     = view_name or self.VIEW_NAME

    def paginator(self, request, queryset = None, paginate_by = None, allow_empty = None, page = None):
        from django.core.paginator import Paginator, InvalidPage
        if queryset is None: queryset = self.queryset
        paginate_by = paginate_by or self.paginate_by
        allow_empty = allow_empty or self.allow_empty
        return Paginator(queryset, paginate_by, allow_empty_first_page=allow_empty)

    def page(self, request, page, pagename = 'page'):
        if not page:
            page = request.GET.get(pagename, 1)
        return page

    def __call__(self, request, url,
                 queryset = None,
                 fields = None,
                 paginate_by = None, page = None,
                 template_name = None, template_loader = None, extra_context = {},
                 login_required = None, context_processors = None,
                 mimetype = None,
                 lookup_kwargs = None,
                 ddinfo_class = None,
                 ddfield_class = None,
                 template_object_name = None,
                 view_name = None,
                 *args, **kwargs):

        from django.core.paginator import InvalidPage
        from softwarefabrica.django.common.models import get_sfapp_field, CommonModel
        from django.db.models.query import QuerySet

        logging.info("DDV.__call__(url:'%s', args:%s, kwargs:%s" % (url, repr(args), repr(kwargs)))

        if (request.method == 'GET') and (not request.path.endswith('/')):
            return HttpResponseRedirect(request.path + '/')

        model      = kwargs.get('model',      None)
        app_label  = kwargs.get('app_label',  None)
        model_name = kwargs.get('model_name', None)

        self.pre_call(request, url, queryset = queryset,
                      fields = fields,
                      paginate_by = paginate_by, page = page,
                      template_name = template_name, template_loader = template_loader,
                      extra_context = extra_context,
                      login_required = login_required,
                      context_processors = context_processors,
                      mimetype = mimetype, lookup_kwargs = lookup_kwargs,
                      ddinfo_class = ddinfo_class,
                      ddfield_class = ddfield_class,
                      template_object_name = template_object_name,
                      view_name = view_name,
                      *args, **kwargs)

        if queryset is None: queryset = self.queryset
        model              = model or self.model
        app_label          = app_label or self.app_label
        model_name         = model_name or self.model_name
        fields             = fields or self.fields
        paginate_by        = paginate_by or self.paginate_by
        template_name      = template_name or self.template_name
        template_loader    = template_loader or self.template_loader
        extra_context      = extra_context or {}
        login_required     = login_required or self.login_required
        context_processors = context_processors or self.context_processors
        mimetype           = mimetype or self.mimetype
        lookup_kwargs      = lookup_kwargs or self.lookup_kwargs
        ddinfo_class       = ddinfo_class or self.ddinfo_class
        ddfield_class      = ddfield_class or self.ddfield_class
        template_object_name = template_object_name or self.template_object_name
        view_name          = view_name or self.view_name

        if login_required and not request.user.is_authenticated():
            return self.redirect_to_login(request)
        if extra_context is None: extra_context = {}

        assert (queryset is not None) or (model is not None) or (app_label and model_name)

        if (app_label and model_name) and (model is None):
            model = self.lookup_model(app_label, model_name)

        assert (queryset is not None) or model

        if queryset is not None:
            assert isinstance(queryset, QuerySet)
            assert (model is None) or (model == queryset.model)
            model = queryset.model
            assert model

        if model is not None:
            assert issubclass(model, models.Model)
            assert (queryset is None) or (model == queryset.model)
            if queryset is None:
                queryset = QuerySet(model)
            app_label  = model._meta.app_label
            model_name = model._meta.object_name
            assert queryset is not None

        assert (queryset is not None)
        assert model

        if view_name is None:
            view_name = '%s-%s-drilldown' % (app_label, model_name)

        queryset = queryset._clone()

        if lookup_kwargs is not None:
            logging.info("lookup_kwargs:%s" % repr(lookup_kwargs))
            filter_kwargs = {}
            for k, v in lookup_kwargs.items():
                filter_kwargs[k] = v
                if k in kwargs:
                    filter_kwargs[k] = kwargs[k]
            logging.info("filter_kwargs:%s" % repr(filter_kwargs))
            queryset = queryset.filter(**filter_kwargs)

        if not self.check_auth(request, queryset = queryset, model = model):
            return self.perm_negated(request, queryset = queryset, model = model)

        # TODO: handle filtered querysets (we need to special-case pagination too)
        # queryset = self.filter_queryset(request, queryset = queryset, model = model)

        assert issubclass(model, models.Model)
        opts = model._meta
        assert isinstance(opts, models.options.Options)

        drilldown_fields = fields
        if issubclass(model, CommonModel):
            drilldown_fields = get_sfapp_field(model, 'drilldown_fields',
                                               get_sfapp_field(model, 'fields',
                                                               fields))
        if drilldown_fields is None:
            drilldown_fields = [f.name for f in opts.fields]

        ddinfo = ddinfo_class(request, url, queryset, drilldown_fields,
                              view_name, args, kwargs, ddfield_class)
        assert isinstance(ddinfo, DrillDownInfo)

        self.parse_url(ddinfo)
        self.filter_queryset(ddinfo)
        self.make_pivot_values(ddinfo)
        self.make_remaining_field_values(ddinfo)
        self.make_bread_crumbs(ddinfo)

        select_field = False
        select_value = False
        if ddinfo.pivot_field:
            select_value = True
        else:
            select_field = True
        if ddinfo.filtered_queryset.count() <= 1:
            select_field = False
            select_value = False

        paginator   = None
        page_obj    = None
        object_list = ddinfo.filtered_queryset
        is_paginated = False
        if paginate_by:
            paginator = self.paginator(request, ddinfo.filtered_queryset, paginate_by, self.allow_empty)
            page = self.page(request, page)
            try:
                page_number = int(page)
            except ValueError:
                if page == 'last':
                    page_number = paginator.num_pages
                else:
                    # Page is not 'last', nor can it be converted to an int.
                    raise Http404
            try:
                page_obj = paginator.page(page_number)
            except InvalidPage:
                raise Http404

            object_list  = page_obj.object_list
            is_paginated = True

        extra_context = self.apply_extra_context(extra_context, self.extra_context)
        c = self.get_context(request,
                             {'model'             : model,
                              'meta'              : model._meta,
                              'url'               : url,
                              'fields'            : drilldown_fields,
                              'ddinfo'            : ddinfo,
                              'used_fields'       : ddinfo.used_fields,
                              'remaining_fields'  : ddinfo.remaining_fields,
                              'pivot_field'       : ddinfo.pivot_field,
                              'pivot_field_values': ddinfo.pivot_field_values,
                              'select_field'      : select_field,
                              'select_value'      : select_value,
                              'found'             : ddinfo.filtered_queryset,
                              'count'             : ddinfo.filtered_queryset.count(),
                              '%s_list' % template_object_name: object_list,
                              '%s_count' % template_object_name: object_list.count(),
                              'paginator'         : paginator,
                              'page_obj'          : page_obj,
                              'is_paginated'      : is_paginated,
                              },
                             context_processors)
            
        c = self.apply_extra_context(c, extra_context)
        c = self._populate_context(c, request, model)
        c = self.populate_context(c, request, model)
        t = self.get_template(model, template_name, template_loader)
        response = self.get_response(t, c, mimetype)
        #self.populate_xheaders(request, response, model, object_id)
        return response

    def parse_url(self, ddinfo):
        assert isinstance(ddinfo, DrillDownInfo)
        url = ddinfo.url
        url = url.rstrip('/')
        url_comps = []
        if len(url) > 0:
            url_comps = url.split('/')
        ddinfo.url_components = url_comps

        pivot_field      = None
        pivot_field_name = None
        u_comps = url_comps
        while len(u_comps) >= 2:
            (field_name, encoded_value) = u_comps[:2]
            u_comps = u_comps[2:]
            #ddinfo.field_values[f] = DrilldownParamEncoder.Decode(v)
            value = DrilldownParamEncoder.Decode(encoded_value)
            field = ddinfo.opts.get_field(field_name)
            dd_field = ddinfo.ddfield_class(ddinfo, field, value)
            #ddinfo.field_values[field_name] = dd_field
            ddinfo.add_field(field_name, dd_field)
            ddinfo.used_fields.append(dd_field)
        if len(u_comps) > 0:
            assert len(u_comps) == 1
            pivot_field_name = u_comps[0]
        ddinfo.pivot_field_name = pivot_field_name
        if pivot_field_name:
            pivot_field = ddinfo.opts.get_field(pivot_field_name)
        ddinfo.pivot_field = pivot_field

        for field_name in ddinfo.drilldown_fields:
            if field_name not in ddinfo.field_values:
                ddinfo.remaining_field_names.append(field_name)
            else:
                # ManyToManyFields must always remain selectable
                dd_field = ddinfo.field_values[field_name]
                if isinstance(dd_field.field, models.ManyToManyField) and (field_name not in ddinfo.remaining_field_names):
                    ddinfo.remaining_field_names.append(field_name)

        return ddinfo

    def filter_queryset(self, ddinfo):
        import operator

        logging.debug("filter queryset")
        assert isinstance(ddinfo, DrillDownInfo)

        filtered_qs = ddinfo.queryset

        # filter on regular fields first (non-many-to-many)
        and_queries = [models.Q()]
        for field_name in ddinfo.field_values.keys():
            dd_fields = ddinfo.get_fields(field_name)
            assert (len(dd_fields) == 1) or isinstance(dd_fields[0].field, models.ManyToManyField)
            if isinstance(dd_fields[0].field, models.ManyToManyField):
                continue
            dd_field = dd_fields[0]
            cs = dd_field.construct_search()
            logging.debug("constructed search:%s" % cs)
            q = models.Q(**cs)
            and_queries.append(q)
        logging.debug("and_queries:%s" % repr(and_queries))
        filtered_qs = filtered_qs.filter(reduce(operator.and_, and_queries))

        # filter on many-to-many
        for field_name in ddinfo.field_values.keys():
            dd_fields = ddinfo.get_fields(field_name)
            if not isinstance(dd_fields[0].field, models.ManyToManyField):
                continue
            for dd_field in dd_fields:
                cs = dd_field.construct_search()
                logging.debug("m2m constructed search:%s" % cs)
                q = models.Q(**cs)
                filtered_qs = filtered_qs.filter(q)

        logging.debug("filtered qs objects:%s" % repr(filtered_qs))
        ddinfo.filtered_queryset = filtered_qs
        return filtered_qs

    @classmethod
    def MakeUrl(cls, model, view_name, field_values, pivot_field=None,
                kwargs=None):
        """
        Return a URL for the drill-down view, with initial filter set to
        (field, value) pairs in ``field_values``, and the optional pivot field
        to ``pivot_field``.
        ``field_values`` can also be a django.utils.datastructures.SortedDict
        """
        import urlparse
        from django.utils.encoding import force_unicode

        assert issubclass(model, models.Model)
        opts = model._meta
        assert isinstance(opts, models.options.Options)

        filter_url = ''
        for (f_name, f_value) in field_values.items():
            try:
                field = opts.get_field(f_name)
            except models.fields.FieldDoesNotExist:
                field = None
            if field:
                enc_value = DrilldownParamEncoder.Encode(_db_python_to_text(field, f_value))
            else:
                enc_value = force_unicode(f_value)
            if filter_url and (not filter_url.endswith('/')):
                filter_url = filter_url + '/'
            filter_url = urlparse.urljoin(filter_url, '%s/%s' % (f_name, enc_value))
        if pivot_field:
            if filter_url and (not filter_url.endswith('/')):
                filter_url = filter_url + '/'
            filter_url = urlparse.urljoin(filter_url, '%s' % pivot_field)
        if filter_url and (not filter_url.endswith('/')):
            filter_url = filter_url + '/'
        reverse_kwargs = dict(kwargs or {},
                              url = filter_url)
        url = reverse(view_name, kwargs=reverse_kwargs)
        return url

    def make_url(self, field_values, pivot_field=None, model=None, view_name=None,
                 kwargs=None):
        view_name = view_name or self.view_name
        model = model or self.model
        return self.MakeUrl(model=model, view_name=view_name,
                            field_values=field_values, pivot_field=pivot_field,
                            kwargs=kwargs)

    def make_pivot_values(self, ddinfo):
        import urlparse
        assert isinstance(ddinfo, DrillDownInfo)
        if not ddinfo.pivot_field:
            return
        base_url = ddinfo.url
        if not base_url.endswith('/'):
            base_url = base_url + '/'

        model = ddinfo.model
        opts  = ddinfo.opts

        if isinstance(ddinfo.pivot_field, models.ManyToManyField):
            rel_model = ddinfo.pivot_field.rel.to
            #logging.debug("rel_model:%s" % rel_model)
            rel_field_query_name = '%s__pk__in' % ddinfo.pivot_field.rel.related_name
            #logging.debug("rel_field_query_name:%s" % rel_field_query_name)
            qs_pks_records = ddinfo.filtered_queryset.values('pk').order_by('pk').distinct()
            qs_pks         = [r['pk'] for r in qs_pks_records]
            #logging.debug("qs_pks:%s" % qs_pks)
            pivot_field_objects = rel_model.objects.filter(**{rel_field_query_name: qs_pks}).distinct()
            pivot_field_keyvalues = [{ddinfo.pivot_field_name: o} for o in pivot_field_objects]
        else:
            pivot_field_keyvalues = ddinfo.filtered_queryset.values(ddinfo.pivot_field_name).order_by(ddinfo.pivot_field_name).distinct()
        pivot_field_values = []
        for kv in pivot_field_keyvalues:
            raw_value = kv[ddinfo.pivot_field_name]
            view_kwargs = dict(ddinfo.view_kwargs or {},
                               url = urlparse.urljoin(base_url, \
                                                      '%s' % DrilldownParamEncoder.Encode(_db_python_to_text(ddinfo.pivot_field, raw_value))))
            url = reverse(ddinfo.view_name,
                          kwargs=view_kwargs)
            item = ddinfo.ddfield_class(ddinfo    = ddinfo,
                                        db_field  = ddinfo.pivot_field,
                                        raw_value = raw_value,
                                        url       = url)
            count = ddinfo.filtered_queryset.filter(**{item.name: item.raw_value}).count()
            item.count = count
            pivot_field_values.append(item)
        ddinfo.pivot_field_values = pivot_field_values
        logging.info(u"pivot field values:%s" % repr(pivot_field_values))
        return self

    def make_remaining_field_values(self, ddinfo):
        import urlparse
        assert isinstance(ddinfo, DrillDownInfo)
        logging.debug("make_remaining_field_values view_kwargs:%s" % ddinfo.view_kwargs)
        for field_name in ddinfo.remaining_field_names:
            db_field = ddinfo.opts.get_field(field_name)
            view_kwargs = dict(ddinfo.view_kwargs,
                               url = urlparse.urljoin(ddinfo.url, field_name))
            item = ddinfo.ddfield_class(ddinfo    = ddinfo,
                                        db_field  = db_field,
                                        raw_value = None,
                                        use_value = False,
                                        url       = reverse(ddinfo.view_name,
                                                            kwargs=view_kwargs))
            if isinstance(db_field, models.ManyToManyField):
                rel_model = db_field.rel.to
                #logging.debug("rel_model:%s" % rel_model)
                rel_field_query_name = '%s__pk__in' % db_field.rel.related_name
                #logging.debug("rel_field_query_name:%s" % rel_field_query_name)
                qs_pks_records = ddinfo.filtered_queryset.values('pk').order_by('pk').distinct()
                qs_pks         = [r['pk'] for r in qs_pks_records]
                #logging.debug("qs_pks:%s" % qs_pks)
                rel_values = rel_model.objects.filter(**{rel_field_query_name: qs_pks}).distinct()
                #logging.debug("rel_values:%s" % rel_values)
                count = rel_values.count()
            else:
                # we use len() instead of .count() here, because .count() would ignore NULL rows
                count = len(ddinfo.filtered_queryset.values(item.name).order_by(item.name).distinct())
            item.count = count
            if count > 0:
                ddinfo.remaining_fields.append(item)
        return self

    def make_bread_crumbs(self, ddinfo):
        from django.utils.datastructures import SortedDict
        assert isinstance(ddinfo, DrillDownInfo)

        ddinfo.bread_crumbs_root = self.make_url({},
                                                 model     = ddinfo.model,
                                                 view_name = ddinfo.view_name,
                                                 kwargs    = ddinfo.view_kwargs)

        field_values = SortedDict()
        for dd_field in ddinfo.used_fields:
            assert isinstance(dd_field, DrillDownField)
            url_field = self.make_url(field_values, pivot_field = dd_field.name,
                                      model = ddinfo.model, view_name = ddinfo.view_name,
                                      kwargs = ddinfo.view_kwargs)
            field_values[dd_field.name] = dd_field.raw_value
            url_value = self.make_url(field_values,
                                      model = ddinfo.model, view_name = ddinfo.view_name,
                                      kwargs = ddinfo.view_kwargs)
            ddinfo.bread_crumbs.append({'field'    : dd_field.field,
                                        'name'     : dd_field.name,
                                        'value'    : dd_field.value,
                                        'url_field': url_field,
                                        'url_value': url_value,})
        return self

    def lookup_model(self, app_label, model_name):
        """
        Return the ``model`` class given ``app_label`` and ``model_name``.
        """
        from django.contrib.contenttypes.models import ContentType
        if not (app_label and model_name):
            raise GenericViewError("%s view must be called with either a model class or an app_label/model_name."
                                   % (self.__class__.__name__,))
        try:
            c_type = ContentType.objects.get(app_label=app_label, model=model_name)
            return c_type.model_class()
        except ObjectDoesNotExist:
            raise Http404("No model found for %s/%s" % (app_label, model_name))

    def get_template(self, model = None, template_name = None, template_loader = None):
        """
        Return the template to use.
        """
        model           = model or self.c_model
        template_name   = template_name or self.template_name
        template_loader = template_loader or self.template_loader

        app_label   = model._meta.app_label
        object_name = model._meta.object_name.lower()
        template_name = template_name or ("%s/%s_drilldown.html" % (app_label, object_name),
                                          "%s/%s_browse.html" % (app_label, object_name),
                                          "%s/object_drilldown.html" % app_label,
                                          "%s/object_browse.html" % app_label,
                                          "%s_drilldown.html" % object_name,
                                          "%s_browse.html" % object_name,
                                          "object_drilldown.html",
                                          "object_browse.html",
                                          "drilldown/object_drilldown.html",
                                          "drilldown/object_browse.html")
        return super(DrillDownView, self).get_template(model, template_name, template_loader)

class GenericDrillDownView(DrillDownView):
    VIEW_NAME = "drilldown-generic-drilldown"

drilldown         = DrillDownView()
generic_drilldown = GenericDrillDownView()
