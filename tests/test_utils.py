from sinophone import options
from sinophone.utils import (
    PostInitCaller,
    PrettyClass,
    fix_ipapy_import_from_collections,
)

from .utils import BaseTestCase


class TestUtils(BaseTestCase):
    def test_post_init_caller(self) -> None:
        class Foo(metaclass=PostInitCaller):
            def __init__(self):
                self.called = False

            def __post_init__(self):
                self.called = True

        foo = Foo()

        self.assertTrue(foo.called)

    def test_translated_name(self) -> None:
        class Foo(PrettyClass):
            """
            吳: 富
            """

        foo = Foo()

        with self.assertRaises(ValueError):
            options.repr_lang = "lol"

        options.repr_lang = "en-Latn"
        self.assertEqual(foo.translated_name, "Foo")
        options.repr_lang = "wuu-Hant"
        self.assertEqual(foo.translated_name, "富")

    def test_fix_ipapy_import_from_collections(self) -> None:
        fix_ipapy_import_from_collections()
        from ipapy.ipastring import IPAString  # noqa: F401
