# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: helpers.py 53 2008-01-03 20:46:35Z s0undt3ch $
# =============================================================================
#             $URL: http://pastie.ufsoft.org/svn/sandbox/PylonsGenshi/pylonsgenshi/helpers.py $
# $LastChangedDate: 2008-01-03 20:46:35 +0000 (Thu, 03 Jan 2008) $
#             $Rev: 53 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2007 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

from webhelpers import *
try:
    from minwebhelpers import *
    _HAVE_MINWEBHELPERS = True
except ImportError:
    _HAVE_MINWEBHELPERS = False
from genshi.builder import tag
from genshi.core import Markup as _Markup

def _wrap_helpers(localdict):
    def helper_wrapper(func):
        def wrapped_helper(*args, **kw):
            return _Markup(func(*args, **kw))
        wrapped_helper.__name__ = func.__name__
        return wrapped_helper
    for name, func in localdict.iteritems():
         if not callable(func) or not \
             func.__module__.startswith('webhelpers.rails'):
             continue
         localdict[name] = helper_wrapper(func)
    if _HAVE_MINWEBHELPERS:
        localdict['javascript_include_tag'] = \
                                        helper_wrapper(javascript_include_tag)
        localdict['stylesheet_link_tag'] = helper_wrapper(stylesheet_link_tag)

_wrap_helpers(locals())

__all__ = [__name for __name in locals().keys() if not __name.startswith('_') ]
