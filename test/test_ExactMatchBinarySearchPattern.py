import unittest

from bgrep import ExactMatchBinarySearchPattern

class ExactMatchBinarySearchPatternTestCase(unittest.TestCase):

    def do_test_match_expected(self, needle, haystack, haystack_offset,
            haystack_length, expected_offset, expected_length,
            expected_complete=True):
        x = ExactMatchBinarySearchPattern(needle)
        result = x.search(haystack, haystack_offset, haystack_length)
        if result is None:
            self.fail("search() returned None")
        (actual_offset, actual_length, actual_state) = result
        self.assertEqual(expected_offset, actual_offset)
        self.assertEqual(expected_length, actual_length)
        if expected_complete:
            self.assertIsNone(actual_state)
        else:
            self.assertIsNotNone(actual_state)

    def do_test_no_match_expected(self, needle, haystack, haystack_offset,
            haystack_length):
        x = ExactMatchBinarySearchPattern(needle)
        result = x.search(haystack, haystack_offset, haystack_length)
        self.assertIsNone(result)


class TestBasicFunctionality(ExactMatchBinarySearchPatternTestCase):

    def test01(self):
        self.do_test_match_expected(b"a", b"a", 0, None, 0, 1)

    def test02(self):
        self.do_test_match_expected(b"abc", b"abc", 0, None, 0, 3)

    def test03(self):
        self.do_test_match_expected(b"abc", b"abcabc", 0, None, 0, 3)

    def test04(self):
        self.do_test_match_expected(b"abc", b"abcabc", 1, None, 3, 3)

    def test05(self):
        self.do_test_match_expected(b"abc", b"abcabc", 3, None, 3, 3)

    def test06(self):
        self.do_test_match_expected(b"abc", b"abcabc", 0, 3, 0, 3)

    def test07(self):
        self.do_test_no_match_expected(b"abc", b"abczbc", 1, 3)

    def test08(self):
        self.do_test_no_match_expected(b"abc", b"", 0, 0)


class TestEmptySearchPattern(ExactMatchBinarySearchPatternTestCase):

    def test_empty_haystack(self):
        self.do_test_match_expected(b"", b"", 0, None, 0, 0)

    def test_haystack_length1(self):
        self.do_test_match_expected(b"", b"a", 0, None, 0, 0)

    def test_haystack_length2(self):
        self.do_test_match_expected(b"", b"ab", 0, None, 0, 0)

    def test_haystack_offset1_length0(self):
        self.do_test_match_expected(b"", b"abc", 1, 0, 1, 0)

    def test_haystack_offset1_length1(self):
        self.do_test_match_expected(b"", b"abc", 1, 1, 1, 0)

    def test_haystack_offset_equals_len(self):
        self.do_test_match_expected(b"", b"abc", 3, 0, 3, 0)

    def test_haystack_offset_greater_than_len_length0(self):
        self.do_test_no_match_expected(b"", b"abc", 4, 0)

    def test_haystack_offset_greater_than_len_length1(self):
        self.do_test_no_match_expected(b"", b"abc", 4, 1)


class TestPartialMatch(ExactMatchBinarySearchPatternTestCase):

    def test_pattern_abc_haystack_a(self):
        self.do_test_match_expected(b"abc", b"a", 0, None, 0, 1, False)

    def test_pattern_abc_haystack_ba(self):
        self.do_test_match_expected(b"abc", b"ba", 0, None, 1, 1, False)

    def test_pattern_abc_haystack_ab(self):
        self.do_test_match_expected(b"abc", b"ab", 0, None, 0, 2, False)

    def test_pattern_abc_haystack_bab(self):
        self.do_test_match_expected(b"abc", b"bab", 0, None, 1, 2, False)
