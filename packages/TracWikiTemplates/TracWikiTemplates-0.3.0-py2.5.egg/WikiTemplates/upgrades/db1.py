# -*- coding: iso8859-15 -*-

# =============================================================================
# $Id: db1.py 55 2008-02-10 05:39:31Z s0undt3ch $
# =============================================================================
#             $URL: http://wikitemplates.ufsoft.org/svn/trunk/WikiTemplates/upgrades/db1.py $
# $LastChangedDate: 2008-02-10 05:39:31Z $
#             $Rev: 55 $
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

import os.path
import os
import sys
from pkg_resources import resource_filename

from trac.core import TracError
from trac.db import DatabaseManager
from WikiTemplates.db_schema import version as templates_version, schema

def do_upgrade(env, ver, db):
    print 'Upgrading WikiTemplates plugin...'

    try:
        cursor = db.cursor()
        db_backend, _ = DatabaseManager(env)._get_connector()

        try:
            QUERY = "INSERT INTO system VALUES (%s,%s)"
            cursor.execute(QUERY, ('templates_version', templates_version))
            ADD_PERMS = True
        except:
            # This next step bellow really ain't necessary, cuz this will be
            # the first time the database will be created
            QUERY = "UPDATE system SET value=%s WHERE name=%s"
            cursor.execute(QUERY, (templates_version, 'templates_version'))
        print ' * Creating database table...',
        try:
            for table in schema:
                for stmt in db_backend.to_sql(table):
                    env.log.debug(stmt)
                    cursor.execute(stmt)
            print ' done'
        except Exception, e:
            print ' failed'
            env.log.error(e, exc_info=1)
            db.rollback()
            raise TracError, e

        # Include default templates
        print ' * Adding default templates to database...',
        try:
            import time
            deflt_templates_dir = resource_filename('WikiTemplates',
                                                    'DefaultTemplates')
            for tpl in os.listdir(deflt_templates_dir):
                env.log.debug("Template: '%s'" % tpl)
                f = open(os.path.join(deflt_templates_dir, tpl))
                body = f.read()
                f.close()

                QUERY = 'INSERT INTO templates VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
                vals = (tpl,                        # name
                        1,                          # version
                        int(time.time()),           # time
                        'Wiki Templates Plugin',    # author
                        '',                         # ipnr
                        body,                       # contents
                        '',                         # comment
                        0                           # read-only
                       )
                cursor.execute(QUERY, vals)

            env.log.debug('First time installing Trac Wiki ' + \
                               'Templates plugin version >= 0.3')
            print 'done'
        except Exception, e:
            print 'failed'
            env.log.debug('Failed to include default templates')
            env.log.error(e, exc_info=1)
            db.rollback()
            raise TracError, e
        print ' * Including default permissions...',
        try:
            for perm in ('VIEW', 'CREATE', 'MODIFY'):
                QUERY = "INSERT INTO permission VALUES (%s,%s)"
                vals = ('anonymous', 'TEMPLATES_' + perm)
                cursor.execute(QUERY, vals)
            print ' done'
        except Exception, e:
            print ' failed'
            env.log.debug('Failed to include default templates '
                          'permissions')
            env.log.error(e, exc_info=1)
            db.rollback()
            raise TracError, e

        # Migrate old templates to our new table
        print ' * Migrating old templates',
        try:
            QUERY = "SELECT * FROM wiki WHERE name LIKE '%templates/%'"
            cursor.execute(QUERY)
            rows = cursor.fetchall()
            env.log.debug("Found %d < 0.3 templates", len(rows))
            for row in rows:
                try:
                    QUERY = 'INSERT INTO templates ' + \
                            'VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
                    VALS = (row[0].split('/').pop(1),   # name
                            int(row[1]),                # version
                            int(row[2]),                # time
                            row[3],                     # author
                            row[4],                     # ipnr
                            row[5].replace('[[Image(wiki:templates/', '[[Image(templates:'),                     # text
                            row[6],                     # comment
                            int(row[7])                 # readonly
                            )
                    cursor.execute(QUERY, VALS)
                    sys.stdout.write('.')
                except Exception, e:
                    print ' failed'
                    env.log.error(e, exc_info=1)
                    db.rollback()
                    raise TracError, e
            print ' done'
        except Exception, e:
            print ' No Wiki templates from versions < 0.3 found.'
            env.log.debug('No wiki templates from versions < 0.3 found.')
        print ' * Deleting old templates...',
        try:
            # Remove those templates under the 'templates/' sub-wiki
            env.log.debug("Deleting old templates from the " + \
                          "'templates/' sub-wiki")
            QUERY = "DELETE FROM wiki WHERE name LIKE '%templates/%'"
            env.log.debug(QUERY)
            cursor.execute(QUERY)
            print ' done'
        except Exception, e:
            print ' failed'
            env.log.debug("Failed to delete old templates from " + \
                          "the 'templates/' sub-wiki")
            env.log.error(e, exc_info=1)
            db.rollback()
            raise TracError, e
        print ' * Migrating attachments from versions < 0.3 ...',
        try:
            query = "SELECT * FROM attachment WHERE id LIKE '%templates/%'"
            cursor.execute(query)
            rows = cursor.fetchall()
            if not rows:
                print 'No attachments found'
            else:
                try:
                    query = "SELECT * FROM attachment WHERE id LIKE '%templates/%'"
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    for row in rows:
                        col = []
                        query = """UPDATE attachment SET type=%s, id=%s WHERE
                        filename=%s AND size=%s AND time=%s AND description=%s AND
                        author=%s AND ipnr=%s"""
                        col.append(u'templates')
                        col.append(row[1].split('/').pop(1))
                        col.append(row[2])
                        col.append(row[3])
                        col.append(row[4])
                        col.append(row[5])
                        col.append(row[6])
                        col.append(row[7])
                        cursor.execute(query, col)
                        sys.stdout.write('.')
                    print ' done'
                except Exception, e:
                    print ' failed'
                    db.rollback()
                    env.log.error(e, exc_info=1)
                    raise TracError, e
                # Move attachements to the new location
                try:
                    print ' * Moving attachements to new dir',
                    from shutil import move, copytree
                    move(os.path.join(env.path, 'attachments/wiki/templates'),
                         os.path.join(env.path, 'attachments/templates'))
                    print ' done'
                    print '  * You should confirm that the attachments have ' + \
                            'the permissions correctly set.'
                except Exception, e:
                    print ' failed'
                    env.log.error(e, exc_info=1)
                    raise TracError, e
        except:
            pass

        db.commit()

    except Exception, e:
        db.rollback()
        env.log.error(e, exc_info=1)
        raise TracError, e
