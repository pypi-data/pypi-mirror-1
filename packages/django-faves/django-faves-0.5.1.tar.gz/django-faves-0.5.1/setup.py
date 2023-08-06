#!/usr/bin/env python
from distutils.core import setup

setup(
      name='django-faves',
      version='0.5.1',
      author='jeffrey.a.croft, Mikhail Korobov',
      author_email='kmike84@gmail.com',
      url='http://bitbucket.org/kmike/django-faves/',      
      
      description = 'Generic favorites pluggable django app',
      long_description = "This app lets users favorite objects in your database (as well as unfavorite them).",
      license = 'New BSD License (http://www.opensource.org/licenses/bsd-license.php)',
      packages=['faves', 'faves.templatetags'],
      package_data={'faves': ['fixtures/*.json','templates/faves/*.html']},      
      
      classifiers=(
          'Development Status :: 3 - Alpha',
          'Environment :: Plugins',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Natural Language :: English',
          'Natural Language :: Russian',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules'
        ),
)