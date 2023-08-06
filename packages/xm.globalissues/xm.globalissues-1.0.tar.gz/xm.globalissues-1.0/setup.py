from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='xm.globalissues',
      version=version,
      description="Find Poi issues globally in the site when adding issue tracker tasks",
      long_description=open(os.path.join("xm", "globalissues", "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
                       
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone',
      author='Hans-Peter Locher',
      author_email='hans-peter.locher@inquant.de',
      url='http://svn.plone.org/svn/collective/xm.globalissues',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['xm'],
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
