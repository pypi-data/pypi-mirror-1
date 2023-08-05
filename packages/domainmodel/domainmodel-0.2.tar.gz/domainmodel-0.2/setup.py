from setuptools import setup, find_packages

import django        # not served from cheeseshop
import mx.DateTime   # not served from cheeseshop

import sys
sys.path.insert(0, './src')
from dm import __version__

setup(
    name = 'domainmodel',
    version = __version__,
    package_dir = { '' : 'src' },
    packages = find_packages('src'),
    
    # no way to specify the dependency on django as we need a specific revision
    install_requires = [
        'SQLObject>=0.6,<=0.7.99',
        'simplejson',
        # 'Django>=0.95'  # Django not served on cheese shop
        # 'mxDateTime',   # not sure about this, maybe wrong name
    ],

    # metadata for upload to PyPI
    author = 'Open Knowledge Foundation and Appropriate Software Foundation',
    author_email = 'kforge-dev@lists.okfn.org',
    license = 'GPL',
    url = 'http://www.kforgeproject.com/',
    download_url = 'http://www.kforgeproject.com/files/domainmodel-%s.tar.gz' % __version__,
    description = 'Toolkit for enterprise application frameworks.',
    long_description = \
"""
DomainModel provides a toolkit for enterprise application frameworks.
""",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'],
)

