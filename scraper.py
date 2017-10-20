# coding=utf-8

import scraperwiki
import lxml.html
import sqlite3
import re
import time

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

    # Additional data is loaded via a somewhat silly AJAX fragment job:

    moreUrl = 'https://www.hcdiputados-ba.gov.ar/includes/undiputado.php?c_codigo=' + memberData['id']

    moreHtml = scraperwiki.scrape(moreUrl)

    # This HTML is such a horrible mess it's easier (just about) to just regex the bits we need out.

    partyRegex = re.search('Bloque:&nbsp;\s*(.*?)\s*</h5>', moreHtml)
    memberData['party'] = partyRegex.group(1)

    districtRegex = re.search('Distrito:&nbsp; </b>\s*(.*?)\s*</div>', moreHtml)
    memberData['district'] = districtRegex.group(1)

    sectionRegex = re.search('Seccion Electoral:&nbsp;</b>\s*(.*?)\s*</div>', moreHtml)
    memberData['section'] = sectionRegex.group(1)

    print memberData

    parsedMembers.append(memberData)

    # Sleep for a bit, let their server cool down
    time.sleep(4)

print 'Counted {} Members'.format(len(parsedMembers))

try:
    scraperwiki.sqlite.execute('DELETE FROM data')
except sqlite3.OperationalError:
    pass
scraperwiki.sqlite.save(
    unique_keys=['id'],
    data=parsedMembers)
