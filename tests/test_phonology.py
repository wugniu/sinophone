from itertools import combinations, product

from sinophone import options
from sinophone.phonetics import IPAConsonant, IPAFeatureGroup, IPAString
from sinophone.phonology import (
    Coda,
    Final,
    Initial,
    Medial,
    Nucleus,
    PhonologicalRule,
    Phonology,
    PhonotacticAcceptability,
    PhonotacticConstraint,
    Syllable,
    SyllableFeatures,
    SyllableInPhonology,
    Tone,
)

from .utils import BaseTestCase


class TestSyllableComponent(BaseTestCase):
    def test_order(self) -> None:
        with self.assertRaises(TypeError):
            Initial("k") < "k"
        self.assertLess(Initial("k"), Medial("k"))

    def test_has_features(self) -> None:
        self.assertTrue(Coda("k").has_features(IPAFeatureGroup("voiceless velar stop")))
        self.assertFalse(Coda("k").has_features(IPAFeatureGroup("-voiceless")))
        self.assertTrue(
            Initial("pf").has_features(IPAFeatureGroup("+non-sibilant-fricative"))
        )

    def test_eq_hash(self) -> None:
        self.assertEqualAndHashEqual(
            Initial("k"), Initial(IPAString([IPAConsonant("voiceless velar stop")]))
        )
        self.assertNotEqualAndHashNotEqual(Initial("k"), Coda("k"))

    def test_color_str_repr(self) -> None:
        options.color = False
        str(Initial("k"))
        repr(Initial("k"))

        options.color = True
        str(Initial("k"))
        repr(Initial("k"))


class TestLeafSyllableComponent(BaseTestCase):
    def test_init_eq_hash(self) -> None:
        with self.assertRaises(TypeError):
            Initial(IPAConsonant("voiceless velar stop"))

        k_initial1 = Initial("k")
        k_initial2 = Initial(IPAString("k"))
        k_initial3 = Initial(Coda("k"))

        self.assertEqualAndHashEqual(k_initial1, k_initial2)
        self.assertEqualAndHashEqual(k_initial2, k_initial3)

    def test_ipa_str(self) -> None:
        k_initial = Initial("k")
        self.assertEqualAndHashEqual(k_initial.ipa_str, IPAString("k"))
        self.assertEqualAndHashEqual(str(k_initial), "k")


class TestBranchSyllableComponent(BaseTestCase):
    def test_init_eq_hash_sub_components_ipa_str_char(self) -> None:
        k = Initial("k")
        u = Medial("ʷ")
        a = Nucleus("ɐ")
        q = Coda("ʔ")
        清入 = Tone("˥˥")

        uaq = Final(u, a, q)
        self.assertEqualAndHashEqual(uaq, Final(u, a, Coda("ʔ")))
        kuaq = Syllable(k, uaq, 清入)
        self.assertEqualAndHashEqual(kuaq, Syllable(k, uaq, Tone("˥˥")))

        self.assertEqual(uaq.sub_components, [u, a, q])
        self.assertEqualAndHashEqual(
            frozenset(kuaq.recursive_sub_components),
            frozenset([k, u, a, q, 清入, uaq]),
        )

        self.assertEqualAndHashEqual(
            kuaq.ipa_str, k.ipa_str + u.ipa_str + a.ipa_str + q.ipa_str + 清入.ipa_str
        )

        self.assertEqualAndHashEqual(
            k.ipa_chars[0], IPAConsonant("voiceless velar stop")
        )


class TestTone(BaseTestCase):
    def test_validate(self) -> None:
        Tone("˥ʔ")
        with self.assertRaises(ValueError):
            Tone("lol")


class TestSyllableFeatures(BaseTestCase):
    def test_init_hash_str(self) -> None:
        sf1 = SyllableFeatures(
            {
                "Initial": {IPAFeatureGroup("+bilabial")},
                "Medial": {IPAFeatureGroup("+labialized")},
            }
        )
        sf2 = SyllableFeatures(
            {
                "Medial": {-IPAFeatureGroup("-labialized")},
                "Initial": {IPAFeatureGroup("bilabial")},
            }
        )
        self.assertEqualAndHashEqual(sf1, sf2)

        str(sf1)

    def test_call(self) -> None:
        k = Initial("k")
        u = Medial("ʷ")
        a = Nucleus("ɐ")
        q = Coda("ʔ")
        清入 = Tone("˥˥")
        uaq = Final(u, a, q)
        kuaq = Syllable(k, uaq, 清入)

        sf1 = SyllableFeatures(
            {
                "Initial": {IPAFeatureGroup("+bilabial")},
                "Coda": {IPAFeatureGroup("+voiceless +stop")},
            }
        )
        sf2 = SyllableFeatures(
            {
                "Initial": {IPAFeatureGroup("+velar")},
                "Coda": {IPAFeatureGroup("+voiceless +stop")},
            }
        )
        sf3 = SyllableFeatures(
            {
                "Initial": {
                    IPAFeatureGroup("+bilabial"),
                    IPAFeatureGroup("+velar +voiceless"),
                },
                "Coda": {IPAFeatureGroup("+voiceless +stop")},
            }
        )

        self.assertFalse(sf1(kuaq))
        self.assertTrue(sf2(kuaq))
        self.assertTrue(sf3(kuaq))


class TestPhonotacticAcceptability(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        pa1 = PhonotacticAcceptability(False, False)
        pa2 = PhonotacticAcceptability(True, False)
        pa3 = PhonotacticAcceptability(False, True)
        pa4 = PhonotacticAcceptability(True, True)
        self.pas = [pa1, pa2, pa3, pa4]

    def test_eq_hash(self) -> None:
        for pa1, pa2 in combinations(self.pas, 2):
            self.assertNotEqualAndHashNotEqual(pa1, pa2)

        self.assertEqualAndHashEqual(self.pas[0], PhonotacticAcceptability())

    def test_and(self) -> None:
        self.assertEqualAndHashEqual(
            self.pas[1] & self.pas[2], PhonotacticAcceptability(False, False)
        )

        pas = set()
        for pa1, pa2 in product(self.pas, self.pas):
            pas.add(pa1 & pa2)
        self.assertEqualAndHashEqual(frozenset(pas), frozenset(self.pas))

        with self.assertRaises(TypeError):
            self.pas[0] & "foo"

    def test_or(self) -> None:
        self.assertEqualAndHashEqual(
            self.pas[1] | self.pas[2], PhonotacticAcceptability(True, True)
        )

        pas = set()
        for pa1, pa2 in product(self.pas, self.pas):
            pas.add(pa1 | pa2)
        self.assertEqualAndHashEqual(frozenset(pas), frozenset(self.pas))

        with self.assertRaises(TypeError):
            self.pas[0] | "foo"


class TestSyllableInPhonology(BaseTestCase):
    def test_color(self) -> None:
        pa1 = PhonotacticAcceptability(False, False)
        pa2 = PhonotacticAcceptability(True, False)
        pa3 = PhonotacticAcceptability(False, True)
        pa4 = PhonotacticAcceptability(True, True)
        pas = [pa1, pa2, pa3, pa4]

        for pa in pas:
            syllable = SyllableInPhonology()
            syllable.acceptability = pa
            self.assertNotEqual(syllable.color, "")


class TestPhonotacticConstraint(BaseTestCase):
    def test_eq_hash_apply(self) -> None:
        sf = SyllableFeatures(
            {
                "Initial": {IPAFeatureGroup("+stop +voiced")},
                "Tone": {IPAFeatureGroup("+extra-high-level")},
            }
        )
        pa = PhonotacticAcceptability(False, False)
        pc = PhonotacticConstraint(sf, pa)

        self.assertEqualAndHashEqual(pc, PhonotacticConstraint(sf, pa))

        bo1 = Syllable(Initial("b"), Final(nucleus=Nucleus("o")), Tone("˥˧"))
        bo2 = Syllable(Initial("b"), Final(nucleus=Nucleus("o")), Tone("˨˧"))

        self.assertEqualAndHashEqual(pc.apply(bo1).acceptability, pa)
        self.assertNotEqualAndHashNotEqual(pc.apply(bo2).acceptability, pa)


class TestPhonologicalRule(BaseTestCase):
    def test_eq_hash_apply(self) -> None:
        sf = SyllableFeatures({"Final": {IPAFeatureGroup("+nasal")}})
        pr = PhonologicalRule(Nucleus("o"), IPAString("ʊ̃"), sf)

        self.assertEqualAndHashEqual(
            pr, PhonologicalRule(Nucleus("o"), IPAString("ʊ̃"), sf)
        )

        lon = Syllable(
            Initial("l"), Final(nucleus=Nucleus("o"), coda=Coda("ŋ")), Tone("˨˧")
        )

        lon = pr.apply(lon)
        self.assertEqualAndHashEqual(lon.phonetic_ipa_str, IPAString("lʊ̃ŋ˨˧"))

        lon.acceptability = PhonotacticAcceptability(True, False)
        self.assertEqualAndHashEqual(lon.acceptability, pr.apply(lon).acceptability)


class TestPhonology(BaseTestCase):
    def test_phonology(self) -> None:
        pc = PhonotacticConstraint(
            SyllableFeatures(
                {
                    "Initial": {IPAFeatureGroup("+stop +voiced")},
                    "Tone": {IPAFeatureGroup("+extra-high-level")},
                }
            ),
            PhonotacticAcceptability(False, False),
        )

        pr = PhonologicalRule(
            Nucleus("o"),
            IPAString("ʊ̃"),
            SyllableFeatures({"Final": {IPAFeatureGroup("+nasal")}}),
        )

        pr2 = PhonologicalRule(
            Final(nucleus=Nucleus("o"), coda=Coda("ŋ")),
            IPAString("ʊ̃"),
            SyllableFeatures({"Final": {IPAFeatureGroup("+nasal")}}),
        )

        kuaq = Syllable(
            Initial("k"),
            Final(
                medial=Medial("ʷ"),
                nucleus=Nucleus("ɐ"),
                coda=Coda("ʔ"),
            ),
            Tone("˥˥"),
        )
        lon = Syllable(
            Initial("l"), Final(nucleus=Nucleus("o"), coda=Coda("ŋ")), Tone("˨˧")
        )
        bo = Syllable(Initial("b"), Final(nucleus=Nucleus("o")), Tone("˨˧"))

        phonology = Phonology(
            syllables={kuaq, bo, lon},
            phonotactics={pc},
            phonological_rules=[pr],
        )

        phonology2 = Phonology(
            syllables={kuaq, bo, lon},
            phonotactics={pc},
            phonological_rules=[pr2],
        )

        phonology.refresh()
        str(phonology)
        repr(phonology)
        phonology.recursive_phoneme_collection
        phonology.leaf_phoneme_collection

        collocations = sorted(phonology.collocations)
        for syl in collocations:
            if str(syl) in ["boŋ˥˥", "bo˥˥", "bʷɐʔ˥˥"]:
                self.assertEqualAndHashEqual(syl.acceptability, pc.acceptability)
            else:
                self.assertEqualAndHashEqual(
                    syl.acceptability, PhonotacticAcceptability(True, True)
                )

        self.assertNotIn(
            "bʊ̃ŋ˥˥", [phonology.pretty_syllable_str(s) for s in collocations]
        )
        phonology.color_syllables = False
        self.assertIn(
            "bʊ̃ŋ˥˥", [phonology.pretty_syllable_str(s) for s in collocations]
        )
        phonology2.color_syllables = False
        self.assertIn(
            "bʊ̃˥˥", [phonology2.pretty_syllable_str(s) for s in collocations]
        )
        phonology.phonetic_str = False
        self.assertNotIn(
            "bʊ̃ŋ˥˥", [phonology.pretty_syllable_str(s) for s in collocations]
        )

        options.color = False
        [repr(s) for s in collocations]

        options.color = True
        phonology.pretty_print_syllable(kuaq)
