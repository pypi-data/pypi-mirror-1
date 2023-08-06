from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = read('Products', 'ColorField', 'version.txt')[:-1]

long_description = (
#                        open("README.txt").read() + "\n" +
                        open(os.path.join("docs", "HISTORY.txt")).read() + "\n" +
                        open(os.path.join("docs", "INSTALL.txt")).read()
#                        open(os.path.join("docs", "CREDITS.txt")).read()
    )

setup(name='Products.ColorField',
      version=version,
      description="ColorField is a color picker and converter for Plone Archetypes.",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Roland Fasching',
      author_email='rof@sterngasse.at',
      url='http://pypi.python.org/pypi/Products.ColorField/',
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
