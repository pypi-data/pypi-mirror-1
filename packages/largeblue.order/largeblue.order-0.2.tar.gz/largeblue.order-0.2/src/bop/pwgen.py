#!/usr/bin/python
#############################################################################
# Name:         pwgen.py
# Purpose:      Helper to generate random cleartext passwords
# Maintainer:   Torsten Kurbad <t.kurbad@iwm-kmrc.de>
# Copyright:    (c) iwm-kmrc.de KMRC - Knowledge Media Research Center
# License:      GPLv2
#############################################################################
__docformat__ = 'restructuredtext'

import random
import string

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('bebop')


class PasswordGeneratorError(Exception):
    """Specialized exception for password generator errors."""


def generateRandomPassword(length=8, digits=2, specials=2):
    """Generate secure first time passwords."""
    chars = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
    nums  = '23456789'
    syms  = ',.!?$%&+-*/'

    passwd = []
    if (digits + specials) >= length:
        raise PasswordGeneratorError(_(
            u'Length cannot be smaller than digits + specials'))
    for i in range(length - (digits + specials)):
        passwd.append(random.choice(chars))
    for i in range(digits):
        passwd.append(random.choice(nums))
    for i in range(specials):
        passwd.append(random.choice(syms))
    random.shuffle(passwd)

    return u'%s' % ''.join(passwd)
