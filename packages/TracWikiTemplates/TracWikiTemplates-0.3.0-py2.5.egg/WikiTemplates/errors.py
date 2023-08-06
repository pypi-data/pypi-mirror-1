# -*- coding: iso8859-15 -*-

# =============================================================================
# $Id: errors.py 38 2006-04-20 18:34:22Z s0undt3ch $
# =============================================================================
#             $URL: http://wikitemplates.ufsoft.org/svn/trunk/WikiTemplates/errors.py $
# $LastChangedDate: 2006-04-20 18:34:22Z $
#             $Rev: 38 $
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

from trac.util import escape

def TemplatesError(message):
    """
    Class to output a pretty error.
    """
    html = """
<div class="system-message">
<strong>Wiki Templates Error:</strong>
<pre>%(message)s</pre>
</div>
""" % {'message': escape(message)}
    return html
