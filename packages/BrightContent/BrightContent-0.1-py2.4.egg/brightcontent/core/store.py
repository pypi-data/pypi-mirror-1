import os
import cStringIO
import glob
import threading
import amara
#import mergeatom
import datetime
from amara import binderytools
from brightcontent.util import fixup_namespaces, quick_xml_scan

ATOM10_NS = u'http://www.w3.org/2005/Atom'
XHTML1_NS = u'http://www.w3.org/1999/xhtml'
ENCODING = 'UTF-8'
DUMMY_URI = u'urn:x-brightcontent:dummy'
COMMON_PREFIXES = { u'atom': ATOM10_NS, u'xh': XHTML1_NS }
DEFAULT_LANG = u'en'
STORE_XML_FILE = 'store.xml'

class repository:
    """
    The Bright Content Atom Store repository
    This is the core Atom capability, with Python API
    For APP access, plug in the brightcontent.core.store.app
    WSGI middleware (which is vaporware at present :-) )
    """
    def get_entries(self, limit=-1, lower_date=None, upper_date=None, slug=None):
        raise NotImplementedError

    def assemble_feed(self, entries, stream=None):
        atom = amara.create_document(
            u'feed', ATOM10_NS, attributes={u'xml:lang': u'en'})
        storedoc = amara.parse(self.store_xml_file,
            prefixes=COMMON_PREFIXES)
        for element in storedoc.feed.xml_children:
            atom.feed.xml_append(element)
        for entry in entries:
            atom.feed.xml_append_fragment(entry)
        fixup_namespaces(atom)
        if stream:
            atom.xml(indent='yes', stream=stream)
            return stream
        else:
            buffer = cStringIO.StringIO()
            atom.xml(indent='yes', stream=buffer)
            return buffer.getvalue()

class flatfile_repository(repository):
    """
    Flat file implementation of the repository
    """
    def __init__(self, storedir):
        self.storedir = storedir
        self.store_xml_file = os.path.join(storedir, STORE_XML_FILE)

    def get_entries(self, offset=0, limit=-1, lower_date=None, upper_date=None, slug=None):
        #appinfo = threading.local()
        #config = appinfo.config

        #For now always get all entries
        filenames = glob.glob(os.path.join(self.storedir, '*'))
        filenames = [ fn for fn in filenames if not fn.endswith(STORE_XML_FILE) ]
        entries = []
        offseted = 0
        for fn in filenames:
            updated = quick_xml_scan(fn, 'atom:updated', prefixes=COMMON_PREFIXES)
            date = amara.binderytools.parse_isodate(updated)
            if not((lower_date and date < lower_date) or (upper_date and date > upper_date)):
                if (slug and os.path.splitext(os.path.split(fn)[1])[0] == slug):
                    continue
                entry = open(fn, 'r').read()
                if offseted >= offset:
                    entries.append(entry)
                else:
                    offseted += 1
                if limit != -1 and len(entries) >= limit:
                    break
        #feed_doc = assemble_feed(feeds, config)
        #return feed_doc
        return entries



if __name__ == '__main__':
    import sys
    from dateutil.relativedelta import *
    from dateutil.tz import tzlocal
    store = flatfile_repository('/tmp/atomstore')
    #entries = get_entries(config, lower_date=datetime.datetime.today(),
    #    upper_date=datetime.datetime.today())
    #print assemble_feed(entries, config)
    #entries = get_entries(config)
    #print assemble_feed(entries, config)
    now = datetime.datetime.now(tzlocal())
    try:
        limit = int(sys.argv[1])
    except IndexError:
        limit = -1
    try:
        start = int(sys.argv[2])
        upper = now + relativedelta(days=-start)
    except IndexError:
        upper = None
    try:
        end = int(sys.argv[3])
        lower = now + relativedelta(days=-end)
    except IndexError:
        lower = None
    try:
        slug = sys.argv[4]
    except IndexError:
        slug = None
    entries = store.get_entries(limit, lower_date=lower, upper_date=upper, slug=slug)
    print store.assemble_feed(entries)

