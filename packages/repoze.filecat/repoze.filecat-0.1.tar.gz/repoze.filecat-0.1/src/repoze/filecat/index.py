import time
import datetime

from zope import interface
from zope import component

from ore.xapian.interfaces import IIndexer

from hachoir_core.stream import InputIOStream
from hachoir_parser import guessParser
from hachoir_metadata.jpeg import JpegMetadata
from hachoir_metadata import extractMetadata
from hachoir_metadata.metadata import extractors
from hachoir_metadata.metadata_item import Data as Metadata

import xappy
import interfaces


def create_indexer(database):
    indexer = xappy.IndexerConnection(database)

    # indexes
    indexer.add_field_action('searchable_text', xappy.FieldActions.INDEX_FREETEXT)
    indexer.add_field_action('author', xappy.FieldActions.INDEX_EXACT)
    indexer.add_field_action('keywords', xappy.FieldActions.TAG)
    indexer.add_field_action('creation_date', xappy.FieldActions.SORTABLE, type='data')

    # metadata
    indexer.add_field_action('title', xappy.FieldActions.STORE_CONTENT)
    indexer.add_field_action('description', xappy.FieldActions.STORE_CONTENT)
    indexer.add_field_action('author', xappy.FieldActions.STORE_CONTENT)

    return indexer


def extract_metadata(stream):
    parser = guessParser(InputIOStream(stream))

    extractor = extractors[type(parser)]

    # use most informative mode
    metadata = extractor(9)

    # register additional metadata attributes
    metadata.register(
        Metadata("keywords", 100, u"Keywords"))
    metadata.register(
        Metadata("object_name", 100, u"Object identifier (typically filename"))
    metadata.register(
        Metadata("headline", 100, u"Descriptive title"))

    # extract metadata
    metadata.extract(parser)

    return metadata

JpegMetadata.IPTC_KEY[25] = "keywords"
JpegMetadata.IPTC_KEY[5] = "object_name"
JpegMetadata.IPTC_KEY[105] = "headline"


class HachoirIndexer(object):
    interface.implements(IIndexer)

    def __init__( self, resource):
        locator = component.getUtility(interfaces.IResourceLocator)
        self.path = locator.get_path(resource)

    def document(self, connection):
        doc = xappy.UnprocessedDocument()

        metadata = extract_metadata(file(self.path))

        data = {}
        for metadata_item in sorted(metadata):
            data[metadata_item.key] = [item.text for item in metadata_item.values]


        # concatenate all metadata value to form searchable text
        searchable_text = " ".join([" ".join(values) for values in data.values()])

        # extract indexable fields
        def getter(key):
            values = data.get(key, ())
            if not len(values):
                return ""
            elif len(values) == 1:
                return values[0]
            else:
                return values[-1]

        title = getter("title")
        description = getter("description")
        author = getter("author")
        creation_date = getter("creation_date")
        keywords = data.get('keywords')

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
                date = datetime.datetime(
                    *time.strptime(creation_date[0], "%Y-%m-%d %H:%M:%S")[0:6])
                doc.fields.append(xappy.Field('creation_date', date))
            except ValueError:
                pass

        if searchable_text:
            doc.fields.append(xappy.Field('searchable_text', searchable_text))

        return doc
