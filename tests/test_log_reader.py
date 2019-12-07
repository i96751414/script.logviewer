# -*- coding: utf-8 -*-

import os
import sys
from tempfile import NamedTemporaryFile
from unittest import TestCase, main

if sys.version_info >= (3, 3):
    from unittest.mock import MagicMock
else:
    from mock import MagicMock

sys.modules["xbmc"] = MagicMock()
sys.modules["xbmcaddon"] = MagicMock()
from resources.lib.logreader import LogReader, SEPARATOR  # noqa
from resources.lib.utils import decode, encode  # noqa


class TestLogReader(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lines = ("\r" * 10000 + "\n" * 10000 + "\r\n" * 10000 + "\n" + "\r\n" * 10000 +
                     "\nline 1\nlá ççç ~ã´\nasdasdad\rasdda" + "ã" * 10000 +
                     "sdasd\r\nolalolaolloaol\n\n\nlast line\n\n" +
                     "\r" * 10000 + "\n" * 10000 + "\r\n" * 10000 + "\n" + "\r\n" * 10000)
        cls.incomplete_line = "incomplete line " + "áà" * 12311

    def setUp(self):
        self.f = NamedTemporaryFile("wb", delete=False)
        self.f.write(encode(self.lines))
        self.f.flush()

    def tearDown(self):
        self.f.close()
        os.remove(self.f.name)

    def test_tail(self):
        reader = LogReader(self.f.name)
        self.assertEqual(reader.tail(), self.lines)
        self.assertEqual(reader.tail(), "")

        self.f.write(encode(self.incomplete_line))
        self.f.flush()

        self.assertEqual(reader.tail(), self.incomplete_line)
        self.assertEqual(reader.tail(), "")

    def test_normal_read_lines(self):
        reader = LogReader(self.f.name)
        original_lines = self.lines.split(decode(SEPARATOR))
        self._test_read_lines(reader.normal_read_lines, original_lines)

    def test_reverse_read_lines(self):
        reader = LogReader(self.f.name)
        original_lines = list(reversed(self.lines.split(decode(SEPARATOR))))
        self._test_read_lines(reader.reverse_read_lines, original_lines)

    def _test_read_lines(self, read_lines, original_lines):
        # Normal test
        lines = list(read_lines())
        self.assertEqual(len(lines), len(original_lines))
        for i, l in enumerate(original_lines):
            self.assertEqual(l, lines[i])

        # Also test when file is being updated
        lines = []
        for i, l in enumerate(read_lines()):
            lines.append(l)
            if i % 1000 == 0:
                self.f.write(b"a\n")
                self.f.flush()

        self.assertEqual(len(lines), len(original_lines))
        for i, l in enumerate(original_lines):
            self.assertEqual(l, lines[i])


if __name__ == "__main__":
    main()
