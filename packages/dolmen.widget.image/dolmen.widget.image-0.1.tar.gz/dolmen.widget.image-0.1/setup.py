from setuptools import setup, find_packages
from os.path import join

name = 'dolmen.widget.image'
version = '0.1'
readme = open(join('src', 'dolmen', 'widget', 'image', 'README.txt')).read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = [
    'setuptools',
    'zope.interface',
    'dolmen.file>=0.2',
    'dolmen.thumbnailer',
    'dolmen.widget.file',
    'grokcore.component',
    'megrok.z3cform.base>=0.1',
    ]

tests_require = install_requires + [
    'zope.testing',
    'zope.app.testing',
    'zope.app.zcmlfiles',
    ]

setup(name = name,
      version = version,
      description = 'Image widget (with thumbnails) for z3c.form, using Grok',
      long_description = readme + '\n\n' + history,
      keywords = 'Grok Zope3 Dolmen Widget Image',
      author = 'Souheil Chelfouh',
      author_email = 'trollfot@gmail.com',
      url = '',
      license = 'GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages = ['dolmen', 'dolmen.widget'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      tests_require = tests_require,
      install_requires = install_requires,
      extras_require = {'test': tests_require},
      test_suite="dolmen.widget.image",
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
