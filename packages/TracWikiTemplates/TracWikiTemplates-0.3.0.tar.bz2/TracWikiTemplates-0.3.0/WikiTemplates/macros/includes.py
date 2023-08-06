# -*- coding: iso8859-15 -*-

# =============================================================================
# $Id: includes.py 48 2006-09-17 17:26:10Z s0undt3ch $
# =============================================================================
#             $URL: http://wikitemplates.ufsoft.org/svn/trunk/WikiTemplates/macros/includes.py $
# $LastChangedDate: 2006-09-17 17:26:10Z $
#             $Rev: 48 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================

###############################################################################
#                                                                             # 
# Copyright © 2006 by Pedro Algarvio                                          # 
#                                                                             #
# This program is free software; you can redistribute it and/or modify it     #
# under the terms of the GNU General Public License as published by the Free  #
# Software Foundation; either version 2 of the License, or (at your option)   #
# any later version.                                                          #
# This program is distributed in the hope that it will be useful, but WITHOUT #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       #
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for   #
# more details.                                                               #
#                                                                             #
###############################################################################

# =============================================================================
# vim: set tabstop=4
# vim: set shiftwidth=4
#
# Display a red square on the 80th char so we can easely limit line width to a
# max of 79 chars, the way it should be.
# vim: autocmd BufEnter * match Error /\%80v/
# =============================================================================

import inspect
from trac.core import *
from trac.wiki.api import IWikiMacroProvider
from trac.wiki.formatter import wiki_to_html
from WikiTemplates.model import WikiTemplate
from WikiTemplates.errors import TemplatesError


class IncludesMacro(Component):
    """Grab a wiki page and include it's full contents inside another.
    To use:
        {{{
        [[Include(WikiPageNameToInclude)]]
        }}}
    [[BR]]
    For more information go to:
        http://wikitemplates.ufsoft.org"""
    implements(IWikiMacroProvider)

    # IWikiMacroProvider methods
    def get_macros(self):
        yield "Include"

    def get_macro_description(self, name):
        return inspect.getdoc(IncludesMacro)

    def render_macro(self, req, name, content):
        if not content:
            raise TracError, "Nothing was passed"

        # First strip args passed
        args = [arg.strip() for arg in content.split('|')]
        if len(args) != 1:
            self.env.log.debug('ARGS PASSED TO INCLUDE: %r', args)
            return TemplatesError(
                "The 'Include' macro doesn't support arguments.\n"
                "It exists to simply include another wiki page into "
                "the current one.\nClick your browser's back button "
                "and correct the error, or check the edit box "
                "below if present.")

        if args[0].startswith('http://') or args[0].startswith('https://'):
            import urllib
            try:
                webpage = urllib.urlopen(args[0])
                html = webpage.read()
                webpage.close()
                self.env.log.debug('INCLUDE CONTENTS: %r', html)
                return html
            except Exception, e:
                return TracError, e
        else:
            contents = WikiTemplate(self.env, args.pop(0), table="wiki")
            return wiki_to_html(contents.text, self.env, req)
