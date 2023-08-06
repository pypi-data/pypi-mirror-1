
import t

def test_basic():
    loc = {"type": "span", "from": 2, "to": 3}
    t.eq(t.extract("ACGT", loc), ("CG", (False, False)))

def test_join():
    loc = {
        "type": "join",
        "segments": [
            {"type": "span", "from": 2, "to": 3},
            {"type": "span", "from": 5, "to": 7}
        ]
    }
    t.eq(t.extract("ACGTACGT", loc), ("CGACG", (False, False)))

def test_complement():
    loc = {
        "type": "complement",
        "segment": {"type": "span", "from": 2, "to": 6}
    }
    t.eq(t.extract("ACCGTT", loc), ("AACGG", (False, False)))

def test_index():
    loc = {"type": "index", "position": 3}
    t.eq(t.extract("ACGTAG", loc), ("G", (False, False)))

def test_fuzzy_span():
    mods = {"from": "fuzzy", "to": "fuzzy"}
    loc = {"type": "span", "from": 2, "to": 3, "modifiers": mods}
    t.eq(t.extract("TCGGGA", loc), ("CG", (True, True)))

def test_fuzzy_join():
    mod1 = {"from": "fuzzy"}
    mod2 = {"to": "fuzzy"}
    loc = {
        "type": "join",
        "segments": [
            {"type": "span", "from": 2, "to": 3, "modifiers": mod1},
            {"type": "span", "from": 5, "to": 7, "modifiers": mod2}
        ]
    }
    t.eq(t.extract("TGGCACGTAA", loc), ("GGACG", (True, True)))
    loc["segments"][0]["modifiers"] = mod2
    t.raises(ValueError, t.extract, "ACGTATACACT", loc)
    del loc["segments"][0]["modifiers"]
    loc["segments"][1]["modifiers"] = mod1
    t.raises(ValueError, t.extract, "ACGTATACACT", loc)

def test_fuzzy_internal_join():
    mod1 = {"from": "fuzzy"}
    mod2 = {"to": "fuzzy"}
    loc = {
        "type": "join",
        "segments": [
            {"type": "span", "from": 2, "to": 3},
            {"type": "span", "from": 4, "to": 5, "modifiers": mod1},
            {"type": "span", "from": 6, "to": 7}
        ]
    }
    t.raises(ValueError, t.extract, "ACGTATACACT", loc)
    loc["segments"][1]["modifiers"] = mod2
    t.raises(ValueError, t.extract, "ACGTATACACT", loc)
    del loc["segments"][1]["modifiers"]
    t.eq(t.extract("ACGTATACACT", loc), ("CGTATA", (False, False)))
    
def test_bad_span_indexes():
    locs = [
        {"type": "span", "from": 10, "to": 1},
        {"type": "span", "from": 10, "to": 20},
        {"type": "span", "from": -1, "to": 10},
        {"type": "span", "from": 1, "to": 10},
        {"type": "index", "position": -1},
        {"type": "index", "position": 10}
    ]
    for l in locs:
        t.raises(IndexError, t.extract, "ACG", l)

def test_bad_type():
    loc = {"type": "choice", "positions": [1, 5]}
    t.raises(ValueError, t.extract, "ACT", loc)