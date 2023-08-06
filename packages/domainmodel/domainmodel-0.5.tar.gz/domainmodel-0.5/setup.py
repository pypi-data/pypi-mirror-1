from setuptools import setup, find_packages

#import django        # not served from cheeseshop
#import mx.DateTime   # not served from cheeseshop

import sys
sys.path.insert(0, './src')
from dm import __version__

setup(
    name = 'domainmodel',
    version = __version__,
    package_dir = { '' : 'src' },
    packages = find_packages('src'),
    scripts = ["bin/domainmodel-admin", "bin/domainmodel-test"],
    zip_safe = False,
    include_package_data = True,
    # no way to specify the dependency on django as we need a specific revision
    install_requires = [
        'SQLObject>=0.7.10, <=0.10.2',
        'simplejson',
        'markdown',
        # for mx datetime
        'egenix-mx-base',
        # 'Django>=0.95'  # Django not served on cheese shop
    ],

    # metadata for upload to PyPI
    author = 'Appropriate Software Foundation, Open Knowledge Foundation',
    author_email = 'kforge-dev@lists.okfn.org',
    license = 'GPL',
    url = 'http://appropriatesoftware.net/domainmodel/Home.html',
    download_url = 'http://appropriatesoftware.net/provide/docs/domainmodel-%s.tar.gz' % __version__,
    description = 'Toolkit for domain model-based enterprise application frameworks.',
    long_description = \
"""
DomainModel provides a toolkit for domain model-based enterprise application frameworks.

Please refer to the Features page of the domainmodel website for more information.

http://appropriatesoftware.net/domainmodel/Home.html

""",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

