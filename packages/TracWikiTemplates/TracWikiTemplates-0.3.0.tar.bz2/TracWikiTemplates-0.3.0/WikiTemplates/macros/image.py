# -*- coding: iso8859-15 -*-

# =============================================================================
# $Id: image.py 81 2006-09-25 02:29:56Z s0undt3ch $
# =============================================================================
#             $URL: http://wikitemplates.ufsoft.org/svn/trunk/WikiTemplates/macros/image.py $
# $LastChangedDate: 2006-09-25 02:29:56Z $
#             $Rev: 81 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================

#
# Copyright (C) 2005-2006 Edgewall Software
# Copyright (C) 2005-2006 Christopher Lenz <cmlenz@gmx.de>
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
# Author: Christopher Lenz <cmlenz@gmx.de>
# Modified by Pedro Algarvio <ufs@ufsoft.org>

# =============================================================================
# vim: set tabstop=4
# vim: set shiftwidth=4
#
# Display a red square on the 80th char so we can easely limit line width to a
# max of 79 chars, the way it should be.
# vim: autocmd BufEnter * match Error /\%80v/
# =============================================================================

import re
from trac.util.html import html, Markup
from trac.wiki.macros import WikiMacroBase

class ImageMacro(WikiMacroBase):
    """Embed an image in wiki-formatted text.

    The first argument is the file specification. The file specification may
    reference attachments or files in three ways:
     * `module:id:file`, where module can be either '''wiki''', '''ticket''' or 
       '''templates''' to refer to the attachment named ''file'' of the
       specified wiki page, ticket or template.
     * `id:file`: same as above, but id is either a ticket shorthand or a Wiki
       page name.
     * `file` to refer to a local attachment named 'file'. This only works from
       within that wiki page, ticket.

    '''Note''': To use the templates attachments, the first form from above 
    '''must''' be used

    Also, the file specification may refer to repository files, using the
    `source:file` syntax (`source:file@rev` works also).

    The remaining arguments are optional and allow configuring the attributes
    and style of the rendered `<img>` element:
     * digits and unit are interpreted as the size (ex. 120, 25%)
       for the image
     * `right`, `left`, `top` or `bottom` are interpreted as the alignment for
       the image
     * `nolink` means without link to image source.
     * `key=value` style are interpreted as HTML attributes or CSS style
        indications for the image. Valid keys are:
        * align, border, width, height, alt, title, longdesc, class, id
          and usemap
        * `border` can only be a number

    Examples:
    {{{
        [[Image(photo.jpg)]]                    # simplest
        [[Image(photo.jpg, 120px)]]             # with size
        [[Image(photo.jpg, right)]]             # aligned by keyword
        [[Image(photo.jpg, nolink)]]            # without link to source
        [[Image(photo.jpg, align=right)]]       # aligned by attribute
    }}}

    You can use image from other page, other ticket or other module.
    {{{
        [[Image(OtherPage:foo.bmp)]]            # if current module is wiki
        [[Image(base/sub:bar.bmp)]]             # from hierarchical wiki page
        [[Image(#3:baz.bmp)]]                   # if in a ticket, point to #3
        [[Image(ticket:36:boo.jpg)]]
        [[Image(source:/images/bee.jpg)]]       # straight from the repository!
        [[Image(htdocs:foo/bar.png)]]           # image file in project htdocs dir.
        [[Image(templates:foo_tpl:bar.png)]]    # image attached to a template
    }}}


    ''Adapted from the Image.py macro created by Shun-ichi Goto
    <gotoh@taiyo.co.jp>''
    """

    def render_macro(self, req, name, content):
        # args will be null if the macro is called without parenthesis.
        if not content:
            return ''
        # parse arguments
        # we expect the 1st argument to be a filename (filespec)
        args = content.split(',')
        if len(args) == 0:
            raise Exception("No argument.")
        filespec = args[0]
        size_re = re.compile('[0-9]+%?$')
        attr_re = re.compile('(align|border|width|height|alt'
                             '|title|longdesc|class|id|usemap)=(.+)')
        quoted_re = re.compile("(?:[\"'])(.*)(?:[\"'])$")
        attr = {}
        style = {}
        nolink = False
        for arg in args[1:]:
            arg = arg.strip()
            if size_re.match(arg):
                # 'width' keyword
                attr['width'] = arg
                continue
            if arg == 'nolink':
                nolink = True
                continue
            match = attr_re.match(arg)
            if match:
                key, val = match.groups()
                m = quoted_re.search(val) # unquote "..." and '...'
                if m:
                    val = m.group(1)
                if key == 'align':
                    style['float'] = val
                elif key == 'border':
                    style['border'] = ' %dpx solid' % int(val);
                else:
                    attr[str(key)] = val # will be used as a __call__ keyword

        # parse filespec argument to get module and id if contained.
        parts = filespec.split(':')
        url = None
        if len(parts) == 3:                 # module:id:attachment
            if parts[0] in ['wiki', 'ticket', 'templates']:
                module, id, file = parts
            else:
                raise Exception("%s module can't have attachments" % parts[0])
        elif len(parts) == 2:
            from trac.versioncontrol.web_ui import BrowserModule
            try:
                browser_links = [link for link,_ in 
                                 BrowserModule(self.env).get_link_resolvers()]
            except Exception:
                browser_links = []
            if parts[0] in browser_links:   # source:path
                module, file = parts
                rev = None
                if '@' in file:
                    file, rev = file.split('@')
                url = req.href.browser(file, rev=rev)
                raw_url = req.href.browser(file, rev=rev, format='raw')
                desc = filespec
            else: # #ticket:attachment or WikiPage:attachment
                # FIXME: do something generic about shorthand forms...
                id, file = parts
                if id and id[0] == '#':
                    module = 'ticket'
                    id = id[1:]
                elif id == 'htdocs':
                    raw_url = url = req.href.chrome('site', file)
                    desc = os.path.basename(file)
                elif id in ('http', 'https', 'ftp'): # external URLs
                    raw_url = url = desc = id+':'+file
                else:
                    module = 'wiki'
        elif len(parts) == 1:               # attachment
            # determine current object
            # FIXME: should be retrieved from the formatter...
            # ...and the formatter should be provided to the macro
            file = filespec
            module, id = 'wiki', 'WikiStart'
            path_info = req.path_info.split('/',2)
            if len(path_info) > 1:
                module = path_info[1]
            if len(path_info) > 2:
                id = path_info[2]
            if module not in ['wiki', 'ticket', 'templates']:
                raise Exception('Cannot reference local attachment from here')
        else:
            raise Exception('No filespec given')
        if not url: # this is an attachment
            from trac.attachment import Attachment
            attachment = Attachment(self.env, module, id, file)
            self.env.log.debug(attachment)
            url = attachment.href(req)
            raw_url = attachment.href(req, format='raw')
            desc = attachment.description
        for key in ['title', 'alt']:
            if desc and not attr.has_key(key):
                attr[key] = desc
        if style:
            attr['style'] = '; '.join(['%s:%s' % (k, escape(v))
                                       for k, v in style.iteritems()])
        result = Markup(html.IMG(src=raw_url, **attr)).sanitize()
        if not nolink:
            result = html.A(result, href=url, style='padding:0; border:none')
        return result
