# vim:fileencoding=utf-8
"""setup script for ``reindent``, originally created by Tim Peters"""

import sys
from setuptools import setup


VERSION = '0.1.0'
ENTRY_POINTS = \
"""[console_scripts]
reindent = reindent:main
"""


def main():
    """just wraps call to ``setup``"""
    setup(name='Reindent', version=VERSION,
        author="Tim Peters", author_email='nottimsemail@notadomain.foo',
        maintainer="Dan Buch", maintainer_email="daniel.buch@gmail.com",
        description='reindent script by Tim Peters',
        keywords=['reindent', 'pep8', 'syntax', 'lint', 'tab', 'space'],
        entry_points=ENTRY_POINTS,
        classifiers=[
            "Development Status :: 6 - Mature",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "License :: Public Domain",
            "Natural Language :: English",
            "Programming Language :: Python",
            "Topic :: Software Development :: Quality Assurance",
            ],
        long_description=''.join([l for l in _get_long_description()]),
        platforms=['all'], license="Public Domain",
        py_modules=['reindent'],
        )
    return 0


def _get_long_description(fname='README.txt'):
    for line in open(fname, 'rb'):
        yield line


if __name__ == '__main__':
    sys.exit(main())
