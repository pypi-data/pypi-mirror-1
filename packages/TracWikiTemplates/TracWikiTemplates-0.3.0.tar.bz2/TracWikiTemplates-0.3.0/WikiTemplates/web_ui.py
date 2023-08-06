# -*- coding: utf-8 -*-
#
# Copyright (C) 2003-2006 Edgewall Software
# Copyright (C) 2003-2005 Jonas Borgström <jonas@edgewall.com>
# Copyright (C) 2004-2005 Christopher Lenz <cmlenz@gmx.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://trac.edgewall.org/wiki/TracLicense.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://trac.edgewall.org/log/.
#
# Author: Jonas Borgström <jonas@edgewall.com>
#         Christopher Lenz <cmlenz@gmx.de>

from trac import __version__
if [int(x.split('dev')[0]) for x in __version__.split('.')][1] > 10:
    raise ImportError("Trac > 0.10.x not supported")

import os
import re
import StringIO

from trac.attachment import attachments_to_hdf
from trac.core import *
from trac.perm import IPermissionRequestor
from trac.Search import ISearchSource, search_to_sql, shorten_result
from trac.Timeline import ITimelineEventProvider
from trac.util import get_reporter_id
from trac.util.datefmt import format_datetime, pretty_timedelta
from trac.util.html import html, Markup
from trac.util.text import shorten_line, to_unicode
from trac.versioncontrol.diff import get_diff_options, hdf_diff
from trac.web.chrome import add_link, add_stylesheet, add_script
from trac.web.chrome import INavigationContributor, ITemplateProvider
from trac.web import HTTPNotFound, IRequestHandler
from trac.wiki.api import IWikiPageManipulator, WikiSystem
from trac.wiki.formatter import wiki_to_html, wiki_to_oneliner
from trac.mimeview.api import Mimeview, IContentConverter

from WikiTemplates.model import WikiTemplate
from WikiTemplates.errors import TemplatesError
from WikiTemplates.attachment import Attachment, AttachmentModule

try:
    from ctxtnavadd.api import ICtxtnavAdder
    IMPLEMENTS = [INavigationContributor, IPermissionRequestor, IRequestHandler,
                  ITimelineEventProvider, ISearchSource, ITemplateProvider,
                  ICtxtnavAdder]
except ImportError:
    IMPLEMENTS = [INavigationContributor, IPermissionRequestor, IRequestHandler,
                  ITimelineEventProvider, ISearchSource, ITemplateProvider]


class InvalidTemplatePage(TracError):
    """Exception raised when a Wiki page fails validation."""


class WikiTemplatesModule(Component):

    implements(*IMPLEMENTS)

    page_manipulators = ExtensionPoint(IWikiPageManipulator)

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        from pkg_resources import resource_filename
        resource_dir = resource_filename(__name__, 'htdocs')
        return [('templates', resource_dir)]

    def get_templates_dirs(self):
        from pkg_resources import resource_filename
        resource_dir = resource_filename(__name__, 'templates')
        return [resource_dir]

    # INavigationContributor methods

    def get_active_navigation_item(self, req):
        return 'templates'

    def get_navigation_items(self, req):
        evil_js = '/'.join(['templates','js','wikitemplates.js'])
        add_script(req, evil_js)

        if not req.perm.has_permission('TEMPLATES_VIEW') or not \
           req.perm.has_permission('TEMPLATES_ADMIN') or not \
           self.env.is_component_enabled(
               'wikitemplates.macros.templates.templatesmacro'):
            return

        yield ('mainnav', 'templates',
               html.A('Wiki Templates',
                      href=req.href.templates(),
                      accesskey=9, id='templatesbtn'))

    # ICtxtnavAdder methods
    def match_ctxtnav_add(self, req):
        if not req.perm.has_permission('TEMPLATES_VIEW') or not \
           self.env.is_component_enabled(
               'wikitemplates.macros.templates.templatesmacro'):
            return False
        self._add_js(req,self._make_js(req))
        return len(req.path_info) <= 1 or req.path_info == '/' or \
                req.path_info.startswith('/wiki') or \
                req.path_info.startswith('/templates')

    def get_ctxtnav_adds(self, req):
        yield (req.href.templates(), 'Wiki Templates Index')

    # IPermissionRequestor methods

    def get_permission_actions(self):
        actions = [
            'TEMPLATES_CREATE',
            'TEMPLATES_DELETE',
            'TEMPLATES_MODIFY',
            'TEMPLATES_VIEW'
        ]
        return actions + [('TEMPLATES_ADMIN', actions)]

    # IRequestHandler methods

    def match_request(self, req):
        match = re.match(r'^/templates(?:/(.*))?', req.path_info)
        if match:
            if match.group(1):
                req.args['page'] = match.group(1)
                self.env.log.debug("Page Match: '%s'", match.group(1))
                self.env.log.debug("Page Match req.args: '%s'",
                                   to_unicode(req.args['page']))
            else:
                req.args['page'] = 'TemplatesIndex'
                self.env.log.debug("Index Match: '%s'",
                                   to_unicode(req.args['page']))
            return True

    def process_request(self, req):
        if req.method == 'POST':
            action = req.args.get('action', 'create')
            if action == 'create':
                redir = req.args.get('new_tpl_name')
                req.args['action'] = 'edit'
                req.redirect(self.env.href.templates(redir))

        action = req.args.get('action', 'view')
        pagename = req.args.get('page', 'TemplatesIndex')
        version = req.args.get('version')

        db = self.env.get_db_cnx()
        cursor = db.cursor()
        req.hdf['templates_base_url'] = self.env.href.templates()
        # Query our DB for the template previews
        if pagename == 'TemplatesIndex':
            # Include all latest versions of every template
            # to show on the templates index
            QUERY = """SELECT name, text from templates WHERE
            version=(SELECT max(t2.version) FROM templates t2 WHERE
            name=t2.name) ORDER BY name ASC"""
            cursor.execute(QUERY)
            req.hdf['templates.showform'] = 1
        else:
            # Include only the latest verion of the template
            # being called.
            QUERY = """SELECT name, text FROM templates WHERE name=%s
            ORDER BY version DESC LIMIT 1"""
            cursor.execute(QUERY, (pagename,))
        templates = cursor.fetchall()
        previews = []
        # REGEX for our variables defenitions {{n}}, n being a digit
        args_re = re.compile(r'\{\{\d+\}\}')
        try:
            for template in templates:
                name = template[0]
                contents = template[1]
                # Dont include the TemplatesIndex
                if name != 'TemplatesIndex':
                    try:
                        # Substitute the var defenitions found on template
                        # by bogus var to get a "real" preview
                        for i in range(1, len(args_re.findall(contents)) + 1):
                            contents = contents.replace('{{%d}}' % i,
                                                        'argument_%d' % i)
                        self.env.log.debug('Replace Results: "%s"' % contents)
                    except:
                        self.env.log.debug('No variables replacing needed.')
                    # Append the dict to the previews list
                    previews.append({'name': name,
                                     'contents': wiki_to_html(contents,
                                                              self.env, req)})
            # Assign our previews list to trac HDF
            req.hdf['previews'] = previews
            self.env.log.debug('TemplatesIndex List: "%s"' % previews)
        except Exception, e:
            # Aparently no entry was found on db, maybe it's a new template,
            # so, we don't include any preview, of course
#            self.env.log.debug("No previous record of '%s' found on DB.")
            self.env.log.debug(e)

        self.env.log.debug('Template Name: %s', pagename)

        # Continue normal wiki behaviour
        if pagename.endswith('/'):
            req.redirect(req.href.templates(pagename.strip('/')))

        db = self.env.get_db_cnx()
        page = WikiTemplate(self.env, pagename, version, db)

        add_stylesheet(req, 'common/css/wiki.css')
        add_stylesheet(req, 'templates/css/wikitemplates.css')

        if req.method == 'POST':
            if action == 'edit':
                latest_version = WikiTemplate(
                    self.env, pagename, None, db).version
                if req.args.has_key('cancel'):
                    req.redirect(req.href.templates(page.name))
                elif int(version) != latest_version:
                    action = 'collision'
                    self._render_editor(req, db, page)
                elif req.args.has_key('preview'):
                    action = 'preview'
                    self._render_editor(req, db, page, preview=True)
                else:
                    self._do_save(req, db, page)
            elif action == 'delete':
                self._do_delete(req, db, page)
            elif action == 'diff':
                get_diff_options(req)
                req.redirect(req.href.templates(
                    page.name, version=page.version,
                    old_version=req.args.get('old_version'), action='diff'))
        elif action == 'delete':
            self._render_confirm(req, db, page)
        elif action == 'edit':
            self._render_editor(req, db, page)
        elif action == 'diff':
            self._render_diff(req, db, page)
        elif action == 'history':
            self._render_history(req, db, page)
        else:
            format = req.args.get('format')
            if format:
                Mimeview(self.env).send_converted(req, 'text/x-trac-wiki',
                                                  page.text, format, page.name)
            self._render_view(req, db, page)

        req.hdf['templates.action'] = action
        req.hdf['templates.current_href'] = req.href.templates(page.name)
        return 'WikiTemplates.cs', None

    # ITimelineEventProvider methods

    def get_timeline_filters(self, req):
        if req.perm.has_permission('TEMPLATES_VIEW'):
            yield ('templates', 'Wiki Templates Changes')

    def get_timeline_events(self, req, start, stop, filters):
        if 'templates' in filters:
            template = WikiSystem(self.env)
            format = req.args.get('format')
            href = format == 'rss' and req.abs_href or req.href
            db = self.env.get_db_cnx()
            cursor = db.cursor()
            cursor.execute("SELECT time,name,comment,author,version "
                           "FROM templates WHERE time>=%s AND time<=%s",
                           (start, stop))
            for t,name,comment,author,version in cursor:
                title = Markup('<em>%s</em> wiki template edited by %s',
                               template.format_page_name(name), author)
                diff_link = html.A('diff', href=href.templates(
                                    name, action='diff', version=version))
                if format == 'rss':
                    comment = wiki_to_html(comment or '--', self.env, req, db,
                                           absurls=True)
                else:
                    comment = wiki_to_oneliner(comment, self.env, db,
                                               shorten=True)
                if version > 1:
                    comment = Markup('%s (%s)', comment, diff_link)
                yield 'templates', href.templates(name), title, t, author, comment

            # Attachments
            def display(id):
                return Markup('ticket ', html.EM('#', id))
            att = AttachmentModule(self.env)
            for event in att.get_timeline_events(req, db, 'templates', format,
                                                 start, stop,
                                                 lambda id: html.EM(id)):
                yield event

    # Internal methods

    def _set_title(self, req, page, action):
        title = name = WikiSystem(self.env).format_page_name(page.name)
        if action:
            title += ' (%s)' % action
        req.hdf['templates.page_name'] = name
        req.hdf['title'] = title
        return title

    def _do_delete(self, req, db, page):
        if page.readonly:
            req.perm.assert_permission('TEMPLATES_ADMIN')
        else:
            req.perm.assert_permission('TEMPLATES_DELETE')

        if req.args.has_key('cancel'):
            req.redirect(req.href.templates(page.name))

        version = int(req.args.get('version', 0)) or None
        old_version = int(req.args.get('old_version', 0)) or version

        if version and old_version and version > old_version:
            # delete from `old_version` exclusive to `version` inclusive:
            for v in range(old_version, version):
                page.delete(v + 1, db)
        else:
            # only delete that `version`, or the whole page if `None`
            page.delete(version, db)
        db.commit()

        if not page.exists:
            req.redirect(req.href.templates())
        else:
            req.redirect(req.href.templates(page.name))

    def _do_save(self, req, db, page):
        if page.readonly:
            req.perm.assert_permission('TEMPLATES_ADMIN')
        elif not page.exists:
            req.perm.assert_permission('TEMPLATES_CREATE')
        else:
            req.perm.assert_permission('TEMPLATES_MODIFY')

        page.text = req.args.get('text')
        if req.perm.has_permission('TEMPLATES_ADMIN'):
            # Modify the read-only flag if it has been changed and the user is
            # TEMPLATES_ADMIN
            page.readonly = int(req.args.has_key('readonly'))

        # Give the manipulators a pass at post-processing the page
        for manipulator in self.page_manipulators:
            for field, message in manipulator.validate_wiki_page(req, page):
                if field:
                    raise InvalidTemplatePage("The Template page field %s is invalid: %s"
                                          % (field, message))
                else:
                    raise InvalidTemplatePage("Invalid Template page: %s" % message)

        page.save(get_reporter_id(req, 'author'), req.args.get('comment'),
                  req.remote_addr)
        req.redirect(req.href.templates(page.name))

    def _render_confirm(self, req, db, page):
        if page.readonly:
            req.perm.assert_permission('TEMPLATES_ADMIN')
        else:
            req.perm.assert_permission('TEMPLATES_DELETE')

        version = None
        if req.args.has_key('delete_version'):
            version = int(req.args.get('version', 0))
        old_version = int(req.args.get('old_version') or 0) or version

        self._set_title(req, page, 'delete')
        req.hdf['templates'] = {'mode': 'delete'}
        if version is not None:
            num_versions = 0
            for v,t,author,comment,ipnr in page.get_history():
                if v >= old_version:
                    num_versions += 1;
                    if num_versions > 1:
                        break
            req.hdf['templates'] = {
                'version': version,
                'old_version': old_version,
                'only_version': num_versions == 1
            }

    def _render_diff(self, req, db, page):
        req.perm.assert_permission('TEMPLATES_VIEW')

        if not page.exists:
            raise TracError("Version %s of template %s does not exist" %
                            (req.args.get('version'), page.name))

        add_stylesheet(req, 'common/css/diff.css')

        self._set_title(req, page, 'diff')

        # Ask web spiders to not index old versions
        req.hdf['html.norobots'] = 1

        old_version = req.args.get('old_version')
        if old_version:
            old_version = int(old_version)
            if old_version == page.version:
                old_version = None
            elif old_version > page.version: # FIXME: what about reverse diffs?
                old_version, page = page.version, \
                                    WikiTemplate(self.env, page.name, old_version)
        latest_page = WikiTemplate(self.env, page.name)
        new_version = int(page.version)
        info = {
            'version': new_version,
            'latest_version': latest_page.version,
            'history_href': req.href.templates(page.name, action='history')
        }

        num_changes = 0
        old_page = None
        prev_version = next_version = None
        for version,t,author,comment,ipnr in latest_page.get_history():
            if version == new_version:
                if t:
                    info['time'] = format_datetime(t)
                    info['time_delta'] = pretty_timedelta(t)
                info['author'] = author or 'anonymous'
                info['comment'] = wiki_to_html(comment or '--',
                                               self.env, req, db)
                info['ipnr'] = ipnr or ''
            else:
                if version < new_version:
                    num_changes += 1
                    if not prev_version:
                        prev_version = version
                    if (old_version and version == old_version) or \
                            not old_version:
                        old_page = WikiTemplate(self.env, page.name, version)
                        info['num_changes'] = num_changes
                        info['old_version'] = version
                        break
                else:
                    next_version = version
        req.hdf['templates'] = info

        # -- prev/next links
        if prev_version:
            add_link(req, 'prev', req.href.templates(page.name, action='diff',
                                                     version=prev_version),
                     'Version %d' % prev_version)
        if next_version:
            add_link(req, 'next', req.href.templates(page.name, action='diff',
                                                     version=next_version),
                     'Version %d' % next_version)

        # -- text diffs
        diff_style, diff_options = get_diff_options(req)

        oldtext = old_page and old_page.text.splitlines() or []
        newtext = page.text.splitlines()
        context = 3
        for option in diff_options:
            if option.startswith('-U'):
                context = int(option[2:])
                break
        if context < 0:
            context = None
        changes = hdf_diff(oldtext, newtext, context=context,
                           ignore_blank_lines='-B' in diff_options,
                           ignore_case='-i' in diff_options,
                           ignore_space_changes='-b' in diff_options)
        req.hdf['templates.diff'] = changes

    def _render_editor(self, req, db, page, preview=False):
        req.perm.assert_permission('TEMPLATES_MODIFY')

        if req.args.has_key('text'):
            page.text = req.args.get('text')
        if preview:
            page.readonly = req.args.has_key('readonly')

        author = get_reporter_id(req, 'author')
        comment = req.args.get('comment', '')
        editrows = req.args.get('editrows')
        if editrows:
            pref = req.session.get('templates_editrows', '20')
            if editrows != pref:
                req.session['templates_editrows'] = editrows
        else:
            editrows = req.session.get('templates_editrows', '20')

        self._set_title(req, page, 'edit')
        info = {
            'page_source': page.text,
            'version': page.version,
            'author': author,
            'comment': comment,
            'readonly': page.readonly,
            'edit_rows': editrows,
            'scroll_bar_pos': req.args.get('scroll_bar_pos', '')
        }
        if page.exists:
            info['history_href'] = req.href.templates(page.name,
                                                      action='history')
            info['last_change_href'] = req.href.templates(page.name,
                                                          action='diff',
                                                          version=page.version)
        if preview:
            info['page_html'] = wiki_to_html(page.text, self.env, req, db)
            info['comment_html'] = wiki_to_oneliner(comment, self.env, db)
            info['readonly'] = int(req.args.has_key('readonly'))
        req.hdf['templates'] = info

    def _render_history(self, req, db, page):
        """Extract the complete history for a given page and stores it in the
        HDF.

        This information is used to present a changelog/history for a given
        page.
        """
        req.perm.assert_permission('TEMPLATES_VIEW')

        if not page.exists:
            raise TracError, "Template %s does not exist" % page.name

        self._set_title(req, page, 'history')

        history = []
        for version, t, author, comment, ipnr in page.get_history():
            history.append({
                'url': req.href.templates(page.name, version=version),
                'diff_url': req.href.templates(page.name, version=version,
                                               action='diff'),
                'version': version,
                'time': format_datetime(t),
                'time_delta': pretty_timedelta(t),
                'author': author,
                'comment': wiki_to_oneliner(comment or '', self.env, db),
                'ipaddr': ipnr
            })
        req.hdf['templates.history'] = history

    def _render_view(self, req, db, page):
        req.perm.assert_permission('TEMPLATES_VIEW')

        page_name = self._set_title(req, page, '')
        if page.name == 'TemplatesIndex':
            req.hdf['title'] = 'Wiki Templates Index'

        version = req.args.get('version')
        if version:
            # Ask web spiders to not index old versions
            req.hdf['html.norobots'] = 1

        # Add registered converters
        for conversion in Mimeview(self.env).get_supported_conversions(
                                             'text/x-trac-wiki'):
            conversion_href = req.href.templates(page.name, version=version,
                                                 format=conversion[0])
            add_link(req, 'alternate', conversion_href, conversion[1],
                     conversion[3])

        latest_page = WikiTemplate(self.env, page.name)
        req.hdf['templates'] = {'exists': page.exists,
                                'version': page.version,
                                'latest_version': latest_page.version,
                                'readonly': page.readonly}
        if page.exists:
            req.hdf['templates'] = {
                'page_html': wiki_to_html(page.text, self.env, req),
                'history_href': req.href.templates(page.name, action='history'),
                'last_change_href': req.href.templates(page.name, action='diff',
                                                       version=page.version)
                }
            if version:
                req.hdf['templates'] = {
                    'comment_html': wiki_to_oneliner(page.comment or '--',
                                                     self.env, db),
                    'author': page.author,
                    'age': pretty_timedelta(page.time)
                    }
        else:
            if not req.perm.has_permission('TEMPLATES_CREATE'):
                raise HTTPNotFound('Template %s not found', page.name)
            req.hdf['templates.page_html'] = html.P(
                'Describe "%s" template here' % page_name)

        # Show attachments
        req.hdf['templates.attachments'] = attachments_to_hdf(self.env, req, db,
                                                         'templates', page.name)
        if req.perm.has_permission('TEMPLATES_MODIFY'):
            attach_href = req.href.attachment('templates', page.name)
            req.hdf['templates.attach_href'] = attach_href

    # TracCtxtnavAdd borrowed Internal Methods
    def _add_js(self, req, data):
        """Add javascript to a page via hdf['project.footer']"""
        footer = req.hdf['project.footer']
        footer += data
        req.hdf['project.footer'] = Markup(footer)

    def _add_js_inc(self, req, file):
        """Add a javascript include via hdf['project.footer']"""
        self._add_js(
            req, """<script type="text/javascript" src="%s"></script>""" % file)

    def _make_js(self, req):
        return """<script type="text/javascript">delete_mainnav_templatesbtn();</script>"""



    # ISearchSource methods

    def get_search_filters(self, req):
        if req.perm.has_permission('TEMPLATES_VIEW'):
            yield ('templates', 'Wiki Templates')

    def get_search_results(self, req, terms, filters):
        if not 'templates' in filters:
            return
        db = self.env.get_db_cnx()
        sql_query, args = search_to_sql(db, ['w1.name', 'w1.author', 'w1.text'], terms)
        cursor = db.cursor()
        cursor.execute("SELECT w1.name,w1.time,w1.author,w1.text "
                       "FROM templates w1,"
                       "(SELECT name,max(version) AS ver "
                       "FROM templates GROUP BY name) w2 "
                       "WHERE w1.version = w2.ver AND w1.name = w2.name "
                       "AND " + sql_query, args)

        for name, date, author, text in cursor:
            yield (req.href.templates(name), '%s: %s' % (name, shorten_line(text)),
                   date, author, shorten_result(text, terms))
