#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module for translating between integer numbers and Esperanto strings.

Examples:

    >>> from eonums import int2eo, eo2int, validate_eo
    >>>
    >>> int2eo(22334455)
    u'dudek du milionoj tricent tridek kvar mil kvarcent kvindek kvin'
    >>>
    >>> eo2int(u"cent dudek tri")
    123
    >>> validate_eo(u"dudek cent tri")
    False
"""

__version__ = "0.9.0"
__license__ = "GNU General Public Licence v3 (GPLv3)"
__author__ = "Dinu Gherman"
__date__ = "2008-09-16"


import re
import unittest


# constants

# single digits
DIGITS = u"nul unu du tri kvar kvin ses sep ok naŭ".split()

# powers of ten
DIGITS10 = DIGITS + [u"dek"]
POW10_SMALL = u"unu dek cent".split()
POW10_BIG = {3: u"mil", 6: u"miliono", 9: u"miliardo"}
for i in range(12, 63, 6):
    POW10_BIG[i] = DIGITS10[i//6] + u"iliono"
    POW10_BIG[i+3] = DIGITS10[i//6] + u"iliardo"
POW10_BIG_INV = dict([(v, k) for (k, v) in POW10_BIG.items()])
del DIGITS10


# helpers 

def digits(num): 
    "Convert an integer into a list of decimal digits, e.g. 234 -> [2, 3, 4]."

    return [int(s) for s in str(num)]
    

def validate_eo(numString, verbose=False): 
    """Validate an Esperanto string as a valid integer number.
    
    Return True or False, e.g.
        "du mil tri milionoj unu" -> False,
        "tri milionoj du mil unu" -> True
        "tridek ducent" -> False
    """

    # check if "big" powers of ten, i.e. 10**(3*k) (k=1,2,3,...), appear 
    # with decreasing values of k, excluding e.g. "du mil tri milionoj"
    bigPowers = re.findall("(\w+lionoj?|\w+iliardoj?|mil)", numString)
    for i, p in enumerate(bigPowers):
        if p.endswith("oj"):
            bigPowers[i] = p[:-1]
    bpows = [POW10_BIG_INV[p] for p in bigPowers]
    bpows2 = bpows[:]
    bpows2.sort(reverse=True)
    if bpows != bpows2:
        if verbose:
            print "failing", bpows, bpows2
        return False

    # check if all occurences of these "big" powers appear 
    # exactly once, excluding e.g. "du mil tri mil"
    counts = [bpows.count(p) for p in bpows]
    if counts != [1] * len(bpows):
        if verbose:
            print "failing", counts, [1] * len(bpows)
        return False

    # check if all "small" powers of ten, i.e. 10**k (k=0,1,2),
    # are "well-formed", excluding e.g. "tridek ducent" and "unu du"
    hundreds = re.split("\w+lionoj?|\w+iliardoj?|mil", numString)
    hundreds = [h.strip() for h in hundreds if h.strip()]
    if verbose:
        print "hundreds", hundreds
    dic = {"digs": "|".join(DIGITS)}
    for h in hundreds:
        if verbose:
            print "testing", repr(h)
        nc = numComponents = len(h.split())
        if nc == 1:
            pat = "^(%(digs)s)?cent$|^(%(digs)s)?dek$|^(%(digs)s)$" % dic
            if not re.match(pat, h):
                if verbose:
                    print "failing (1)", h
                return False
        elif nc == 2:
            pat1 = "^(%(digs)s)?cent +(%(digs)s)?dek$" % dic
            pat2 = "^(%(digs)s)?cent +(%(digs)s)$" % dic
            pat3 = "^(%(digs)s)?dek +(%(digs)s)$" % dic
            if not re.match("|".join([pat1, pat2, pat3]), h):
                if verbose:
                    print "failing (2)", h
                return False
        elif nc == 3:
            pat = "^(%(digs)s)?cent +(%(digs)s)?dek +(%(digs)s)$" % dic
            if not re.match(pat, h):
                if verbose:
                    print "failing (3)", h
                return False
        elif nc == 0 or nc > 3:
            if verbose:
                print "failing (0)", h
            return False
            
    return True
    

# conversion functions

def int2eo(num, validate=True, verbose=False):
    """Convert an (almost) arbitrarily long integer into an Esperanto string.
    
    Raises a ValueError for numbers >= 10**66.
    
    Examples: 
         234 -> u"ducent tridek kvar"
        1024 -> u"mil dudek kvar"
        2048 -> u"du mil kvardek ok"
    """

    msg = "Unknown Esperanto name for this big number: %d. " % num
    msg += "The largest integer value is 10**66 - 1."
    if num >= 10**66:
        raise ValueError, msg

    if verbose:
        print "Input:", num

    if num < 10:
        return DIGITS[num]

    ndigits = digits(num)
    ndigits = ndigits[::-1]
    res = ""
    for (i, n) in enumerate(ndigits):
        nextMax3Digits = ndigits[i:i+3]
        l = len(nextMax3Digits)
        if verbose:
            print "next3", nextMax3Digits, [1, 0, 0][:l]
        j = i % 3
        eodig = DIGITS[n]
        if n == 1:
            if j in (1, 2) or (i == 3 and nextMax3Digits == [1, 0, 0][:l]):
                eodig = ""
        val = POW10_SMALL[j]
        if j == 0:
            val = ""
            # handle value 10**3
            if i == 3:
                if nextMax3Digits != [0]*l:
                    res = "mil " + res.strip()
            # handle values 10**k, k=6,9,12,...
            elif i > 3:
                # get name for 10**k, e.g. "miliono"
                v = ""
                if nextMax3Digits > [0, 0, 0][:l]:
                    v = POW10_BIG[i]
                # check if plural "j" is needed for "miliono", etc.
                if nextMax3Digits[::-1] > [1, 0, 0][:l][::-1]:
                    v += "j"
                res = v + " " + res.strip()
        if n != 0:
            res = "%s%s " % (eodig, val) + res.strip()

        res = res.strip()

        if verbose:
            print "i:%d, j:%d, n:%d|%s, res:%s" % (i, j, n, eodig, repr(res))

    if verbose:
        print "Output:", res
        print

    # catch expressions which are not "well formed"
    if validate and validate_eo(res) == False:
        raise ValueError, u"Invalid expression: '%s'" % res
    
    return res


def eo2int(numString, validate=True, verbose=False):
    """Convert an integer string in Esperanto into an integer.
    
    Raises a ValueError when encountering substrings that do not
    describe valid Esperanto numbers, like "du mil tri mil" or "foo".

    Examples: 
        u"ducent tridek kvar" -> 234
        u"mil dudek kvar"     -> 1024
        u"du mil kvardek ok"  -> 2048
        u"du what kvardek ok"  -> ValueError
    """

    if verbose:
        print "Input:", numString

    # catch expressions which are not "well formed"
    if validate and validate_eo(numString) == False:
        raise ValueError, u"Invalid expression: '%s'" % numString
    
    # if we have a single digit number like u"kvin", 
    # return its integer value immediately
    if numString in DIGITS:
        return DIGITS.index(numString)
    
    # split combined expressions like u"ducent" into u"du cent"
    expanded = re.sub("(%s)(cent|dek)" % "|".join(DIGITS[2:]), 
        lambda m:m.groups()[0] + " " + m.groups()[1], numString)
    
    # build a list of eo strings like [u"du", u"cent", u"tri"]
    strList = expanded.split()
    
    total = 0
    value999 = 0
    value = 1
    for s in strList:
        if verbose:
            format = "s: %s, val: %d, val999: %d, total: %d"
            print format % (s, value, value999, total)
        if s in DIGITS:
            value = DIGITS.index(s)
        elif s == u"dek":
            if value == 0:
                value = 1
            value999 = value999 + value * 10
            value = 0
        elif s == u"cent":
            if value == 0:
                value = 1
            value999 = value999 + value * 100
            value = 0
        elif s == u"mil":
            value999 = value999 + value
            value999 = max(1, value999)
            total = total + value999 * 1000
            value999 = 0
            value = 0
        elif s in POW10_BIG_INV:
            value999 = value999 + value
            total = total + value999 * (10**POW10_BIG_INV[s])
            value999 = 0
            value = 0
        elif s.endswith(u"oj") and s[:-1] in POW10_BIG_INV:
            value999 = value999 + value
            total = total + value999 * (10**POW10_BIG_INV[s[:-1]])
            value999 = 0
            value = 0
        else:
            # encountered sth. that has nothing to do with an Esperanto number
            raise ValueError, "Unknown subexpression '%s'" % s

        if verbose:
            format = "s: %s, val: %d, val999: %d, total: %d"
            print format % (s, value, value999, total)
            print 

    value999 = value999 + value
    total = total + value999

    if verbose:
        format = "s: %s, val: %d, val999: %d, total: %d"
        print format % (s, value, value999, total)
               
    return total


# tests

TEST_CASES = {}
TEST_CASES.update({
    "digits": 
        zip(range(10), DIGITS)
})
TEST_CASES.update({
    "doubledigits": [
        (11, u"dek unu"), 
        (19, u"dek naŭ"), 
        (20, u"dudek"), 
        (22, u"dudek du"), 
        (88, u"okdek ok"), 
    ], 
    "hundreds": [
        (100, u"cent"), 
        (102, u"cent du"), 
        (120, u"cent dudek"), 
        (123, u"cent dudek tri"), 
        (888, u"okcent okdek ok"), 
    ], 
    "milions": [
        (  1000000, u"unu miliono"), 
        (  1001000, u"unu miliono mil"), 
        (  2000000, u"du milionoj"), 
        ( 10000000, u"dek milionoj"), 
        ( 21000000, u"dudek unu milionoj"), 
        (100000000, u"cent milionoj"), 
    ], 
    "big": [
        (    10**63, u"unu dekiliardo"), 
        (  2*10**63, u"du dekiliardoj"), 
        ( 10*10**63, u"dek dekiliardoj"), 
        (100*10**63, u"cent dekiliardoj"), 
    ], 
    "other": [
        (  1000, u"mil"), 
        ( 10000, u"dek mil"), 
        (100000, u"cent mil"), 
        (  1234, u"mil ducent tridek kvar"), 
        ( 11234, u"dek unu mil ducent tridek kvar"), 
        (  2048, u"du mil kvardek ok"), 
        (22334455, u"dudek du milionoj tricent tridek kvar mil kvarcent kvindek kvin"), 
    ], 
})


class EsperantoValidationTestCase(unittest.TestCase):
    "Test validation of Esperanto integer numbers."

    def test0(self):
        "Test validation of Esperanto integer numbers"

        validations = [
            ("du triilionoj kvar mil kvin milionoj", False),
            ("du triilionoj kvin milionoj kvar mil", True),
            ("du mil tri milionoj", False),
            ("du mil tri mil", False),
            ("unu miliono mil", True),
            ("du milionoj mil", True),
            ("du mil tri cent", False),
            ("du mil tricent", True),
            ("unu", True),
            ("nulcent nuldek nul", True),
        ]
        for numString, exp in validations:
            res = validate_eo(numString, verbose=False)
            args = (numString, res, exp)
            msg = "Input: '%s', response: %s, expected: %s" % args
            self.assertEqual(res, exp, msg)
        

class Int2EsperantoTestCase(unittest.TestCase):
    "Test conversion from integers to Esperanto."

    def test_int2eo_digits(self):
        "Convert single digit integers to Esperanto."

        eoMap = TEST_CASES["digits"]
        for i, exp in eoMap:
            res = int2eo(i, verbose=False)
            self.assertEqual(res, exp)
        

    def test_int2eo_doubledigits(self):
        "Convert selected two digit integers to Esperanto."

        eoMap = TEST_CASES["doubledigits"]
        for i, exp in eoMap:
            res = int2eo(i, verbose=False)
            self.assertEqual(res, exp)


    def test_int2eo_hundreds(self):
        "Convert selected three digit integers to Esperanto."

        eoMap = TEST_CASES["hundreds"]
        for i, exp in eoMap:
            res = int2eo(i, verbose=False)
            self.assertEqual(res, exp)
        

    def test_int2eo_milions(self):
        "Convert selected integers >= 1e6 to Esperanto."

        eoMap = TEST_CASES["milions"]
        for i, exp in eoMap:
            res = int2eo(i, verbose=False)
            self.assertEqual(res, exp)
        

    def test_int2eo_big(self):
        "Convert selected really big integers to Esperanto."

        eoMap = TEST_CASES["big"]
        for i, exp in eoMap:
            res = int2eo(i, verbose=False)
            self.assertEqual(res, exp)
        

    def test_int2eo_other(self):
        "Convert selected other integers to Esperanto."

        eoMap = TEST_CASES["other"]
        for i, exp in eoMap:
            res = int2eo(i, verbose=False)
            self.assertEqual(res, exp)
        

    def test_int2eo_too_big(self):
        "Convert too big integer to Esperanto."

        self.assertRaises(ValueError, int2eo, 10**70)
        

    def template_test_failing(self):
        "Test failing case."

        i, exp = 10000000, u"dek milionoj"
        res = int2eo(i, verbose=True)
        self.assertEqual(res, exp)


class Esperanto2IntTestCase(unittest.TestCase):
    "Test conversion from Esperanto strings to integers."

    def test_eo2int_digits(self):
        "Convert single digit Esperanto strings to integers."

        eoMap = TEST_CASES["digits"]
        for exp, eo in eoMap:
            res = eo2int(eo, verbose=False)
            self.assertEqual(res, exp)


    def test_eo2int_rest(self):
        "Convert remaining Esperanto strings into integers."

        for kind in TEST_CASES:
            if kind != "digits":
                eoMap = TEST_CASES[kind]
                for exp, eo in eoMap:
                    res = eo2int(eo, verbose=False)
                    self.assertEqual(res, exp)
        

class RoundtripTestCase(unittest.TestCase):
    "Test conversion from integers to Esperanto and back to integers."

    def test_int2eo2int(self):
        "Convert integers to Esperanto and back to integers."

        for i in range(100000):
            eo = int2eo(i, validate=False, verbose=False)
            j = eo2int(eo, validate=True, verbose=False)
            try:
                self.assertEqual(i, j)
            except AssertionError:
                print "Error: %d -> '%s' -> %d" % (i, eo, j)
                eo = int2eo(i, validate=False, verbose=False)
                j = eo2int(eo, validate=True, verbose=False)
                self.assertEqual(i, j)


if __name__ == "__main__":
    unittest.main()
