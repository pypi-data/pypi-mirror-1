import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description=(
        read('README')
        + '\n' +
        read('CHANGES')
        + '\n' +
        'Download\n'
        '**********************\n'
        )

open('doc.txt', 'w').write(long_description)

setup(
  name = "python-twitter",
  version = "0.4",
  py_modules = ['twitter'],
  author='DeWitt Clinton',
  author_email='dewitt@google.com',
  description='A python wrapper around the Twitter API',
  long_description=long_description,
  license='Apache License 2.0',
  url='http://code.google.com/p/python-twitter/',
  keywords='twitter api',
  install_requires = 'setuptools',
  include_package_data = True,
  zip_safe=False,
  classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Communications :: Chat',
    'Topic :: Internet',
  ],
)
