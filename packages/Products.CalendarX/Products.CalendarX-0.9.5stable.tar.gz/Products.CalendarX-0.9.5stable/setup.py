from setuptools import setup, find_packages
import os

def _textFromPath(*names):
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, *names)
    return open(path, 'r').read().strip()

version = _textFromPath('Products', 'CalendarX', 'version.txt')
long_description = '\n\n'.join(
    (_textFromPath('README.txt'),
     _textFromPath('docs', 'HISTORY.txt')
     ))

setup(name='Products.CalendarX',
      version=version,
      description=("CalendarX is a customizable, open source metacalendar "
                   "application written for the Plone content management "
                   "system on top of Zope and Python."),
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Framework :: Zope2",
          "Programming Language :: Python",
          "Operating System :: OS Independent",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Office/Business :: Scheduling",
          "Natural Language :: Catalan",
          "Natural Language :: Czech",
          "Natural Language :: Danish",
          "Natural Language :: English",
          "Natural Language :: German",
          "Natural Language :: French",
          "Natural Language :: Italian",
          "Natural Language :: Japanese",
          "Natural Language :: Dutch",
          "Natural Language :: Portuguese (Brazilian)",
          "Natural Language :: Swedish",
        ],
      keywords='plone calendar',
      author='Lupa Zurven',
      author_email='lupa at zurven dot com',
      url='http://svn.plone.org/svn/collective/Products.CalendarX/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [distutils.setup_keywords]
      paster_plugins = setuptools.dist:assert_string_list

      [egg_info.writers]
      paster_plugins.txt = setuptools.command.egg_info:write_arg
      """,
      paster_plugins = ["ZopeSkel"],
      )
