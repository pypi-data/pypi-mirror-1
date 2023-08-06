# -*- coding: utf-8 -*-
import sys, os, pkginfo, datetime

pkg_info = pkginfo.Develop(os.path.join(os.path.dirname(__file__),'..'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx'
    ]

intersphinx_mapping = {'http://docs.python.org/dev': None}

copyright_owner = 'Peter Bunyan, Jonathan Marshall, Petra Chong, GLC Ltd.'
# General
source_suffix = '.txt'
master_doc = 'index'
project = pkg_info.name
copyright = '2008-%s %s' % (datetime.datetime.now().year,copyright_owner)
version = release = pkg_info.version
exclude_trees = ['_build']
unused_docs = ['description']
pygments_style = 'sphinx'

# Options for HTML output
html_theme = 'default'
htmlhelp_basename = project+'doc'

# Options for LaTeX output
latex_documents = [
  ('index',project+'.tex', project+u' Documentation',
   copyright_owner, 'manual'),
]

