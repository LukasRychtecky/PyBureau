
import sys
import urllib
import urllib2
import unicodedata

from xml.dom.minidom import parse

from .exceptions import InvalidCardError


URL = "http://aplikace.mvcr.cz/neplatne-doklady/doklady.aspx"

TYPE_ID = 0
TYPE_PASSPORT_CENTRAL = 4
TYPE_PASSPORT_LOCAL   = 5
TYPE_FIREARMS_LICENSE = 6


def validate(number, type=TYPE_ID):
  data = urllib.urlencode({ 'dotaz': number, 'doklad': type })

  request = urllib2.Request(URL, data)
  response = urllib2.urlopen(request)

  dom = parse(response)
  _error(dom)

  elements = dom.getElementsByTagName("odpoved");
  if not elements:
    return

  answer = elements.pop()
  if answer.attributes["evidovano"].value == "ano":
    raise InvalidCardError('Card with number %s is invalid' % number)


def _text(nodelist):
  rc = []
  for node in nodelist:
    if node.nodeType == node.TEXT_NODE:
      rc.append(node.data)
  return unicodedata.normalize('NFKD', ''.join(rc)).encode('ascii', 'ignore')


def _error(dom):
  elements = dom.getElementsByTagName("chyba");
  if elements:
    error = elements.pop()
    raise Exception("Error returned from the remote server: %s", _text(error.childNodes))


if __name__ == "__main__":
  if not len(sys.argv) in [2, 3]:
    print('Pass card number, and type (0 by default) as a function argument')
    print('Card types:\n0 ... identity card\n4 ... central passport (purple)\n5 ... local passport (green)\n6 ... firearms license')
    sys.exit(2)

  number = sys.argv[1]
  type = TYPE_ID
  if len(sys.argv) == 3:
    type = int(sys.argv[2])

  try:
    validate(number, type)
    print('Card with number %s is NOT INVALID' % number)
  except InvalidCardError:
    print('Card with number %s is INVALID' % number)

  sys.exit(1)
