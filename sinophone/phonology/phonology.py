from copy import deepcopy
from dataclasses import asdict, dataclass, field
from itertools import product
from typing import (
    AbstractSet,
    Callable,
    Dict,
    List,
    Literal,
    MutableSet,
    Sequence,
    TypeVar,
)

from ..options import options
from ..phonetics.ipa_utils import IPAString
from ..phonetics.phonetics import IPAFeatureGroup
from ..utils import (
    PrettyClass,
    color_str,
    dict_to_frozenset,
    obj_to_mro_chain_names,
    repr_set_in_order,
    sinophone_warning,
)
from .syllable import (
    Final,
    Initial,
    LeafSyllableComponent,
    Syllable,
    SyllableComponent,
    Tone,
)

SyllablePattern = Callable[[Syllable], bool]
"""
吳: (匹配) 音節模式
"""

S = TypeVar("S", bound=Syllable)
"""
`Syllable` and its subclasses
"""


@dataclass(repr=False, order=True)
class SyllableFeatures(PrettyClass):
    """
    吳: 音節特徵

    A friendly way of generating a `SyllablePattern` callable.
    `syllable_component_features` is a dictionary of component names
    to sets of features. When called, it returns `True` if all syllable
    components matches any of the features in the set that is its key.

    幫助生成一個 `(匹配) 音節模式` 可調對象。
    """

    syllable_component_features: Dict[
        Literal[
            "Syllable",
            "Initial",
            "Final",
            "Medial",
            "Nucleus",
            "Coda",
            "Tone",
        ],  # Literal[tuple(SyllableComponent.COMPONENT_ORDER)]
        AbstractSet[IPAFeatureGroup],
    ] = field(default_factory=dict)

    def __str__(self) -> str:
        str_builder = [
            f"'{k}': {{{', '.join(repr(str(f)) for f in v)}}}"
            for k, v in self.syllable_component_features.items()
        ]
        return f"{{{', '.join(str_builder)}}}"

    def __hash__(self) -> int:
        return hash(
            (
                type(self).__name__,
                dict_to_frozenset(
                    {
                        k: frozenset(v)
                        for k, v in self.syllable_component_features.items()
                    }
                ),
            )
        )

    def __call__(self, syllable: S) -> bool:
        for component in syllable.recursive_sub_components:
            for (
                component_name,
                set_of_features,
            ) in self.syllable_component_features.items():
                if component_name in obj_to_mro_chain_names(component):
                    if not any(
                        [
                            component.has_features(features)
                            for features in set_of_features
                        ]
                    ):
                        return False
        return True


@dataclass(repr=False, order=True)
class PhonotacticAcceptability(PrettyClass):
    """
    吳: 音位排列受容性
    """

    existent: bool = False
    """
    吳: 是否存在
    """
    grammatical: bool = False
    """
    吳: 是否合法
    """

    def __str__(self) -> str:
        return str(asdict(self))

    def __hash__(self) -> int:
        return hash((type(self).__name__, dict_to_frozenset(asdict(self))))

    @property
    def color_code(self) -> str:
        if self.existent:
            if self.grammatical:
                return "ExistentGrammatical"
            else:
                return "ExistentUngrammatical"
        else:
            if self.grammatical:
                return "NonexistentGrammatical"
            else:
                return "NonexistentUngrammatical"

    def __or__(self, other) -> "PhonotacticAcceptability":
        if "PhonotacticAcceptability" not in obj_to_mro_chain_names(other):
            raise TypeError(
                f"unsupported operand type(s) for |: '{type(self)}' and '{type(other)}'"
            )
        return type(self)(
            existent=self.existent or other.existent,
            grammatical=self.grammatical or other.grammatical,
        )

    def __and__(self, other) -> "PhonotacticAcceptability":
        if "PhonotacticAcceptability" not in obj_to_mro_chain_names(other):
            raise TypeError(
                f"unsupported operand type(s) for &: '{type(self)}' and '{type(other)}'"
            )
        return type(self)(
            existent=self.existent and other.existent,
            grammatical=self.grammatical and other.grammatical,
        )


class SyllableInPhonology(Syllable):
    """
    吳: 音節在音系中個實現
    """

    acceptability: PhonotacticAcceptability = PhonotacticAcceptability(True, True)

    @property
    def color(self) -> str:
        if not options.color:
            return ""
        return options.color_scheme.get(self.acceptability.color_code, "")

    @classmethod
    def from_syllable(cls, syllable: S) -> "SyllableInPhonology":
        new_syllable = cls(
            deepcopy(syllable.initial),
            deepcopy(syllable.final),
            deepcopy(syllable.tone),
        )
        if hasattr(syllable, "acceptability"):
            new_syllable.acceptability = syllable.acceptability  # type: ignore
        return new_syllable


@dataclass(repr=False, order=True)
class PhonotacticConstraint(PrettyClass):
    """
    吳: 音位排列制約

    音位排列，普譯曰「語音組合法」，日譯曰「音素配列論」。

    在墶認爲音節總個結構只好是 聲母+韻母+聲調 個情況下頭，畀出其他個音位排列規則。
    """

    syllable_pattern: SyllablePattern = SyllableFeatures()
    acceptability: PhonotacticAcceptability = PhonotacticAcceptability()

    def __str__(self) -> str:
        return f"{self.syllable_pattern}: {self.acceptability}"

    def __hash__(self) -> int:
        return hash((type(self).__name__, self.syllable_pattern, self.acceptability))

    def apply(self, syllable: S) -> SyllableInPhonology:
        new_syllable = SyllableInPhonology.from_syllable(syllable)
        if self.syllable_pattern(new_syllable):
            new_syllable.acceptability &= self.acceptability
        return new_syllable


@dataclass(repr=False, order=True)
class PhonologicalRule(PrettyClass):
    """
    吳: 音韻規則
    """

    phoneme: SyllableComponent = Syllable()
    phonetic_ipa_str: IPAString = IPAString()
    syllable_pattern: SyllablePattern = SyllableFeatures()

    def __str__(self) -> str:
        return f"{self.phoneme} -> {self.phonetic_ipa_str} / {self.syllable_pattern}"

    def __hash__(self) -> int:
        return hash(
            (
                type(self).__name__,
                self.phoneme,
                self.phonetic_ipa_str,
                self.syllable_pattern,
            )
        )

    def apply(self, syllable: S) -> SyllableInPhonology:
        new_syllable = SyllableInPhonology.from_syllable(syllable)
        if self.syllable_pattern(new_syllable):
            for component in new_syllable.recursive_sub_components:
                if component == self.phoneme:
                    component.phonetic_ipa_str = self.phonetic_ipa_str
        return new_syllable


@dataclass(repr=False)
class Phonology(PrettyClass):
    """
    吳: 音韻體系
    (音系)
    """

    # 音節
    initials: MutableSet[Initial] = field(default_factory=set)
    finals: MutableSet[Final] = field(default_factory=set)
    tones: MutableSet[Tone] = field(default_factory=set)
    syllables: MutableSet[Syllable] = field(default_factory=set)

    # 音系
    phonotactics: MutableSet[PhonotacticConstraint] = field(default_factory=set)
    phonological_rules: Sequence[PhonologicalRule] = field(default_factory=list)

    # 設定
    color_syllables: bool = True
    """
    Whether to color syllables based on phonotactic acceptability,
    different from `sinophone.options.color`,
    which controls coloring of syllable components.
    """
    phonetic_str: bool = True

    def refresh(self) -> None:
        self.update_phoneme_collections_from_syllables()
        self.update_rendered_syllables()

    def __post_init__(self) -> None:
        self.refresh()

    def __str__(self) -> str:
        str_builder: List[str] = [
            repr_set_in_order(self.phoneme_collection),
            repr_set_in_order(self.syllables),
            repr_set_in_order(self.phonotactics),
            str(self.phonological_rules),
        ]
        return " ".join(str_builder)

    def update_phoneme_collections_from_syllables(self) -> None:
        for syllable in self.syllables:
            for sub_component in syllable.sub_components:
                if (
                    isinstance(sub_component, Initial)
                    and sub_component not in self.initials
                ):
                    self.initials.add(sub_component)
                elif (
                    isinstance(sub_component, Final)
                    and sub_component not in self.finals
                ):
                    self.finals.add(sub_component)
                elif (
                    isinstance(sub_component, Tone) and sub_component not in self.tones
                ):
                    self.tones.add(sub_component)

    @property
    def phoneme_collection(self) -> AbstractSet[SyllableComponent]:
        return self.initials | self.finals | self.tones

    @property
    def recursive_phoneme_collection(self) -> AbstractSet[SyllableComponent]:
        recursive_phoneme_collection = set(self.phoneme_collection)
        return recursive_phoneme_collection.union(
            *[syl_comp.recursive_sub_components for syl_comp in self.phoneme_collection]
        )

    @property
    def leaf_phoneme_collection(self) -> AbstractSet[LeafSyllableComponent]:
        leaf_phoneme_collection = set()
        for phoneme in self.recursive_phoneme_collection:
            if isinstance(phoneme, LeafSyllableComponent):
                leaf_phoneme_collection.add(phoneme)
        return leaf_phoneme_collection

    @property
    def collocations(self) -> AbstractSet[SyllableInPhonology]:
        collocations = set()
        for initial, final, tone in product(self.initials, self.finals, self.tones):
            collocations.add(self.render_syllable(Syllable(initial, final, tone)))
        return collocations

    def render_syllable(self, syllable: Syllable) -> SyllableInPhonology:
        syllable_in_phonology = SyllableInPhonology.from_syllable(syllable)
        syllable_in_phonology.acceptability = PhonotacticAcceptability(True, True)

        for constraint in self.phonotactics:
            syllable_in_phonology = constraint.apply(syllable_in_phonology)
        for rule in self.phonological_rules:
            syllable_in_phonology = rule.apply(syllable_in_phonology)

        return syllable_in_phonology

    def update_rendered_syllables(self) -> None:
        self.rendered_syllables = [
            self.render_syllable(syllable) for syllable in sorted(self.syllables)
        ]

    def pretty_syllable_str(self, syllable: S) -> str:
        rendered_syllable = self.render_syllable(syllable)

        pretty_str = ""

        if self.phonetic_str:
            pretty_str = str(rendered_syllable.phonetic_ipa_str)
        else:
            pretty_str = str(rendered_syllable.ipa_str)

        if options.color and self.color_syllables:
            pretty_str = color_str(
                pretty_str, rendered_syllable.acceptability.color_code
            )

        return pretty_str

    def pretty_print_syllable(self, syllable: S) -> None:
        try:
            print(self.pretty_syllable_str(syllable))
        except UnicodeEncodeError:
            # ! cannot reproduce this error in my local Windows environment
            sinophone_warning("UnicodeEncodeError caught. Check your encoding.")
