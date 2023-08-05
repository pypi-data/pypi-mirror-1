from setuptools import setup, find_packages

from svnrepo import __version__

setup(
    name = 'svnrepo',
    version = __version__,
    py_modules=['svnrepo'],
    scripts = [],

    # metadata for upload to PyPI
    author = "Rufus Pollock (Open Knowledge Foundation)",
    author_email = "rufus@rufuspollock.org",
    description = \
"A pythonic API to a local subversion repository.",
    long_description = \
"""
A pythonic API to a local subversion repository using the official subversion python bindings.
""",
    license = "MIT",
    keywords = "svn subversion python api",
    url = "http://www.rufuspollock.org/code/svnrepo/", 
    download_url = "http://www.rufuspollock.org/code/svnrepo/svnrepo.py",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'],
)
