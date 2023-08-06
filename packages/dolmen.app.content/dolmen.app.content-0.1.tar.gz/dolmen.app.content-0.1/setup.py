from setuptools import setup, find_packages
from os.path import join

name = 'dolmen.app.content'
version = '0.1'
readme = open(join('src', 'dolmen', 'app', 'content', 'README.txt')).read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = [
    'setuptools',
    'grok',
    'PILwoTk',
    'zope.index',
    'dolmen.blob>=0.2.1',
    'dolmen.content>=0.2.2',
    'dolmen.forms.crud>=0.2',
    'dolmen.thumbnailer>=0.2.1',
    'dolmen.app.site>=0.1',
    'dolmen.app.layout>=0.2',
    ]

tests_require = install_requires + [
    'zope.testing',
    'zope.app.testing',
    'zope.app.zcmlfiles'
    ]

setup(name = name,
      version = version,
      description = 'Dolmen applications content utilities',
      long_description = readme[readme.find('\n\n'):] + '\n' + history,
      keywords = 'Grok Zope3 CMS Dolmen',
      author = 'Souheil Chelfouh',
      author_email = 'trollfot@gmail.com',
      url = 'http://gitweb.dolmen-project.org/',
      download_url = '',
      license = 'GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages = ['dolmen', 'dolmen.app'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      tests_require = tests_require,
      install_requires = install_requires,
      extras_require = {'test': tests_require},
      test_suite="dolmen.app.content",
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
