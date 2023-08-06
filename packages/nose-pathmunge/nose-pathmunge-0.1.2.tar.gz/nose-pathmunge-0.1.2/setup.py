import os
import sys
try:
    import ez_setup
    ez_setup.use_setuptools()
except ImportError:
    pass
from setuptools import setup

# Use a cute trick to include the rest-style docs as the long_description
# therefore having it self-doc'ed and hosted on pypi
f = open(os.path.join(os.path.dirname(__file__), 'README.txt'))
long_description = f.read().strip()
f.close()

setup(
    name='nose-pathmunge',
    version='0.1.2',
    author='Jesse Noller',
    author_email = 'jnoller@gmail.com',
    description = 'Add additional directories to sys.path for nose.',
    long_description = long_description,
    license = 'Apache License, Version 2.0',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Testing',
      ],
    py_modules=['pathmunge'],
    packages=[''],
    package_dir={'': 'src'},
    package_data = {'': ['README.txt']},
    entry_points = {
        'nose.plugins.0.10': [
            'pathmunge = pathmunge:PathMunge',
            ]
        }
    )
