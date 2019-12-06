# -*- coding: utf-8 -*-

import os
from tempfile import NamedTemporaryFile
from unittest import TestCase, main

from resources.lib.logreader import LogReader, encode, decode, SEPARATOR


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
        lines = list(reader.normal_read_lines())
        original_lines = self.lines.split(decode(SEPARATOR))

        self.assertEqual(len(lines), len(original_lines))
        for i, l in enumerate(original_lines):
            self.assertEqual(l, lines[i])

    def test_reverse_read_lines(self):
        reader = LogReader(self.f.name)
        lines = list(reader.reverse_read_lines())
        original_lines = self.lines.split(decode(SEPARATOR))

        self.assertEqual(len(lines), len(original_lines))
        for i, l in enumerate(reversed(original_lines)):
            self.assertEqual(l, lines[i])


if __name__ == "__main__":
    main()
