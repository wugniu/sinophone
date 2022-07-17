import logging
from unittest import TestCase

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


class BaseTestCase(TestCase):
    def setUp(self) -> None:
        logging.info("=" * 60)
        logging.info(f"{self.id()} begin")

    def tearDown(self) -> None:
        logging.info(f"{self.id()} finish")

    def assertEqualAndHashEqual(self, first, second, msg="") -> None:
        self.assertEqual(first, second, msg)
        self.assertEqual(hash(first), hash(second), msg)

    def assertNotEqualAndHashNotEqual(self, first, second, msg="") -> None:
        self.assertNotEqual(first, second, msg)
        self.assertNotEqual(hash(first), hash(second), msg)
