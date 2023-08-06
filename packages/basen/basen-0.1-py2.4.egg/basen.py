#! /usr/bin/python
# -*- coding: utf-8 -*-
""" BaseN

You can define the Numeral system by the base(radix) or digits(numerals)

Licence: GPL3 or Python Software Foundation License
Copyright: (c) 2008 MIZUNO J.Y.
Reference:
    Math::BaseCalc [http://search.cpan.org/dist/Math-BaseCalc/]
    Wikipedia [http://ja.wikipedia.org/w/index.php?title=%E4%BD%8D%E5%8F%96%E3%82%8A%E8%A8%98%E6%95%B0%E6%B3%95&oldid=20340698]
"""
__author__ = 'MIZUNO J.Y. http://p.mjy.name/'
__date__ = '2008/08/03'
__version__ = '0.1'


_preset = {'bin': lambda:['0', '1'],
           'hex': lambda:_chr_list('09', 'af'),
           'HEX': lambda:_chr_list('09', 'AF'),
           'oct': lambda:_chr_list('07'),
           #'64': lambda:_chr_list('AZ', 'az', '09', '+', '/'),
           #'62': lambda:_chr_list('09', 'az', 'AZ'),
           }

def _chr_list(*couples):
    r = []
    for c in couples:
        if len(c) == 1:
            r.extend(c)
        else:
            r.extend(map(chr, range(ord(c[0]), ord(c[1])+1)))
    return r

def _split_with_point(seq, separator):
    int_part = None
    fraction_part = None
    for c, i in enumerate(seq):
        if i == separator:
            int_part = seq[:c]
            break
    if int_part is None:  # there is no separator
        int_part = seq[:]
        #fraction_part = None
    else:
        fraction_part = seq[c+1:]
        if separator in fraction_part:
           raise ValueError, "two or more decimal point exists"
    return int_part, fraction_part

def _property2(func):
    return property(func, lambda s,v:func(s, v, _get=False))


class BaseN(object):
    """ >>> from basen import *

        >>> b = BaseN('bin')
        >>> b.str(2)
        '10'
        >>> b.int('10')
        2
        >>> b.float('-10.1')
        -2.5

        >>> b = BaseN(digits='._', point=':', negative_sign='>')
        >>> b.str(2)
        '_.'
        >>> b.int('_.')
        2
        >>> b.float('>_.:_')
        -2.5
    """
    __slots__ = ('_trans', '_point', '_negative_sign', '_after_point',
                 '_n', '_digits') 

    @_property2
    def point(self, sign=None, _get=True):
        """ >>> b = BaseN(2)
            >>> b.point
            '.'
            >>> b.str(0.5)
            '0.1'

            >>> b.point = '@'
            >>> b.str(0.5)
            '0@1'
        """
        if _get:
            return self._point
        if not sign in self._digits:
            self._point = sign
        else:
            raise ValueError, "%r is included in digits" % sign

    @_property2
    def negative_sign(self, sign=None, _get=True):
        """ >>> b = BaseN(2)
            >>> b.negative_sign
            '-'
            >>> b.str(-2)
            '-10'

            >>> b.negative_sign = '>'
            >>> b.str(-2)
            '>10'
        """
        if _get:
            return self._negative_sign
        if not sign in self._digits:
            self._negative_sign = sign
        else:
            raise ValueError, "%r is included in digits" % sign

    @_property2
    def after_point(self, num=None, _get=True):
        """ >>> b = BaseN(2)
            >>> b.after_point
            17
            >>> b.str(1.1)
            '1.00011001100110011'

            >>> b.after_point = 3
            >>> b.str(1.1)
            '1.000'
        """
        if _get:
            return self._after_point
        if num >= 1 and isinstance(num, (int, long)):
            self._after_point = num
        else:
           raise ValueError, \
                 "after_point must be an integer of 1 or more"

    def __init__(self, n=None, digits=None,
                 point='.', negative_sign='-', after_point=17,
                 join=None):
        """ >>> b = BaseN('bin')
            >>> b = BaseN(2)
            >>> b = BaseN(digits=['0','1'])
            >>> b = BaseN(digits='01')
        """
        self._trans = {}
        self._digits = []
        self.point = point
        self.negative_sign = negative_sign
        self.after_point = after_point
        if n != None and digits == None:
            self.n(n)
        elif digits != None and n == None:
            self.digits(digits)
        else:
            raise TypeError, \
                  "BaseN() takes argument either 'n' or 'digits'"

    def digits(self, digit_set=None):
        """ >>> bn = BaseN(4)
            >>> bn.digits()
            ('0', '1', '2', '3')

            >>> bn.digits('0XYZ')
            >>> bn.digits()
            ('0', 'X', 'Y', 'Z')
        """
        if digit_set is None:
            return self._digits

        tmp_digits = tuple(digit_set)
        tmp_n = len(tmp_digits)
        if tmp_n < 2:
            raise ValueError, "digits is necessary for 2 or more"
        tmp_trans = {}
        for c, dig in enumerate(tmp_digits):
            tmp_trans[dig] = c
        if len(tmp_trans) < tmp_n:
            raise ValueError, "there is duplicate data in digits"
        self._digits = tmp_digits
        self._trans = tmp_trans
        self._n = tmp_n

    def n(self, num_or_preset=None):
        """ >>> bn = BaseN(2)
            >>> bn.n()
            2
            >>> bn.digits('0XYZ')
            >>> bn.n()
            4
            >>> bn.n(4)
            >>> bn.digits()
            ('0', '1', '2', '3')
            >>> bn.n('hex')
            >>> bn.n()
            16
        """
        if num_or_preset == None:
            return self._n

        if isinstance(num_or_preset, (int, long)):
            if num_or_preset > 62 or num_or_preset < 2:
                raise ValueError, '%r is not in the range from 2 to 62' \
                                  % num_or_preset
            self.digits(_chr_list('09', 'az', 'AZ')[0:num_or_preset])
        elif isinstance(num_or_preset, str):
            if not num_or_preset in _preset:
                raise ValueError, \
                      "%r is not preset base name" % num_or_preset
            self.digits(_preset[num_or_preset]())
        else:
            raise TypeError, \
                  "the argument must be a str or a integer, not %r" \
                  % type(num_or_preset)

    def str(self, num):
        """ >>> bn = BaseN(4)
            >>> bn.str(5)
            '11'
            >>> bn.str(5.5)
            '11.2'
            >>> bn.str(0.2)
            '0.03030303030303030'
            >>> bn.float(bn.str(0.2))
            0.19999999995343387
        """
        return self._digits[0][0:0].join(self.list(num))

    def list(self, num):
        """ >>> bn = BaseN(digits=('O', 'I', 'II', 'III'))
            >>> bn.list(4)
            ['I', 'O']
            >>> bn.list(4.5)
            ['I', 'O', '.', 'II']
            >>> bn.float(bn.list(0.25))
            0.25
        """
        r = []
        # negative numbers
        if num < 0:
            r.append(self.negative_sign)
            num = abs(num)

        if isinstance(num, (int, long)):
            r.extend(self._int_to_list(num))
            return r
        elif isinstance(num, float):
            int_part = int(num)
            fraction_part = num - int_part
            r.extend(self._int_to_list(int_part))
            r.append(self.point)
            r.extend(self._fraction_to_list(fraction_part))
            return r
        else:
            raise TypeError, \
                  "the argument must be a integer or a float, not %r" \
                  % type(num)

    def _fraction_to_list(self, num):
        r = []
        while num > 0 and len(r) < self._after_point:
            tmp = (num * self._n)
            int_part = int(tmp)
            r.append(self._digits[int_part])
            num = tmp - int_part

        return r or [self._digits[0]]

    def _int_to_list(self, num):
        r = []
        while num > 0:
            num, mod = divmod(num, self._n)
            r.insert(0, self._digits[mod])

        return r or [self._digits[0]]

    def float(self, string):
        """ >>> bn = BaseN(4)
            >>> bn.float('1')
            1.0
            >>> bn.float('1.1')
            1.25
        """
        if string[0] == self.negative_sign:
            return -1 * self.float(string[1:])

        i_part, f_part = _split_with_point(string, self._point)

        r = 0.0
        if i_part:
            r += self.int(i_part)
        if f_part:
            r += float(self.int(f_part)) / (self._n ** len(f_part))

        return r

    def int(self, string):
        """ >>> bn = BaseN(4)
            >>> bn.int('10')
            4
            >>> bn.int('10.1')
            4
        """
        if string[0] == self.negative_sign:
            return -1 * self.int(string[1:])

        if self._point:
            string, nonuse = _split_with_point(string, self.point)

        r = 0
        for s in string:
            r = r * self._n + self._trans[s]

        return r


if __name__ == "__main__":
    #calc = BaseCalc(digits_oct())
    #calc = BaseN('HEX')
    #, point=':', negative_sign='>', after_point=3)
    #for x in xrange(100):
    #    #x = (x + 0.123456789) *-1
    #    #x = float(x)
    #    print x, calc.str(x), calc.float(calc.str(x)), calc.int(calc.str(x))
    #print calc.str(0.1) , calc.float(calc.str(0.1))

    import doctest
    doctest.testmod()

