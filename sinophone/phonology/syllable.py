from dataclasses import dataclass
from functools import total_ordering
from typing import Dict, List, Union, overload

from ..options import AnsiColors
from ..phonetics.ipa_utils import IPAChar, IPAConsonant, IPAString
from ..phonetics.phonetics import IPAFeatureGroup
from ..utils import PostInitCaller, PrettyClass, obj_to_mro_chain_names

SYLLABLE_STRUCTURE: Dict[str, List[str]] = {
    "Syllable": ["Initial", "Final", "Tone"],
    "Initial": [],
    "Final": ["Medial", "Nucleus", "Coda"],
    "Medial": [],
    "Nucleus": [],
    "Coda": [],
    "Tone": [],
}


@total_ordering
class SyllableComponent(PrettyClass, metaclass=PostInitCaller):
    """
    吳: 音節要素
        - 梢音節要素
        - 榦音節要素
            - 根音節要素
    """

    COMPONENT_ORDER = [
        "SyllableComponent",
        "LeafSyllableComponent",
        "BranchSyllableComponent",
        "RootSyllableComponent",
        "Syllable",
        "SyllableInPhonology",
        "Initial",
        "Final",
        "Medial",
        "Nucleus",
        "Coda",
        "Tone",
    ]
    COMPONENT_ORDER_DICT = dict((item, i) for i, item in enumerate(COMPONENT_ORDER))

    @property
    def component_order(self) -> int:
        return self.COMPONENT_ORDER_DICT[type(self).__name__]

    def has_features(self, features: IPAFeatureGroup) -> bool:
        return any([ipa_char.has_features(features) for ipa_char in self.ipa_str])

    def __post_init__(self) -> None:
        self._phonetic_ipa_str = None

    def __str__(self) -> str:
        return self._substr

    def __repr__(self) -> str:
        color = self.color
        return f"{color}<{self.translated_name} {self._subrepr}{color}>{AnsiColors.END}"

    def __eq__(self, other) -> bool:
        return (
            type(self) == type(other)
            and "SyllableComponent" in obj_to_mro_chain_names(other)
            and self.ipa_str == other.ipa_str
        )

    def __lt__(self, other) -> bool:
        if "SyllableComponent" not in obj_to_mro_chain_names(other):
            raise TypeError("Cannot compare SyllableComponent to non-SyllableComponent")
        return (
            self.ipa_str < other.ipa_str
            if self.component_order == other.component_order
            else self.component_order < other.component_order
        )

    def __hash__(self) -> int:
        ...

    @property
    def sub_components(self) -> List["SyllableComponent"]:
        ...

    @property
    def recursive_sub_components(self) -> List["SyllableComponent"]:
        ...

    @property
    def ipa_str(self) -> IPAString:
        ...

    @property
    def phonetic_ipa_str(self) -> IPAString:
        ...

    @phonetic_ipa_str.setter
    def phonetic_ipa_str(self, value) -> None:
        ...

    @property
    def ipa_chars(self) -> List[IPAChar]:
        return list(self.ipa_str.ipa_chars)

    @property
    def _substr(self) -> str:
        ...

    @property
    def _subrepr(self) -> str:
        ...


class LeafSyllableComponent(SyllableComponent):
    """
    吳: 梢音節要素
    """

    @overload
    def __init__(self, component: str) -> None:
        ...

    @overload
    def __init__(self, component: IPAString = IPAString()) -> None:
        ...

    @overload
    def __init__(self, component: "SyllableComponent") -> None:
        ...

    def __init__(
        self, component: Union[IPAString, "SyllableComponent", str] = IPAString()
    ) -> None:
        if isinstance(component, SyllableComponent):
            component = component.ipa_str
        elif isinstance(component, str):
            component = IPAString(component)
        elif isinstance(component, IPAString):
            ...
        else:
            raise TypeError("Invalid component type")
        self._component = component

    def __hash__(self) -> int:
        return hash((type(self).__name__, self.ipa_str))

    @property
    def sub_components(self) -> List["SyllableComponent"]:
        return []

    @property
    def recursive_sub_components(self) -> List["SyllableComponent"]:
        return self.sub_components

    @property
    def ipa_str(self) -> IPAString:
        return self._component

    @property
    def phonetic_ipa_str(self) -> IPAString:
        return (
            self._phonetic_ipa_str
            if self._phonetic_ipa_str is not None
            else self.ipa_str
        )

    @phonetic_ipa_str.setter
    def phonetic_ipa_str(self, value) -> None:
        self._phonetic_ipa_str = value

    @property
    def _substr(self) -> str:
        return str(self.ipa_str)

    @property
    def _subrepr(self) -> str:
        return f"'{self.ipa_str}'"


class BranchSyllableComponent(SyllableComponent):
    """
    吳: 榦音節要素
    """

    # decorate subclasses with dataclass to ensure the attribute `__match_args__`
    # __match_args__: List[str]

    def __hash__(self) -> int:
        return hash((type(self).__name__, tuple(self.sub_components)))

    @property
    def sub_components(self) -> List[SyllableComponent]:
        cls_name = type(self).__name__
        if "Syllable" in obj_to_mro_chain_names(self):
            cls_name = "Syllable"
        return [
            getattr(self, sub_component.lower())
            for sub_component in SYLLABLE_STRUCTURE[cls_name]
            # getattr(self, sub_component_name)
            # for sub_component_name in self.__match_args__
        ]

    @property
    def recursive_sub_components(self) -> List["SyllableComponent"]:
        recursive_sub_components = []
        for sub_component in self.sub_components:
            recursive_sub_components.append(sub_component)
            if sub_component.sub_components:
                recursive_sub_components.extend(sub_component.sub_components)
        return recursive_sub_components

    @property
    def ipa_str(self) -> IPAString:
        ipa_str = IPAString()
        for sub_component in self.sub_components:
            if sub_component:
                ipa_str += sub_component.ipa_str
        return ipa_str

    @property
    def phonetic_ipa_str(self) -> IPAString:
        if self._phonetic_ipa_str is not None:
            return self._phonetic_ipa_str

        phonetic_ipa_str = IPAString()
        for sub_component in self.sub_components:
            if sub_component:
                phonetic_ipa_str += sub_component.phonetic_ipa_str
        return phonetic_ipa_str

    @phonetic_ipa_str.setter
    def phonetic_ipa_str(self, value) -> None:
        self._phonetic_ipa_str = value

    @property
    def _substr(self) -> str:
        return "".join(map(str, self.sub_components))

    @property
    def _subrepr(self) -> str:
        color = self.color
        return f"{color}[{' '.join(map(repr, self.sub_components))}{color}]"


class RootSyllableComponent(BranchSyllableComponent):
    """
    吳: 根音節要素
    """


class Initial(LeafSyllableComponent):
    """
    吳: 聲母
    """


class Medial(LeafSyllableComponent):
    """
    吳: 介音
    """


class Nucleus(LeafSyllableComponent):
    """
    吳: 韻腹
    """


class Coda(LeafSyllableComponent):
    """
    吳: 韻尾
    """


class Tone(LeafSyllableComponent, metaclass=PostInitCaller):
    """
    吳: 聲調
    """

    def __post_init__(self) -> None:
        super().__post_init__()
        self.validate()

    def validate(self) -> None:
        for i, tone in enumerate(self.ipa_str):
            if not tone.is_tone:
                if i == len(self.ipa_str) - 1 and tone == IPAConsonant(
                    "voiceless glottal stop"
                ):
                    continue
                raise ValueError(f"'{self.ipa_str}' is not a tone.")


@dataclass(repr=False, eq=False)
class Final(BranchSyllableComponent):
    """
    吳: 韻母

    漢語個韻母，一般可以分析爲 介音+韻腹+韻尾
    """

    medial: Medial = Medial()
    nucleus: Nucleus = Nucleus()
    coda: Coda = Coda()


@dataclass(repr=False, eq=False)
class Syllable(RootSyllableComponent):
    """
    吳: 音節

    漢語個音節，一般可以分析爲 聲母+韻母+聲調
    """

    initial: Initial = Initial()
    final: Final = Final()
    tone: Tone = Tone()
