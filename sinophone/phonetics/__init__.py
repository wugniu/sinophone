"""
Phonetics

語音
"""

from copy import deepcopy

from .ipa_utils import (
    DG_ALL_DESCRIPTORS,
    IPAChar,
    IPAConsonant,
    IPADescriptor,
    IPADescriptorGroup,
    IPADiacritic,
    IPAString,
    IPATone,
    IPAVowel,
)
from .phonetics import IPAFeature, IPAFeatureGroup

ALL_DESCRIPTORS = deepcopy(DG_ALL_DESCRIPTORS)
"""All valid IPA descriptors can be found in this ``IPADescriptorGroup``."""

__all__ = [
    "ALL_DESCRIPTORS",
    "IPAChar",
    "IPAConsonant",
    "IPADescriptor",
    "IPADescriptorGroup",
    "IPADiacritic",
    "IPAFeature",
    "IPAFeatureGroup",
    "IPAString",
    "IPATone",
    "IPAVowel",
]
