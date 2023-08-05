import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

name = "zc.rst2"
setup(
    name = name,
    version = "0.2",
    author = "Jim Fulton",
    author_email = "jim@zope.com",
    description = "Script for converting reStructuredText to various formats",
    long_description= read('README.txt'),
    license = "ZPL 2.1",
    keywords = "reStructutedText",
    url='http://www.python.org/pypi/'+name,

    install_requires = ['docutils', 'setuptools'],
    data_files = [('.', ['README.txt'])],
    packages = ['zc', 'zc.rst2'],
    package_dir = {'': 'src'},
    namespace_packages = ['zc'],
    include_package_data = True,
    entry_points = {'console_scripts': ['rst2 = %s:main' % name]}, 
    zip_safe=True,
    )
