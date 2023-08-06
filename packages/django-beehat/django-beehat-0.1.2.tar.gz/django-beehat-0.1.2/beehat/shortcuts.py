# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 John Paulett (john -at- paulett.org)
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

from django.shortcuts import render_to_response
from django.template import RequestContext

def render_response(request, *args, **kwargs):
    """Adds the RequestContext to django.shortcuts.render_to_response."""
    kwargs['context_instance'] = RequestContext(request)
    return render_to_response(*args, **kwargs)
