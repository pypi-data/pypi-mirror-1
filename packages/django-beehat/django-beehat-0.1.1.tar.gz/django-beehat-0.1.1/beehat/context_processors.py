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
    """Provide template tags for information about a Mercurial repository.

    Useful if you wish to display the current version of the code. Requires the
    template to be generated with a :class:`django.template.RequestContext` object.
    Provides two template tags, ``rev`` and ``tag``.

    From :file:`settings.py` reads the ``REPO_DIR`` variable (defaults to ``.``),
    which specifies the root of the Mercurial repository.
    """
    repo_dir = settings.REPO_DIR if hasattr(settings, 'REPO_DIR') else '.'
    repo = hg.repository(ui.ui(), repo_dir)
    ctx = repo.changectx(repo.changelog.tip())
    return {'tag': ctx.tags()[0],
            'rev': ctx.rev()}
