#! /usr/bin/env python
"""
This is an installation script for the trace2html utility

To run the tests (requires setuptools)::

    $ python setup.py test

To byte-compile::

    $ python setup.py build

To install it system-wide::

    $ sudo python setup.py install

To get more options::

    $ python setup.py --help
"""


try:
    from setuptools import setup
    use_setuptools = True
except ImportError:
    print 'setuptools could not be found: please run "python ez_setup.py"'
    print 'to get the last version'
    from distutils.core import setup
    use_setuptools = False


setup_options = {
    'name': 'trace2html',
    'version': '0.2.0',
    'author': 'Olivier Grisel',
    'author_email': 'olivier.grisel@ensta.org',
    'url': 'http://champiland.homelinux.net/trace2html',
    'description': 'HTML coverage report generator for trace.py',
    'long_description': file("README.txt").read() + file("NEWS.txt").read(),
    'license': 'GNU GPL v2',
    'scripts': ['src/trace2html.py'],
    'packages': ['trace2htmldata'],
    'package_dir': {'trace2htmldata': 'src/trace2htmldata'},
    'package_data': {'trace2htmldata': ['*.css', '*.js']},
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
}

if use_setuptools:
    setup_options['test_suite'] = 'src.trace2html.test_suite'

# run setup
setup(**setup_options)

