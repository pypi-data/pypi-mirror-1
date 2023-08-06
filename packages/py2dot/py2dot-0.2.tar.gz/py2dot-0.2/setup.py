#!/usr/bin/env python

from distutils.core import setup

setup(name='py2dot',
      version='0.2',
      author='Lorenzo Bolla',
      author_email='lbolla@gmail.com',
      url='http://pypi.python.org/pypi/py2dot',
      py_modules=['py2dot'],
      description='Python to Dot converter',
      long_description='''py2dot is a Python script to generate a dot file from a Python script.''',
      download_url='http://pypi.python.org/pypi/py2dot',
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python',
                   'Topic :: Utilities',
                   ]
)
