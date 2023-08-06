from setuptools import setup, find_packages
from os.path import join

name = 'dolmen.app.layout'
version = '0.3'
readme = open(join('src', 'dolmen', 'app', 'layout', 'README.txt')).read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = [
    'setuptools',
    'grok',
    'grokcore.view',
    'grokcore.viewlet',
    'dolmen.content',
    'dolmen.forms.base',
    'dolmen.forms.crud >= 0.2.1',
    'dolmen.app.site',
    'dolmen.app.security',
    'megrok.menu',
    'megrok.resource',
    'megrok.resourceviewlet',
    'megrok.z3ctable >= 1.3',
    'megrok.z3cform.base',
    'megrok.z3cform.composed',
    'megrok.layout >= 0.9',
    'z3c.flashmessage',
    'zope.component',
    'zope.interface',
    'zope.traversing',
    'zope.publisher',
    'zope.browsermenu'
    ]

tests_require = [
    'zope.security',
    'zope.publisher',
    'zope.securitypolicy',
    'zope.testing',
    'zope.app.testing',
    'zope.app.zcmlfiles',
    ]

setup(name = name,
      version = version,
      description = 'Layout and page models for Dolmen applications',
      long_description = readme + '\n\n' + history,
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
      test_suite="dolmen.app.layout",
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
