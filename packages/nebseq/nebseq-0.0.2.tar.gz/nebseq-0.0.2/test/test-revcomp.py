# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the BioNEB package released
# under the MIT license.
#
import t
def test_simple():
    t.eq(t.revcomp("ACGT"), "ACGT")
    t.eq(t.revcomp("TGGGGCCAA"), "TTGGCCCCA")
    t.eq(t.revcomp("CCCCA"), "TGGGG")
    t.eq(t.revcomp("MDggC"), "GccHK")

def test_degenerate():
    # This was a fun one to figure out.
    t.eq(t.revcomp("W"), "W")
    t.eq(t.revcomp("S"), "S")
