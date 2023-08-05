# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: templating.py 51 2008-01-03 20:14:08Z s0undt3ch $
# =============================================================================
#             $URL: http://pastie.ufsoft.org/svn/sandbox/PylonsGenshi/pylonsgenshi/templating.py $
# $LastChangedDate: 2008-01-03 20:14:08 +0000 (Thu, 03 Jan 2008) $
#             $Rev: 51 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2007 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

import os
import pylons
from genshi.filters import Translator
from genshi.template import TemplateLoader, Context

import logging

log = logging.getLogger(__name__)

def template_loaded(template):
    template.filters.insert(0, Translator(pylons.i18n.ugettext))

loader = TemplateLoader(
    search_path = pylons.config['pylons.paths']['templates'],
    auto_reload = True,
    callback = template_loaded)

def _update_names(ns):
    """Return a dict of Pylons vars and their respective objects updated
    with the ``ns`` dict."""
    d = dict(
        c=pylons.c._current_obj(),
        g=pylons.g._current_obj(),
        h=pylons.config.get('pylons.h') or pylons.h._current_obj(),
        render=render,
        request=pylons.request._current_obj(),
        translator=pylons.translator._current_obj(),
        ungettext=pylons.i18n.ungettext,
        _=pylons.i18n._,
        N_=pylons.i18n.N_
        )

    # If the session was overriden to be None, don't populate the session
    # var
    if pylons.config['pylons.environ_config'].get('session', True):
        d['session'] = pylons.session._current_obj()
    d.update(ns)
    log.debug("Updated render namespace with pylons vars: %s", d)
    return Context(**d)

def render(filename, method='xhtml', encoding='utf-8', **options):
    template = loader.load(filename.replace('.', os.sep)+'.html',
                           encoding=encoding)
    if not options:
        options = {}
    engine_dict = Context() #s_update_names(options)
    return template.generate(engine_dict)
