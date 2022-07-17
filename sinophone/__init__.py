"""
`Sinophone` /ˈsaɪnəˌfoʊn/: Python package for manipulating Chinese phonology.

`三耨風` /se˥˨꜒.noʔ꜓.foŋ꜔꜕/：用於處理漢語音韻個 Python 模塊。
"""

__author__ = "Yuanhao 'Nyoeghau' Chen"
__license__ = "MIT"
__version__ = "0.0.1"
__email__ = "nyoeghau@nyoeghau.com"


from . import phonetics, phonology
from .options import options

__all__ = [
    "options",
    "phonetics",
    "phonology",
]
