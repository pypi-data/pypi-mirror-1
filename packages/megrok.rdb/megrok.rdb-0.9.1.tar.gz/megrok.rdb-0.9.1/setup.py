from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = read('src/megrok/rdb/README.txt') + '\n' +\
    read('CHANGES.txt')

setup(name='megrok.rdb',
      version = '0.9.1',
      description="SQLAlchemy based RDB support for Grok.",
      long_description=long_description,
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Zope3',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Zope Public License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Database',
                   ],
      keywords='rdb relational sqlalchemy grok database',
      author='Grok Team',
      author_email='grok-dev@zope.org',
      license='ZPL',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['megrok'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.interface',
          'zope.schema',
          'zope.component',
          'zope.event',
          'zope.location',
          'grokcore.component',
          'zope.app.container', # want to depend on zope.container directly but can't yet to retain grok compatibility
          'martian < 0.12', # 0.12 is too new for grokcore.component right now..
          'SQLAlchemy > 0.5beta2',
          'zope.sqlalchemy',
          'z3c.saconfig >= 0.9',
         ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
