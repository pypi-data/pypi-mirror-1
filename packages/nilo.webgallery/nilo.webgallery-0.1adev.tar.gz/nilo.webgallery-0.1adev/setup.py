from setuptools import setup, find_packages
import os

version = '0.1a'

setup(name='nilo.webgallery',
      version=version,
      description="A simple http server serving a web gallery out of a directory structure.",
      long_description="To use, simply start the 'webgallery' script in a directory you want to serve. It will then be browsable via http://some_address:8000/ (port configuration coming soon). To end, press ctrl-c.",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web gallery http server',
      author='Daniel Havlik',
      author_email='nielow@gmail.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      package_data = {
            'nilo.webgallery': ['templates/*.html', 'resources/*.css',
                'resources/*.js', 'resources/*.gif', 'resources/*.png'],
          },
      namespace_packages=['nilo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'pil',
          'jinja2',
          # -*- Extra requirements: -*-
      ],
      entry_points={
        'console_scripts': [
            'webgallery = nilo.webgallery.runscript:runner',],
        }, 
      )
