from setuptools import setup, find_packages
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
    install_requires = [
        'SQLObject>=0.7.10, <=0.12.0',
        'simplejson',
        'markdown>=1.7, <=2.0.1',
        'egenix-mx-base', # for mx datetime
        'django>=0.96.3,<=1.1'
    ],
    # Metadata for upload to PyPI.
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

