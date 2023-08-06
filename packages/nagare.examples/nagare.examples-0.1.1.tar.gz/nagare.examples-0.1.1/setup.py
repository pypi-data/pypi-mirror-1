#--
# Copyright (c) 2008, 2009 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

VERSION='0.1.1'

from setuptools import setup, find_packages

setup(
      name = 'nagare.examples',
      version = VERSION,
      author = 'Alain Poirier',
      author_email = 'alain.poirier at net-ng.com',
      description = 'Demo and examples for the Nagare web framework',
      license = 'BSD',
      keywords = 'web wsgi framework sqlalchemy elixir seaside continuation ajax stackless',
      url = 'http://www.nagare.org',
      download_url = 'http://www.nagare.org/download',
      packages = find_packages(),
      include_package_data = True,
      package_data = {'' : ['*.cfg']},
      zip_safe = False,
      dependency_links = ('http://www.nagare.org/download/',),
      install_requires = ('nagare[database]', 'docutils', 'PIL'),
      namespace_packages = ('nagare.examples',),
      entry_points = '''
      [nagare.applications]
      demo = nagare.examples.demo:app
      wiki = nagare.examples.wiki.wiki9:app
      gallery = nagare.examples.gallery.gallery7:app
      portal = nagare.examples.portal:app
      ''',
      classifiers = (
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Operating System :: Microsoft :: Windows :: Windows NT/2000',
        'Operating System :: Unix',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
      )
     )
