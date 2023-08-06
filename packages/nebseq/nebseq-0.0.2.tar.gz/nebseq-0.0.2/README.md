
nebseq - Basic Biological Sequence Manipulations
================================================

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

