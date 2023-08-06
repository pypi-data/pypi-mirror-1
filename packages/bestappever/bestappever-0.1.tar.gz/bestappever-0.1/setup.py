import os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

setup(name='bestappever',
      version='0.1',
      description='An example application which uses repoze.bfg',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Christian Scholz',
      author_email='cs@comlounge.net',
      url='http://mrtopf.de/blog/tutorials/a-first-look-at-repozebfg/',
      keywords='web wsgi bfg zope example',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
            'repoze.bfg',
            ],
      tests_require=[
            'repoze.bfg',
            ],
      test_suite="bestappever",
      entry_points = """\
      [paste.app_factory]
      app = bestappever.run:app
      """
      )

