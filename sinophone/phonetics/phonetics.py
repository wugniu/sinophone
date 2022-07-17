from functools import total_ordering
from typing import Collection, Iterator, MutableSet, Union, overload

from ..utils import PrettyClass, obj_to_mro_chain_names
from .ipa_utils import DG_ALL_DESCRIPTORS


@total_ordering
class IPAFeature(PrettyClass):
    """
    吳: IPA 區別特徵
    """

    def __init__(self, descriptor: str, presence: bool = True) -> None:
        if descriptor[0] == "+" or descriptor[0] == "-":
            if descriptor[0] == "-":
                presence = not presence
            descriptor = descriptor[1:]

        for ipa_descriptor in DG_ALL_DESCRIPTORS:
            if descriptor in ipa_descriptor.labels:
                self.ipa_descriptor = ipa_descriptor
                self.presence = presence
                return

        raise ValueError(f"Unknown descriptor: {descriptor}")

    def __str__(self) -> str:
        return f"{'+' if self.presence else '-'}{self.ipa_descriptor.canonical_label}"

    def __pos__(self) -> "IPAFeature":
        return IPAFeature(self.ipa_descriptor.canonical_label, self.presence)

    def __neg__(self) -> "IPAFeature":
        return IPAFeature(self.ipa_descriptor.canonical_label, not self.presence)

    def __eq__(self, other) -> bool:
        return (
            type(self) == type(other)
            and "IPAFeature" in obj_to_mro_chain_names(other)
            and self.presence == other.presence
            and self.ipa_descriptor == other.ipa_descriptor
        )

    def __gt__(self, other) -> bool:
        if "IPAFeature" not in obj_to_mro_chain_names(other):
            raise TypeError("Cannot compare IPAFeature to non-IPAFeature")
        if self.presence != other.presence:
            return self.presence
        return (
            self.ipa_descriptor.canonical_label > other.ipa_descriptor.canonical_label
        )

    def __hash__(self) -> int:
        return hash(
            (type(self).__name__, self.presence, self.ipa_descriptor.canonical_label)
        )


@total_ordering
class IPAFeatureGroup(MutableSet[IPAFeature], PrettyClass):
    """
    吳: IPA 區別特徵組

    A set of (meaningful) IPA features.
    """

    @overload
    def __init__(self, features: str) -> None:
        ...

    @overload
    def __init__(self, features: Collection[IPAFeature] = None) -> None:
        ...

    def __init__(self, features: Union[str, Collection[IPAFeature]] = None) -> None:
        self.features: MutableSet[IPAFeature] = set()
        if features is not None:
            if isinstance(features, str):
                features = [IPAFeature(feature) for feature in features.split()]
            for feature in features:
                self.add(feature)

    def __str__(self) -> str:
        return " ".join([str(feature) for feature in self.features])

    def __contains__(self, value) -> bool:
        return value in self.features

    def __iter__(self) -> Iterator[IPAFeature]:
        return iter(self.features)

    def __len__(self) -> int:
        return len(self.features)

    def __pos__(self) -> "IPAFeatureGroup":
        return IPAFeatureGroup([+feature for feature in self.features])

    def __neg__(self) -> "IPAFeatureGroup":
        return IPAFeatureGroup([-feature for feature in self.features])

    def __or__(self, other) -> "IPAFeatureGroup":
        if "IPAFeatureGroup" not in obj_to_mro_chain_names(other):
            raise TypeError(
                f"Cannot concatenate {type(other)} that is not an IPAFeatureGroup"
            )
        return type(self)(features=self.features | other.features)

    def __eq__(self, other) -> bool:
        return (
            type(self) == type(other)
            and "IPAFeatureGroup" in obj_to_mro_chain_names(other)
            and tuple(sorted(self)) == tuple(sorted(other))
        )

    def __lt__(self, other) -> bool:
        if "IPAFeatureGroup" not in obj_to_mro_chain_names(other):
            raise TypeError("Cannot compare IPAFeatureGroup to non-IPAFeatureGroup")
        return tuple(sorted(self)) < tuple(sorted(other))

    def __hash__(self) -> int:
        return hash((type(self).__name__, frozenset(self.features)))

    def add(self, value) -> None:
        if "IPAFeature" in obj_to_mro_chain_names(value):
            self.features.add(value)
        else:
            raise TypeError(f"{value} is not an IPA feature")

    def discard(self, value) -> None:
        return self.features.discard(value)
