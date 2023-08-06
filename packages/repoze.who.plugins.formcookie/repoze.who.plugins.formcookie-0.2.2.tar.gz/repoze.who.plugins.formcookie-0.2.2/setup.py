from setuptools import setup, find_packages
import sys, os

version = '0.2.2'

setup(name='repoze.who.plugins.formcookie',
      version=version,
      description="Similar to RedirectingFormPlugin, but stores came_from in cookie instead of url query string",
      long_description="""\
      Documentation at http://docs.fubar.si/formcookie/
      Source at http://www.bitbucket.org/iElectric/repozewhopluginsformcookie/
      """,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='repoze.who plugins form cookie authentication',
      author='Domen "iElectric" Kozar',
      author_email='domen@dev.si',
      url='http://www.fubar.si',
      license='none',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages = ['repoze', 'repoze.who', 'repoze.who.plugins'],
      include_package_data=True,
      test_suite='nose.collector',
      tests_require=['webob', 'webtest', 'nose'],
      zip_safe=False,
      install_requires=[
        'setuptools',
        'repoze.who',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
