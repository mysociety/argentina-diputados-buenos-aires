# coding=utf-8

import scraperwiki
import lxml.html
import sqlite3
import re

BASE_URL = 'https://www.hcdiputados-ba.gov.ar/'

# Read in a page
html = scraperwiki.scrape(BASE_URL + 'index.php?id=diputados')
#
# # Find something on the page using css selectors
root = lxml.html.fromstring(html)
members = root.cssselect('div[class=\'derecha_un_tercio\']')

parsedMembers = []

for member in members:

    memberData = {}

    memberName = member.cssselect('div[class=\'nombre_diputado\']')[0]

    memberData['name'] = memberName.text.strip().replace('\n', ' ')

    click = memberName.attrib['onclick']
    idRegex = re.search('obtenerDiputado\(\'([0-9]*)\',\'llamadaDesdeIndex\'\)', click)
    memberData['id'] = idRegex.group(1)

    memberData['image'] = BASE_URL + member.cssselect('img')[0].attrib['src']

    print memberData

    parsedMembers.append(memberData)

print 'Counted {} Members'.format(len(parsedMembers))

try:
    scraperwiki.sqlite.execute('DELETE FROM data')
except sqlite3.OperationalError:
    pass
scraperwiki.sqlite.save(
    unique_keys=['id'],
    data=parsedMembers)
