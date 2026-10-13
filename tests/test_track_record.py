import re

from sim.track_record import record_text

IDENTIFYING = ("Bolsonaro", "Lula", "PEC", "Eletrobras", "Rio Grande", "pandemic", "tariff", "Hunger", "reform", "court-ordered")


def test_record_has_no_years_or_named_events():
    for group in ("pl", "pt"):
        text = record_text(group)
        assert not re.search(r"\b(19|20)\d\d\b", text), text
        for word in IDENTIFYING:
            assert word not in text, (group, word)


def test_record_keeps_the_numbers_of_each_year():
    pl, pt = record_text("pl"), record_text("pt")
    assert pl.count("- Year ") == 2 and pt.count("- Year ") == 3
    assert "-1.20" in pl and "0.55" in pl
    assert "-2.42" in pt and "-0.39" in pt
