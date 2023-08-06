import os
from setuptools import setup, find_packages, Extension

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='repoze.bfg.httprequest',
      version = '0.4.1',
      description='Adaptable request interfaces.',
      author='Malthe Borch and Stefan Eletzhofer',
      author_email='repoze-dev@lists.repoze.org',
      url='http://pypi.python.org/pypi/repoze.bfg.httprequest',
      long_description="\n".join((
          read('README.txt'), read('src/repoze/bfg/httprequest/README.txt'))),
      keywords = "zope3 repoze bfg",
      classifiers = [
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['repoze', 'repoze.bfg'],
      install_requires=['setuptools',
                        'repoze.bfg',
                        'zope.interface',
                        'zope.component',
                        'zope.security',
                        'zope.testing',
                        ],  
      include_package_data = True,
      zip_safe = False,
      test_suite="repoze.bfg.httprequest.tests.test_doctests.test_suite",
      )
