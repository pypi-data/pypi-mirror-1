import os
from setuptools import setup, find_packages, Extension

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='repoze.bfg.htmlpage',
      version = '0.3.1',
      description='Dynamic HTML pages for repoze.bfg',
      long_description=read('README.txt'),
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
                        'repoze.bfg.skins',
                        'zope.configuration',
                        'chameleon.html',
                        ],  
      include_package_data = True,
      zip_safe = False,
      )
