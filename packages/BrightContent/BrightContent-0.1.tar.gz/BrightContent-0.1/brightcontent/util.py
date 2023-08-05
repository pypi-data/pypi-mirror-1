import amara

def fixup_namespaces(node):
    """
    reduces namespace clutter in documents by looking for duplicate namespace
    declarations and preferring those set as document prefixes
    """
    doc = node.rootNode
    nss = dict(zip(doc.xmlns_prefixes.values(), doc.xmlns_prefixes.keys()))
    if node.namespaceURI in nss:
        node.xmlnsPrefix = nss[node.namespaceURI]
        node.nodeName = node.prefix and node.prefix + ':' + node.localName or node.localName
    for child in node.xml_xpath(u'*'): fixup_namespaces(child)
    return


def quick_xml_scan(source, field, **kwargs):
    #See http://copia.ogbuji.net/blog/2006-01-08/Recipe__fa
    val = unicode(amara.pushbind(source, field, **kwargs).next())
    return val


class node_wrapper:
    def __init__(self, node):
        self.node = node
        return

    def __iter__(self):
        return iter([self.node.xml()])


#Based on Ian Bicking algorithm in PEP 333
def get_base_url(environ):
    from urllib import quote
    url = environ['wsgi.url_scheme']+'://'

    if environ.get('HTTP_HOST'):
        url += environ['HTTP_HOST']
    else:
        url += environ['SERVER_NAME']

        if environ['wsgi.url_scheme'] == 'https':
            if environ['SERVER_PORT'] != '443':
               url += ':' + environ['SERVER_PORT']
        else:
            if environ['SERVER_PORT'] != '80':
               url += ':' + environ['SERVER_PORT']

    url += quote(environ.get('SCRIPT_NAME', '')) + '/'
    return url

    
