from setuptools import setup, find_packages

install_requires = ['BeautifulSoup']

classifiers = """
Intended Audience :: Education
Intended Audience :: Developers
Intended Audience :: Information Technology
License :: OSI Approved :: GNU General Public License (GPL)
Programming Language :: Python
Development Status :: 3 - Alpha
"""

setup(
    name = 'iii',
    version = '0.3',  # remember to update iii/__init__.py on release!
    url = 'http://bitbucket.org/anarchivist/iii',
    author = 'Mark A. Matienzo',
    author_email = 'mark@matienzo.org',
    license = 'GPL',
    packages = find_packages(),
    install_requires = install_requires,
    description = 'Utilities to work with the Innovative Interfaces, Inc.' + \
                    ' integrated library system',
    classifiers = filter(None, classifiers.split('\n')),
)
