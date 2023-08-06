from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='anthill.exampletheme',
      version=version,
      description="Example theme for anthill.skinner",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone anthill skin theme',
      author='Simon Pamies',
      author_email='s.pamies@banality.de',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['anthill'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'anthill.skinner>=0.2',
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
