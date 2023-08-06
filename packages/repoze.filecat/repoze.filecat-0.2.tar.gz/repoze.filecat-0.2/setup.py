import os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

requires = [
    'setuptools',
    'repoze.bfg',
    'xappy',
    'lxml',
    'ore.xapian',
    'jsonlib',
    'docutils',
    ]

setup(name='repoze.filecat',
      version='0.2',
      description='A file catalog with an HTTP frontend.',
      long_description=read("README.txt") + '\n\n' +  read("CHANGES.txt"),
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Malthe Borch and Stefan Eletzhofer',
      author_email="repoze-dev@lists.repoze.org",
      url='http://www.repoze.org',
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      keywords='web wsgi bfg zope',
      package_dir = {'': 'src'},
      packages=find_packages("src"),
      include_package_data=True,
      namespace_packages=['repoze'],
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="repoze.filecat.tests",
      entry_points = """\
      [paste.app_factory]
      make_app = repoze.filecat.run:make_app
      """
      )

