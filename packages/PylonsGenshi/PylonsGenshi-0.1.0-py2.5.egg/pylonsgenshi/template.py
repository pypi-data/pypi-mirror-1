# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: template.py 51 2008-01-03 20:14:08Z s0undt3ch $
# =============================================================================
#             $URL: http://pastie.ufsoft.org/svn/sandbox/PylonsGenshi/pylonsgenshi/template.py $
# $LastChangedDate: 2008-01-03 20:14:08 +0000 (Thu, 03 Jan 2008) $
#             $Rev: 51 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2007 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

from paste.script.templates import Template

class PylonsGenshiTemplate(Template):
    _template_dir = 'templates/default'
    summary = 'Pylons+Genshi template'
    egg_plugins = ['Pylons', 'Genshi']

    def pre(self, command, output_dir, vars):
        """Called before template is applied."""
        package_logger = vars['package']
        if package_logger == 'root':
            # Rename the app logger in the rare case a project is named 'root'
            package_logger = 'app'
        vars['package_logger'] = package_logger

