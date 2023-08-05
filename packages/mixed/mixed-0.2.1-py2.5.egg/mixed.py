#!/usr/bin/python
"""Handles arithmetic for mixed numbers and fractions.

>>> m = Mixed('33 1/3')
>>> print m * 2
66 2/3

Catherine Devlin   http://catherinedevlin.blogspot.com   Feb 28, 2008
"""

# Thanks to Yannick Gingras for Python 2.4 backport

import re, doctest

def gcd(*args):
    """Greatest Common Divisor between two integers.
    
    >>> gcd(6, 8)
    2
    >>> gcd(7,3)
    1
    >>> gcd(250, 400)
    50
    >>> gcd(1,4)
    1
    >>> gcd(-32,64)
    32
    """
    arg = abs(args[0])
    result = set(n for n in range(1, arg+1) if not (arg % n))
    for arg in args[1:]:
        arg = abs(arg)
        result &= set(n for n in range(1, arg+1) if not (arg % n))
    return max(result or (1,))

class Mixed(int):
    """Handles mixed numbers and fractions.
    """
    float_precision = 3
    knownFractions = {}
    for d in range(8,1,-1):
        for n in range(d-1,0,-1):
            knownFractions[int(round(float(n) / float(d) * (10**float_precision)))] = (n, d)
    reader = re.compile(r'(\-)?(\s*(\d+)[\s\-]+)?(\d+)\s*/\s*(\d+)')
    @classmethod
    def _new_from_tuple_(cls, i):
        """Input in form: (whole number, numerator, denominator)"""
        inst = super(Mixed, cls).__new__(cls, i[0] or 0)
        inst.num = i[1]
        inst.denom = i[2]
        return inst
    @classmethod
    def _new_from_str_(cls, i):
        result = Mixed.reader.search(i)
        if not result:
            raise TypeError, 'Could not interpret as mixed number'
        (sign, discard, whole, num, denom) = result.groups()
        if sign:
            whole = whole and sign + whole
            num = num and sign + num
        inst = super(Mixed, cls).__new__(cls, whole or 0)
        inst.num = int(num)
        inst.denom = int(denom)
        return inst
    @classmethod
    def _new_from_float_(cls, i):
        """
        >>> print Mixed(-2.5)
        -2 1/2
        >>> print Mixed(.66666667)
        2/3
        >>> print Mixed('3.13')
        3 13/100
        >>> print Mixed(4./3.)
        1 1/3
        """
        num = int(round(i - int(i), cls.float_precision) * (10**cls.float_precision))
        sign = (i < 0 and -1 or 1)
        known = cls.knownFractions.get(abs(num))
        if known:
            num = known[0] * sign
            denom = known[1]
        else:
            denom = 10**Mixed.float_precision
        return cls._new_from_tuple_((int(i), num, denom)).reduced()
        
    def __new__(cls, i):
        """
        >>> print Mixed('8-1/2')
        8 1/2
        >>> print Mixed('-5/8')
        -5/8
        >>> print Mixed('4')
        4
        """
        if isinstance(i, float):
            return cls._new_from_float_(i)
        if ((len(i) == 3) and (isinstance(i, tuple) or isinstance(i, list))):
            return cls._new_from_tuple_(i)
        try:
            return cls._new_from_str_(i)
        except:
            try:
                return int(i)
            except ValueError:
                if isinstance(i, basestring):
                    try:
                        i = float(i)
                        return cls._new_from_float_(i)
                    except:
                        pass
        raise TypeError, 'Could not interpret as mixed number'
    def __str__(self):
        if int(self):
            return "%d %d/%d" % (int(self), abs(self.num), self.denom)
        else:
            return "%d/%d" % (self.num, self.denom)
    def __repr__(self):
        return "Mixed('%s')" % (self.__str__())
    def __nonzero__(self):
        """
        >>> bool(Mixed('-1/7'))
        True
        """
        return bool(int(self) or self.num)
    def __float__(self):
        return super(Mixed, self).__float__() + float(self.num) / float(self.denom)
    def _num_improper(self):
        return int(self) * self.denom + self.num
    def improper(self):
        return Mixed((0, self._num_improper(), self.denom))
    def __add__(self, other):
        """
        >>> print Mixed('-1-1/2') + 2
        1/2
        >>> print Mixed('-3-7/8') + Mixed('3/8')
        -3 1/2
        >>> print Mixed('3/4') + Mixed('1/2')
        1 1/4
        >>> print Mixed('1-1/2') + Mixed('2/3')
        2 1/6
        """
        if isinstance(other, Mixed):
            denom = self.denom * other.denom
            num = (self._num_improper() * other.denom) + (other.num * self.denom)
            return Mixed((0, num, denom)).reduced()
        elif isinstance(other, int):
            return Mixed((0, self._num_improper() + other * self.denom, self.denom)).reduced()
        elif isinstance(other, float):
            return other + float(self)
        return super(Mixed, self).__add__(other)
    def __radd__(self, other):
        """
        >>> print 2 + Mixed('1 1/2')
        3 1/2
        """
        return self + other
    def __mul__(self, other):
        """
        >>> print Mixed('-1-1/4') * 2
        -2 1/2
        >>> print Mixed('-3 1/3') * 3 - 2
        -12
        >>> print Mixed('1/3') * Mixed('2 1/2')
        5/6
        
        """
        if isinstance(other, Mixed):
            return Mixed((0, self._num_improper() * other._num_improper(), self.denom * other.denom)).reduced()
        elif isinstance(other, int):
            return Mixed((int(self) * other, self.num * other, self.denom)).reduced()
        elif isinstance(other, float):
            return float(self) * other
    def __rmul__(self, other):
        """
        >>> print 2 * Mixed('-1-1/4')
        -2 1/2
        """
        return self * other
    def __sub__(self, other):
        """
        >>> print Mixed('2 1/2') - Mixed('2/3')
        1 5/6
        
        """
        return self + (other * -1)
    def __rsub__(self, other):
        """
        >>> print 2 - Mixed('1 1/2')
        1/2
        """
        return (-1 * self) + other
    def __div__(self, other):
        """
        >>> print Mixed('-5/8') / 2
        -5/16
        """
        if isinstance(other, Mixed):
            return Mixed((0, self._num_improper() * other.denom, self.denom * other._num_improper())).reduced()            
        elif isinstance(other, int):
            return Mixed((0, self._num_improper(), self.denom * other)).reduced()
        elif isinstance(other, float):
            return float(self) / other
    def __rdiv__(self, other):
        """
        >>> print 4 / Mixed('1/2')
        8
        >>> print -3 / Mixed('2/5')
        -7 1/2
        """
        if isinstance(other, Mixed):
            return Mixed((0, other._num_improper() * self.denom, other.denom * self._num_improper())).reduced()            
        elif isinstance(other, int):
            return Mixed((0, other * self.denom, self._num_improper())).reduced()
        elif isinstance(other, float):
            return float(self) / other        
        return other.__div__(self)
    def __pow__(self, pow):
        """
        >>> Mixed('1/2') ** 3
        Mixed('1/8')
        """
        return Mixed((0, self._num_improper() ** pow, self.denom ** pow)).reduced()
    def __rpow__(self, other):
        """
        >>> 16 ** Mixed('1/2')
        4.0
        """
        return other ** float(self)
    def __cmp__(self, other):
        """
        >>> Mixed('1 1/2') > Mixed('4/3')
        True
        >>> Mixed('1 1/2') > Mixed('5/3')
        False
        >>> Mixed ('-2 2/5') < -2
        True
        >>> Mixed('2/4') == Mixed('1/2')
        True
        """
        if isinstance(other, Mixed):
            return cmp(self._num_improper() * other.denom, other._num_improper() * self.denom)
        elif isinstance(other, int):
            return cmp(self.reduced(), Mixed((other, 0, self.denom)))
        elif isinstance(other, float):
            return cmp(float(self), other)
    def _num_too_large(self):
        sgn = (self.num < 0) and -1 or 1 
        extrawholes = ((self.num * sgn) // self.denom) * sgn
        if not extrawholes:
            return self
        result = Mixed((int(self) + extrawholes, self.num - extrawholes*self.denom, self.denom))
        return result
    def _reduce_denom(self):
        divisor = gcd(self.num, self.denom)
        if divisor > 1:
            self.num /= divisor
            self.denom /= divisor
        return self                
    def reduced(self):
        """
        >>> print Mixed('14/8').reduced()
        1 3/4
        """
        result = self._num_too_large()._reduce_denom()
        if not result.num:
            return int(result)
        return result
    def _mult_frac(self, multfrac):
        return Mixed((int(self), self.num * multfrac, self.denom * multfrac))
    def _in_common_denom(self, other):
        return (self._mult_frac(other.denom), other._mult_frac(self.denom))
    
if __name__ == '__main__':
    doctest.testmod()
