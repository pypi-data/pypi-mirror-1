import sys

try:
    from setuptools import setup
    has_setuptools = True
except ImportError:
    from distutils.core import setup
    has_setuptools = False

from metainfo import setup_meta

def convert_options():
    if has_setuptools:
        return
    del_options = ['install_requires', 'test_suite', 'zip_safe',
                   'entry_points']
    for option in del_options:
        del setup_meta[option]
    setup_meta['scripts'] = ['scripts/paver']

convert_options()
setup(**setup_meta)
