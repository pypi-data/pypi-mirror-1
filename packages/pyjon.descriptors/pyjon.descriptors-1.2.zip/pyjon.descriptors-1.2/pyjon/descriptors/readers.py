"""defines specialized readers that will be used by the pyjon descriptors
"""
__all__ = ['CSVReader', 'DirtyXMLReader', 'FixedLengthReader']

import logging

import csv
from pyjon.descriptors.input import InputItem
from pyjon.descriptors.exceptions import (MaxLenError, MinLenError,
        MissingFieldError, SourceError, TooManyFieldsError, TooFewFieldsError,
        RemainingDataError)

from pyjon.descriptors.casters import Caster

import os
import tempfile

#from sgmllib import SGMLParser
from pyjon.descriptors.beautifulsoup import BeautifulSoup, BeautifulStoneSoup, SoupStrainer
import xml.sax.saxutils as saxutils

log = logging.getLogger(__name__)

import re
#sub_ampersand_notfollowed_bysemicolumn = "&(?!.*;)"
sub_ampersand = re.compile("&")

import codecs

class ItemFactory(object):
    def __init__(self, schemaroot, encoding, caster):
        """ a small factory that produces InputItems from csv rows or dirty xml
        row. The only constraint is to feed it with some indexable (row will be
        accessed using the indexes from the schema)
        
         @param schemaroot: the root node of a descriptor schema that describes
        how to read the input stream.
        @type schemaroot: elementtree.Element node
    
        @param encoding: the encoding that was declared in the header of the
        stream. This encoding will be used to read the data.
        @type encoding: string
    
        @param caster: a caster instance that will transform arbitrary strings into
        python object
        @type caster: a spaceport.caster.Caster instance
        """
        self.schemaroot = schemaroot
        self.encoding = encoding
        self.caster = caster
        
        schema_fields = schemaroot.findall('fields/field')
        
        self.schema_fields = list()
        
        for field in schema_fields:
            type_node = field.find('type')
            type_dict = dict(name=type_node.text.lower().strip(),
                             items=dict(type_node.items()))
            
            field_dict = dict(name=field.get('name'),
                              type=type_dict,
                              index=int(field.find('source').text) - 1)
            
            if field_dict['name'] is None:
                msg = "Attribute name is missing from the field node"
                raise KeyError(msg)
            
            mandatory=field.get('mandatory')
            if not mandatory is None:
    
                if mandatory.lower() == 'false' or mandatory.lower() == 'no' \
                        or mandatory == '0':
                    field_dict['mandatory'] = False
    
                elif mandatory.lower() == 'true' or mandatory.lower() == 'yes' \
                        or mandatory == '1':
                    field_dict['mandatory'] = True
    
            else:
                msg = "Attribute 'mandatory' is missing from the field node %s" % \
                        field['name']
                raise KeyError(msg)
            
            length_node = field.find('length')
            if length_node is not None:
                field_dict['has_length'] = True
                field_dict['min_length'] = int(length_node.get('min') or 0)
                field_dict['max_length'] = int(length_node.get('max') or 0) or None
            else:
                field_dict['has_length'] = False
            
            self.schema_fields.append(field_dict)
            
    def create_item(self, row, record_num=None):
        """ creates an item from a row or record
    
        @param row: a csv row or dirtyxml record
        @type row: anything that can be accessed by index to retrieve fields
        """
        item = InputItem()
        encoding = self.encoding
        caster = self.caster
    
        for field in self.schema_fields:
            raw_value = row[field['index']]
    
            # check length if the node was present
            if field['has_length']:
                # max length is not always defined
                if field['max_length']:
                    if len(raw_value) > field['max_length']:
                        msg = "Object length %s is over Max length %s for field %s" % (
                                len(raw_value), field['max_length'], field['name'])
                        raise MaxLenError(msg)
    
                # min length is always defined with a default to 0
                if len(raw_value) < field['min_length']:
                    msg = "Object length %s is under Min length %s for field %s" % (
                            len(raw_value), field['min_length'], field['name'])
                    raise MinLenError(msg)
    
            if raw_value == '' and field['mandatory']:
                msg = 'Missing field or value: %s, record: %s' % (
                        field['name'], record_num or "unknown")
                raise MissingFieldError(msg)
    
            else:
                # set a py_value
                py_value = None
    
            if raw_value is None:
                unicode_value = None
            else:
                if isinstance(raw_value, unicode):
                    unicode_value = raw_value
                else:
                    unicode_value = raw_value.decode(encoding)
            try:
                py_value = caster.to_python(unicode_value, field['type'])

            except ValueError, e:
                # if field is not mandatory and value was blank,
                # then we have a already a py_value set to None
                # so we just let go of the exception
                if field['mandatory']:
                    raise ValueError('%s for field name: %s, record: %s' % (
                            e, field['name'], record_num or "unknown"))
    
            setattr(item, field['name'], py_value)
    
        return item

class InputDialect(csv.Dialect):
    """A subclass of the csv.Dialect class"""

    def __init__(self, delimiter):
        """@param delimiter: the character to be used as a delimiter
        @type delimiter: string
        """
        self.delimiter = delimiter
        self.doublequote = True
        # in python 2.4 this cannot be None
        self.escapechar = '\\'
        self.lineterminator = '\r\n'
        self.quotechar = '"'
        self.quoting = csv.QUOTE_ALL
        self.skipinitialspace = False

        csv.Dialect.__init__(self)

class CSVReader(object):
    """a reader that specializes in csv interpretation and
    reading.
    The csv reader will set a 'data_row__' attribute on the produced
    items for consumption by the splitter if you specify the keep_source_ref
    flag.
    """
    def __init__(self, encoding, schema_root, keep_source_ref=True):
        """@param encoding: the encoding that was declared by the stream in its
        header. This will be used by our readers to handle characters.
        @type encoding: string

        @param schema_root: the schema root node as it was read from the xml
        file by an ET.parse() call
        @type schema_root: a xml.etree.ElementTree

        @param keep_source_ref: a flag to specifie if a reference to the csv
        row should be kept. The default value is True. BatchSplitters should
        specify this flag to True in order to be able to access the data.
        In a near future the default value may become false as soon as all
        splitters have switched the flag to their preferred value.

        @type keep_source_ref: Boolean
        """
        self.encoding = encoding
        self.caster = Caster()
        self.schema_root = schema_root
        self.keep_source_ref = keep_source_ref
        
        self.item_factory = ItemFactory(self.schema_root, self.encoding, self.caster)

    def read(self, source):
        """A specialized reader that interprets csv files
        use the schema to read the given stream. Yields
        InputItem instances that can be consumed.

        The file must have been opened in binary mode because
        the underliying module for csv support is encoding and format
        agnostic and must be able to interpret carriage returns and line
        feeds.

        @param source: the file-like stream to process
        @type source: file like object
        """
        return self.__read(source)

    def __read(self, source):
        """produces an iterator for the csv reader

        @param source: the file-like to process, it must be opened
        in 'rb' mode
        @type source: open file object
        """
        separator = self.schema_root.find('header/format/delimiter').text
        startline = int(self.schema_root.find('header/format/startline').text)
        numcols = len(self.schema_root.findall('fields/field'))
        dialect = InputDialect(separator)

        csv_reader = csv.reader(source, dialect)

        for row_index, row in enumerate(csv_reader):
            #log.debug('reading %s %s' % (row, len(row)))
            if row_index+1 < startline:
                continue

            if len(row) == numcols:
                input_item = self.item_factory.create_item(row, record_num=row_index+1)

                if self.keep_source_ref:
                    # this is only used by the splitter
                    # no need to set this value in case we are
                    # not reading data for a splitter.
                    input_item.data_row__ = row

            else:
                msg = 'Line %s in source, as %s columns instead of %s' % (
                        row_index, len(row), numcols)
                if len(row) > numcols:
                    raise TooManyFieldsError(msg)
                else:
                    raise TooFewFieldsError(msg)

            yield input_item
            
    def get_record_count(self, source):
        count = 0
        for line in source:
            count += 1
        source.seek(0)
        return count


class DirtyXMLParser():
    """an pseudo xml parser that should be ultra resiliant.
    It parses some simple tag soup (<rc><it></it></rc> feeds) and does not care about
    the source encoding. In this parser everything is treated
    as bytes.
    The decoding to unicode must be performed by the implementor
    that will pick-up records.
    """

    def __init__(self):
        """create a dirty xml sax like parser that is somewhat
        resilient to really broken XML streams
        """
        self.records = list()
        self.remaining_data = ''

    def reset(self):
        """reset data to make sure the parser can be reused
        """
        self.records = list()
        self.remaining_data = ''

    def feed(self, data):
        """
        Checks for the last </rc> end tag in the data,
        feeds the content to the parser and add the object to the self.records list.
        Remaining parts (all if no </rc> is found) is kept in memory to be prepended on next pass.

        @param data: the chunk of stream to handle
        @type data: string
        """
        search_for = '</rc>'
        data = self.remaining_data + data
        last_rc = data.rfind(search_for)
        if not last_rc == -1:
            last_pos = last_rc + len(search_for)
            self.remaining_data = data[last_pos:]
            rc = SoupStrainer('rc')
            soup = BeautifulStoneSoup(data[:last_pos], convertEntities=None, parseOnlyThese=rc)
            for rc in soup:
                record = list()
                for it in rc('it'):
                    if it.string:
                        record_string = it.string.strip()
                        if record_string:
                            # We use the saxutils unescaper function, this is safe
                            # and handle all the entities, not just the named ones.
                            record.append(saxutils.unescape(record_string))
                        else:
                            record.append(None)
                    else:
                        record.append(None)
                self.records.append(record)
        else:
            self.remaining_data = data

    def finalize(self):
        """
        Function called whern the feed has ended. Does the checks to see that
        there is no important trailing data or raise an exception.
        """
        def remaining_stripper(remaining):
            remaining = remaining.strip()
            remaining = remaining.replace('</xml>', '')
            return remaining

        remaining = remaining_stripper(self.remaining_data)
        if remaining:
            if '<it>' in remaining or '<rc>' in remaining:
                raise RemainingDataError, '%s' % remaining
            else:
                pass
        else:
            pass

class FastMLParser():
    """a pseudo xml parser that should be fast, and specialised for <rc><it></it></rc> feeds.
    It parses some simple tag soup and does not care about
    the source encoding. In this parser everything is treated
    as bytes.
    The decoding to unicode must be performed by the implementor
    that will pick-up records.
    """

    def __init__(self):
        """create a dirty xml like parser that is very fast 
        """
        self.records = list()
        self.remaining_data = ''
        
        self.rc_re = re.compile('<rc>(.*?)</rc>', re.M | re.S | re.X)
        self.it_re = re.compile('<it>(.*?)</it>', re.M | re.S | re.X)

    def reset(self):
        """reset data to make sure the parser can be reused
        """
        self.records = list()
        self.remaining_data = ''

    def feed(self, data):
        """
        Checks for the last </rc> end tag in the data,
        feeds the content to the parser and add the object to the self.records list.
        Remaining parts (all if no </rc> is found) is kept in memory to be prepended on next pass.

        @param data: the chunk of stream to handle
        @type data: string
        """
        search_for = '</rc>'
        data = self.remaining_data + data
        last_rc = data.rfind(search_for)
        if not last_rc == -1:
            last_pos = last_rc + len(search_for)
            self.remaining_data = data[last_pos:]
            rcs = self.rc_re.findall(data[:last_pos])
            for rc in rcs:
                rc = rc.replace('<it />', '<it></it>')
                rc = rc.replace('<it/>', '<it></it>')
                its = self.it_re.findall(rc)
                
                record = list()
                for it in its:
                    record_string = it.strip()
                    if record_string:
                        record.append(record_string)
                    else:
                        record.append(None)
                self.records.append(record)
        else:
            self.remaining_data = data

    def finalize(self):
        """
        Function called whern the feed has ended. Does the checks to see that
        there is no important trailing data or raise an exception.
        """
        def remaining_stripper(remaining):
            remaining = remaining.strip()
            remaining = remaining.replace('</xml>', '')
            return remaining

        remaining = remaining_stripper(self.remaining_data)
        if remaining:
            if '<it>' in remaining or '<rc>' in remaining:
                raise RemainingDataError, '%s' % remaining
            else:
                pass
        else:
            pass

class DirtyXMLReader(object):
    """a reader that specializes in dirty xml (<rc><it></it></rc> feeds) interpretation and
    reading
    """
    def __init__(self, encoding, schema_root, buffersize=16384, mode="safe"):
        """@param encoding: the encoding that was declared by the stream in its
        header. This will be used by our readers to handle characters.
        @type encoding: string

        @param schema_root: the schema root node as it was read from the xml
        file by an ET.parse() call
        @type schema_root: a xml.etree.ElementTree

        @param buffersize: an optionnal buffer size to control how much data
        is read from the source and fed to the parser at once. The default
        value is 16384 which equals to 16k and should be left as-is.
        This keyword argument is mainly intended for unit-tester to be able
        to emulate large files by forcing the reader to yield some data before
        the parser as been fed the whole file.
        @type buffersize: integer
        
        @param mode: an optionnal mode to set the parser that should be used.
        @type mode: string (values: "safe" or "fast")
        """
        self.encoding = encoding
        self.buffersize = buffersize
        self.caster = Caster()
        self.schema_root = schema_root
        self.numcols = len(self.schema_root.findall('fields/field'))
        
        if mode == "fast":
            self.dirtyxmlparser = FastMLParser()
        else:
            self.dirtyxmlparser = DirtyXMLParser()
            
        self.item_factory = ItemFactory(self.schema_root, self.encoding, self.caster)

    def read(self, source):
        """A specialized reader that interprets dirty xml files from DECLEASE
        use the schema to read the given stream. Yields InputItem instances
        that can be consumed.

        @param source: the file-like stream to process
        @type source: file like object
        """
        return self.__read(source)

    def __read(self, source):
        """produces an iterator for the dirtyxml reader

        @param source: the file-like to process
        @type source: open file object
        """
        numcols = self.numcols
        data_available = True
        total_records = 0
        
        while data_available:
            # read data default is (16k by 16k) in memory to avoid saturation
            if hasattr(source, 'read'):
                data = source.read(self.buffersize)
            else:
                try:
                    data = source.next()
                except StopIteration:
                    data_available = False

            if len(data) == 0 or not data_available:
                # set flag to indicate the end of the while
                data_available = False
                self.dirtyxmlparser.finalize()

            else:
                # whatever the ampersand it should be encoded as a normal
                # entity, this way we will keep the original entities
                data = sub_ampersand.sub("&amp;", data)

                self.dirtyxmlparser.feed(data)

                for record in self.dirtyxmlparser.records:
                    total_records += 1

                    if len(record) == numcols:
                        input_item = self.item_factory.create_item(record,
                                record_num=total_records)

                    else:
                        msg = 'Record %s in source, as %s fields instead of %s' % (
                                total_records, len(record), numcols)
                        if len(record) > numcols:
                            raise TooManyFieldsError(msg)
                        else:
                            raise TooFewFieldsError(msg)

                    yield input_item

                # reset the records to empty list to avoid get the same next time
                self.dirtyxmlparser.records = list()
            
    def get_record_count(self, source):
        count = 0
        
        data_available = True
        while data_available:
            data = source.read(self.buffersize)
            if len(data) == 0:
                # set flag to indicate the end of the while
                data_available = False
                
            count += data.count('</rc>')
            
        source.seek(0)
        return count


class FixedLengthReader(object):
    """a reader that specializes in csv interpretation and
    reading.
    The csv reader will set a 'data_row__' attribute on the produced
    items for consumption by the splitter if you specify the keep_source_ref
    flag.
    """
    def __init__(self, encoding, schema_root, keep_source_ref=True):
        """@param encoding: the encoding that was declared by the stream in its
        header. This will be used by our readers to handle characters.
        @type encoding: string

        @param schema_root: the schema root node as it was read from the xml
        file by an ET.parse() call
        @type schema_root: a xml.etree.ElementTree

        @param keep_source_ref: a flag to specifie if a reference to the csv
        row should be kept. The default value is True. BatchSplitters should
        specify this flag to True in order to be able to access the data.
        In a near future the default value may become false as soon as all
        splitters have switched the flag to their preferred value.

        @type keep_source_ref: Boolean
        """
        self.encoding = encoding
        self.caster = Caster()
        self.schema_root = schema_root
        self.keep_source_ref = keep_source_ref
        
        log.debug('ItemFactory(%s, %s, %s)' % (
            self.schema_root,
            self.encoding,
            self.caster
        ))
        
        self.item_factory = ItemFactory(self.schema_root, self.encoding, self.caster)

    def read(self, source):
        """A specialized reader that interprets csv files
        use the schema to read the given stream. Yields
        InputItem instances that can be consumed.

        The file must have been opened in binary mode because
        the underliying module for csv support is encoding and format
        agnostic and must be able to interpret carriage returns and line
        feeds.

        @param source: the file-like stream to process
        @type source: file like object
        """
        return self.__read(source)

    def __read(self, source):
        """produces an iterator for the csv reader

        @param source: the file-like to process, it must be opened
        in 'rb' mode
        @type source: open file object
        """
        startline = int(self.schema_root.find('header/format/startline').text)
        numcols = len(self.schema_root.findall('fields/field'))
        fields = self.schema_root.findall('fields/field')
        lengths = list()
        for field in fields:
            length_node = field.find('length')
            if length_node.text:
                lengths.append(int(length_node.text))
            else:
                raise ValueError('Descriptor should have length info for fixed length reader')
        
        total_length=sum(lengths)
        #fixed_file = codecs.open(source, 'rb', self.encoding)
        
        for row_index, line in enumerate(source):
            #log.debug('reading %s %s' % (row, len(row)))
            if row_index+1 < startline:
                continue
            
            line = line.rstrip('\r\n')
            
            if len(line) == total_length:
                
                row = list()
                cur_pos = 0
                for length in lengths:
                    row.append(line[cur_pos:cur_pos+length].strip())
                    cur_pos += length
                
                input_item = self.item_factory.create_item(row, record_num=row_index+1)

                if self.keep_source_ref:
                    # this is only used by the splitter
                    # no need to set this value in case we are
                    # not reading data for a splitter.
                    input_item.data_row__ = row

            else:
                msg = 'Line %s in source, has %s characters instead of %s' % (
                        row_index, len(line), total_length)
                if len(line) > total_length:
                    raise MaxLenError(msg)
                else:
                    raise MinLenError(msg)

            yield input_item
            
    def get_record_count(self, source):
        count = 0
        for line in source:
            count += 1
        source.seek(0)
        return count