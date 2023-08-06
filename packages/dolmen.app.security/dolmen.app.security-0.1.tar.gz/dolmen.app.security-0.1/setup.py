from os.path import join
from setuptools import setup, find_packages

name = 'dolmen.app.security'
version = '0.1'
readme = open(join('src', 'dolmen', 'app', 'security', 'README.txt')).read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = [
    'setuptools',
    'grok >= 1.0',
    'zope.interface',
    ]

setup(name = name, 
      version = version,
      description = "Dolmen application security declarations",
      long_description = readme + '\n\n' + history,
      keywords = 'Dolmen CMS Grok Security',
      author = 'Souheil Chelfouh',
      author_email = 'trollfot@gmail.com',
      url = '',
      license = 'GPL',
      packages = find_packages('src', exclude = ['ez_setup']),
      package_dir = {'': 'src'},
      namespace_packages = ['dolmen', 'dolmen.app'],
      include_package_data = True,
      zip_safe = False,
      install_requires = install_requires,
      test_suite = "dolmen.app.security",
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Zope3',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
          ],
      )
