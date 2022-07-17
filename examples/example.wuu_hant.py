from sinophone import options
from sinophone.phonetics import *
from sinophone.phonology import *

# 設置語言爲吳語
options.repr_lang = "wuu-Hant"

# Syllable 音節
# 阿拉來建立一眼音節。
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
# 在墶終端裏向，實際輸出是彩色個。
<音節 [<聲母 'k'> <韻母 [<介音 ''> <韻腹 'ɐ'> <韻尾 'ʔ'>]> <聲調 '˥˥'>]>
"""

lon = Syllable(Initial("l"), Final(nucleus=Nucleus("o"), coda=Coda("ŋ")), Tone("˨˧"))

bo = Syllable(Initial("b"), Final(nucleus=Nucleus("o")), Tone("˨˧"))


# PhonologicalRule 音韻規則
# 阿拉來創建一隻音韻規則，講 /o/ 在墶鼻音前頭變爲 [ʊ̃]。
pr = PhonologicalRule(
    Nucleus("o"),
    IPAString("ʊ̃"),
    SyllableFeatures({"Final": {IPAFeatureGroup("+nasal")}}),
)
pr
"""
<音韻規則 "o -> ʊ̃ / {'Final': {'+nasal'}}">
"""


# PhonotacticConstraint 音位排列制約
# 阿拉來創建一隻音位排列制約，講任何非鼻音、非邊近音個濁音
# 弗能夠交極高調（˥）搭配。
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
<音位排列制約 {'Initial': {'-nasal +voiced -lateral-approximant'},
'Tone': {'+extra-high-level'}}: {'existent': False, 'grammatical': False}>
"""

# Phonology 音系
# 阿拉來根據上述對象建立一隻音系。
phonology = Phonology(
    syllables={kaq, bo, lon},
    phonotactics={pc},
    phonological_rules=[pr],
)

# 從音節推導出音節要素
sorted(phonology.initials)
"""
[<聲母 'b'>, <聲母 'k'>, <聲母 'l'>]
"""

# 弗考慮音位排列規則，自動組合所有音節要素。
spc = sorted(phonology.collocations)

# 拿上頭個列表上色，打印出來
for syllable in spc:
    phonology.pretty_print_syllable(syllable)
"""
.. 從簡省略輸出
拿完全交音位排列規則衝突個音節標紅，完全符合音位排列規則個音節標綠。
關於其他顏色代表個意思，請看 `sinophone.options.RAINBOW_COLOR_SCHEME`。
"""

# 列舉完全交音位排列規則衝突個音節
[
    syllable.phonetic_ipa_str
    for syllable in spc
    if phonology.render_syllable(syllable).acceptability
    != PhonotacticAcceptability(True, True)
]
"""
[<IPA 字符串 'bʊ̃ŋ˥˥'>, <IPA 字符串 'bo˥˥'>, <IPA 字符串 'bɐʔ˥˥'>]
"""
