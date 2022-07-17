from itertools import product

from sinophone.phonetics import (
    ALL_DESCRIPTORS,
    IPAConsonant,
    IPADescriptor,
    IPADescriptorGroup,
    IPADiacritic,
    IPAFeature,
    IPAFeatureGroup,
    IPAString,
    IPATone,
    IPAVowel,
)

from .utils import BaseTestCase


class TestIPAChar(BaseTestCase):
    def test_str(self) -> None:
        self.assertEqual(str(IPAVowel("open back unrounded")), "ɑ")
        self.assertEqual(str(IPAConsonant("voiceless glottal stop")), "ʔ")
        self.assertEqual(str(IPADiacritic("creaky-voiced")), "̰")
        self.assertEqual(str(IPATone("low-level")), "˨")

    def test_canonical_representation(self) -> None:
        self.assertEqual(
            IPAVowel("open back unrounded").canonical_representation,
            "open back unrounded vowel",
        )
        self.assertEqual(
            IPAConsonant("voiceless glottal stop").canonical_representation,
            "voiceless glottal stop",
        )
        self.assertEqual(
            IPADiacritic("creaky-voiced").canonical_representation,
            "creaky-voiced",
        )
        self.assertEqual(
            IPATone("low-level").canonical_representation,
            "low-level",
        )

    def test_init(self) -> None:
        with self.assertRaises(ValueError):
            IPADiacritic("velar")
        with self.assertRaises(ValueError):
            IPATone("velar")
        with self.assertRaises(ValueError):
            IPAVowel("velar")

    def test_eq_hash(self) -> None:
        self.assertEqualAndHashEqual(
            IPAVowel("open back unrounded vowel"), IPAVowel("unrounded open back")
        )
        self.assertNotEqualAndHashNotEqual(
            IPAVowel("open back unrounded"), IPAVowel("close back unrounded")
        )
        self.assertNotEqualAndHashNotEqual(
            IPAVowel("open back unrounded"), IPAConsonant("voiceless glottal stop")
        )

    def test_order(self) -> None:
        with self.assertRaises(TypeError):
            IPAConsonant("voiceless velar stop") < "g"

        self.assertLess(
            IPAConsonant("voiceless velar stop"),
            IPAConsonant("voiced velar stop"),
        )
        self.assertLess(
            IPAConsonant("voiceless velar stop"),
            IPAConsonant("voiceless glottal stop"),
        )
        self.assertLess(
            IPAConsonant("voiceless glottal stop"),
            IPAConsonant("voiceless velar approximant"),
        )


class TestIPAString(BaseTestCase):
    def test_str(self) -> None:
        self.assertEqual(str(IPAString("kɑ")), "kɑ")

    def test_eq_hash_init(self) -> None:
        with self.assertRaises(TypeError):
            IPAString(IPAConsonant("voiceless velar stop"))

        ka1 = IPAString("kɑ")
        ka2 = IPAString(ka1)
        ka3 = IPAString(
            [
                IPAConsonant("voiceless velar stop"),
                IPAVowel("open back unrounded"),
            ]
        )

        self.assertEqualAndHashEqual(ka1, ka2)
        self.assertEqualAndHashEqual(ka2, ka3)

    def test_order(self) -> None:
        with self.assertRaises(TypeError):
            IPAString("k") < "kɑ"

        self.assertLess(IPAString("k"), IPAString("kɑ"))
        self.assertLess(IPAString("kɑ"), IPAString("gɑ"))

    def test_add(self) -> None:
        with self.assertRaises(TypeError):
            IPAString("k") + IPAVowel("open back unrounded")

        self.assertEqualAndHashEqual(IPAString("k") + IPAString("ɑ"), IPAString("kɑ"))

    def test_get_item(self) -> None:
        self.assertEqualAndHashEqual(
            IPAString("kɑ")[0], IPAConsonant("voiceless velar stop")
        )

    def test_canonical_representation(self) -> None:
        IPAString("kɑ").canonical_representation


class TestIPADescriptor(BaseTestCase):
    def test_canonical_label(self) -> None:
        plosive_desc_list = ["plosive", "stop"]
        self.assertEqual(
            IPADescriptor(plosive_desc_list).canonical_label, plosive_desc_list[0]
        )

    def test_eq_hash_init_str(self) -> None:
        with self.assertRaises(TypeError):
            IPADescriptor("plosive")

        plosive1 = IPADescriptor(["plosive", "stop"])
        plosive2 = IPADescriptor(plosive1)
        self.assertEqualAndHashEqual(plosive1, plosive2)

        self.assertEqual(str(plosive1), "plosive")


class TestIPADescriptorGroup(BaseTestCase):
    def test_canonical_value(self) -> None:
        self.assertEqual(ALL_DESCRIPTORS.canonical_value("stop"), "plosive")

    def test_eq_hash_init_set_str_repr(self) -> None:
        with self.assertRaises(TypeError):
            IPADescriptorGroup(IPADescriptor(["plosive", "stop"]))
        with self.assertRaises(TypeError):
            IPADescriptorGroup(["plosive", "stop"])  # type: ignore
        with self.assertRaises(TypeError):
            IPADescriptorGroup([IPAFeatureGroup("plosive")])  # type: ignore

        self.assertEqualAndHashEqual(
            ALL_DESCRIPTORS,
            ALL_DESCRIPTORS | IPADescriptorGroup([IPADescriptor(["plosive", "stop"])]),
        )
        self.assertEqualAndHashEqual(
            ALL_DESCRIPTORS,
            ALL_DESCRIPTORS | IPADescriptorGroup(ALL_DESCRIPTORS),
        )

        with self.assertRaises(TypeError):
            ALL_DESCRIPTORS | IPADescriptor(["plosive", "stop"])

        str(ALL_DESCRIPTORS)
        repr(ALL_DESCRIPTORS)


class TestIPAFeature(BaseTestCase):
    def test_eq_hash_pos_neg_init(self) -> None:
        with self.assertRaises(ValueError):
            IPAFeature("nonsense", True)

        velar1 = IPAFeature("+velar")
        velar2 = IPAFeature("velar")
        velar3 = -IPAFeature("-velar")
        velar4 = +velar1
        velar5 = +velar2

        velars = [velar1, velar2, velar3, velar4, velar5]

        for velar_a, velar_b in product(velars, velars):
            self.assertEqualAndHashEqual(velar_a, velar_b)

    def test_order(self) -> None:
        with self.assertRaises(TypeError):
            IPAFeature("-velar") < "+velar"

        self.assertLess(IPAFeature("-velar"), IPAFeature("+velar"))


class TestIPAFeatureGroup(BaseTestCase):
    def test_eq_hash_pos_neg_set_init(self) -> None:
        with self.assertRaises(ValueError):
            IPAFeatureGroup("nonsense")
        with self.assertRaises(TypeError):
            IPAFeatureGroup(["nonsense"])  # type: ignore

        self.assertEqualAndHashEqual(
            IPAFeatureGroup("+velar +bilabial"),
            +IPAFeatureGroup("velar +bilabial"),
        )
        self.assertEqualAndHashEqual(
            -IPAFeatureGroup("+velar -bilabial"),
            +IPAFeatureGroup([-IPAFeature("velar"), IPAFeature("+bilabial")]),
        )
        self.assertEqualAndHashEqual(
            IPAFeatureGroup("+velar -bilabial"),
            IPAFeatureGroup("velar") | -IPAFeatureGroup("bilabial"),
        )
        self.assertNotEqualAndHashNotEqual(
            IPAFeatureGroup("-velar -bilabial"),
            IPAFeatureGroup("velar") | -IPAFeatureGroup("bilabial"),
        )

        self.assertIn(IPAFeature("velar"), IPAFeatureGroup("velar"))

        ifg = IPAFeatureGroup("+velar -bilabial")
        self.assertNotEqualAndHashNotEqual(ifg, IPAFeatureGroup("velar"))
        ifg.discard(IPAFeature("+velar"))
        self.assertEqualAndHashEqual(ifg, IPAFeatureGroup("-bilabial"))

        with self.assertRaises(TypeError):
            IPAFeatureGroup("-velar") | "+velar"

    def test_order(self):
        with self.assertRaises(TypeError):
            IPAFeatureGroup("-velar") < "+velar"
        self.assertLess(IPAFeatureGroup("-velar"), IPAFeatureGroup("+velar"))
