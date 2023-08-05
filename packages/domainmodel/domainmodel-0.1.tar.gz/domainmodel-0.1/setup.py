from setuptools import setup, find_packages

# get the version number 
import sys
sys.path.insert(0, './src')
from dm import __version__

setup(
    name = 'domainmodel',
    version = __version__,
    package_dir = { '' : 'src' },
    packages = find_packages('src'),
    
    # no way to specify the dependency on django as we need a specific revision
    install_requires = ['SQLObject>=0.6,<=0.7.99'], # 'Django>=0.95,'],

    # metadata for upload to PyPI
    author = 'Open Knowledge Foundation',
    author_email = 'kforge-dev@lists.okfn.org',
    license = 'LGPL',
    url = 'http://www.kforgeproject.com/',
    download_url = 'http://www.kforgeproject.com/files/domainmodel-%s.tar.gz' % __version__,
    description = 'Framework for enterprise applications.',
    long_description = \
"""
DomainModel provides a framework for enterprise software applications.
""",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'],
)

