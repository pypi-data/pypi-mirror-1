from distutils.core import setup

# patch distutils if it can't cope with the "classifiers" or "download_url"
# keywords (prior to python 2.3.0).
from distutils.dist import DistributionMetadata
if not hasattr(DistributionMetadata, 'classifiers'):
    DistributionMetadata.classifiers = None
if not hasattr(DistributionMetadata, 'download_url'):
    DistributionMetadata.download_url = None
    
setup(
    name = 'pyunv',
    version = '0.1a1',
    description = 'BusinessObjects universe file (*.unv) parser',
    long_description = """\
BusinessObjects universe file (*.unv) parser
-------------------------------------

Reads these objects from the universe file:
 - Universe parameters
 - Tables
 - Virtual Tables
 - Classes
 - Objects
 - Conditions
 - Joins (coming soon)

Requires Python 2.6 or later
""",
    author='David Peckham',
    author_email = 'dave.peckham@me.com',
    url = 'http://web.me.com/dave.peckham/python/PyUnv.html',
    download_url = 'http://web.me.com/dave.peckham/python/PyUnv_files/',
    license = "LGPL",
    platforms = ['POSIX', 'Windows'],
    keywords = ['encoding'],
    classifiers = [
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    packages = ['pyunv']
    )
