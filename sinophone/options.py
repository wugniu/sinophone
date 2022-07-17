import os
from copy import copy
from dataclasses import dataclass, field
from typing import Dict


class AnsiColors(object):
    """
    ANSI colors and styles.
    """

    os.system("")
    """
    https://stackoverflow.com/questions/12492810/...
    python-how-can-i-make-the-ansi-escape-codes-to-work-also-in-windows
    """

    BLACK = "\033[0;30;48m"
    RED = "\033[0;31;48m"
    GREEN = "\033[0;32;48m"
    YELLOW = "\033[0;33;48m"
    BLUE = "\033[0;34;48m"
    PURPLE = "\033[0;35;48m"
    CYAN = "\033[0;36;48m"
    PLAIN = "\033[0;37;48m"
    BOLD = "\033[1;37;48m"
    END = "\033[0;37;0m"


RAINBOW_COLOR_SCHEME: Dict[str, str] = {
    "Syllable": AnsiColors.PLAIN,
    "Initial": AnsiColors.RED,
    "Final": AnsiColors.YELLOW,
    "Medial": AnsiColors.GREEN,
    "Nucleus": AnsiColors.CYAN,
    "Coda": AnsiColors.BLUE,
    "Tone": AnsiColors.PURPLE,
    "ExistentGrammatical": AnsiColors.GREEN,
    "NonexistentGrammatical": AnsiColors.CYAN,
    "ExistentUngrammatical": AnsiColors.YELLOW,
    "NonexistentUngrammatical": AnsiColors.RED,
    "SinophoneWarning": AnsiColors.YELLOW,
}


class LanguageCode(object):
    ENGLISH = "en-Latn"
    WU_CHINESE_IN_SINOGRAPH = "wuu-Hant"

    @classmethod
    def is_code_valid(cls, code: str) -> bool:
        return code in [getattr(cls, k) for k in dir(cls) if not k.startswith("_")]


@dataclass
class Options(object):
    color: bool = True
    """
    Whether to use ANSI colors in the `__repr__` of some classes.
    """

    _repr_lang: str = LanguageCode.ENGLISH
    """
    Which language to use in `__repr__` of some classes.
    """

    color_scheme: Dict[str, str] = field(
        default_factory=lambda: copy(RAINBOW_COLOR_SCHEME)
    )
    """
    Which color scheme to use in `__repr__` of some classes.
    """

    @property
    def repr_lang(self) -> str:
        return self._repr_lang

    @repr_lang.setter
    def repr_lang(self, lang: str) -> None:
        if not LanguageCode.is_code_valid(lang):
            raise ValueError(f"Unknown language code: {lang}")
        self._repr_lang = lang


options = Options()
"""
`sinophone` package options.
"""
