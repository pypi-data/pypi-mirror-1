#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebseq package released under the MIT license.
#

"""
Import as usual
---------------

    >>> import nebseq

Reverse complements
-------------------

The only note here is that `revcomp` does not check the input
sequence to see if it looks like DNA or RNA. 

    >>> nebseq.revcomp('ACGT')
    'ACGT'
    >>> nebseq.revcomp('TTACC')
    'GGTAA'

And if we give it garbage it just gives us garbage back.
    
    >>> nebseq.revcomp('ZQ')
    'QZ'

Translation
-----------

The translation function should allow for full support of sequence
translation. This includes things like trimming the first couple
bases and using alternate translation tables. There is also
support for the more esoteric post translational modifications
that can be found in some Genbank files as well as translating
partial peptides (for things like fuzzy coordinates).

Basic translation:

    >>> nebseq.translate('TTGGCCAAGGAACGA', table=11)
    'MAKER'

Showing the effects of a partial peptide translation. By default
the first codon should be a start codon according to the selected
translation table, if not then its converted to an 'X'

    >>> nebseq.translate('GCCAAG')
    'XK'
    >>> nebseq.translate('GCCAAG', partial=True)
    'AK'

Or we can remove the first couple of bases for fuzzy coordinates.

    >>> nebseq.translate('TTGCCAAG', start=2, partial=True)
    'AK'

Modifications are specified as an (index, amino_acid) two-tuple. Notice
that modification indexes are specified as one-based indexes into the
amino acid sequence.

    >>> nebseq.translate('ATGAAGGAA', modifications=[(2, 'U')])
    'MUE'

Extraction
----------

Sequence extraction is for when you want to slice out part of a larger
sequence. This is useful if you use the `nebgb` module and its
definition of locations parsed from strings like `join(1..5,9..100)`.

    >>> location = {'type': 'span', 'from': 4, 'to': 10}
    >>> nebseq.extract('ACCGTACCATAGTT', location)
    ('GTACCAT', (False, False))
    >>> location = {
    ...     "type": "complement",
    ...     "segment": {
    ...         "type": "join",
    ...         "segments": [
    ...             {"type": "span", "from": 3, "to": 8},
    ...             {"type": "span", "from": 10, "to": 14}
    ...         ]
    ...     }
    ... }
    >>> nebseq.extract('ACCGTATTTCGGGGACAT', location)
    ('CCCCGAATACG', (False, False))


"""

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

setup(
    name = "nebseq",
    description = "Basic Biological Sequence Manipulations",
    long_description = __doc__,
    author = "Paul Joseph Davis",
    author_email = "davisp@neb.com",
    url = "http://github.com/davisp/nebseq",
    version = "0.0.1",
    license = "MIT",
    keywords = "bioinformatics sequence reverse-complement translation",
    platforms = ["any"],
    zip_safe = False,

    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],

    py_modules = ["nebseq"],

    setup_requires = ["setuptools>=0.6c8"],
    tests_require = ["nose>=0.10.0"],

    test_suite = "nose.collector"
)
