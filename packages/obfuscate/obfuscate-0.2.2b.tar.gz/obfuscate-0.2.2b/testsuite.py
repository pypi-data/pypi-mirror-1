"""Unit tests for obfuscate.py"""

from __future__ import division

import string
import unittest


# Module being tested.
import obfuscate

# =========================
# === Utility functions ===
# =========================

def make_iterable_test_data():
    """Return a list of iterables and a list of the iterables as strings.

    Returns a tuple with two items. The first is a list of assorted iterables,
    the second is the same data converted to strings:
        ([a, b, c, ..., z], [''.join(a), ..., ''.join(z)])
    """
    # First do the re-usable iterables.
    iterables = TEST_ITERABLES + [[BYTES]]
    strings = [''.join(it) for it in iterables]
    # Now add the use-once iterables.
    for s in TEST_STRINGS:
        iterables.append(reversed(s))
        strings.append(s[::-1])
        iterables.append(iter(s))
        strings.append(s)
    return (iterables, strings)


# =============================
# === Data sets for testing ===
# =============================

# Define some common data sets for testing.

ASCII = ''.join([chr(i) for i in xrange(128)])
BYTES = ''.join([chr(i) for i in xrange(256)])


ASCII_TEST_STRINGS = [
    # These should all be strings.
    "", "    ", "\n", "\0", "\01\r\n",
    "abcdEFGH", "1234567890", "#!@*&^%()-<>+",
    "some text 1234 \t\v\f\r AND MORE",
    "NOBODY expects the Spanish Inquistition!!!",
    ]

TEST_STRINGS = ASCII_TEST_STRINGS + ["ABC\xc8 \xc9123", "\xa1\xfe\xff"]

ASCII_TEST_ITERABLES = [
    # Make sure all of these are re-usable. No iterators!
    # Assorted empty iterables:
    [], (), {}, set(),
    # Lists:
    ['\0~'], ["a", "bb", "ccc", "DDDD"],
    # Tuples:
    ('alpha', 'beta', 'gamma', 'delta'),
    (';@ab 35', '+%~1', '\n\t\v #', '*=$m\0'),
    # Sets:
    set('z'), set(['', 'v']),
    ]

TEST_ITERABLES = ASCII_TEST_ITERABLES + [("ABC\xc8 ", "\xc9123"),
    ["\xa1\xfe", "\xff"]]


# ===================
# === Test suites ===
# ===================

class GlobalTest(unittest.TestCase):
    def testState(self):
        """Test the state of globals."""
        self.assertEquals(len(obfuscate.BYTES), 256)
        self.assertEquals(obfuscate.BYTES, BYTES)
    def testMeta(self):
        """Test existence of metadata."""
        for meta in "__doc__  __version__  __date__  __author__  __all__".split():
            self.failUnless(hasattr(obfuscate, meta))


class AbstractClassTest(unittest.TestCase):
    """Test the behaviour of the abstract base classes."""
    targets = [obfuscate._SelfInvertingMonoCipher, obfuscate._MonoSubCipher]
    def testAbstract(self):
        """Test that each abstract class cannot be instantiated."""
        for target in self.targets:
            self.assertRaises(TypeError, target, [])


class SelfInvertingMonoCipherTest(unittest.TestCase):
    """Test the behaviour of the _SelfInvertingMonoCipher class."""

    # Since the class is an abstract class, we subclass it and work with that.
    class target(obfuscate._SelfInvertingMonoCipher):
        TABLE = BYTES

    def testConstructor(self):
        """Test that the constructor doesn't return a class instance."""
        cls = self.target
        self.failIf(isinstance(cls(''), cls))
        self.failIf(isinstance(cls([]), cls))

    def testCall(self):
        """Test that calling the class returns the correct object type."""
        # Note that we don't instantiate the class, but use it as a function.
        # See the source for an explanation.
        self.failUnless(isinstance(self.target(''), basestring))
        self.failUnless(hasattr(self.target([]), 'next'))

    def testStream(self):
        """Test the stream classmethod."""
        message = "Nobody expects the Spanish Inquisition!".split()
        it = self.target.stream(message, BYTES)
        self.assertEquals(it.next(), 'Nobody')
        self.assertEquals(it.next(), 'expects')
        self.assertEquals(it.next(), 'the')
        self.assertEquals(it.next(), 'Spanish')
        self.assertEquals(it.next(), 'Inquisition!')
        self.assertRaises(StopIteration, it.next)


class MonoSubCipherTest(unittest.TestCase):
    """Test the behaviour of the _MonoSubCipher class."""

    plaintext =  "Nobody expects the Spanish Inquisition!"
    ciphertext = "No5oy2 x1pxzts thx Sp4nish Inquisition~"

    # Since the class is an abstract class, we subclass it and work with that.
    class target(obfuscate._MonoSubCipher):
        TABLE    = string.maketrans("abcdef12345xyz!~?", "45zyxabcdef123~?!")
        REVTABLE = string.maketrans("45zyxabcdef123~?!", "abcdef12345xyz!~?")

    def testConstructor(self):
        """Test that the constructor does return a class instance."""
        self.failUnless(isinstance(self.target(), self.target))

    def testStream(self):
        """Test the stream classmethod."""
        inst = self.target()
        message = self.plaintext.split()
        it = inst.stream(message, BYTES)
        for word in message:
            self.assertEquals(it.next(), word)
        self.assertRaises(StopIteration, it.next)

    def testEncrypt(self):
        """Test encryption."""
        inst = self.target()
        self.assertEquals(inst.encrypt(self.plaintext), self.ciphertext)

    def testDecrypt(self):
        """Test encryption."""
        inst = self.target()
        self.assertEquals(inst.decrypt(self.ciphertext), self.plaintext)

    def testRoundTrip(self):
        inst = self.target()
        self.assertEquals(inst.decrypt(inst.encrypt(BYTES)), BYTES)
        self.assertEquals(inst.encrypt(inst.decrypt(BYTES)), BYTES)


class DualMethodTest(unittest.TestCase):
    """Test the dualmethod descriptor."""

    class K(object):
        @obfuscate.dualmethod
        def method(this, x):
            """This is a doc string."""
            return (this, type(this), x)

    def testDualMethodOther(self):
        """Other tests on dualmethod."""
        self.failUnlessEqual(self.K.method.__doc__, "This is a doc string.")

    def testDualMethodInstance(self):
        """Test calling the dual method on the instance."""
        instance = self.K()
        result = instance.method(123)
        self.failUnlessEqual(result, (instance, self.K, 123))

    def testDualMethodClass(self):
        """Test calling the dual method on the class."""
        result = self.K.method(123)
        self.failUnlessEqual(result, (self.K, type, 123))

    def testDualMethodDirect(self):
        """Test calling the descriptor directly."""
        instance = self.K()
        result = self.K.__dict__['method'].__get__(instance)(123)
        self.failUnlessEqual(result, (instance, self.K, 123))


class SelfInvertingTests(unittest.TestCase):
    """Test self-inverting ciphers."""

    ciphers = [
        obfuscate.rot13, obfuscate.rot5, obfuscate.rot18, obfuscate.rot47,
        obfuscate.atbash, obfuscate.frob
        ]

    def testInvertStrings(self):
        """Test ciphers self-invert correctly with string arguments."""
        for cipher in self.ciphers:
            for s in TEST_STRINGS + [BYTES]:
                self.failUnlessEqual(cipher(cipher(s)), s)

    def testInvertIter(self):
        """Test ciphers self-invert correctly with iterator arguments."""
        for cipher in self.ciphers:
            for it, s in zip(*make_iterable_test_data()):
                self.failUnlessEqual(''.join(cipher(cipher(it))), s)

    def testRot13AgainstBuiltin(self):
        """Compare rot13 against the Python version."""
        for s in ASCII_TEST_STRINGS + [ASCII]:
            self.failUnlessEqual(s.encode('rot13'), obfuscate.rot13(s))


class FunctionTests(unittest.TestCase):
    """Test stand-alone functions."""

    def test_is_string(self):
        is_string = obfuscate.is_string
        for x in ['', 'abc', ' \n', '123']:
            self.failUnless(is_string(x))
        for x in [None, [], iter('abc'), 123, {}]:
            self.failIf(is_string(x))

    def test_remove_duplicates(self):
        remove_duplicates = obfuscate.remove_duplicates
        testdata = [
            ('', ''), ('A', 'A'), ('ABCDEF\n', 'ABCDEF\n'), ('spam 123', 'spam 123'),
            ('aardvark', 'ardvk'), ('moon river', 'mon rive'), ('TELEPHONE', 'TELPHON'),
            ]
        for arg, result in testdata:
            self.assertEquals(remove_duplicates(arg), result)

    def test_key2permutation(self):
        key2permutation = obfuscate.key2permutation
        testdata = [
            ('', []), ('A', [0]), ('ABCDEFGH', [0, 1, 2, 3, 4, 5, 6, 7]),
            ('spam', [3, 2, 0, 1]), ('zyxwabc', [6, 5, 4, 3, 0, 1, 2]),
            # Tests with duplicates.
            ('moon', [0, 2, 3, 1]), ('telephone', [8, 0, 4, 1, 7, 3, 6, 5, 2]),
            ]
        for arg, result in testdata:
            self.assertEquals(key2permutation(arg), result)

    def test_ceildiv(self):
        ceildiv = obfuscate.ceildiv
        self.assertEquals(ceildiv(10, 2), 5)
        self.assertEquals(ceildiv(11, 2), 6)
        self.assertEquals(ceildiv(12, 2), 6)
        self.assertEquals(ceildiv(11, -2), -5)


class CaesarTest(unittest.TestCase):
    """Test Caesar cipher."""

    target = obfuscate.Caesar

    def roundtrip(self, shift, message):
        """Verify that the given shift round-trips correctly."""
        inst = self.target(shift)
        self.assertEquals(inst.decrypt(inst.encrypt(message)), message)
        self.assertEquals(inst.encrypt(inst.decrypt(message)), message)

    def testRoundTrip(self):
        """Test that all Caesar shifts round-trip correctly."""
        for i in range(26):
            for s in TEST_STRINGS + [BYTES]:
                self.roundtrip(i, s)

    def testModulo(self):
        """Test that Caesar shifts are modulo 26."""
        for i in range(26):
            inst1 = self.target(i)
            inst2 = self.target(i+26)
            self.assertEquals(inst1.encrypt(BYTES), inst2.encrypt(BYTES))

    def testRot13(self):
        """Test that a Caesar shift of 13 is the same as rot13."""
        caesar13 = self.target(13)
        for s in ASCII_TEST_STRINGS:
            self.failUnlessEqual(caesar13.encrypt(s), s.encode('rot13'))

    def testIter(self):
        """Test that Caesar works with interables other than strings."""
        caesar0 = self.target(0)  # Null cipher.
        for it, s in zip(*make_iterable_test_data()):
            self.assertEquals(''.join(caesar0.encrypt(it)), s)


class KeywordTest(unittest.TestCase):

    target = obfuscate.Keyword

    def testGenerateKey(self):
        """Test the key generation method."""
        data = [
            ('',    'abcdefghijklmnopqrstuvwxyz'),
            ('z',   'zabcdefghijklmnopqrstuvwxy'),
            ('zyx', 'zyxabcdefghijklmnopqrstuvw'),
            ("Nobody expects the Spanish Inquisition!",
                "nobdyexpctshaiquvwzfgjklmr"),
            ]
        genkey = self.target.generate_key
        for key, result in data:
            assert len(result) == 26
            self.assertEquals(genkey(key), result)

    def testStrEncryption(self):
        """Test Keyword cipher works as expected with strings."""
        null_cipher = self.target('')
        for s in TEST_STRINGS + [BYTES]:
            self.assertEquals(null_cipher.encrypt(s), s)

    def testIterEncryption(self):
        """Test Keyword cipher works as expected with iterables."""
        null_cipher = self.target('')
        for it, s in zip(*make_iterable_test_data()):
            self.assertEquals(''.join(null_cipher.encrypt(it)), s)

    def testRoundTrip(self):
        """Test the Keyword cipher round-trips correctly."""
        for key in ('cheeseshop', 'ethel the aardvark', 'norwegian blue',
        'monty python', 'spanish inquisition'):
            cipher = self.target(key)
            for s in TEST_STRINGS + [BYTES]:
                self.assertEquals(cipher.decrypt(cipher.encrypt(s)), s)
            for it, s in zip(*make_iterable_test_data()):
                result = cipher.decrypt(cipher.encrypt(it))
                self.assertEquals(''.join(result), s)


class AffineTest(unittest.TestCase):

    target = obfuscate.Affine

    goodm = (10, 26, 52, 62, 94, 256)
    keys = [ # Known good key parameters, with arbitrary values of b.
        # Valid values of a for m=10 are 1, 3, 7, 9.
        (1, 6, 10),     (3, 1, 10),     (7, 9, 10),     (9, 4, 10),
        # Valid a for m=26 are 1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25.
        (1, 3, 26),     (3, 7, 26),     (5, 0, 26),     (7, 2, 26),
        (9, 17, 26),    (11, 21, 26),   (15, 8, 26),    (17, 3, 26),
        (19, 19, 26),   (21, 9, 26),    (23, 14, 26),   (25, 16, 26),
        # Arbitrarily selected values of a for m=52, 62, 94 and 256.
        (1, 17, 52),    (17, 11, 52),   (33, 0, 52),    (51, 42, 52),
        (1, 38, 62),    (13, 20, 62),   (45, 12, 62),   (61, 59, 62),
        (1, 87, 94),    (23, 72, 94),   (55, 80, 94),   (93, 36, 94),
        (1, 101, 256),  (29, 200, 256), (193, 11, 256), (255, 142, 256),
        ]

    def testBadAlphabetSize(self):
        """Test that the Affine class will not instantiate with invalid alphabet size."""
        for m in range(-10, 300):
            if m in self.goodm: continue
            self.assertRaises(ValueError, self.target, 1, 1, m)

    def testBadParams(self):
        """Test that the Affine class will not instantiate with bad key parameters."""
        bad = [  # Selected values of a that are not coprime with m.
            (0, 1, 10),     (2, 1, 10),     (6, 1, 10),     (8, 1, 10),
            (0, 1, 26),     (4, 1, 26),     (12, 1, 26),    (20, 1, 26),
            (0, 1, 52),     (8, 1, 52),     (28, 1, 52),    (42, 1, 52),
            (0, 1, 62),     (14, 1, 62),    (31, 1, 62),    (60, 1, 62),
            (0, 1, 94),     (47, 1, 94),    (68, 1, 94),    (92, 1, 94),
            (0, 1, 256),    (14, 1, 256),   (60, 1, 256),   (100, 1, 256),
            ]
        for a, b, m in bad:
            self.assertRaises(ValueError, self.target, a, b, m)

    def testGoodParams(self):
        """Test that the Affine class will instantiate with good key parameters."""
        for a, b, m in self.keys:
            self.failUnless(isinstance(self.target(a, b, m), self.target))

    def testCaesar(self):
        """Test that the Affine class can implement a Caesar shift."""
        for shift in range(26):
            affine = self.target(1, shift, 26)
            caesar = obfuscate.Caesar(shift)
            self.assertEquals(affine.encrypt(BYTES), caesar.encrypt(BYTES))

    def testAtbash(self):
        """Test that the Affine class can implement the Atbash cipher."""
        affine = self.target(25, 25, 26)
        self.assertEquals(affine.encrypt(BYTES), obfuscate.atbash(BYTES))

    def testStrEncryption(self):
        """Test the Affine cipher works as expected with strings."""
        for m in self.goodm:
            null_cipher = self.target(1, 0, m)
            for s in TEST_STRINGS + [BYTES]:
                self.assertEquals(null_cipher.encrypt(s), s)

    def testIterEncryption(self):
        """Test the Affine cipher works as expected with iterables."""
        for m in self.goodm:
            null_cipher = self.target(1, 0, m)
            for it, s in zip(*make_iterable_test_data()):
                self.assertEquals(''.join(null_cipher.encrypt(it)), s)

    def testRoundTrip(self):
        """Test the Affine cipher round-trips correctly."""
        for key in self.keys:
            cipher = self.target(*key)
            for s in TEST_STRINGS + [BYTES]:
                self.assertEquals(cipher.decrypt(cipher.encrypt(s)), s)
            for it, s in zip(*make_iterable_test_data()):
                result = cipher.decrypt(cipher.encrypt(it))
                self.assertEquals(''.join(result), s)


class PlayfairTest(unittest.TestCase):
    """Test Playfair cipher."""

    target = obfuscate.Playfair
    alphabet = 'ABCDEFGHIKLMNOPQRSTUVWXYZ'
    assert len(alphabet) == 25

    # Note that not all characters in these keys are significant.
    testkeys = ['cherry pie', 'king george', 'PLAYFAIRCIPHER',
        'yellow-green', 'xyz1234%^&cba', 'UVW+-*/9876mnopq']
    testdata = [ # Caution here! This implementation of Platfair is lossy.
        # (plaintext, ciphertext)
        ('Jumping Jack Flash', 'IUMPINGIACKFLASH'),
        ('Beware the Jabberwock', 'BEWARETHEIABBERWOCKX'),
        ('abcd1234\nxyz', 'ABCDXYZX'),
        ('Nobody expects the Spanish Inquisition!', 'NOBODYEXPECTSTHESPANISHINQUISITION'),
        ('Lions and tigers and bears, oh my!', 'LIONSANDTIGERSANDBEARSOHMY'),
        ('Trip to the moon', 'TRIPTOTHEMOXON'),
        ('Double XX', 'DOUBLEXQXQ'),
        ]

    def testPadding(self):
        """Test the PADDING attribute."""
        padding = self.target.PADDING
        self.failUnlessEqual(len(padding), 2)
        self.failIfEqual(padding[0], padding[1])
        self.failUnless(padding[0] in self.alphabet)
        self.failUnless(padding[1] in self.alphabet)

    def testInstantiate(self):
        """Test that Playfair can be instantiated."""
        self.assert_(isinstance(self.target(''), self.target))

    def testRoundTrip(self):
        """Test round-tripping of the Playfair cipher."""
        # Caution here: this implementation of Playfair is lossy!
        for key in self.testkeys:
            inst = self.target(key)
            for plaintext, ciphertext in self.testdata:
                result = inst.decrypt(inst.encrypt(plaintext))
                self.assertEquals(result, ciphertext)

    def testPreprocess(self):
        """Test Playfair preprocess method."""
        it = self.target.preprocess('ajk12z\n')
        self.assertEquals(it.next(), 'A')
        self.assertEquals(it.next(), 'I')
        self.assertEquals(it.next(), 'K')
        self.assertEquals(it.next(), 'Z')
        self.assertRaises(StopIteration, it.next)

    # TODO - test cases for these methods?
    # digraphs transform_digraph transform encrypt decrypt


class Playfair6Test(PlayfairTest):
    """Test Playfair6 cipher."""

    target = obfuscate.Playfair6
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    assert len(alphabet) == 36

    testdata = PlayfairTest.testdata[3:] + [
        ('Jumping Jack Flash', 'JUMPINGJACKFLASH'),
        ('Beware the Jabberwock', 'BEWARETHEJABBERWOCKX'),
        ('abcd1234\nxyz', 'ABCD1234XYZX'),
        ]

    def testPreprocess(self):
        """Test Playfair preprocess method."""
        it = self.target.preprocess('ajk12z\n')
        self.assertEquals(it.next(), 'A')
        self.assertEquals(it.next(), 'J')
        self.assertEquals(it.next(), 'K')
        self.assertEquals(it.next(), '1')
        self.assertEquals(it.next(), '2')
        self.assertEquals(it.next(), 'Z')
        self.assertRaises(StopIteration, it.next)


class Playfair16Test(PlayfairTest):
    """Test Playfair16 cipher."""

    target = obfuscate.Playfair16
    alphabet = BYTES
    assert len(alphabet) == 256

    testdata = [
        ('Jumping Jack Flash', 'Jumping Jack Flash'),
        ('Beware the Jabberwock', 'Beware the Jabberwock\xa0'),
        ('abcd1234\nxyz', 'abcd1234\nxyz'),
        ('Nobody expects the Spanish Inquisition!', 'Nobody expects the Spanish Inquisition!\xa0'),
        ('Lions and tigers and bears, oh my!', 'Lions and tigers and bears, oh my!'),
        ('Trip to the moon', 'Trip to the moon'),
        ('Double XX', 'Double XX\xa0'),
        ('XXY\xa0\xa0X', 'X\xa0XY\xa0\xa1\xa0X'),
        ]

    def testPreprocess(self):
        """Test Playfair preprocess method."""
        it = self.target.preprocess(BYTES)
        for i in range(len(BYTES)):
            self.assertEquals(it.next(), BYTES[i])
        self.assertRaises(StopIteration, it.next)


class RowTransposeTest(unittest.TestCase):
    """Test the row transposition cipher."""

    target = obfuscate.RowTranspose

    testdata = [("zoology\n", 4, "zooyolg\n"),
        ("Nobody expects the Spanish Inquisition!", 3,
            "Ns o Ibtnohqdeuy i Ssepixatpnieiocsnth!"),
        ("hidden files", 2, "h ifdidleens"),
        ("hidden files", 6, "hde ieidnfls"),
        ]

    def testAttr(self):
        """Test that the class has the appropriate attributes."""
        self.assert_(hasattr(self.target, 'PADDING'))
        self.assertEquals(len(self.target.PADDING), 1)

    def testGet(self):
        """Test the get method"""
        text = "abcde"  "fghij"  "klmno"  # Consider as three rows.
        width = 5
        # Test calling on both the class and the instance.
        for obj in (self.target, self.target()):
            pad = obj.PADDING
            get = obj.get
            self.assertEquals(get(text, 0, 0, width), 'a')
            self.assertEquals(get(text, 0, 4, width), 'e')
            self.assertEquals(get(text, 1, 3, width), 'i')
            self.assertEquals(get(text, 2, 4, width), 'o')
            self.assertEquals(get(text, 999, 999, width), pad)
        # Test iterator padding.
        obj = self.target()
        obj.PADDING = iter('abc')
        self.assertEquals(obj.get(text, 999, 999, width), 'a')
        self.assertEquals(obj.get(text, 999, 999, width), 'b')
        self.assertEquals(obj.get(text, 999, 999, width), 'c')

    def testValidation(self):
        """Test the private method _validate"""
        validator = self.target._validate
        self.assertRaises(ValueError, validator, 1, 99)
        self.assertRaises(ValueError, validator, 99, 1)
        self.assert_(validator(2, 2) is None)

    def testRoundTrip(self):
        """Test encryption and decryption round-trip correctly."""
        msg = "this is the secret message which is very secret okay thanks"
        for rows in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15):
            # Pad the text.
            n = rows - (len(msg) % rows)
            plaintext = "x"*n + msg
            assert len(plaintext) % rows == 0
            # Test the round-trip.
            ciphertext = self.target.encrypt(plaintext, rows)
            self.failIf(ciphertext == plaintext)
            self.failUnless(self.target.decrypt(ciphertext, rows) == plaintext)

    def testEncrypt(self):
        """Test the encrypt method."""
        # Test that calling on both the class and the instance works.
        for obj in (self.target, self.target()):
            encrypt = obj.encrypt
            for plaintext, rows, ciphertext in self.testdata:
                self.assertEquals(encrypt(plaintext, rows), ciphertext)

    def testDecrypt(self):
        """Test the decrypt method."""
        # Test that calling on both the class and the instance works.
        for obj in (self.target, self.target()):
            decrypt = obj.decrypt
            for plaintext, rows, ciphertext in self.testdata:
                self.assertEquals(decrypt(ciphertext, rows), plaintext)


class RailFenceTest(unittest.TestCase):

    target = obfuscate.RailFence

    def test_iter_rails(self):
        """Test iter_rails method."""
        it = self.target.iter_rails(7)
        self.assert_(hasattr(it, 'next'))
        self.assertEquals([it.next() for _ in xrange(15)],
            [0, 1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1, 0, 1, 2])

    def test_make_fence(self):
        """Test the make_fence method."""
        msg = "this is the message"
        result = self.target.make_fence(msg, 4)
        result1 = self.target.make_fence(msg, 4)
        self.assertEquals(result, result1)
        self.assertEquals(result,
            [list('tsme'), list('hi  eg'), list('i tesa'), list('shs')])

    def testEncrypt(self):
        """Test encryption with RailFence."""
        #(this, plaintext, rails, key=None):
        # Test that calling on both the class and the instance works.
        for obj in (self.target, self.target()):
            encrypt = obj.encrypt
            msg = "secret-message"
            self.assertEquals(encrypt(msg, 2), "sce-esgertmsae")
            self.assertEquals(encrypt(msg, 5), "seemsc-srtaeeg")

    def testEncryptWithKeys(self):
        """Test key-based encryption with RailFence."""
        encrypt = self.target.encrypt
        msg = "secret-message"
        for key in ('AB', [0, 1], 'mq', 'ex', '23'):
            self.assertEquals(encrypt(msg, 2, key), "sce-esgertmsae")
        for key in ('BA', [1, 0], 'qm', 'xe', '42'):
            self.assertEquals(encrypt(msg, 2, key), "ertmsaesce-esg")
        self.assertEquals(encrypt(msg, 3, [0, 1, 2]), "seegertmsaec-s")
        self.assertEquals(encrypt(msg, 3, [0, 2, 1]), "seegc-sertmsae")
        self.assertEquals(encrypt(msg, 3, [1, 0, 2]), "ertmsaeseegc-s")
        self.assertEquals(encrypt(msg, 3, [1, 2, 0]), "ertmsaec-sseeg")
        self.assertEquals(encrypt(msg, 3, [2, 0, 1]), "c-sseegertmsae")
        self.assertEquals(encrypt(msg, 3, [2, 1, 0]), "c-sertmsaeseeg")
        self.assertEquals(encrypt(msg, 3, "HAL"), "ertmsaeseegc-s")

    def testBadKeys(self):
        """Test key-based encryption fails for bad keys."""
        encrypt = self.target.encrypt
        for key in (range(6), range(8), range(1, 9)):
            self.assertRaises(ValueError, encrypt, "message", 4, key)



# =================================================================

if __name__ == '__main__':
    tests_failed, tests_run = obfuscate.selftest(obfuscate)
    if tests_failed == 0:
        print "%d doctests passed" % tests_run
    unittest.main()



