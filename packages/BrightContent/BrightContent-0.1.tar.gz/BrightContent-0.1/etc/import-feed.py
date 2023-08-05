import sys
import os
import amara
from brightcontent.core.store import COMMON_PREFIXES, ATOM10_NS
from brightcontent.util import fixup_namespaces, quick_xml_scan

def id_to_fname(id_):
    return '-'.join(id_.split('/')[-4:])
    #return id.replace(os.path.sep, '-')

input_file_or_url = sys.argv[1]
try:
    output_dir = sys.argv[2]
except IndexError:
    output_dir = '/tmp/atomstore'

doc = amara.parse(input_file_or_url, prefixes=COMMON_PREFIXES)
store = amara.create_document(u"atom:feed", ns=ATOM10_NS)
for nonentry in doc.feed.xml_xpath(u'*[not(self::atom:entry)]'):
    store.feed.xml_append(nonentry)
f = open(os.path.join(output_dir, 'store.xml'), 'w')
fixup_namespaces(store)
f.write(store.xml(indent=u"yes"))
f.close()
for entry in doc.feed.entry:
    fname = id_to_fname(unicode(entry.id))
    print fname
    f = open(os.path.join(output_dir, fname), 'w')
    f.write(entry.xml())
    f.close()

