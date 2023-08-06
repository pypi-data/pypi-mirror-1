from os.path import join
from setuptools import setup, find_packages

readme = open(join('src', 'dolmen', 'field', 'README.txt')).read()
history = open(join('docs', 'HISTORY.txt')).read()
name = 'dolmen.field'
version = '0.3'

setup(name = name,
      version = version,
      description = 'Generic Formlib fields',
      long_description = readme + '\n\n' + history,
      keywords = 'Grok Zope3 Dolmen',
      author = 'Souheil Chelfouh',
      author_email = 'trollfot@gmail.com',
      url = 'http://gitweb.dolmen-project.org',
      download_url = 'http://pypi.python.org/pypi/dolmen.field',
      license = 'GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
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
