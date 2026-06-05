import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'Hotel Management System'
copyright = '2026'
author = 'Vitaliy Vyborov, Shvetsov Maksim'

# Extensions
extensions = [
    'myst_parser',
]

# Markdown source files
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# Master document
master_doc = 'index'

# Exclude patterns
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML theme
html_theme = 'alabaster'

# HTML static files
html_static_path = ['_static']

# Templates
templates_path = ['_templates']
