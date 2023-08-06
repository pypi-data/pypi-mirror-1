import re
import datetime
import logging
import docutils.parsers.rst
import docutils.core
import docutils.nodes

from lxml import etree

from repoze.filecat import jpeg

re_xpacket_start = re.compile(r'<\?xpacket.*\?>')
re_xpacket_end = re.compile(r'<\?xpacket.*\?>$')

xmp_header = 'http://ns.adobe.com/xap/1.0/\x00'

empty_xmpdoc = etree.fromstring("""<x:xmpmeta xmlns:x="adobe:ns:meta/"></x:xmpmeta>""")

logger = logging.getLogger("repoze.filecat")

def extract_xmp_from_jpeg(stream):
    segment = jpeg.read(stream, "\xE1", xmp_header)
    if segment is None:
        logger.info("Unable to find XMP segment in file: %s." % stream.name)
        return empty_xmpdoc
        
    document = segment[len(xmp_header):]
    
    ms = re_xpacket_start.search(document)
    me = re_xpacket_end.search(document)    
    if ms and me:
        source = document[ms.end():me.start()].strip('\n ')
        return etree.fromstring(source)

    raise ValueError("Invalid XMP application segment.")
        
def extract_dc_from_rst(stream):
    document = docutils.core.publish_doctree(stream.read())
    metadata = {}
    
    class visitor(docutils.nodes.NodeVisitor):
        def visit_author(self, node):
            metadata['author'] = unicode(node[0])

        def visit_title(self, node):
            metadata['title'] = unicode(node[0])

        def visit_date(self, node):
            date = datetime.date(*(
                map(int, unicode(node[0]).split('-'))))
            metadata['creation_date'] = date

        def visit_document(self, node):
            metadata['searchable_text'] = node.astext()

        def unknown_visit(self, node):
            pass

    document.walk(visitor(document))
    return metadata
        
