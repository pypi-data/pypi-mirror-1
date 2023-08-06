from setuptools import setup, find_packages
import os

version = '0.2.4'

setup(name='nilo.webgallery',
      version=version,
      description="A simple http server serving a web gallery out of a directory structure.",
      long_description="""To use, simply start the 'webgallery' script in a directory you want to serve.

It will then be browsable via http://localhost:8000/. To end, press ctrl-c.

More info at webgallery --help.
For detailed documentation visit http://packages.python.org/nilo.webgallery.""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Topic :: Communications :: File Sharing",
          "Intended Audience :: End Users/Desktop",
          "Environment :: Console",
          "Environment :: No Input/Output (Daemon)",
          "Operating System :: OS Independent",
          "Topic :: Communications :: File Sharing",
          "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
          "Topic :: Multimedia :: Graphics :: Presentation",
          "Topic :: Multimedia :: Graphics :: Viewers",
          "Topic :: Multimedia :: Video :: Display",
          "Topic :: Multimedia :: Sound/Audio :: Players",
          "Topic :: System :: Archiving",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web gallery http server',
      author='Daniel Havlik',
      author_email='nielow@gmail.com',
      url='http://packages.python.org/nilo.webgallery',
      license='GPL',
      setup_requires=["setuptools_hg"],
      packages=find_packages(exclude=['ez_setup']),
      package_data = {
            'nilo.webgallery': [ 'templates/*.html', 'resources/*.css',
                'resources/*.js', 'resources/*.gif', 'resources/*.png'],
          },
      namespace_packages=['nilo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'PIL',
          'jinja2',
          # -*- Extra requirements: -*-
      ],
      entry_points={
        'console_scripts': [
            'webgallery = nilo.webgallery.runscript:runner',],
        }, 
      )
