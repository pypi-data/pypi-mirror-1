#!/usr/bin/env python

# $Id: setup.py 91 2008-04-21 15:25:08Z s0undt3ch $

from setuptools import setup, find_packages

PACKAGE = 'TracWikiTemplates'
VERSION = '0.3.0'
AUTHOR = 'Pedro Algarvio'
AUTHOR_EMAIL = 'ufs@ufsoft.org'
SUMMARY = 'Trac Plugin to pre-format parts of the Wiki page using it'
DESCRIPTION = """
===========================
 Trac WikiTemplates Plugin
===========================

WikiTemplates is a `Trac <http://trac.edgewall.org>`_ plugin.
This plugin will provide you a way to include parts of other wiki pages,
the templates, into our current wiki page.

**NOTE:** This plugin is not Trac 0.11 compatible, nor will it be untill
someone submits a patch for it. My time is scarce, a lot has changed with
Trac 0.11 and I simple don't have the time to update this plugin.

**Why This?**
You could have a template that makes the text red colored with a monospace
font, and use the template instead of making multiple span's,

Some Usage Examples
-------------------
The template:
::

 {{{
 #!html
 <span style="color: #339900; font-family: monospace;">{{1}}</span>
 }}}

To use that template, one would put on the wiki page being edited:
::

 [[T(GreenText|The Green Text Passed)]]

The HTML output:
::

 <span style="color: rgb(51, 153, 0); font-family: monospace;">The Green Text Passed</span>

Another example would be:

The template:
::

 {{{
 #!html
 <span style="color: #339900; font-family: monospace;">{{1}}</span> <span style="color: red;">{{2}}</span>
 }}}

Wiki implementation:
::

[[T(GreenAndRedText|The Green Text Passed|And The Red Not Monospace Text)]]

The HTML Output(with line breaks for readability):
::

 <span style="color: rgb(51, 153, 0); font-family: monospace;">The Green Text Passed</span>
 <span style="color: red;">And The Red Not Monospace Text</span>

Of course this isn't that really usefull but just imagine the possibilities,
too many to name here.

As of version >=0.3.0, WikiTemplates also supports inclusion of whole wiki
pages(with no arguments parsing) and even off site pages. Examples:

Include a wiki page:
::

 [[Include(WikiPageName)]]

Include an off-site page:
::

 [[Include(http://the.url.to.site.com/page)]]

You can find more info on the
`WikiTemplates <http://wikitemplates.ufsoft.org/>`_ site where bugs and new
feature requests should go to.

Download and Installation
-------------------------

WikiTemplates can be installed with `Easy Install
<http://peak.telecommunity.com/DevCenter/EasyInstall>`_ by typing::

    > easy_install TracWikiTemplates

"""
HOME_PAGE = 'http://wikitemplates.ufsoft.org'
LICENSE = 'BSD'

setup(name=PACKAGE,
      version=VERSION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url=HOME_PAGE,
      download_url='http://python.org/pypi/TracWikiTemplates',
      description=SUMMARY,
      long_description=DESCRIPTION,
      license=LICENSE,
      platforms="OS Independent - Anywhere Python and Trac >=0.10 is known to run.",
      install_requires = ['TracCtxtnavAdd'],
      packages=find_packages(),
      package_data={
          'WikiTemplates': [
              'templates/*.cs',
              'htdocs/css/*.css',
              'htdocs/img/*.png',
              'htdocs/js/*.js',
              'DefaultTemplates/*'
          ]
      },
      entry_points = {
          'trac.plugins': [
              'wikitemplates = WikiTemplates',
          ]
      },
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Text Processing',
          'Topic :: Utilities',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ]
     )
