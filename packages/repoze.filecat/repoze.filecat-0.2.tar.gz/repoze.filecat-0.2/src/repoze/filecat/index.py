import os
import re
import time
import datetime
import mimetypes
import unicodedata

from zope import interface
from zope import component

from ore.xapian.interfaces import IIndexer

import xappy
import interfaces
import extraction

def trim_join(strings):
    return "".join(map(trim, strings))

def trim(string):
    if string is not None:
        return string.replace('\n', ' ').replace('  ', ' ').strip()

def normalize(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """

    value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)

def create_indexer(database):
    indexer = xappy.IndexerConnection(database)

    # indexes
    indexer.add_field_action('short_name', xappy.FieldActions.INDEX_EXACT)
    indexer.add_field_action('searchable_text', xappy.FieldActions.INDEX_FREETEXT)
    indexer.add_field_action('author', xappy.FieldActions.INDEX_EXACT)
    indexer.add_field_action('keywords', xappy.FieldActions.TAG)
    indexer.add_field_action('modified_date', xappy.FieldActions.SORTABLE, type='date')
    indexer.add_field_action('creation_date', xappy.FieldActions.SORTABLE, type='date')
    indexer.add_field_action('mime_type', xappy.FieldActions.INDEX_EXACT)

    # metadata
    indexer.add_field_action('title', xappy.FieldActions.STORE_CONTENT)
    indexer.add_field_action('short_name', xappy.FieldActions.STORE_CONTENT)
    indexer.add_field_action('description', xappy.FieldActions.STORE_CONTENT)
    indexer.add_field_action('author', xappy.FieldActions.STORE_CONTENT)
    indexer.add_field_action('modified_date', xappy.FieldActions.STORE_CONTENT)
    indexer.add_field_action('creation_date', xappy.FieldActions.STORE_CONTENT)
    indexer.add_field_action('keywords', xappy.FieldActions.STORE_CONTENT)
    indexer.add_field_action('mime_type', xappy.FieldActions.STORE_CONTENT)
    
    return indexer

def search(query=None, start=None, limit=None, **kw):
    searcher = component.getUtility(interfaces.IXapianConnection).get_connection()

    if query is not None:
        query = searcher.query_parse(query)
    elif kw:
        assert len(kw) == 1, \
               "Single keyword-argument supported only."
        query = searcher.query_field(*(kw.items()[0]))
    else:
        query = searcher.query_all()
        
    return searcher.search(query, start, start+limit)

class Indexer(object):
    interface.implements(IIndexer)

    def __init__( self, resource):
        locator = component.getUtility(interfaces.IResourceLocator)
        self.path = locator.get_path(resource)

    def document(self, connection=None):
        mimetype, encoding = mimetypes.guess_type(self.path)

        try:
            method = getattr(self, 'document_%s' % (
                mimetype.replace('/', '_').replace('-', '_')))
        except AttributeError:
            raise ValueError("Unable to handle file-type: %s." % mimetype)

        doc = method(connection)

        # add modified date
        doc.fields.append(xappy.Field('modified_date', datetime.date(
            *time.localtime(os.path.getmtime(self.path))[:3])))

        # add mimetype
        doc.fields.append(xappy.Field('mime_type', mimetype))
        
        return doc

    def document_text_x_rst(self, connection):
        doc = xappy.UnprocessedDocument()
        metadata = extraction.extract_dc_from_rst(file(self.path))

        doc.fields.append(xappy.Field('title', metadata['title']))
        doc.fields.append(xappy.Field('author', metadata['author']))
        doc.fields.append(xappy.Field('creation_date', metadata['creation_date']))
        doc.fields.append(xappy.Field('searchable_text', metadata['searchable_text']))
        doc.fields.append(xappy.Field('short_name', normalize(metadata['title'])))

        return doc

    def document_image_jpeg(self, connection):
        doc = xappy.UnprocessedDocument()

        metadata = extraction.extract_xmp_from_jpeg(file(self.path))

        # iterate over all metadata text
        searchable_text = " ".join(
            text.strip('\n ') for text in metadata.itertext())

        # set up XML namespaces for queries
        namespaces = {
            'dc': 'http://purl.org/dc/elements/1.1/',
            'xmp': 'http://ns.adobe.com/xap/1.0/',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'exif': 'http://ns.adobe.com/exif/1.0/'}

        def xpath(query):
            return metadata.xpath(query, namespaces=namespaces)

        try:
            title = trim_join(xpath('.//dc:title')[0].itertext())
        except IndexError:
            title = u""

        try:
            description = trim_join(xpath('.//dc:description')[0].itertext())
        except IndexError:
            description = u""
            
        try:
            author = trim_join(xpath('.//dc:creator')[0].itertext())
        except IndexError:
            author = u""
            
        try:
            meta = xpath('.//rdf:Description')[0]
            creation_date = trim(
                meta.attrib.get(
                    '{%(exif)s}DateTimeOriginal' % namespaces) or
                meta.attrib.get(
                    '{%(xmp)s}CreateDate' % namespaces))
        except IndexError:
            creation_date = None
        
        keywords = map(trim, xpath('.//dc:subject//rdf:li/text()'))

        # fill document fields
        if title:
            doc.fields.append(xappy.Field('title', title))

        if description:
            doc.fields.append(xappy.Field('description', description))

        if keywords:
            for keyword in keywords:
                doc.fields.append(xappy.Field('keywords', keyword))

        if author:
            doc.fields.append(xappy.Field('author', author))

        if creation_date:
            try:
                date = datetime.datetime(*map(int, re.split('[^\d]', creation_date)[:-1]))
                doc.fields.append(xappy.Field('creation_date', date))
            except ValueError:
                pass

        if searchable_text:
            doc.fields.append(xappy.Field('searchable_text', searchable_text))

        short_name, ext = os.path.splitext(os.path.basename(self.path))
        doc.fields.append(xappy.Field('short_name', normalize(short_name)))

        return doc
