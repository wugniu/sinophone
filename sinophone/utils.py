import sys
import warnings
from inspect import getdoc
from typing import AbstractSet, Any, FrozenSet, List

from .options import AnsiColors, LanguageCode, options


class PostInitCaller(type):
    """
    Call `__post_init__` after `__init__`.

    https://stackoverflow.com/a/17496524/11946514
    """

    def __call__(cls, *args, **kwargs) -> Any:
        obj = type.__call__(cls, *args, **kwargs)
        obj.__post_init__()
        return obj


class PrettyClass(object):
    """
    This class is pretty when printed.
    """

    def __repr__(self) -> str:
        OPEN_DELIMS = "([{'\""
        FALLBACK_DELIMS = ["'", '"']

        original_self_str = str(self)

        fallback_delim = FALLBACK_DELIMS[0]
        if FALLBACK_DELIMS[0] in original_self_str:
            if FALLBACK_DELIMS[1] not in original_self_str:
                fallback_delim = FALLBACK_DELIMS[1]
            elif original_self_str.index(FALLBACK_DELIMS[0]) < original_self_str.index(
                FALLBACK_DELIMS[1]
            ):
                fallback_delim = FALLBACK_DELIMS[1]

        self_str = (
            original_self_str
            if original_self_str[0] in OPEN_DELIMS
            else f"{fallback_delim}{original_self_str}{fallback_delim}"
        )

        color = self.color
        if color:
            return f"{color}<{self.translated_name} {self_str}{color}>{AnsiColors.END}"
        else:
            return f"<{self.translated_name} {self_str}>"

    @property
    def color(self) -> str:
        if not options.color:
            return ""
        return options.color_scheme.get(type(self).__name__, "")

    @property
    def translated_name(self) -> str:
        """
        The name of the component in a language specified in `options.repr_lang`.
        """

        if options.repr_lang == LanguageCode.ENGLISH:
            return self.en_latn_name
        elif options.repr_lang == LanguageCode.WU_CHINESE_IN_SINOGRAPH:
            return self.wuu_hant_name
        else:  # pragma: no cover
            raise ValueError(f"Unknown language code: {options.repr_lang}")

    @property
    def en_latn_name(self) -> str:
        return type(self).__name__

    @property
    def wuu_hant_name(self) -> str:
        """
        Wu Chinese translation of a `SyllableComponent` in Sinographs
        is always preceded by `吳:` in the docstring.
        """
        return self._get_translated_name_from_docstring_identifier("吳:")

    def _get_translated_name_from_docstring_identifier(self, identifier: str) -> str:
        docstring = getdoc(type(self))
        assert docstring is not None
        for line in docstring.split("\n"):
            if line.startswith(identifier):
                return line[len(identifier) :].strip()
        return type(self).__name__  # pragma: no cover


class SinophoneWarning(Warning):
    ...


def color_str(content: str = "", color_code: str = "") -> str:
    return f"{options.color_scheme.get(color_code, '')}{content}{AnsiColors.END}"


def repr_set_in_order(unordered_set: AbstractSet) -> str:
    return f"{{{str(sorted(unordered_set))[1:-1]}}}"


def obj_to_mro_chain_names(obj: object) -> List[str]:
    return [cls.__name__ for cls in type(obj).__mro__]


def sinophone_warning(msg: str) -> None:  # pragma: no cover
    warnings.warn(color_str(msg, "SinophoneWarning"), category=SinophoneWarning)


def warn_about_dict_ordering() -> None:
    if sys.version_info < (3, 7):  # pragma: no cover
        if options.repr_lang == LanguageCode.ENGLISH:
            sinophone_warning("Dict ordering is not guaranteed in Python < 3.7")
        elif options.repr_lang == LanguageCode.WU_CHINESE_IN_SINOGRAPH:
            sinophone_warning("辭典在墶 Python < 3.7 當中弗一定保證順序")
        else:
            raise ValueError(f"Unknown language code: {options.repr_lang}")


def fix_ipapy_import_from_collections() -> None:
    """
    Fix bug in ipapy for 3.10 and above.
    """

    import sys
    from collections.abc import MutableSequence

    if sys.version_info >= (3, 10):
        setattr(sys.modules["collections"], "MutableSequence", MutableSequence)


def dict_to_frozenset(d: dict) -> FrozenSet:
    return frozenset(sorted(d.items()))
