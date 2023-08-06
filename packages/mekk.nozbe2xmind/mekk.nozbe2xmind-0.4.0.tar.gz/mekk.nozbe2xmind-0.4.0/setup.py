# -*- coding: utf-8 -*-
# (c) 2008, Marcin Kasperski

from setuptools import setup, find_packages

version = '0.4.0'
long_description = open("README.txt").read()
classifiers = [
    "Programming Language :: Python",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    # TODO: Development Status, Environment, Topic
    ]

setup(name='mekk.nozbe2xmind',
      version=version,
      description="Sync between Nozbe API and XMind data files.",
      long_description=long_description,
      classifiers=classifiers,
      keywords='xmind,Nozbe',
      author='Marcin Kasperski',
      author_email='Marcin.Kasperski@mekk.waw.pl',
      url='http://mekk.waw.pl/python/xmind',
      license='LGPL',
      package_dir={'':'src'},
      packages=find_packages('src', exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['mekk'],
      test_suite = 'nose.collector',
      zip_safe=False,
      install_requires=[
          'lxml', 'Twisted', 'simplejson',
          'mekk.xmind>=0.3.0',
      ],
      tests_require=[
          'nose', 
      ],
      #include_package_data = True,
      package_data = {
          'mekk.nozbe2xmind' : ['*.xmp'],
      },
      #scripts = [
      #           "scripts/nozbe2xmind",
      #],
      entry_points = {
        'console_scripts': [
            'nozbe2xmind = mekk.nozbe2xmind.run:run',
            ],
        },

)
