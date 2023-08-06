import os
from setuptools import setup, find_packages

def read(*filenames):
    return open(os.path.join(os.path.dirname(__file__), *filenames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

setup(name='clio',
      version = '0.5',
      description="A publication/history system for SQLAlchemy.",
      long_description=long_description,
      # Use classifiers that are already listed at:
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Zope Public License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Database',
                   'Topic :: Software Development :: Libraries',
                   ],
      keywords="history workflow sqlalchemy",
      author="Martijn Faassen",
      author_email="faassen@startifact.com",
      license="ZPL",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'SQLAlchemy >= 0.5.6',
                        'MySQL_python',
                        'zope.interface',
                        ],
      entry_points="""
      # Add entry points here
      """,
      )
