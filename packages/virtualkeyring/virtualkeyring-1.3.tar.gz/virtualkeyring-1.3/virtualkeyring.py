#!/usr/bin/python
#  Copyright 2007 Olivier Grisel <olivier.grisel@ensta.org>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Utility script to build a set of strong yet rebuildable passwords

:author: Olivier Grisel <olivier.grisel@ensta.org>

The final password is build from a potentialy weak but easy to remember yet
secret master password and a domain-specific key like the name of the website
you are building a password for.

The password is then the 8th first characters of the letters + digits encoding of
sha1 digest of the concatenation of the master password and the domain key::

  >>> make_password("myprecious", "paypal")
  'muvcEizM'

  >>> make_password("myprecious", "jdoe@example.com", uppercase=False, length=6)
  'ykn0nu'

  >>> make_password("myprecious", "jdoe@example.com", digits=False, length=10)
  'bdnrAGgJqe'

"""

import optparse
import sha
import string
import sys
from itertools import izip
from getpass import getpass

ONE_BYTE = 2 ** 8
DEFAULT_LENGTH = 8 # default password length
DEFAULT_ALPHABET = string.lowercase + string.uppercase + string.digits

def bytes2number(bs):
    """Convert a python string (of bytes) into a python integer

    >>> bytes2number('0')
    48
    >>> bytes2number('00')
    12336
    >>> bytes2number('a0')
    24880

    """
    n = 0
    for i, c in izip(xrange(len(bs)), reversed(bs)):
        n += ord(c) * (ONE_BYTE ** i)
    return n


def number2string(n, alphabet='01'):
    """Compute the string representation of ``n`` in letters in ``alphabet``

    >>> number2string(0)
    '0'
    >>> number2string(1, '01')
    '1'
    >>> number2string(2, '01')
    '10'
    >>> number2string(3)
    '11'
    >>> number2string(4, '01')
    '100'

    >>> number2string(58, string.digits + 'abcdef')
    '3a'

    >>> number2string(-1, '01') #doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: -1 is not a natural number

    """
    base = len(alphabet)
    if n == 0:
        return alphabet[n]
    elif n < 0:
        raise ValueError("%d is not a natural number" % n)
    acc = []
    while n != 0:
        n, remainder = divmod(n, base)
        acc.append(alphabet[remainder])
    return ''.join(reversed(acc))


def bytes2string(bs, alphabet):
    """Transcode a string of bytes into an arbitrary alphabet"""
    return number2string(bytes2number(bs), alphabet)


def make_password(master_password, domain_key, lowercase=True, uppercase=True,
                  digits=True, length=DEFAULT_LENGTH, alphabet=None):
    """Build a password out of a master key and a domain key"""

    # build the sha1 hash of the concatenation of the keys
    hash = sha.new(master_password + domain_key).digest()

    if alphabet is None:
        # determine the list of acceptable characters
        alphabet = ''
        alphabet += lowercase and string.lowercase or ''
        alphabet += uppercase and string.uppercase or ''
        alphabet += digits and string.digits or ''

    if not alphabet:
        raise ValueError('empty alphabet')

    # re-write the hash in the given alphabet and take the first chars as
    # final password
    return bytes2string(hash, alphabet)[:length]


def get_password(domain_key=None, lowercase=True, uppercase=True,
                 digits=True, length=DEFAULT_LENGTH, alphabet=None):
    """Prompt for master password and domain key. Return a password"""
    # password and domain prefix (if None) are read interactively from stdin to
    # avoid password data to be stored in the shell command history
    master_password = getpass("master password: ")
    if domain_key is None:
        domain_key = raw_input("domain key [e.g. 'login@host']: ")
    return make_password(master_password, domain_key,
                         uppercase=uppercase, digits=digits,
                         length=length, alphabet=alphabet)


def parse_args(args):
    usage = "vkr -l 10 -a abcdefghijklmnopqrstuvwyz0123456789"
    parser = optparse.OptionParser(usage=usage)

    parser.add_option('-l', '--lenght',
                      dest='length',
                      default=DEFAULT_LENGTH,
                      type="int",
                      help=("Lenght of the generated password (default: %d)" %
                            DEFAULT_LENGTH))

    parser.add_option('-a', '--alphabet',
                      dest='alphabet',
                      default=DEFAULT_ALPHABET,
                      help=("Characters to be used for the generated password"
                            " (default: %s)" % DEFAULT_ALPHABET))

    return parser.parse_args(args=args)


def main():
    options, _ = parse_args(sys.argv)

    passwd = get_password(length=options.length,
                          alphabet=options.alphabet)
    print "your password is:", passwd
    print "please clean your console (ctrl-L) after usage"


if __name__ == "__main__":
   main()
