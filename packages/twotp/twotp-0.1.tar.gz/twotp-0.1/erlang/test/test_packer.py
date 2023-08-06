# Copyright (c) 2007-2008 Thomas Herve <therve@free.fr>.
# See LICENSE for details.

"""
Packer tests.
"""

from twisted.trial.unittest import TestCase

from erlang.term import Atom, Tuple, Pid, Reference, List
from erlang.packer import Packer, UnhandledClass



class PackTestCase(TestCase):
    """
    Test packing of erlang terms.
    """

    def setUp(self):
        """
        Create a test packer.
        """
        self.packer = Packer()


    def test_packChar(self):
        """
        Pack an integer on 1 byte, not the erlang term.
        """
        self.assertEquals(self.packer.packChar(3), "\x03")


    def test_packCharError(self):
        """
        Char values are limited between 0 and 255, so values out of this
        range should raise an error.
        """
        self.assertRaises(ValueError, self.packer.packChar, 302)
        self.assertRaises(ValueError, self.packer.packChar, -3)


    def test_packShort(self):
        """
        Pack integers on 2 bytes, not the erlang terms.
        """
        self.assertEquals(self.packer.packShort(3), "\x00\x03")
        self.assertEquals(self.packer.packShort(2032), "\x07\xf0")


    def test_packShortError(self):
        """
        Short values are limited between 0 and 65535, so values out of this
        range should raise an error.
        """
        self.assertRaises(ValueError, self.packer.packShort, 723120)


    def test_packInt(self):
        """
        Test packing integers, not the erlang terms.
        """
        self.assertEquals(self.packer.packInt(3), "\x00\x00\x00\x03")
        self.assertEquals(self.packer.packInt(2032), "\x00\x00\x07\xf0")
        self.assertEquals(self.packer.packInt(723120), "\x00\x0b\x08\xb0")


    def test_packIntError(self):
        """
        Int values should fit in 32 bits, so values out of this range should
        raise an error.
        """
        self.assertRaises(ValueError, self.packer.packInt, pow(2, 32) + 312)


    def test_packAtom(self):
        """
        Pack an atom term.
        """
        self.assertEquals(self.packer.packOneTerm(Atom("yes")), "d\x00\x03yes")


    def test_packNewReference(self):
        """
        Test packing a new reference.
        """
        r = Reference(Atom("bar"), [3, 4], 2)
        self.assertEquals(self.packer.packOneTerm(r),
            "r\x00\x02d\x00\x03bar\x02\x00\x00\x00\x03\x00\x00\x00\x04")


    def test_packSmallInteger(self):
        """
        Test packing a small integer.
        """
        self.assertEquals(self.packer.packOneTerm(123), "a\x7b")


    def test_packBigInteger(self):
        """
        Test packing a big integer.
        """
        self.assertEquals(self.packer.packOneTerm(1230), "b\x00\x00\x04\xce")
        self.assertEquals(self.packer.packOneTerm(-123), "b\xff\xff\xff\x85")


    def test_packSmallString(self):
        """
        Test packing a small string.
        """
        self.assertEquals(self.packer.packOneTerm("spam"), "k\x00\x04spam")


    def test_packFloat(self):
        """
        Test packing a float.
        """
        self.assertEquals(self.packer.packOneTerm(1.234),
            "c1.23399999999999998579e+00\x00\x00\x00\x00\x00")


    def test_packString(self):
        """
        Test packing a big string.
        """
        # Fake size of short for not allocating a huge string
        self.packer.MAX_SHORT = 15
        longString = "x" * 20
        term = self.packer.packOneTerm(longString)
        self.assertEquals(term,
            "l\x00\x00\x00\x14axaxaxaxaxaxaxaxaxaxaxaxaxaxaxaxaxaxaxaxj")


    def test_packPid(self):
        """
        Test packing a Pid.
        """
        p = Pid(Atom("foo"), 1234, 12, 2)
        self.assertEquals(self.packer.packOneTerm(p),
            "gd\x00\x03foo\x00\x00\x04\xd2\x00\x00\x00\x0c\x02")


    def test_packReference(self):
        """
        Test packing an old style reference.
        """
        r = Reference(Atom("bar"), 3, 2)
        self.assertEquals(self.packer.packOneTerm(r),
            "ed\x00\x03bar\x00\x00\x00\x03\x02")


    def test_packSmallTuple(self):
        """
        Test packing a tuple of atoms.
        """
        t = Tuple((Atom("a"), Atom("b")))
        self.assertEquals(self.packer.packOneTerm(t),
            "h\x02d\x00\x01ad\x00\x01b")


    def test_packLargeTuple(self):
        """
        Test packing a large tuple of atoms.
        """
        # Limit the size for not building a huge list
        self.packer.MAX_CHAR = 2
        t = Tuple((Atom("a"), Atom("b"), Atom("c")))
        self.assertEquals(self.packer.packOneTerm(t),
            "i\x00\x00\x00\x03d\x00\x01ad\x00\x01bd\x00\x01c")


    def test_packList(self):
        """
        Test packing a list of atoms.
        """
        t = List((Atom("a"), Atom("b")))
        self.assertEquals(self.packer.packOneTerm(t),
            "l\x00\x00\x00\x02d\x00\x01ad\x00\x01bj")


    def test_packEmptyList(self):
        """
        Test packing an empty list.
        """
        self.assertEquals(self.packer.packOneTerm([]), "j")


    def test_packUnhandledClass(self):
        """
        Try packing an object not handled.
        """
        d = {"a": 1}
        self.assertRaises(UnhandledClass, self.packer.packOneTerm, d)


    def test_termToBinary(self):
        """
        C{termToBinary} should produce a fully compliant object with the
        C{MAGIC_VERSION} flag.
        """
        self.assertEquals(self.packer.termToBinary(123), "\x83a\x7b")

