import unittest

from slugify import slugify_title


class SlugifyTitleTests(unittest.TestCase):
    def test_lowercases_letters(self) -> None:
        self.assertEqual(slugify_title("Hello World"), "hello-world")

    def test_collapses_repeated_separators(self) -> None:
        self.assertEqual(slugify_title("hello___world---again"), "hello-world-again")

    def test_removes_punctuation(self) -> None:
        self.assertEqual(slugify_title("Hello, World!"), "hello-world")

    def test_preserves_digits(self) -> None:
        self.assertEqual(slugify_title("Version 2 Release"), "version-2-release")

    def test_strips_leading_and_trailing_separators(self) -> None:
        self.assertEqual(slugify_title("  ---Hello World___  "), "hello-world")

    def test_empty_or_whitespace_only_input(self) -> None:
        self.assertEqual(slugify_title(""), "")
        self.assertEqual(slugify_title("   "), "")


if __name__ == "__main__":
    unittest.main()
