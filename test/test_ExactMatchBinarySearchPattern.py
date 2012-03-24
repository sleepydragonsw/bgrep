import unittest

from bgrep import ExactMatchBinarySearchPattern

class Test(unittest.TestCase):

    def test_EmptyNeedle_EmptyHaystack(self):
        self.do_test_match_expected(b"", b"", 0, 0, 0, 0, None)

    def test_EmptyNeedle_NonEmptyHaystack(self):
        self.do_test_match_expected(b"", b"abc", 0, 0, 0, 0, None)

    def test_EmptyNeedle_NonEmptyHaystack_NonZeroOffset(self):
        self.do_test_match_expected(b"", b"abc", 2, 0, 2, 0, None)

    def test_NeedleA_HaystackA(self):
        self.do_test_match_expected(b"A", b"A", 0, 0, 0, 0, None)

    def do_test_match_expected(self, needle, haystack, haystack_offset,
            haystack_length, expected_offset, expected_length, expected_state):
        x = ExactMatchBinarySearchPattern(needle)
        result = x.search(haystack, haystack_offset, haystack_length)
        if result is None:
            self.fail("search() returned None")
        (actual_offset, actual_length, actual_state) = result
        self.assertEqual(expected_offset, actual_offset)
        self.assertEqual(expected_length, actual_length)
        if expected_state is None:
            self.assertIsNone(actual_state)
        else:
            self.assertEqual(expected_state, actual_state)
