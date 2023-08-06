#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:

from distutils.core import setup

LONG_DESCRIPTION = """This module supports the calculation of ISBN checksums with
``calculate_checksum()``, the conversion between ISBN-10 and ISBN-13 with
``convert()`` and the validation of ISBNs with ``validate()``.

All the ISBNs must be passed in as ``str`` types, even if it would seem
reasonable to accept some ``int`` forms.  The reason behind this is English
speaking countries use ``0`` for their group identifier, and Python would treat
ISBNs beginning with ``0`` as octal representations producing incorrect results.
While it may be feasible to allow some cases as non-``str`` types the complexity
in design and usage isn't worth the minimal benefit.

The functions in this module also support 9-digit SBNs for people with older
books in their collection.
"""

def main():
    setup(
        name="pyisbn",
        version="0.5.2",
        description="A module for working with 10- and 13-digit ISBNs",
        long_description=LONG_DESCRIPTION,
        author="James Rowe",
        author_email="jnrowe@gmail.com",
        url="http://www.jnrowe.ukfsn.org/projects/pyisbn.html",
        packages=["pyisbn", ],
        license="GNU General Public License Version 3",
        keywords="ISBN ISBN-10 ISBN-13 SBN",
        classifiers=['Development Status :: 4 - Beta',
            'Intended Audience :: Other Audience',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.4',
            'Programming Language :: Python :: 2.5',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 3',
            'Topic :: Other/Nonlisted Topic',
            'Topic :: Text Processing :: Indexing',
        ],
    )

if __name__ == "__main__":
    main()

