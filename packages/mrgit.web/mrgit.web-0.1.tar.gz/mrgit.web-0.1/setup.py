import os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

setup(name='mrgit.web',
      version='0.1',
      description='mrgit.web',
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
      author='Rok Garbas',
      author_email='rok@garbas.si',
      url='http://code.garbas.si/mrgit.web',
      keywords='web wsgi repoze bfg zope git gitweb',
      packages=find_packages(),
      #packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['mrgit', 'mrgit.web'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
            'repoze.bfg',
            'GitPython',
            'Pygments',
            ],
      tests_require=[
            'repoze.bfg',
            'GitPython',
            ],
      test_suite="mrgit.web",
      entry_points = """\
      [paste.app_factory]
      repo = mrgit.web.app:repo
      repos = mrgit.web.app:repos
      """
      )

