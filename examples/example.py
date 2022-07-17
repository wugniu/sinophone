from sinophone.phonetics import *
from sinophone.phonology import *

# Syllable 音節
# Let's create some syllables.
kaq = Syllable(
    Initial("k"),
    Final(
        nucleus=Nucleus("ɐ"),
        coda=Coda("ʔ"),
    ),
    Tone("˥˥"),
)
kaq
"""
# note that the output is actually colored when printed to the shell.
<Syllable [<Initial 'k'> <Final [<Medial ''> <Nucleus 'ɐ'> <Coda 'ʔ'>]> <Tone '˥˥'>]>
"""

lon = Syllable(Initial("l"), Final(nucleus=Nucleus("o"), coda=Coda("ŋ")), Tone("˨˧"))

bo = Syllable(Initial("b"), Final(nucleus=Nucleus("o")), Tone("˨˧"))


# PhonologicalRule 音韻規則
# Let's create a phonological rule, saying that /o/
# becomes [ʊ̃] when it is followed by a nasal.
pr = PhonologicalRule(
    Nucleus("o"),
    IPAString("ʊ̃"),
    SyllableFeatures({"Final": {IPAFeatureGroup("+nasal")}}),
)
pr
"""
<PhonologicalRule "o -> ʊ̃ / {'Final': {'+nasal'}}">
"""


# PhonotacticConstraint 音位排列制約
# Let's create a phonotactic constraint, saying that
# voiced non-nasal, non-lateral-approximant consonants
# cannot collocate with extra-high-level tone.
pc = PhonotacticConstraint(
    SyllableFeatures(
        {
            "Initial": {
                IPAFeatureGroup("-nasal -lateral-approximant +voiced"),
            },
            "Tone": {IPAFeatureGroup("+extra-high-level")},
        }
    ),
    PhonotacticAcceptability(False, False),
)
pc
"""
<PhonotacticConstraint {'Initial': {'-lateral-approximant -nasal +voiced'},
'Tone': {'+extra-high-level'}}: {'existent': False, 'grammatical': False}>
"""

# Phonology 音系
# Let's create a simple phonology with the above elements.
phonology = Phonology(
    syllables={kaq, bo, lon},
    phonotactics={pc},
    phonological_rules=[pr],
)

# Automatically generate syllable components from syllables.
sorted(phonology.initials)
"""
[<Initial 'b'>, <Initial 'k'>, <Initial 'l'>]
"""

# Automatically collocate to create hypothetical syllables,
# regardless of phonotactics.
spc = sorted(phonology.collocations)

# Pretty-print the above list.
for syllable in spc:
    phonology.pretty_print_syllable(syllable)

"""
.. output abbreviated for brevity
Syllables are colored red if completely contradicting phonotactics, 
green if completely phonotactically acceptable.
See `sinophone.options.RAINBOW_COLOR_SCHEME` for more colors.
"""

# List hypothetical syllables which contradict phonotactics.
[
    syllable.phonetic_ipa_str
    for syllable in spc
    if phonology.render_syllable(syllable).acceptability
    != PhonotacticAcceptability(True, True)
]
"""
[<IPAString 'bʊ̃ŋ˥˥'>, <IPAString 'bo˥˥'>, <IPAString 'bɐʔ˥˥'>]
"""
