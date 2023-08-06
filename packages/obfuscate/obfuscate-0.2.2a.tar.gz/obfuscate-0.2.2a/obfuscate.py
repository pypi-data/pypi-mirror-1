#!/usr/bin/env python

##  Module obfuscate.py
##
##  Copyright (c) 2010 Steven D'Aprano.
##
##  Permission is hereby granted, free of charge, to any person obtaining
##  a copy of this software and associated documentation files (the
##  "Software"), to deal in the Software without restriction, including
##  without limitation the rights to use, copy, modify, merge, publish,
##  distribute, sublicense, and/or sell copies of the Software, and to
##  permit persons to whom the Software is furnished to do so, subject to
##  the following conditions:
##
##  The above copyright notice and this permission notice shall be
##  included in all copies or substantial portions of the Software.
##
##  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
##  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
##  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
##  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
##  CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
##  TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
##  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Obfuscate text using a variety of classical cryptographic methods and
simple obfuscation functions.

***  DISCLAIMER: These routines are not cryptographically secure,  ***
***  and should not be used where serious security is required.    ***

Run this module from the commandline to run the doctests:

    $ python obfuscate.py

Most of these ciphers are polymorphic and can process either strings or streams.
(Obvious exceptions are transposition ciphers,which typically need to operate
on the entire message.) If the message (plaintext or ciphertext) passed to the
cipher is a string-like object, they return a string. Any other iterable is
treated as a stream, and the cipher returns an iterator object. For example:

>>> rot13("string")  # Processing a string returns a string.
'fgevat'
>>> import itertools
>>> stream = itertools.cycle("an infinite string of characters")
>>> it = rot13(stream)
>>> _ = [stream.next() for _ in range(76)]  # Advance the stream.
>>> [it.next() for _ in range(6)]
['f', 'g', 'e', 'v', 'a', 't']

In general, the iterable is not limited to individual characters, it can be a
sequence of arbitrary-sized blocks (but see documentation for individual
ciphers for any restrictions):

>>> it = rot13(['Send', ' help ', ' now.'])
>>> it.next()
'Fraq'
>>> it.next()
' uryc '
>>> it.next()
' abj.'
>>> it.next()
Traceback (most recent call last):
    ...
StopIteration

"""

from __future__ import division


# Module metadata.
__version__ = "0.2.2a"
__date__ = "2010-02-09"
__author__ = "Steven D'Aprano <steve+python@pearwood.info>"


__all__ = [
    # Self-inverting monoalphabetic substitution ciphers.
    'rot13', 'rot5', 'rot18', 'rot47', 'atbash',
    # Other monoalphabetic substitution ciphers.
    'Caesar', 'Keyword', 'Affine', 'Playfair', 'Playfair6', 'Playfair16',
    # Transposition ciphers.
    'RowTranspose', 'RailFence',
    # Steganographic padding.
    'Chaff',
    # Polyalphabetic substitution ciphers.
    'Vigenere', 'frob',
    ]



import functools
import hashlib
import itertools
import random
import string

BYTES = string.maketrans('', '')  # ASCII characters from 0 to 255.


# === Utility classes and functions ===

def is_string(obj):
    """Return True if obj is string-like, otherwise False.

    >>> is_string("hello world")
    True
    >>> is_string(iter("hello world"))
    False

    """
    # FIX ME -- is there a better way to do this?
    # How about UserString and MutableString?
    return isinstance(obj, basestring)


def remove_duplicates(s):
    """Remove duplicate characters from string s.

    >>> remove_duplicates("visit australia now")
    'vist aurlnow'

    """
    t = []
    for c in s:
        if c not in t:
            t.append(c)
    assert len(t) == len(set(t))
    return ''.join(t)


def key2permutation(key):
    """Return a permutation of range(len(key)).

    >>> key2permutation("bcda")
    [1, 2, 3, 0]
    >>> key2permutation("PYTHON")
    [3, 5, 4, 0, 2, 1]

    Ties are decided by going left to right.

    >>> key2permutation("PYTPHON")
    [3, 6, 5, 4, 0, 2, 1]

    Keys are case-sensitive, and are ordered according to their ordinal value.
    """
    key = [(c, i) for (i, c) in enumerate(key)]
    tmp = sorted(key)
    return [tmp.index(x) for x in key]


class dualmethod(object):
    """Descriptor implementing dualmethods (combination class/instance method).

    Returns a method which takes either an instance or a class as the first
    argument. When called on an instance, the instance is passed as the first
    argument. When called as a class, the class itself is passed instead.

    >>> class Example(object):
    ...     @dualmethod
    ...     def method(this):
    ...         if type(this) is type:
    ...             print "I am the class '%s'." % this.__name__
    ...         else:
    ...             print "I am an instance of the class '%s'." % this.__class__.__name__
    ...
    >>> Example.method()
    I am the class 'Example'.
    >>> Example().method()
    I am an instance of the class 'Example'.

    """
    def __init__(self, func):
        self.func = func
    def __get__(self, obj, cls=None):
        if cls is None:  cls = type(obj)
        if obj is None:  obj = cls
        @functools.wraps(self.func)
        def newfunc(*args, **kwargs):
            return self.func(obj, *args, **kwargs)
        return newfunc


# === Monoalphabetic substitution ciphers ===


class _SelfInvertingMonoCipher(object):
    """Abstract base class for self-inverting monoalphabetic ciphers.

    This class implements self-inverting ciphers using a single translation
    table to perform both encryption and decryption.
    """

    # Note: This is an abstract base class, do not instantiate it.
    # Furthermore, subclasses also don't instantiate: the class object itself
    # is used as a singleton callable (or functor in C++ terminology).
    def __new__(cls, message):
        if cls is _SelfInvertingMonoCipher:
            raise TypeError("abstract base class, do not instantiate")
        # As this returns an object other than an instance of cls, this
        # class and it's subclasses can not be instantiated. Instead,
        # treat the class as if it were a function that holds state.
        if is_string(message):
            func = string.translate
        else:
            func = cls.stream
        return func(message, cls.TABLE)

    @classmethod
    def stream(cls, message, table):
        """Transform an iterable message with a translation table."""
        translate = string.translate
        for block in message:
            yield translate(block, table)


class rot13(_SelfInvertingMonoCipher):
    """Obfuscate and unobfuscate text using rot13.

    rot13 is the Usenet standard for obfuscating spoilers, punchlines of jokes
    and other sensitive but unimportant information. It obfuscates the letters
    a...z and A...Z, shifting each letter by 13. Other characters are left
    unchanged. It is equivalent to a Caesar cipher with a shift of 13.

    rot13 is self-inverting: calling it again reverses the cipher:

    >>> rot13("Colonel Mering in the library with the candlestick")
    'Pbybary Zrevat va gur yvoenel jvgu gur pnaqyrfgvpx'
    >>> rot13('Pbybary Zrevat va gur yvoenel jvgu gur pnaqyrfgvpx')
    'Colonel Mering in the library with the candlestick'

    When passed an iterable other than a string, rot13 returns an iterator:

    >>> it = rot13(iter('ATTACK AT DAWN!'))
    >>> it.next()
    'N'
    >>> ''.join(it)
    'GGNPX NG QNJA!'

    """
    tmp = string.ascii_lowercase
    tmp = tmp[13:] + tmp[:13]
    tmp += tmp.upper()
    TABLE = string.maketrans(string.ascii_letters, tmp)
    del tmp


class rot5(_SelfInvertingMonoCipher):
    """Obfuscate and unobfuscate text using rot5.

    rot5 is the equivalent of rot13 for the digits 0...9. See rot13
    for additional details.

    >>> rot5('Phone +079 2136-4568.')
    'Phone +524 7681-9013.'
    >>> list(rot5(['a', 'b', 'c', '1', '2', '3']))
    ['a', 'b', 'c', '6', '7', '8']

    """
    TABLE = string.maketrans("0123456789", "5678901234")


class rot18(_SelfInvertingMonoCipher):
    """Obfuscate and unobfuscate text using rot18.

    rot18 combines rot13 and rot5 in one cipher. The name is somewhat
    misleading, as it does not implement a Caesar shift of 18. It shifts
    letters by 13 and digits by 5. See rot13 for additional details.

    >>> rot18('Send 23 men to sector 42.')
    'Fraq 78 zra gb frpgbe 97.'
    >>> list(rot18(['a', 'b', 'c', '1', '2', '3']))
    ['n', 'o', 'p', '6', '7', '8']

    """
    tmp = string.ascii_lowercase
    tmp = tmp[13:] + tmp[:13]
    tmp = tmp + tmp.upper() + "5678901234"
    TABLE = string.maketrans(string.ascii_letters + string.digits, tmp)
    del tmp


class rot47(_SelfInvertingMonoCipher):
    """Obfuscate and unobfuscate text using rot47.

    rot47 is the equivalent to rot13 extended to the 94 characters between
    ASCII 33 and 126 inclusive. Is is a self-inverting Caesar shift of 47.
    See rot13 for additional details.

    >>> rot47("Shhh... this is a secret message")
    '$999]]] E9:D :D 2 D64C6E >6DD286'
    >>> rot47('$999]]] E9:D :D 2 D64C6E >6DD286')
    'Shhh... this is a secret message'

    When passed an iterable, rot47 returns an iterator:

    >>> it = rot47(['a', 'b', 'c', '1', '2', '3'])
    >>> [it.next() for _ in range(6)]
    ['2', '3', '4', '`', 'a', 'b']

    """
    TABLE = string.maketrans(BYTES[33:127], BYTES[80:127] + BYTES[33:80])


class atbash(_SelfInvertingMonoCipher):
    """Obfuscate and unobfuscate text using the ancient Hebrew atbash method.

    Letters are swapped A <-> Z, B <-> Y, C <-> X and so forth. atbash is
    self-inverting and case-preserving.

    >>> atbash('LET THERE BE LIGHT')
    'OVG GSVIV YV ORTSG'
    >>> atbash('OVG GSVIV YV ORTSG')
    'LET THERE BE LIGHT'

    When passed an iterable, atbash returns an iterator:

    >>> it = atbash(tuple('Adam'))
    >>> it.next()
    'Z'
    >>> ''.join(it)
    'wzn'

    """
    TABLE = string.maketrans(
        string.ascii_letters,
        string.ascii_lowercase[::-1] + string.ascii_uppercase[::-1]
        )


class _MonoSubCipher(object):
    """Abstract base class for monoalphabetic substitution ciphers.

    This class implements encryption and decryption as seperate methods, using
    a pair of translation tables.
    """

    # Note: This is an abstract base class, do not instantiate it.
    def __init__(self, *args, **kwargs):
        if cls is _MonoSubCipher:
            raise TypeError("abstract base class, do not instantiate")

    def stream(self, message, table):
        """Transform an iterable message with a translation table."""
        translate = string.translate
        for block in message:
            yield translate(block, table)

    def transform(self, message, table):
        if is_string(message):
            func = string.translate
        else:
            func = self.stream
        return func(message, table)

    def encrypt(self, plaintext):
        return self.transform(plaintext, self.TABLE)

    def decrypt(self, ciphertext):
        return self.transform(ciphertext, self.REVTABLE)


class Caesar(_MonoSubCipher):
    """Caesar substitution cipher.

    The Caesar cipher is a case-preserving cipher that shifts each letter by a
    fixed amount. Julius Caesar himself used a shift of 3, that is A->D, B->E,
    C->F and so forth.

    Instantiate the class by passing an integer shift, then calling the encrypt
    and decrypt methods:

    >>> x = Caesar(3)
    >>> x.encrypt('INVADE GAUL ON WEDNESDAY')
    'LQYDGH JDXO RQ ZHGQHVGDB'
    >>> x.decrypt('LQYDGH JDXO RQ ZHGQHVGDB')
    'INVADE GAUL ON WEDNESDAY'

    Shifts are taken module 26, so that a shift of 27, 53, ... is equivalent
    to 1. A shift of 0, 26, 52... is equivalent to the null cipher:

    >>> Caesar(26).encrypt('BEWARE THE TREACHERY OF BRUTUS')
    'BEWARE THE TREACHERY OF BRUTUS'

    Hence there are only 25 substitutions possible with the Caesar cipher.

    The Caesar cipher can operate on arbitrary iterables as well as strings,
    returning an iterator in that case:

    >>> stream = ['Beware the ', 'Goths!']
    >>> it = Caesar(5).encrypt(stream)
    >>> it.next()
    'Gjbfwj ymj '
    >>> it.next()
    'Ltymx!'

    """
    def __init__(self, shift):
        shift = shift % 26
        alpha = string.ascii_letters
        shifted = string.ascii_lowercase
        shifted = shifted[shift:] + shifted[:shift]
        shifted += shifted.upper()
        self.TABLE = string.maketrans(alpha, shifted)
        self.REVTABLE = string.maketrans(shifted, alpha)

    def encrypt(self, plaintext):
        """Obfuscate plaintext using the Caesar substitution cipher.

        Returns a string if plaintext is a string. If plaintext is a non-string
        iterable, returns an iterator.

        >>> x = Caesar(6)
        >>> x.encrypt("attack at dawn")
        'gzzgiq gz jgct'

        """
        return super(Caesar, self).encrypt(plaintext)

    def decrypt(self, ciphertext):
        """Unobfuscate ciphertext using the Caesar substitution cipher.

        Returns a string if ciphertext is a string. If ciphertext is a
        non-string iterable, returns an iterator.

        >>> x = Caesar(6)
        >>> x.decrypt("gzzgiq gz jgct")
        'attack at dawn'

        """
        return super(Caesar, self).decrypt(ciphertext)


class Keyword(_MonoSubCipher):
    """Simple case-preserving keyword cipher.

    The Keyword cipher is a case-preserving cipher that uses an alphabetical
    password to shift each letter in the message.

    Instantiate the class by passing a password, then calling the encrypt and
    decrypt methods:

    >>> x = Keyword('mary queen of scots')
    >>> x.encrypt("DEATH TO ALL TYRANTS")
    'YQMGN GW MCC GLBMVGD'
    >>> x.decrypt('YQMGN GW MCC GLBMVGD')
    'DEATH TO ALL TYRANTS'

    Both the encrypt and decrypt methods return a string when given a string
    argument. If given a non-string iterable arguments, they will return an
    iterator.

    >>> it = x.encrypt(['Spanish ambassador ', 'sending gold.'])
    >>> it.next()
    'Dxmvodn mtamddmywb '
    >>> it.next()
    'dqvyove ewcy.'

    """

    def __init__(self, key):
        key = self.generate_key(key)
        key += key.upper()
        # Save the translation tables.
        self.TABLE = string.maketrans(string.ascii_letters, key)
        self.REVTABLE = string.maketrans(key, string.ascii_letters)

    @staticmethod
    def generate_key(key):
        """Generate a 26 lowercase character key from an arbitrary key phrase.

        >>> Keyword.generate_key('SWORDFISH')
        'swordfihjklmnpqtuvxyzabceg'

        """
        lowercase = string.ascii_lowercase
        # Remove anything that isn't a letter, and duplicates.
        key = filter(lambda c: c in lowercase, key.lower())
        key = remove_duplicates(key)
        # Add the rest of the letters, starting after the last character
        # in the key and wrapping around.
        if key:
            p = lowercase.index(key[-1])
            key += lowercase[p+1:] + lowercase[:p+1]
        else:
            key = lowercase
        # Remove duplicates again.
        key = remove_duplicates(key)
        assert set(key) == set(lowercase)
        return key


    def encrypt(self, plaintext):
        """Obfuscate plaintext using a simple keyword cipher.

        Returns a string if plaintext is a string. If plaintext is a
        non-string iterable, returns an iterator.

        >>> Keyword('aardvark').encrypt("ATTACK AT DAWN")
        'ACCADQ AC VAGU'

        """
        return super(Keyword, self).encrypt(plaintext)

    def decrypt(self, ciphertext):
        """Unobfuscate ciphertext using a simple keyword cipher.

        Returns a string if ciphertext is a string. If ciphertext is a
        non-string iterable, returns an iterator.

        >>> Keyword('aardvark').decrypt("ACCADQ AC VAGU")
        'ATTACK AT DAWN'

        """
        return super(Keyword, self).decrypt(ciphertext)


class Affine(_MonoSubCipher):
    """Generalisation of a large class of monoalphabetic substitution ciphers.

    The affine cipher is characterised by three parameters, a, b and m. The
    parameter m is equal to the size of the alphabet that can be encrypted.
    In the affine cipher the letters of the alphabet are mapped to integers in
    the range 0...(m-1), then transformed to a different value using modular
    arithmetic. The transformed integer is then mapped back to a letter.

    Instantiate the class by passing integer values for a and b, and optionally
    m (default of 26, implying the alphabet is case-preserving A...Z). Then
    call the encrypt and decrypt methods:

    >>> x = Affine(5, 17)
    >>> x.encrypt('Bury the gold behind the roses.')
    'Wnyh ial vjug wlafeg ial yjdld.'
    >>> x.decrypt('Wnyh ial vjug wlafeg ial yjdld.')
    'Bury the gold behind the roses.'

    The encryption function E(x) and decryption function D(x) for a single
    letter are:

        E(x) = (a*x + b) % m
        D(x) = q*(x - b) % m

    where x is the ordinal value of each letter (e.g. a=0, b=1, etc.) and q is
    the multiplicative inverse of a modulo m. That is, q satisfies the equation
    1 = (a*q) % m. This implies that a and m are coprime.

    a and m must be coprime, otherwise encryption is not 1:1 and decryption is
    not possible. This implementation only allows certain values for m, and
    selects the alphabet according to the value of m. Valid values for m are:

        m       |   Alphabet transformed
        --------+--------------------------------------
        10      |   digits 0...9 only
        26      |   case-preserving letters A...Z
        52      |   case-sensitive letters
        62      |   case-sensitive letters plus digits
        94      |   ASCII characters 33 to 126
        256     |   all ASCII characters 0 to 255

    If m is not one of these values, or if a and m are not coprime, ValueError
    is raised.

    When encrypting or decrypting, any character outside of the relevant
    alphabet is returned unchanged.

    Both the encrypt and decrypt methods accept iterables as the message
    (plaintext or ciphertext) argument. If the message is a string, the method
    returns a string, otherwise it returns an iterable:

    >>> x = Affine(3, 2)
    >>> it = x.encrypt(['Better than ', 'rot13!'])
    >>> it.next()
    'Fohhob hxcp '
    >>> it.next()
    'bsh13!'

    """

    def __init__(self, a, b, m=26):
        # Check that m has a valid value.
        if m not in (10, 26, 52, 62, 94, 256):
            raise ValueError('bad alphabet size m=%s' % m)
        # Generate the inverse of a and the affine transformation function(s).
        q = self.get_inverse(a, m)
        assert q > 0
        assert (q*a) % m == 1
        e = lambda x: (a*x+b) % m  # encryption
        if __debug__:
            d = lambda x: q*(x-b) % m  # decryption
        # Generate the alphabet.
        if m == 10:
            alphabet = string.digits
        elif m == 26:
            # We have to treat this case as a special case later, due to
            # case-preserving properties.
            alphabet = string.ascii_lowercase
        elif m == 52:
            alphabet = string.ascii_letters
        elif m == 62:
            alphabet = string.ascii_letters + string.digits
        elif m == 94:
            alphabet = BYTES[33:127]
        else:
            assert m == 256
            alphabet = BYTES
        # Generate the transformed integer values.
        cipherbet = [e(x) for x in range(len(alphabet))]
        assert [d(x) for x in cipherbet] == range(len(alphabet))
        # And convert back to letters.
        cipherbet = ''.join([alphabet[i] for i in cipherbet])
        # Now handle the special case.
        if m == 26:
            alphabet += alphabet.upper()
            cipherbet += cipherbet.upper()
        assert len(alphabet) == len(cipherbet)
        # Finally generate the necessary translation tables.
        self.TABLE = string.maketrans(alphabet, cipherbet)
        self.REVTABLE = string.maketrans(cipherbet, alphabet)

    @staticmethod
    def get_inverse(a, m):
        """Return the multiplicative inverse of a modulo m.

        >>> Affine.get_inverse(3, 7)
        5
        >>> (5*3) % 7
        1

        Raises ValueError if a is not coprime to m.
        """
        # Calculate the extended GCD of a and m.
        xx, x = 0, 1
        yy, y = 1, 0
        mm = m
        while mm:
            quotient = a//mm
            a, mm = mm, a%mm
            xx, x = x - quotient*xx, xx
            yy, y = y - quotient*yy, yy
        # a is now the GCD.
        if a != 1:
            raise ValueError('bad a for given m (a and m must be coprime)')
        # x is the inverse, but be sure to return a positive number.
        return x % m

    def encrypt(self, plaintext):
        """Obfuscate plaintext using the affine cipher.

        Returns a string if plaintext is a string. If plaintext is a
        non-string iterable, returns an iterator.

        >>> Affine(3, 21, m=52).encrypt('Send James to Paris.')
        'XHiE wvfHx Al OvuTx.'
        >>> Affine(11, 9, m=62).encrypt('Agents 86 and 99 arriving on Thursday.')
        'Vn1CGv XB jCQ 88 jkkJ2JCn NC iyRkvQjz.'

        """
        return super(Affine, self).encrypt(plaintext)

    def decrypt(self, ciphertext):
        """Unobfuscate ciphertext using the affine cipher.

        Returns a string if ciphertext is a string. If ciphertext is a
        non-string iterable, returns an iterator.

        >>> Affine(3, 21, m=52).decrypt('XHiE wvfHx Al OvuTx.')
        'Send James to Paris.'
        >>> Affine(11, 9, m=62).decrypt('Vn1CGv XB jCQ 88 jkkJ2JCn NC iyRkvQjz.')
        'Agents 86 and 99 arriving on Thursday.'

        """
        return super(Affine, self).decrypt(ciphertext)


class PlayfairTable(object):
    """Helper class for the Playfair family of ciphers."""

    def __init__(self, table):
        size = int(len(table)**0.5)
        if size**2 != len(table):
            raise ValueError('table is not square')
        self.TABLE = table
        self._TABLE_SIZE = size

    @property
    def size(self):
        return self._TABLE_SIZE

    def find(self, digraph):
        """Return a pair of coordinates for the letters in the given digraph.

        >>> table = PlayfairTable('abcdefghijklmnop')
        >>> table.find("fo")
        ((1, 1), (3, 2))

        """
        a, b = digraph
        return self.cfind(a), self.cfind(b)

    def get(self, a, b):
        """Return the digraph specified by the pair of coordinates a, b.

        >>> table = PlayfairTable('abcdefghijklmnop')
        >>> table.get((1, 1), (3, 2))
        'fo'

        """
        return self.cget(a) + self.cget(b)

    def cfind(self, c):
        """Return the (row, column) where single letter c is found in the table.

        >>> table = PlayfairTable('abcdefghi')
        >>> table.cfind('c')
        (0, 2)
        >>> table.cfind('h')
        (2, 1)

        """
        i = self.TABLE.index(c)
        return divmod(i, self.size)

    def cget(self, coord):
        """Return the single letter at the given coordinate in the table.

        >>> table = PlayfairTable('abcdefghi')
        >>> table.cget((0, 2))
        'c'
        >>> table.cget((2, 1))
        'h'

        """
        return self.TABLE[coord[0]*self.size + coord[1]]

    def __str__(self):
        """Return the string representation of the instance.

        >>> table = PlayfairTable('abcdefghi')
        >>> print table
        a b c
        d e f
        g h i

        """
        L = []
        size = self.size
        for i in range(size):
            L.append(' '.join(self.TABLE[i*size: i*size+size]))
        return '\n'.join(L)


class Playfair(object):
    """Obfuscate or unobfuscate msg using the Playfair cipher.

    The Playfair cipher operates on digraphs (pairs of letters) rather than
    single characters. It is a lossy cipher:

    - letters are converted to uppercase;
    - characters other than letters are lost;
    - the letter J is converted to I;
      (historically, some people kept J and I distinct, but dropped Q)
    - repeated characters may be separated by a pad character;
      (this implementation uses X and Q as padding)
    - and the message is padded to an even length.

    >>> x = Playfair('playfair example')
    >>> x.encrypt('Hide the gold in the tree stump')
    'BMODZBXDNABEKUDMUIXMMOUVIF'
    >>> x.decrypt('BMODZBXDNABEKUDMUIXMMOUVIF')
    'HIDETHEGOLDINTHETREXESTUMP'

    The advantage of Playfair is that, as it operates on digraphs rather than
    single letters, frequency analysis is more difficult and generally requires
    a much longer sample of ciphertext. However, as the key is limited to
    uppercase letters A-Z (excluding J), Playfair is still a weak cipher by
    modern standards.
    """

    PADDING = 'XQ'  # This must be exactly two distinct uppercase letters.
    assert len(PADDING) == 2
    assert PADDING[0] != PADDING[1]
    assert PADDING[0] in string.ascii_uppercase
    assert PADDING[1] in string.ascii_uppercase
    assert 'J' not in PADDING

    def __init__(self, key):
        self.TABLE = PlayfairTable(self.prepare_key(key))

    @dualmethod
    def prepare_key(this, key):
        """Return the prepared encryption key from the unprepared key.

        >>> Playfair.prepare_key('')
        'ABCDEFGHIKLMNOPQRSTUVWXYZ'
        >>> Playfair.prepare_key('swordfish')
        'SWORDFIHABCEGKLMNPQTUVXYZ'

        """
        alphabet = string.ascii_uppercase.replace('J', '')
        key = key.upper().replace('J', 'I')
        key = filter(lambda c: c in alphabet, key)
        key = remove_duplicates(key + alphabet)
        assert set(key) == set(alphabet)
        assert len(key) == 25
        return key

    @staticmethod
    def preprocess(stream):
        """Yield characters in stream after pre-processing.

        Converts letters to uppercase and replace J with I.

        >>> ''.join(Playfair.preprocess('Jumping Jack Flash!'))
        'IUMPINGIACKFLASH'

        """
        alphabet = string.ascii_uppercase.replace('J', '')
        for c in stream:
            c = c.upper()
            if c in alphabet:
                yield c
            elif c == 'J':
                yield 'I'

    def digraphs(self, stream):
        """Yield digraphs from stream, breaking up double letters.

        >>> x = Playfair('')
        >>> list(x.digraphs('Simon says jump'))
        ['SI', 'MO', 'NS', 'AY', 'SI', 'UM', 'PX']
        >>> list(x.digraphs('ABBCDDEXXY'))
        ['AB', 'BC', 'DX', 'DE', 'XQ', 'XY']

        """
        X, Q = self.PADDING
        stream = self.preprocess(stream)
        prev = ''
        for c in stream:
            if prev:
                if c == prev:
                    yield prev + (Q if prev==X else X)
                    prev = c
                else:
                    yield prev + c
                    prev = ''
            else:
                prev = c
        if prev:
            yield prev + (Q if prev==X else X)

    def transform_digraph(self, digraph, delta):
        """Transform a digraph.

        a and b should be coordinate pairs indexing a position within
        self.TABLE. a must not equal b.

        delta should be either +1 or -1. Any other value will lead to undefined
        behaviour. Use +1 for encryption, and -1 for decryption.

        Returns a pair of transformed coordinates.

        >>> x = Playfair('')
        >>> x.transform_digraph('GK', 1)  # Same row.
        'HF'
        >>> x.transform_digraph('SC', 1)  # Same column.
        'XH'
        >>> x.transform_digraph('ME', 1)
        'PB'

        """

        size = self.TABLE.size
        a, b = self.TABLE.find(digraph)  # Get the coordinates of both letters.
        if a == b:
            raise ValueError('equal coordinates')
        if a[0] == b[0]:
            # Letters are in the same row. Move each one position to the right
            # (or left), wrapping around if needed.
            a = a[0], (a[1]+delta)%size
            b = b[0], (b[1]+delta)%size
        elif a[1] == b[1]:
            # Letters are in the same column. Move each one position down
            # (or above), wrapping if necessary.
            a = (a[0]+delta)%size, a[1]
            b = (b[0]+delta)%size, b[1]
        else:
            # Neither the same column or row. Move to the opposite corner
            # of the rectangle defined by a and b, keeping the row unchanged.
            a, b = (a[0], b[1]), (b[0], a[1])
        return self.TABLE.get(a, b)

    def transform(self, message, delta):
        if is_string(message):
            digraphs = self.digraphs(message)
            return ''.join([self.transform_digraph(d, delta) for d in digraphs])
        else:
            def chained():
                for block in message:
                    for c in block:
                        yield c
            # FIXME: can the above be replaced safely by itertools.chain?
            return (self.transform_digraph(d, delta) for d in chained())

    def encrypt(self, plaintext):
        """Obfuscate plaintext lossily using the Playfair cipher.

        Returns a string if plaintext is a string. If plaintext is a
        non-string iterable, returns an iterator.

        >>> x = Playfair('playfair')
        >>> x.encrypt('flee at once')
        'PAKUHPNQSIKU'

        """
        return self.transform(plaintext, 1)

    def decrypt(self, ciphertext):
        """Unobfuscate ciphertext using the Playfair cipher.

        Returns a string if ciphertext is a string. If ciphertext is a
        non-string iterable, returns an iterator.

        >>> x = Playfair('playfair')
        >>> x.decrypt('PAKUHPNQSIKU')
        'FLEXEATONCEX'

        """
        return self.transform(ciphertext, -1)


class Playfair6(Playfair):
    """Variant of the Playfair cipher extended to letters and numbers.

    Named "Playfair6" as the translation table is 6*6.

    Like the original Playfair cipher, this is lossy:
        - letters are converted to uppercase;
        - characters other than letters and digits are lost;
        - repeated characters may be separated by a pad character;
        - and the message is padded to an even length.

    Unlike the original Playfair, J is allowed as a letter.
    """

    @dualmethod
    def prepare_key(this, key):
        """Return the prepared encryption key from the unprepared key.

        >>> Playfair6.prepare_key('')
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        >>> Playfair6.prepare_key('swordfish')
        'SWORDFIHABCEGJKLMNPQTUVXYZ0123456789'

        """
        alphabet = string.ascii_uppercase + string.digits
        key = key.upper()
        key = filter(lambda c: c in alphabet, key)
        key = remove_duplicates(key + alphabet)
        assert set(key) == set(alphabet)
        assert len(key) == 36
        return key

    @staticmethod
    def preprocess(stream):
        """Yield characters in stream after pre-processing.

        Converts letters to uppercase.

        >>> ''.join(Playfair6.preprocess('123 Jumping Jack Flash!'))
        '123JUMPINGJACKFLASH'

        """
        alphabet = string.ascii_uppercase + string.digits
        for c in stream:
            c = c.upper()
            if c in alphabet:
                yield c

    def encrypt(self, plaintext):
        """Obfuscate plaintext lossily using the Playfair6 cipher.

        Returns a string if plaintext is a string. If plaintext is a
        non-string iterable, returns an iterator.

        >>> x = Playfair6('playfair7')
        >>> x.encrypt('meet at 3pm')
        'NDCVYSPRH1'

        """
        return super(Playfair6, self).encrypt(plaintext)

    def decrypt(self, ciphertext):
        """Unobfuscate ciphertext using the Playfair6 cipher.

        Returns a string if ciphertext is a string. If ciphertext is a
        non-string iterable, returns an iterator.

        >>> x = Playfair6('playfair7')
        >>> x.decrypt('NDCVYSPRH1')
        'MEETAT3PMX'

        """
        return super(Playfair6, self).decrypt(ciphertext)


class Playfair16(Playfair):
    """Variant of the Playfair cipher extended to all 256 ASCII characters.

    Named "Playfair16" as the translation table is 16*16.

    Like the original Playfair cipher, this is lossy:
        - repeated characters may be separated by a pad character;
        - and the message is padded to an even length.

    Unlike the original Playfair cipher, this is capable of encrypting all
    ASCII characters.

    This implementation arbitrarily chooses characters \\xa0 and \\x8a for
    padding.
    """

    PADDING = '\xa0\x8a'  # This must be exactly two distinct characters.
    assert len(PADDING) == 2
    assert PADDING[0] != PADDING[1]

    @dualmethod
    def prepare_key(this, key):
        """Return the prepared encryption key from the unprepared key.

        >>> Playfair16.prepare_key('swordfish')[:10]
        'swordfih\\x00\\x01'

        """
        key = remove_duplicates(key + BYTES)
        assert set(key) == set(BYTES)
        assert len(key) == 256
        return key

    @staticmethod
    def preprocess(stream):
        return iter(stream)

    def encrypt(self, plaintext):
        """Obfuscate plaintext lossily using the Playfair16 cipher.

        Returns a string if plaintext is a string. If plaintext is a
        non-string iterable, returns an iterator.
        """
        return super(Playfair16, self).encrypt(plaintext)

    def decrypt(self, ciphertext):
        """Unobfuscate ciphertext using the Playfair16 cipher.

        Returns a string if ciphertext is a string. If ciphertext is a
        non-string iterable, returns an iterator.
        """
        return super(Playfair16, self).decrypt(ciphertext)


# === Transposition ciphers ===

class RowTranspose(object):
    """Basic transposition cipher.

    Obfuscates a message by transposing characters in the message as if it
    were written in a rectangular array, then reading in the opposite direction
    (down instead of across). The plaintext "ATTACK.AT.DAWN.SEND.FLOWERS" with
    three rows is written as:

        ATTACK.AT
        .DAWN.SEN
        D.FLOWERS

    The ciphertext is generated by reading down the columns instead of across
    the rows, giving "A.DTD.TAFAWLCNOK.W.SEAERTNS".

    >>> RowTranspose.encrypt('attack at dawn send flowers', 3)
    'a dtd tafawlcnok w seaertns'
    >>> RowTranspose.decrypt('a dtd tafawlcnok w seaertns', 3)
    'attack at dawn send flowers'

    Instantiating the RowTranspose class is optional; methods will work
    correctly whether you call them on the class or the instance:

    >>> s = "Meet behind railway station at 3pm."
    >>> a = RowTranspose.encrypt(s, 7)  # Call on the class.
    >>> b = RowTranspose().encrypt(s, 7)  # Call on the instance.
    >>> a, a == b
    ('Mbdlso ee wtn3ehraa ptiaytam ni it.', True)

    Unless the length of the plaintext is an exact multiple of the number of
    rows, the ciphertext will be padded with extra characters (default space).
    In general, such padding is not reversable unless you choose a character
    which is recognisable as not part of the plaintext, but doing may give away
    the number of rows. You can set the padding character by assigning to the
    PADDING attribute: if it is a single character, it is used repeatedly,
    otherwise it should be a iterator whose next method yields the character.
    """
    PADDING = ' '

    @staticmethod
    def ceildiv(x, y):
        """Return x/y rounded up to the nearest integer.

        >>> ceildiv = RowTranspose.ceildiv
        >>> ceildiv(10, 2)
        5
        >>> ceildiv(11, 2)
        6
        >>> ceildiv(-11, 2)
        -5

        """
        return x//y + bool(x%y)

    @dualmethod
    def get(this, text, row, col, width):
        """Return the character in text at (row,col).

        If there is no such character, returns an appropriate
        padding character.
        """

        # Consider text 'abcdefgh' as a 4x2 array:
        #   abcd
        #   efgh
        #
        # The character at (row, col) is found at (row*width + col).
        try:
            return text[row*width + col]
        except IndexError:
            pad = this.PADDING
            if isinstance(pad, str) and len(pad) == 1:
                return pad
            else:
                return pad.next()

    @dualmethod  # Should this be a staticmethod?
    def _validate(this, rows, width):
        if rows < 2:
            raise ValueError("you must use at least two rows")
        if width < 2:
            raise ValueError('too few characters for %d rows' % rows)

    @dualmethod
    def transpose(this, text, numrows, numcols):
        """Yield values from a transposed text block."""
        for col in xrange(numcols):
            for row in xrange(numrows):
                yield (this.get(text, row, col, numcols))

    @dualmethod
    def encrypt(this, plaintext, rows):
        """Obfuscate plaintext using a basic transposition row cipher.

        plaintext is written out into the given number of rows, then read back
        down the columns.

        >>> RowTranspose.encrypt('meet at the dance tomorrow', 4)
        'm noetcreherte o  twado tam '
        >>> RowTranspose.encrypt('secret message', 2)
        'smeecsrseatg e'

        """
        width = this.ceildiv(len(plaintext), rows)
        this._validate(rows, width)
        return ''.join(this.transpose(plaintext, rows, width))

    @dualmethod
    def decrypt(this, ciphertext, rows):
        """Unobfuscate ciphertext using a basic transposition row cipher.

        >>> RowTranspose.decrypt('m noetcreherte o  twado tam ', 4)
        'meet at the dance tomorrow  '
        >>> RowTranspose.decrypt('smeecsrseatg e', 2)
        'secret message'

        """
        width = this.ceildiv(len(ciphertext), rows)
        this._validate(rows, width)
        # Swap order of row/column relative to encryption.
        return ''.join(this.transpose(ciphertext, width, rows))


class RailFence(object):
    """Obfuscate and unobfuscate text using the RailFence transposition cipher.

    The message is transposed by writing it out as if on a rail fence. E.g. the
    message "WE ARE DISCOVERED FLEE AT ONCE" with three rails is written as
    follows (after removing spaces):

        W...E...C...R...L...T...E
        .E.R.D.S.O.E.E.F.E.A.O.C.
        ..A...I...V...D...E...N..

    (note that the pattern of writing the letters goes down, then up, then
    down, and repeats in this fashion).

    The text is then encrypted by reading across the rows:

        WECRLTE ERDSOEEFEAOC AIVDEN

    >>> RailFence.encrypt("WEAREDISCOVEREDFLEEATONCE", 3)
    'WECRLTEERDSOEEFEAOCAIVDEN'

    Instantiating the RailFence class is optional; methods will work correctly
    whether you call them on the class or the instance:

    >>> RailFence.encrypt("Hello world", 4)  # Call on the class.
    'Hwe olordll'
    >>> RailFence().encrypt("Hello world", 4)  # Call on the instance.
    'Hwe olordll'

    RailFence takes an optional key that tells in which order to read back the
    rows. The key can be either a permutation of the ints 0, 1, ..., (rails-1),
    or a string, which is then converted to a permutation.

    >>> RailFence.encrypt("Advance to the east ridge", 4)
    'Aehtedc tes gvnt  ardaoei'
    >>> RailFence.encrypt("Advance to the east ridge", 4, 'EAST')
    'dc tes gAehtevnt  ardaoei'

    """

    @staticmethod
    def iter_rails(n):
        """Yield 0, 1, ..., n-2, n-1, n-2, n-3, ..., 1, 0, 1, 2, ...

        Counts up through range(n), then down back to 0, then up, and so forth.

        >>> it = RailFence.iter_rails(5)
        >>> [it.next() for _ in range(20)]
        [0, 1, 2, 3, 4, 3, 2, 1, 0, 1, 2, 3, 4, 3, 2, 1, 0, 1, 2, 3]
        >>> it = RailFence.iter_rails(8)
        >>> [it.next() for _ in range(20)]
        [0, 1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2, 1, 0, 1, 2, 3, 4, 5]

        """
        i = 0
        while 1:
            if i == 0:
                delta = 1
            elif i == n-1:
                delta = -1
            yield i
            i += delta

    @dualmethod
    def make_fence(this, msg, rails):
        fence = [[] for _ in range(rails)]
        it = this.iter_rails(rails)
        for c in msg:
            rail = it.next()  # The rail we add to.
            assert 0 <= rail < rails
            fence[rail].append(c)
        return fence

    @dualmethod
    def encrypt(this, plaintext, rails, key=None):
        """Obfuscate plaintext using the RailFence cipher.

        plaintext is written out into the given number of rows, then read back
        down the columns in the order given by keys.

        >>> RailFence.encrypt('nothing is what it appears', 3, 'spy')
        'ohn swa tapasniihiprtg t e'

        """
        fence = this.make_fence(plaintext, rails)
        if key is None:
            permute = range(rails)
        elif isinstance(key, str):
            permute = key2permutation(key)
        else:
            permute = key
            if sorted(permute) != range(rails):
                raise ValueError
        tmp = []
        for i in permute: tmp.extend(fence[i])
        return ''.join(tmp)

    @dualmethod
    def decrypt(this, ciphertext, rails, key=None):
        """Unobfuscate... """
        # FIX ME -- currently unimplemented.
        raise NotImplementedError


# === Steganographic padding ===

def randchars(alpha=None):
    """Yield an infinite string of randomly selected characters.

    The characters are chosen randomly from alpha. By default, the full range
    of ASCII characters (bytes 0 through 255) are used.

    Note that this is not guaranteed to be cryptographically strong.
    """
    if alpha is None:
        alpha = BYTES
    while 1:
        yield random.choice(alpha)


class Chaff(object):
    """Pad a message with chaff, or cryptographic nulls (insignificant characters).

    (Not to be confused with Ron Rivest's strong cryptographic technique
    "chaffing and winnowing".)
    """

    # We default to md5 for the internal hash function. Change this to
    # hashlib.sha512 for extra strength, at the cost of speed.
    _hash = hashlib.md5

    BUFFER_SIZE = 64

    def __init__(self, width, stream=None):
        # Apply width characters of chaff to each plaintext character, on average.
        self.factor = width*2
        if stream is None:
            self.stream = randchars()
        else:
            self.stream = iter(stream)

    def hash(self, s):
        """Return the hash of string s as a long integer.

        >>> Chaff(0, '').hash('librarian')
        71747721734195069858424710002407141750L

        """
        s = self._hash(s).digest()
        return long(s.encode('hex'), 16)

    @staticmethod
    def get_chars(n, stream):
        """Return n characters from iterable stream.

        >>> Chaff.get_chars(10, (chr(n) for n in xrange(40, 100)))
        '()*+,-./01'

        """
        stream = iter(stream)
        return ''.join([stream.next() for _ in xrange(n)])

    @staticmethod
    def mod_key(key):
        """Return the modified key.

        >>> Chaff.mod_key("swordfish")
        'wordfisht'
        >>> Chaff.mod_key("wordfisht")
        'ordfishtx'

        """
        return key[1:] + chr((ord(key[0])+1) & 0xFF)

    def pad(self, msg, key):
        """Pad msg with junk characters (chaff).

        The amount of chaff added is controlled by self.factor. It is very
        approximately factor//2 extra bytes per char in msg.

        >>> x = Chaff(3, '?'*100)
        >>> x.pad('HELLO', 'swordfish')
        '???H???E?L?L????O'
        >>> x.pad('GOODBYE', 'aardvark')
        '???G?????O?????O????D?????B??Y?????E?????'

        """
        # TODO: make this an iterator, yielding every BUFFER_SIZE characters.
        buffer = []
        factor = self.factor
        # Calculate how much chaff to use. We hash the key to produce an
        # integer checksum which is approximately uniformly distributed
        # between 0 and (factor-1), with an average of very approximately
        # factor//2.
        n = self.hash(key) % factor
        key = self.mod_key(key)  # Update the key.
        # Add that many characters of chaff to the buffer.
        buffer.append(self.get_chars(n, self.stream))
        for c in msg:
            # Add one non-chaff character.
            buffer.append(c)
            # And some more chaff.
            n = self.hash(key) % factor
            key = self.mod_key(key)
            buffer.append(self.get_chars(n, self.stream))
        return ''.join(buffer)

    def unpad(self, msg, key):
        """Remove chaff from msg.

        >>> x = Chaff(3, '')
        >>> x.unpad('???H???E?L?L????O', 'swordfish')
        'HELLO'
        >>> x.unpad('???G?????O?????O????D?????B??Y?????E?????', 'aardvark')
        'GOODBYE'

        """
        buffer = []
        factor = self.factor
        msg = iter(msg)
        try:
            # Calculate how much chaff to throw away.
            n = self.hash(key) % factor
            key = self.mod_key(key)
            self.get_chars(n, msg)
            while 1:
                # Save one non-chaff character.
                buffer.append(msg.next())
                # And toss away more chaff.
                n = self.hash(key) % factor
                key = self.mod_key(key)
                self.get_chars(n, msg)
        except StopIteration:
            return ''.join(buffer)


# === Polyalphabetic substitution ciphers ===

def _monofrob(msg, k):
    """Private function implementing a monoalphabetic version of frob.

    >>> _monofrob('abc\\x87', 135)
    '\\xe6\\xe5\\xe4\\x00'
    >>> list(_monofrob(list('\\xe6\\xe5\\xe4\\0'), 135))
    ['a', 'b', 'c', '\\x87']

    """
    # This has a fairly hefty overhead in preparing the translation table.
    # By my testing, it isn't worth calling this function for small strings
    # less than 45-50 characters. I haven't tested the break-even point for
    # iterables, but I expect that the cost of preparing the table will be
    # relatively small compared to the cost of iteration, so hopefully the
    # break-even point may be smaller.
    tmp = ''.join([chr(n^k) for n in xrange(256)])
    table = string.maketrans(BYTES, tmp)
    assert string.maketrans(tmp, BYTES) == table
    if is_string(msg):
        return string.translate(msg, table)
    else:
        return itertools.imap(string.translate, msg, itertools.cycle([table]))


def frob(msg, key='*'):
    """Obfuscate or unobfuscate msg by XORing with the characters of key.

    frob is a self-inverting cipher. The default behaviour to use chr(42),
    or '*', as the key, which is similar to the GNU C utility memfrob.

    If msg is a string, frob returns a string:

    >>> frob('magic')
    'GKMCI'
    >>> frob('ADVANCE AT DAWN', 'xyz')
    '9=,979=Y;,Y>9.4'
    >>> frob('9=,979=Y;,Y>9.4', 'xyz')
    'ADVANCE AT DAWN'

    If msg is some other iterable, frob returns an iterator:

    >>> it = frob(list('magic'))
    >>> it.next()
    'G'
    >>> ''.join(it)
    'KMCI'

    """
    if len(key) == 1:
        # A key of length 1 means that frob will be monoalphabetic. If that is
        # the case, we can speed up the encryption with a special case. However,
        # the overhead of this makes it unattractive for very small strings.
        if not is_string(msg) or len(msg) > 45:
            # The _monofrob function has a fairly high setup cost, due to the
            # need to prepare a translation table. By my measurements, the
            # break-even point is around 45 characters.
            return _monofrob(msg, ord(key))
    # If we reach here without returning, either we have a longer key (and
    # therefore polyalphabetic), or a tiny string. Either way, we continue.
    key = itertools.cycle(map(ord, key))
    if is_string(msg):
        msg = map(ord, msg)
        # The following is a slight performance optimization. By
        # pre-allocating the buffer in a list comp (as opposed to
        # using a generator expression), the call to join will operate
        # slightly faster. This leads to a speed increase of
        # approximately 15-20% according to my tests.
        buffer = [chr(c^k) for (c,k) in itertools.izip(msg, key)]
        return ''.join(buffer)
    else:
        return itertools.imap(lambda c, k: chr(c^k), msg, key)


class Vigenere(object):
    """Vigenere polyalphabetic substitution cipher.

    Note: reversing the Vigenere cipher (that is, use decrypt on the plain text
    to generate the ciphertext, and use encrypt on the ciphertext to generate
    the plaintext) is known as the "variant Beaufort cipher".

    The Vigenere cipher shifts each letter in the message by a variable amount
    given by a key, leaving non-letters untouched. It is equivalent to using
    the key to select between multiple Caesar ciphers with different shifts,
    with "A" (in the key) equivalent to a shift of 1, "B" to 2, and so forth.

    >>> v = Vigenere()
    >>> v.encrypt('ATTACK AT DAWN', key='swordfish')
    'TQISGQ JM LTTC'
    >>> v.decrypt('TQISGQ JM LTTC', key='swordfish')
    'ATTACK AT DAWN'

    Instantiating the Vigenere class is optional; methods will work correctly
    whether you call them on the class or the instance:

    >>> msg = "advance towards the enemy's left flank immediately"
    >>> pwrd = 'fancy trousers'
    >>> Vigenere().encrypt(msg, pwrd) == Vigenere.encrypt(msg, pwrd)
    True

    Non-letter characters in the key produce an arbitrary but consistent shift
    between 0 and 26.
    """
    @staticmethod
    def alpha_ord(c):
        """Static method alpha_ord(c) -> int

        Returns the ordinal value of case-insensitive letter c relative to
        'A', i.e. 'A' -> 0, 'B' -> 1, ... 'Z' -> 25. All other characters
        return some arbitrary value between 0 and 25.

        >>> alpha_ord = Vigenere.alpha_ord
        >>> alpha_ord('d')
        3
        >>> alpha_ord('x')
        23
        >>> alpha_ord('$')
        10

        """
        i = (string.ascii_lowercase.find(c) + 1) or (string.ascii_uppercase.find(c) + 1)
        if i:  
            i -= 1
        else:  # Non-letter.
            i = ord(c) % 26
        assert 0 <= i < 26
        return i

    @dualmethod
    def shift(this, c, n):
        """Method shift(c, n) -> char

        Shifts letters A-Za-z by n positions, e.g. n=4 gives:
        'A' -> 'E', 'B' -> 'F', ... 'Z' -> 'D'.

        Non letters are returned unchanged.

        >>> shift = Vigenere.shift
        >>> shift('b', 3)
        'e'
        >>> shift('x', 5)
        'c'
        >>> shift('D', -4)
        'Z'
        >>> shift('$', 5)
        '$'

        """
        if c in string.ascii_lowercase:
            base = 97  # ord('a')
        elif c in string.ascii_uppercase:
            base = 65  # ord('A')
        else:
            # Non-letter, bail out early.
            return c
        # If we get here, c is an letter.
        o = this.alpha_ord(c)
        return chr(base + (o + n) % 26)

    @dualmethod
    def prepare_shifts(this, key):
        f = this.alpha_ord
        return [f(c)+1 for c in key]

    @dualmethod
    def transform(this, text, shifts):
        """Yield characters of text transformed by shifts."""
        numshifts = len(shifts)
        i = -1  # Handle the index ourselves, rather than use enumerate.
        # This is necessary because we do not wish to increment i unless
        # the plaintext character is a letter.
        letters = string.ascii_letters
        for c in text:
            if c in letters:
                i += 1
            # Note that although we pass a shift to the shift method, if
            # c is a non-letter it returns c unchanged without consuming
            # the shift value.
            yield this.shift(c, shifts[i % numshifts])

    @dualmethod
    def encrypt(this, plaintext, key):
        shifts = this.prepare_shifts(key)
        return ''.join(this.transform(plaintext, shifts))

    @dualmethod
    def decrypt(this, ciphertext, key):
        shifts = [-n for n in this.prepare_shifts(key)]
        return ''.join(this.transform(ciphertext, shifts))



# From the command line, run doctests.
if __name__ == '__main__':
    try:
        ## Unfortunately, as of Python 2.6.4, doctest doesn't run tests in
        ## method descriptors. Try using my own patched version.
        #import doctest_patched as doctest
        raise ImportError
    except ImportError:
        import warnings
        warnings.warn("doctests for dualmethods will be skipped")
        import doctest
    doctest.testmod()

