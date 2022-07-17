"""
Fix problems in `ipapy`, and augment its classes for purposes of `sinophone`.
"""

from functools import total_ordering
from itertools import chain
from typing import (
    TYPE_CHECKING,
    AbstractSet,
    Collection,
    FrozenSet,
    Iterator,
    List,
    MutableSequence,
    Sequence,
    Union,
    overload,
)

from ipapy import IPA_TO_UNICODE as _OLD_IPA_TO_UNICODE
from ipapy.ipachar import (
    D_DIACRITIC,
    D_TONE,
    DG_ALL_DESCRIPTORS as _OLD_DG_ALL_DESCRIPTORS,
    DG_DIACRITICS,
    DG_TONES,
    IPAChar as _OldIPAChar,
    IPAConsonant as _OldIPAConsonant,
    IPADiacritic as _OldIPADiacritic,
    IPATone as _OldIPATone,
    IPAVowel as _OldIPAVowel,
    variant_to_list,
)
from ipapy.ipadescriptor import (
    IPADescriptor as _OldIPADescriptor,
    IPADescriptorGroup as _OldIPADescriptorGroup,
)

from ..utils import (
    PrettyClass,
    fix_ipapy_import_from_collections,
    obj_to_mro_chain_names,
    warn_about_dict_ordering,
)

fix_ipapy_import_from_collections()
from ipapy.ipastring import IPAString as _OldIPAString  # noqa: E402

if TYPE_CHECKING:  # pragma: no cover
    from .phonetics import IPAFeature, IPAFeatureGroup

IPA_TO_UNICODE_PATCH = {
    "extra-high-level tone": "˥",
    "high-level tone": "˦",
    "mid-level tone": "˧",
    "low-level tone": "˨",
    "extra-low-level tone": "˩",
}
IPA_TO_UNICODE = _OLD_IPA_TO_UNICODE.copy()
IPA_TO_UNICODE.update(IPA_TO_UNICODE_PATCH)
IPA_TO_ORDER = {ipa: i for i, ipa in enumerate(IPA_TO_UNICODE.keys())}


@total_ordering
class IPAChar(PrettyClass, _OldIPAChar):
    """
    吳: IPA 字元
    """

    def __init__(self, descriptors: str) -> None:
        super().__init__(descriptors)

    @property
    def unicode_repr(self) -> str:
        return IPA_TO_UNICODE[self._old_canonical_representation]

    @unicode_repr.setter
    def unicode_repr(self, value):
        ...

    @property
    def ipa_order(self) -> int:
        warn_about_dict_ordering()
        return IPA_TO_ORDER[self._old_canonical_representation]

    @property
    def _old_canonical_representation(self) -> str:
        super()._compute_canonical_string()
        return super().canonical_representation

    def __eq__(self, other) -> bool:
        return (
            type(self) == type(other)
            and "IPAChar" in obj_to_mro_chain_names(other)
            and self._old_canonical_representation
            == other._old_canonical_representation
        )

    def __lt__(self, other) -> bool:
        if "IPAChar" not in obj_to_mro_chain_names(other):
            raise TypeError("Cannot compare IPAChar to non-IPAChar")
        return self.ipa_order < other.ipa_order

    def __hash__(self) -> int:
        return hash((type(self).__name__, self._old_canonical_representation))

    def has_feature(self, feature: "IPAFeature") -> bool:
        return (
            self.has_descriptor(feature.ipa_descriptor.canonical_label)
            == feature.presence
        )

    def has_features(self, features: "IPAFeatureGroup") -> bool:
        return all(self.has_feature(feature) for feature in features)


class IPAConsonant(IPAChar, _OldIPAConsonant):
    """
    吳: IPA 輔音

    descriptors = '{voicing} {place} {manner}'
    """

    @property
    def canonical_representation(self) -> str:
        return " ".join([self.voicing, self.place, self.manner])


class IPADiacritic(IPAChar, _OldIPADiacritic):
    """
    吳: IPA 附標

    descriptors = '{diacritic}'
    """

    @property
    def canonical_representation(self) -> str:
        return self.diacritic

    @property
    def descriptors(self) -> List[str]:
        desc = [D_DIACRITIC.canonical_label]
        desc.extend(self.__descriptors)
        return desc

    @descriptors.setter
    def descriptors(self, descriptors) -> None:
        for p in variant_to_list(descriptors):
            if p in DG_DIACRITICS:
                self.diacritic = p
        try:
            self.__descriptors = [self.diacritic]
        except AttributeError:
            raise ValueError(f"Unrecognized value for diacritic: {descriptors}")
        self._compute_canonical_string()


class IPATone(IPAChar, _OldIPATone):
    """
    吳: IPA 聲調

    descriptors = '{tone_level}'
    """

    @property
    def canonical_representation(self) -> str:
        return self.tone_level

    @property
    def descriptors(self) -> List[str]:
        desc = [D_TONE.canonical_label]
        desc.extend(self.__descriptors)
        return desc

    @descriptors.setter
    def descriptors(self, descriptors) -> None:
        self.__descriptors = []
        for p in variant_to_list(descriptors):
            if p in DG_TONES:
                self.__descriptors.append(p)
        if not self.__descriptors:
            raise ValueError(f"Unrecognized value for tone: {descriptors}")
        self._compute_canonical_string()


class IPAVowel(IPAChar, _OldIPAVowel):
    """
    吳: IPA 元音

    descriptors = '{height} {backness} {roundness}'
    """

    @property
    def canonical_representation(self) -> str:
        return " ".join([self.height, self.backness, self.roundness, "vowel"])


@total_ordering
class IPAString(PrettyClass, _OldIPAString, MutableSequence[IPAChar]):
    """
    吳: IPA 字符串
    """

    @overload
    def __init__(self, ipa_str: str = "") -> None:  # pragma: no cover
        ...

    @overload
    def __init__(self, ipa_str: Sequence[IPAChar]) -> None:  # pragma: no cover
        ...

    def __init__(self, ipa_str: Union[str, Sequence[IPAChar]] = "") -> None:
        if isinstance(ipa_str, str):
            super().__init__(unicode_string=ipa_str)
        elif isinstance(ipa_str, Sequence):
            super().__init__(ipa_chars=list(ipa_str))
        else:
            raise TypeError(
                "IPAString must be initialized with a string or sequence of IPAChars"
            )

        # use newly defined IPAChar subclasses
        self.ipa_chars: Sequence[IPAChar] = [
            globals()[type(ipa_char).__name__](ipa_char.canonical_representation)
            if type(ipa_char)
            in [v for k, v in globals().items() if k.startswith("_OldIPA")]
            else globals()[type(ipa_char).__name__](
                ipa_char._old_canonical_representation
            )
            for ipa_char in self.__ipa_chars
        ]

    def __str__(self) -> str:
        return "".join(map(str, self))

    def __eq__(self, other) -> bool:
        return (
            type(self) == type(other)
            and "IPAString" in obj_to_mro_chain_names(other)
            and self.ipa_chars == other.ipa_chars
        )

    def __lt__(self, other) -> bool:
        if "IPAString" not in obj_to_mro_chain_names(other):
            raise TypeError("Cannot compare IPAString to non-IPAString")
        return tuple(self) < tuple(other)

    def __hash__(self) -> int:
        return hash((type(self).__name__, tuple(self.ipa_chars)))

    def __add__(self, other) -> "IPAString":
        if "IPAString" not in obj_to_mro_chain_names(other):
            raise TypeError(
                f"Cannot concatenate {type(other)} that is not an IPAString"
            )
        return type(self)(list(chain(self.ipa_chars, other.ipa_chars)))

    def __iadd__(self, other) -> "IPAString":
        return self + other

    def __iter__(self) -> Iterator[IPAChar]:
        for ipa_char in self.ipa_chars:
            yield ipa_char

    def __getitem__(self, i) -> IPAChar:
        return self.ipa_chars[i]

    @property
    def canonical_representation(self) -> str:
        return f'{", ".join(map(lambda ch: ch.canonical_representation, self))}'


class IPADescriptor(PrettyClass, _OldIPADescriptor):
    """
    吳: IPA 描述器
    """

    @overload
    def __init__(self, labels: Sequence[str]) -> None:
        ...

    @overload
    def __init__(self, labels: "IPADescriptor") -> None:
        ...

    def __init__(self, labels: Union[Sequence[str], "IPADescriptor"]) -> None:
        if isinstance(labels, Sequence) and not isinstance(labels, str):
            super().__init__(list(labels))
        elif isinstance(labels, IPADescriptor):
            super().__init__(labels.labels)
        else:
            raise TypeError(
                "IPADescriptor must be initialized with a sequence of labels"
            )

    def __str__(self) -> str:
        return self.canonical_label

    def __eq__(self, other) -> bool:
        return (
            type(self) == type(other)
            and "IPADescriptor" in obj_to_mro_chain_names(other)
            and self.canonical_label == other.canonical_label
        )

    def __hash__(self) -> int:
        return hash((type(self).__name__, self.canonical_label))


class IPADescriptorGroup(
    PrettyClass, _OldIPADescriptorGroup, AbstractSet[IPADescriptor]
):
    """
    吳: IPA 描述器組
    """

    def __init__(self, descriptors: Collection[IPADescriptor]) -> None:
        if not isinstance(descriptors, (Collection, _OldIPADescriptorGroup)):
            raise TypeError(
                "IPADescriptorGroup must be initialized "
                "with a collection of IPADescriptors"
            )

        try:
            self.descriptors = frozenset(
                [
                    self._check_IPADescriptor(
                        globals()[type(descriptor).__name__](descriptor.labels)
                    )
                    for descriptor in (
                        set(descriptors.descriptors)
                        if isinstance(descriptors, _OldIPADescriptorGroup)
                        else set(descriptors)
                    )
                ]
            )
        except (KeyError):
            raise TypeError(
                "IPADescriptorGroup must be initialized "
                "with a collection of IPADescriptors"
            )

    def __str__(self) -> str:
        return " ".join([str(descriptor) for descriptor in self.descriptors])

    def __repr__(self) -> str:
        return f"<{type(self).__name__} [{self}]>"

    def __eq__(self, other) -> bool:
        return (
            type(self) == type(other)
            and "IPADescriptorGroup" in obj_to_mro_chain_names(other)
            and self.descriptors == other.descriptors
        )

    def __or__(self, other):
        if "IPADescriptorGroup" not in obj_to_mro_chain_names(other):
            raise TypeError(
                f"Cannot concatenate {type(other)} that is not an IPADescriptorGroup"
            )
        return type(self)(descriptors=self.descriptors | other.descriptors)

    def __iter__(self) -> Iterator[IPADescriptor]:
        return iter(self.descriptors)

    def __hash__(self) -> int:
        return hash((type(self).__name__, self.descriptors))

    @staticmethod
    def _check_IPADescriptor(descriptor: IPADescriptor) -> IPADescriptor:
        if "IPADescriptor" in obj_to_mro_chain_names(descriptor):
            return descriptor
        else:
            raise TypeError(
                "IPADescriptorGroup only accepts IPADescriptor objects, "
                f"not {type(descriptor).__name__}"
            )

    @property
    def descriptors(self) -> FrozenSet[IPADescriptor]:
        return self.__descriptors

    @descriptors.setter
    def descriptors(self, value) -> None:
        self.__descriptors = value


DG_ALL_DESCRIPTORS = IPADescriptorGroup(_OLD_DG_ALL_DESCRIPTORS)
"""
吳: 所有描述器
"""
