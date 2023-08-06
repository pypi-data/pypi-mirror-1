# -*- coding: iso8859-15 -*-

# =============================================================================
# $Id: db_schema.py 41 2006-04-25 08:48:35Z s0undt3ch $
# =============================================================================
#             $URL: http://wikitemplates.ufsoft.org/svn/trunk/WikiTemplates/db_schema.py $
# $LastChangedDate: 2006-04-25 08:48:35Z $
#             $Rev: 41 $
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

from trac.core import *
from trac.db_default import Table, Column, Index

# Version of WikiTemplates Schema
version = 1


# A copy of trac's wiki dtabase schema since templates will be a subwiki
# with a templates/ handler.
schema = [
    Table('templates', key=('name', 'version'))[
        Column('name'),
        Column('version', type='int'),
        Column('time', type='int'),
        Column('author'),
        Column('ipnr'),
        Column('text'),
        Column('comment'),
        Column('readonly', type='int'),
        Index(['time'])]
]
