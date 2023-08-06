# -*- coding: utf-8 -*-

import sys, os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '../../../src'))

from github.tools import version, release, project, copyright, author

# Extension
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx', 'sphinx.ext.todo', 'github.tools.sphinx']
intersphinx_mapping = {'http://docs.python.org/': None}

# Source
master_doc = 'index'
templates_path = ['_templates']
source_suffix = '.rst'
exclude_trees = []
pygments_style = 'sphinx'

# html build settings
html_theme = 'default'
html_static_path = ['_static']

# htmlhelp settings
htmlhelp_basename = '%sdoc' %project

# latex build settings
latex_documents = [
  ('index', '%s.tex' % project, u'%s Documentation' % project,
   author, 'manual'),
]