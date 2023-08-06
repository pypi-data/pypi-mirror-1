# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 John Paulett (john -at- paulett.org)
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
from django.template import Context, loader, RequestContext

def render(template, context, request=None):
    """Help function for rendering a template given a context.
    Useful in custom template tags.  The template is the typical path to the
    template file (e.g. 'registration/login.html').  The context is a dictionary
    of data to provide the template.

    If the optional HttpRequest object is provided, the function will render
    the template using a django.template.RequestContext.
    """
    
    t = loader.get_template(template)
    if request is None:
        c = Context(context)
    else:
        c = RequestContext(context)
    return t.render(c)
