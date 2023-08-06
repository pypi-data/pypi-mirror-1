#!/usr/bin/env python
import os
from setuptools import setup, find_packages

README = os.path.join(os.path.dirname(__file__), 'README.txt')
long_description = open(README).read() + '\n\n'

setup(
  name = 'Camelot',
  version = '07.09',
  description = 'A python GUI framework on top of  Sqlalchemy  and PyQt, inspired by the Django admin interface. Start building desktop applications at warp speed, simply by adding some additional information to you model definition.',
  long_description = long_description,
  keywords = 'qt pyqt sqlalchemy elixir desktop gui framework',
  author = 'Conceptive Engineering',
  author_email = 'project-camelot@conceptive.be',
  url = 'http://www.conceptive.be/projects/camelot/',
  include_package_data = True,
  license = 'GPL, Commercial',
  platform = 'Linux, Windows, OS X',
  install_requires = ['SQLAlchemy==0.4.7', 
                      'Elixir>=0.6.1', 
                      'sqlalchemy-migrate>=0.5.3',
                      'pyExcelerator>=0.6.4a',
                      'Jinja>=1.2',
                      'PIL>=1.1.6', ],
  entry_points = """
    [distutils.commands]
    camelot_admin = camelot.bin.camelot_admin
    camelot_manage = camelot.bin.camelot_manage
  """,
  packages = find_packages() )

