import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='ore.wsgiapp',
      version='0.3.2',
      description="glue for wsgi zope3 apps w/o zodb",
      long_description=( read('src','ore','wsgiapp','README.txt')
                         + '\n\n' +
                         read('changes.txt')
                         ),
      keywords='',
      author='Kapil Thangavelu',
      author_email='kapil.foss@gmail.com',
      license='ZPL',
      # Get more from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python',
                   'Environment :: Web Environment',
                   'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                   'Framework :: Zope3',
                   ],
      packages=find_packages('src'),
      package_dir = {'':'src'},
      namespace_packages = ['ore',],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zope.publisher',
                        'zope.traversing',
                        'zope.event',
                        'zope.app.wsgi>=3.4.0',
                        'zope.app.appsetup',
                        'zope.app.zcmlfiles',
                        'zope.testing',
                        ],
      entry_points = """
      [paste.app_factory]
      main = ore.wsgiapp.startup:application_factory
      """
      )
