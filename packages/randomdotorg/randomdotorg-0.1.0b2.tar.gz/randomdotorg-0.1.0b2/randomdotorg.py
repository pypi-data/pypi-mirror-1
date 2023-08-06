#!/usr/bin/env python

#### Copyright (c) Clovis Fabricio Costa
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Alternate random number generator using random.org http
service as source.

RANDOM.ORG is a true random number service that generates randomness
via atmospheric noise.

To use just create a instance of the `RandomDotOrg` class, and use it as
you would use a `random.Random` instance.
"""

__version__ = '0.1.0b2'
__url__ = 'http://pypi.python.org/pypi/randomdotorg'
__all__ = ['RandomDotOrg']
__author__ = "Clovis Fabricio <nosklo at gmail dot com>"
__license__ = "GPL-3"


import random
import urllib
import urllib2


def _fetch_randomorg(service, **kwargs):
    """Internal function to make a fetch in a random.org service.
    >>> _fetch_randomorg('numbers', num=3, min=10, max=20)
    ['15', '11', '18']
    """
    url = "http://random.org/%s/?%s"
    options = dict(format='plain', num=1, col=1, base=10) # default options
    options.update(kwargs)
    url = url % (service, urllib.urlencode(options))
    headers = {'User-Agent': 'RandomDotOrg.py/%s + %s' % (__version__, __url__)}
    req = urllib2.Request(url, headers=headers)
    return urllib2.urlopen(req).read().splitlines()


class RandomDotOrg(random.Random):
    """Alternate random number generator using random.org http
    service as source.

    RANDOM.ORG is a true random number service that generates randomness
    via atmospheric noise.
    """

    #--- New methods
    def get_quota(self):
        """
        Returns used bit quota
        """
        return int(_fetch_randomorg('quota')[0])

    def multirange(self, start, stop=None, step=1, ammount=1):
        """Efficiently fetches multiple numbers in a range. Equivalent to
        running .randrange() method multiple times, but fetches all numbers
        at once.
        Returns a list of the numbers.
        """
        if stop is None:
            start, stop = 0, start
        xr = xrange(start, stop, step)
        n = len(xr)
        if n == 0:
            raise ValueError('range is empty')
        positions = _fetch_randomorg('integers', num=ammount, min=0, max=n - 1)
        return [xr[int(pos)] for pos in positions]

    def multirandom(self, ammount=1):
        """Efficiently fetches multiple random floats. Equivalent to
        running .random() method multiple times, but fetches all numbers
        at once.
        Returns a list of the numbers.
        """
        ammount = ammount * 5
        pool = _fetch_randomorg('integers', num=ammount, min=0, max=999)
        grouped = (pool[i:i+5] for i in xrange(0, ammount, 5))
        floats = [float('0.%s' % ''.join(number.rjust(3, '0') for number in intlist))
                  for intlist in grouped]
        return floats

    #--- Required overwritten methods
    def random(self):
        """Get the next random number in the range [0.0, 1.0)."""
        return self.multirandom(ammount=1)[0]

    def getrandbits(self, k):
        """getrandbits(k) -> x.  Generates a long int with k random bits."""
        k = int(k)
        if k <= 0:
            raise ValueError('number of bits must be greater than zero')
        bits = _fetch_randomorg('integers', num=k, min=0, max=1, base=2)
        return long(''.join(bits), 2)

    #--- Stub & Not implemented methods
    def _stub(self, *args, **kwds):
        "Stub method. Not used for a random.org random number generator."
        return None
    seed = jumpahead = _stub

    def _notimplemented(self, *args, **kwds):
        "Method should not be called for a random.org number generator."
        raise NotImplementedError('Random.org entropy source state saving is not implemented.')
    getstate = setstate = _notimplemented

    #--- Methods reimplemented to save bit quota (each .random() spends 50 bits)
    def shuffle(self, l):
        """l -> shuffle list l in place; return None.
        """
        order = _fetch_randomorg('sequences', min=0, max=len(l) - 1)
        for index, content in enumerate(l[:]):
            l[int(order[index])] = content

    def choice(self, seq):
        """Choose a random element from a non-empty sequence."""
        n = len(seq)
        if not seq:
            return None
        if n == 1:
            return seq[0]
        pos = int(_fetch_randomorg('integers', min=0, max=n - 1)[0])
        return seq[pos]

    def sample(self, population, k):
        """Chooses k unique random elements from a population sequence."""
        n = len(population)
        if not 0 <= k <= n:
            raise ValueError, "sample larger than population"
        order = _fetch_randomorg('sequences', min=0, max=n - 1)
        result = [population[int(order[n])] for n in xrange(k)]
        return result

    def randrange(self, start, stop=None, step=1):
        """Choose a random item from range([start,] stop[, step]).
        """
        return self.multirange(start=start, stop=stop, step=step, ammount=1)[0]


if __name__ == '__main__':
    r = RandomDotOrg()
    print "Current random.org quota:", r.get_quota()
    L = ['duck', 'dog', 'cat', 'cow', 'gnu']
    print "Random from L:", r.choice(L)
    print "3 distinct random elements from L:", r.sample(L, 3)
    r.shuffle(L)
    print "Random-ordered L:", L
    print "3 ints between [2, 33) step 3:", r.multirange(2, 33, 3, ammount=3)
    print "int between 10 and 20 (inclusive):", r.randint(10, 20)
    print "3 floats in range [0, 1):", r.multirandom(ammount=3)
