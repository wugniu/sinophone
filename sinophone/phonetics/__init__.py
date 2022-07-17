"""
Phonetics

語音
"""

from copy import deepcopy

from .ipa_utils import (  # IPAChar,
    DG_ALL_DESCRIPTORS,
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

__all__ = [
    "ALL_DESCRIPTORS",
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
