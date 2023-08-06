from distutils.core import setup

# patch distutils if it can't cope with the "classifiers" or "download_url"
# keywords (prior to python 2.3.0).
from distutils.dist import DistributionMetadata
if not hasattr(DistributionMetadata, 'classifiers'):
    DistributionMetadata.classifiers = None
if not hasattr(DistributionMetadata, 'download_url'):
    DistributionMetadata.download_url = None
    
setup(
    name = 'addhrefs',
    version = '0.9.6',
    description = 'Adds HTML links to text',
    long_description = """\
addhrefs.py
---------------------

Turns plain text into HTML with links on URLs and email addresses

Recommended: Python 2.3 or later
""",
    author='Peter Bengtsson',
    author_email = 'mail@peterbe.com',
    url = 'http://www.peterbe.com',
    download_url = 'http://www.peterbe.com/plog/add-hrefs-III',
    license = "Python",
    platforms = ['POSIX', 'Windows'],
    keywords = ['addhrefs', 'linkifyer', 'urlfinder', 'emailfinder'],
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Communications",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Other/Nonlisted Topic",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    py_modules = ['addhrefs',]
    )
