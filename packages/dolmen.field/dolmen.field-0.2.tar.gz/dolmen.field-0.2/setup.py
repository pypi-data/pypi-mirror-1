from os.path import join
from setuptools import setup, find_packages

name = 'dolmen.field'
version = '0.2'

setup(name = name,
      version = version,
      description = 'Generic Formlib fields',
      long_description = open(join('dolmen/field', 'README.txt')).read() + '\n',
      keywords = 'Grok Zope3 Dolmen',
      author = 'Souheil Chelfouh',
      author_email = 'souheil@chelfouh.com',
      url = 'http://tracker.trollfot.org/',
      download_url = 'http://pypi.python.org/pypi/dolmen.field',
      license = 'GPL',
      packages = find_packages(),
      namespace_packages = ['dolmen'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      install_requires=[
          'setuptools',
          'zope.schema',
          'zope.interface'
      ],
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
      ],
)
