# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebseq package released under the MIT license.
#
import string

DEGENERATES = {
    "A": "A",   "C": "C",   "G": "G",   "T": "T",   "U": "U",
    "W": "AT",  "S": "CG",  "M": "AC",  "K": "GT",  "R": "AG",  "Y": "CT",
    "B": "AGT", "D": "ACT", "H": "ACT", "V": "ACG", "N": "ACGT"
}

COMPLEMENTS = [
    "ACGTUNSWMKRYVDHBacgtunswmkryvdhb",
    "TGCAANSWKMYRBHDVtgcaanswkmyrbhdv"
]
TRANSTABLE = string.maketrans(COMPLEMENTS[0], COMPLEMENTS[1])

def revcomp(seq):
    """
    Given a DNA or RNA sequence return the reverse complement. Makes
    no checks to verify that the input sequence is actually DNA or RNA.
    
    Degenerate bases are also complemented.
    """
    return seq.translate(TRANSTABLE)[::-1]

# Three letter codes
AMINO_ACID_TLC = {
    "ALA": "A", "ASX": "B", "CYS": "C", "ASP": "D", "GLU": "E", "PHE": "F",
    "GLY": "G", "HIS": "H", "ILE": "I", "LYS": "K", "LEU": "L", "MET": "M",
    "ASN": "N", "PYL": "O", "PRO": "P", "GLN": "Q", "ARG": "R", "SER": "S",
    "THR": "T", "SEC": "U", "VAL": "V", "TRP": "W", "XAA": "X", "TYR": "Y",
    "GLX": "Z",
    # Due to Genbank awesomeness
    "OTHER": "X", 
    "TERM": "*"
}

def _codons():
    return [
        "%s%s%s" % (b1, b2, b3)
        for b1 in "TCAG"
        for b2 in "TCAG"
        for b3 in "TCAG"
    ]
CODONS = _codons()

CODON_TABLE_DATA = [
# 1 TTTTTTTTTTTTTTTTCCCCCCCCCCCCCCCCAAAAAAAAAAAAAAAAGGGGGGGGGGGGGGGG
# 2 TTTTCCCCAAAAGGGGTTTTCCCCAAAAGGGGTTTTCCCCAAAAGGGGTTTTCCCCAAAAGGGG
# 3 TCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAG
    """1
    FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG
    ---M---------------M---------------M----------------------------""",
    """2
    FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIMMTTTTNNKKSS**VVVVAAAADDEEGGGG
    --------------------------------MMMM---------------M------------""",
    """3
    FFLLSSSSYY**CCWWTTTTPPPPHHQQRRRRIIMMTTTTNNKKSSRRVVVVAAAADDEEGGGG
    ----------------------------------MM----------------------------""",
    """4
    FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG
    --MM---------------M------------MMMM---------------M------------""",
    """5
    FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIMMTTTTNNKKSSSSVVVVAAAADDEEGGGG
    ---M----------------------------MMMM---------------M------------""",
    """6
    FFLLSSSSYYQQCC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG
    -----------------------------------M----------------------------""",
    """9
    FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIIMTTTTNNNKSSSSVVVVAAAADDEEGGGG
    -----------------------------------M---------------M------------""",
    """10
    FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG
    ---M---------------M------------MMMM---------------M------------""",
    """11
    FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG
    ---M---------------M------------MMMM---------------M------------""",
    """12
    FFLLSSSSYY**CC*WLLLSPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG
    -------------------M---------------M----------------------------""",
    """13
    FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIMMTTTTNNKKSSGGVVVVAAAADDEEGGGG
    ---M------------------------------MM---------------M------------""",
    """14
    FFLLSSSSYYY*CCWWLLLLPPPPHHQQRRRRIIIMTTTTNNNKSSSSVVVVAAAADDEEGGGG
    -----------------------------------M----------------------------""",
    """15
    FFLLSSSSYY*QCC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG
    -----------------------------------M----------------------------""",
    """16
    FFLLSSSSYY*LCC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG
    -----------------------------------M----------------------------""",
    """21
    FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIMMTTTTNNNKSSSSVVVVAAAADDEEGGGG
    -----------------------------------M---------------M------------""",
    """22
    FFLLSS*SYY*LCC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG
    -----------------------------------M----------------------------""",
    """23
    FF*LSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG
    --------------------------------M--M---------------M------------"""
]

CODON_TABLES = {}
class TranslationTable(object):
    def __init__(self, codons, starts):
        """
        You shouldn't need to create translation tables by hand. You can
        access the predefined tables in nebseq.CODON_TABLES using the
        table's integer id.
        """
        self.codons = codons
        self.starts = starts
    def translate(self, codon, is_stop=False):
        """
        Translate a three letter codon into the appropriate amino acid.
        
        `is_stop` is a boolean that determines if the codon should
        be translated as a '*' or 'X'.

        Returns an (acid, is_start) tuple where is_start is a boolean
        that flags if this should be translated as 'M' when in the
        first position of an mRNA transcript.

        Handles degenerate amino acid codes 'B', 'Z', and 'J'.
        """
        assert len(codon) == 3, "Invalid codon: %s" % codon
        degen = map(lambda b: DEGENERATES.get(b, b), codon)
        degencodons = [
            "%s%s%s" % (b1, b2, b3)
            for b1 in degen[0]
            for b2 in degen[1]
            for b3 in degen[2]
        ]
        acids = set(map(lambda x: self.codons.get(x, 'X'), degencodons))
        starts = set(map(lambda x: self.starts.get(x, False), degencodons))
        if len(acids) == 1 and acids == set("*") and not is_stop:
            acid = "X"
        elif len(acids) == 1:
            acid = acids.pop()
        elif acids == set("DN"):
            acid = "B"
        elif acids == set("EQ"):
            acid = "Z"
        elif acids == set("IL"):
            acid = "J"
        else:
            acid = "X"
        if len(starts) > 1:
            start = False
        else:
            start = starts.pop()
        return (acid, start)

def _mk_tables():
    for tbl in [t.split() for t in CODON_TABLE_DATA]:
        tid = int(tbl[0])
        trans = dict(zip(CODONS, tbl[1]))
        starts = dict(zip(CODONS, map(lambda x: x == "M", tbl[2])))
        CODON_TABLES[tid] = TranslationTable(trans, starts)
_mk_tables()

def translate(seq, table=1, start=0, modifications=None, partial=False):
    """
    Translate a DNA sequence into it's amino acid representation.

    `seq` is the input sequence
    `table` is the integer id of the translation table
    `start` is the index at which to start translation
    `modifications` is a list of 2-tuples that are an (`index`, `replacement`)
        pair. `index` must be a multiple of three and accounts for the
        `start` offset. `replacement` should be the amino acid to insert.
    `partial` is a boolean that determines whether to process the first
        and last amino acids for start and stop status. It can also be
        a tuple of (start, stop) that selectively processes either end
        of the sequence.
    """
    if start > 0:
        seq = seq[start:]
    if modifications is None:
        modifications = []
    if isinstance(partial, bool):
        partial = (partial, partial)
    if table not in CODON_TABLES:
        raise ValueError("Unknown translation table: %s" % table)
    if len(seq) < 3:
        raise ValueError("Sequnce length is too short.")
    if len(seq) % 3 != 0:
        raise ValueError("Sequence length is not a multiple of three.")
    t = CODON_TABLES[table]
    (acid, is_start) = t.translate(seq[:3], len(seq) == 3)
    if not partial[0] and is_start:
        ret = ["M"]
    elif not partial[0] and start < 1:
        ret = ["X"]
    else:
        ret = [acid]
    seqlen = len(seq)
    for i in xrange(3, seqlen-(seqlen%3), 3):
        ret.append(t.translate(seq[i:i+3], i == len(seq) - 3)[0])
    ret = ''.join(ret)
    for m in modifications:
        idx = m[0]-1
        if idx < 0 or idx >= len(ret):
            raise IndexError("Invalid modification coordinate: %s" % m[0])
        ret = "%s%s%s" % (ret[:idx], m[1], ret[idx+1:])
    if not partial[1] and ret[-1:] == "*":
        ret = ret[:-1]
    return ret


EXTRACT_TYPES = {}
def extract(sequence, location, one_based=True):
    """
    Exctract a subsequence from a larger molecule using a nested dict location
    specification. The understood dictionary types are:
    
        {"type": "complement", "segment": SUB_DICT}
        {"type": "join": "segments": [LIST_OF_SUBDICTS]}
        {"type": "span", "from": INT, "to": INT, "modifiers": OPTIONAL}
            MODIFIERS = {"from": "fuzzy", "to": "fuzzy"} both keys are optional
        {"type": "index", "position": INT}
        
    These specifications are designed to match up with how the nebgb package
    extracts location information from Genbank files.
    
    `one_based` is a boolean that determines if offsets start at 0 or 1.
        Defaults to True for ease of use with Genbank style specifications.

    This function returns a two-tuple of (sequence, (from_fuzzy, to_fuzzy))
    """
    loctype = location["type"]
    func = EXTRACT_TYPES.get(loctype)
    if not func:
        raise ValueError("Unknown location type: %r" % loctype)
    return func(sequence, location, one_based)

def _extract_comp(seq, loc, one_based):
    assert loc["type"] == "complement"
    seq, (start, stop) = extract(seq, loc["segment"], one_based)
    return (revcomp(seq), (stop, start))

def _extract_join(seq, loc, one_based):
    assert loc["type"] == "join"
    data = map(lambda l: extract(seq, l, one_based), loc["segments"])
    if len(data) > 1:
        for d in data[1:-1]:
            if d[1] != (False, False):
                raise ValueError("Internal join segments cannot be fuzzy.")
        if data[0][1][1] != False:
            raise ValueError("First join segment cannot have a fuzzy end.")
        if data[-1][1][0] != False:
            raise ValueError("Last join segment cannot have a fuzzy start.")
    seq = ''.join(s[0] for s in data)
    return (seq, (data[0][1][0], data[-1][1][1]))

def _extract_span(seq, loc, one_based):
    assert loc["type"] == "span"
    fr = int(loc["from"])
    to = int(loc["to"])
    if to < fr:
        raise IndexError("'from' must be less than 'to': %d > %d" % (fr, to))
    if one_based:
        fr -= 1
        to -= 1
    if fr < 0:
        raise IndexError("'from' coordinate must be positive: %d" % fr)
    if fr > len(seq):
        raise IndexError("'from' coordinate exceeds sequence length: %d" % fr)
    if to < 0:
        raise IndexError("'to' coordinate must be positive: %d" % to)
    if to > len(seq):
        raise IndexError("'to' cooridnate exceeds sequence length: %d" % to)
    frfuzzy = loc.get("modifiers", {}).get("from") == "fuzzy"
    tofuzzy = loc.get("modifiers", {}).get("to") == "fuzzy"
    return (seq[fr:to+1], (frfuzzy, tofuzzy))

def _extract_index(seq, loc, one_based):
    assert loc["type"] == "index"
    pos = int(loc["position"])
    if one_based:
        pos -= 1
    if pos < 0:
        raise IndexError("'position' must be positive: %d" % pos)
    if pos > len(seq):
        raise IndexError("'position' exceeds sequence length: %d" % pos)
    fuzz = loc.get("fuzzy", False)
    return (seq[pos], (fuzz, fuzz))

EXTRACT_TYPES.update({
    "complement": _extract_comp,
    "join": _extract_join,
    "span": _extract_span,
    "index": _extract_index
})