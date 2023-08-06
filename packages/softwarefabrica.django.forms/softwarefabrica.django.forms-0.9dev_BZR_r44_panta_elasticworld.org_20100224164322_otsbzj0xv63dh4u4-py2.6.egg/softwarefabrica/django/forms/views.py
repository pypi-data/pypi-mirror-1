# views.py
#
# Copyright (C) 2010 Marco Pantaleoni. All rights reserved
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

from django.http import HttpRequest, HttpResponse
from django.db.models import get_model
from django.utils.encoding import force_unicode
from django.conf import settings

from softwarefabrica.django.utils.viewshelpers import render_to_response, json_response

import logging

def ajax_cascade_select(request):
    """
    AJAX - cascaded select support

    View that handles AJAX calls performed by SelectCascadeField and
    SelectCascadePopupField (and the associated widgets).

    Associated to the named url 'forms-ajax-cascade-select'.
    """
    assert isinstance(request, HttpRequest)
    #logging.debug(request)
    master_app        = request.REQUEST.get('master_app', request.REQUEST.get('app', ''))
    master_model_name = request.REQUEST['master_model']
    master_pk         = request.REQUEST['master_id']
    slave_app         = request.REQUEST.get('slave_app', master_app)
    slave_model_name  = request.REQUEST['slave_model']
    slave_pivot_field = str("%s" % request.REQUEST.get('slave_pivot', 'master'))
    #logging.debug("Master model:%s PK:%s  - slave:%s" % (master_model_name, master_pk, slave_model_name))
    master_model = get_model(master_app, master_model_name)
    slave_model  = get_model(slave_app, slave_model_name)
    slave_objects = slave_model.objects.filter(**{slave_pivot_field: master_pk})
    data = [dict(pk = obj.pk, text=force_unicode(obj)) for obj in slave_objects]
    #return json_response(request, slave_objects)
    return json_response(request, data)
