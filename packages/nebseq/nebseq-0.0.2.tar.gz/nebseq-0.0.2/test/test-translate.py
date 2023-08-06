# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the BioNEB package released
# under the MIT license.
#
import t

def test_single():
    t.eq(t.translate("TGG", partial=True), "W")
    t.eq(t.translate("CTG", table=11, partial=True), "L")

def test_alternate():
    t.eq(t.translate("TGA", partial=True), "*")
    t.eq(t.translate("TGA", table=2, partial=True), "W")

def test_length_check():
    t.raises(ValueError, t.translate, "AC")

def test_table_check():
    t.raises(ValueError, t.translate, "TTGTTG", -1)

def test_start_codon_replace():
    t.eq(t.translate("TTGTTG"), "ML")

def test_simple_degenerate():
    t.eq(t.translate("ACN", partial=True), "T")

def test_degenerate_causes_not_start():
    t.eq(t.translate("GTG", table=2), "M")
    t.eq(t.translate("GTG", table=2, partial=True), "V")
    t.eq(t.translate("GTR", table=2), "X")
    t.eq(t.translate("GTR", table=2, partial=True), "V")

def test_degnerate_to_X():
    t.eq(t.translate("CAY", partial=True), "H")
    t.eq(t.translate("CAR", partial=True), "Q")
    t.eq(t.translate("CAN", partial=True), "X")

def test_degenerate_error():
    t.eq(t.translate("ATG", table=11, partial=True), "M")
    t.eq(t.translate("ATC", table=11, partial=True), "I")
    t.eq(t.translate("ATS", table=11, partial=True), "X")

def test_degenerate_in_seq():
    seq = "CTGATCGTCATSTGTATCACC"
    t.eq(t.translate(seq, table=11, partial=True), "LIVXCIT")

def test_degenerate_regresion():
    t.eq(t.translate("GCGCCCAAKACGCAA", table=11, partial=True), "APXTQ")

def test_degenerates():
    t.eq(t.translate("RAY", partial=True), "B")
    t.eq(t.translate("SAG", partial=True), "Z")
    t.eq(t.translate("MTT", partial=True), "J")

def test_codon_start():
    seq = "CTATGATCGTCATCTGTATCACC"
    t.raises(ValueError, t.translate, seq)
    t.eq(t.translate(seq, start=2), "MIVICIT")

def test_modified():
    seq = "CTGATCGTCATSTGTATCACC"
    trans = t.translate(seq, table=11, partial=True, modifications=[(3, "W")])
    t.eq(trans, "LIWXCIT")

def test_partial():
    seq = "AAACTGCTTTAA"
    t.eq(t.translate(seq), "XLL")
    t.eq(t.translate(seq, partial=True), "KLL*")
    t.eq(t.translate(seq, partial=(True, False)), "KLL")
    t.eq(t.translate(seq, partial=(False, True)), "XLL*")
    t.eq(t.translate(seq, partial=(False, False)), "XLL")
