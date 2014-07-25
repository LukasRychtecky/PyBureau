from __future__ import unicode_literals

import sys
import urllib
import urllib2
import unicodedata

from xml.dom.minidom import parse

from .exceptions import InvalidCardError, InvalidFormatCardError


class CardValidator(object):
    URL = 'http://aplikace.mvcr.cz/neplatne-doklady/doklady.aspx'

    TYPE_ID = 0
    TYPE_PASSPORT_CENTRAL = 4
    TYPE_PASSPORT_LOCAL   = 5
    TYPE_FIREARMS_LICENSE = 6

    @classmethod
    def validate(cls, number, type=TYPE_ID):
        '''Detect and invalid card (IDs, passports, etc.) against the central repository provided by the ministry.

        Keyword arguments:
        number -- string with card number
        type -- integer of card type
                0 (default) ... identity card
                4 ... passport (central, purple)
                5 ... passport (local, green)
                6 ... firearms license

        '''
        data = urllib.urlencode({ 'dotaz': number, 'doklad': type })
        request = urllib2.Request(cls.URL, data)
        response = urllib2.urlopen(request)

        dom = parse(response)
        cls._error(dom)

        elements = dom.getElementsByTagName('odpoved');
        if not elements:
            return

        answer = elements.pop()
        if answer.attributes['evidovano'].value == 'ano':
            raise InvalidCardError('Card with number %s is invalid' % number)

    @classmethod
    def _text(cls, nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return unicodedata.normalize('NFKD', ''.join(rc)).encode('ascii', 'ignore')

    @classmethod
    def _error(cls, dom):
        elements = dom.getElementsByTagName('chyba');
        if elements:
            error = elements.pop()
            raise InvalidFormatCardError('Error returned from the remote server: %s' % cls._text(error.childNodes))


if __name__ == '__main__':
    if not len(sys.argv) in [2, 3]:
        print 'Pass card number, and type (0 by default) as a function argument'
        print 'Card types:\n0 ... identity card\n4 ... central passport (purple)\n5 ... local passport (green)\n6 ... firearms license'
        sys.exit(2)

    number = sys.argv[1]
    type = CardValidator.TYPE_ID
    if len(sys.argv) == 3:
        type = int(sys.argv[2])

    try:
        CardValidator.validate(number, type)
        print 'Card with number %s is NOT INVALID' % number

    except InvalidCardError:
        print 'Card with number %s is INVALID' % number

    sys.exit(1)
