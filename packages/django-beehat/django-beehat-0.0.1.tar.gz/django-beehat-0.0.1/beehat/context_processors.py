# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 John Paulett (john -at- paulett.org)
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

from mercurial import hg, ui
from django.conf import settings

def vcs(request):
    """Provides template tags for information about a Mercurial repository.
    
    Installation:

     * Install mercurial (requires patch for mod_wsgi:
       pip install -e hg+http://bitbucket.org/johnpaulett/hg-stable-custom/#egg=mercurial
     * Add `beehat.context_processors.vcs` to the `TEMPLATE_CONTEXT_PROCESSORS`
       in settings.py
     * Optionally, in settings.py define `REPO_DIR` as path to repository root.
       Defaults to '.'
     * Place {{ rev }} and {{ tag }} template tags in your template
    """
    repo_dir = settings.REPO_DIR if hasattr(settings, 'REPO_DIR') else '.'
    repo = hg.repository(ui.ui(), repo_dir)
    ctx = repo.changectx(repo.changelog.tip())
    return {'tag': ctx.tags()[0],
            'rev': ctx.rev()}
