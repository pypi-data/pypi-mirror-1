"""the Descriptor implementation. A descriptor maintains information
about a file or flow and provides the necessary method to iterate over
the flow and return InputItems to be used in the rest of the process
"""
import logging
from pyjon.descriptors.readers import CSVReader, DirtyXMLReader, FixedLengthReader

import logging

log = logging.getLogger(__name__)

class Descriptor(object):
    """a Descriptor object uses a schema to read a stream of file
    it will then yield InputItem instances that can be consumed
    by the internal parts of spaceport
    """
    def __init__(self, payload_tree, encoding, buffersize=16384):
        """@param payload_tree: the descriptor schema as an ElementTree instance
        @type payload_tree: ET.ElementTree instance

        @param encoding: the encoding of the stream to read (ie: 'utf-8')
        @type encoding: string

        @param buffersize: the desired size in bytes of the read buffer.
        This parameter will be ignored for csv readers and will be passed
        down to readers that implement their own buffering
        (DirtyXMLReader at the moment).
        This is an optionnal argument and will default to 16384.
        @type buffersize: integer
        """
        self.schema_root = payload_tree
        self.input_type = self.schema_root.find('header/format').get('name')
        reader_mode = self.schema_root.find('header/format').get('mode')

        if reader_mode is None:
            reader_mode = 'safe'

        if not (reader_mode == 'safe' or reader_mode == 'fast'):
            msg = 'the descriptor mode should be either'
            msg += ' fast or safe, not %s' % reader_mode
            raise ValueError(msg)

        if self.input_type == 'csv':
            # we need a reader attribute, always :)
            log.debug("Starting CSVReader")
            self.reader = CSVReader(encoding, self.schema_root)
        
        elif self.input_type == 'fixedlength':
            self.reader = FixedLengthReader(encoding, self.schema_root)

        elif self.input_type == 'dirtyxml':
            if reader_mode == 'safe':
                log.debug("Starting DirtyXMLReader in safe mode")
                self.reader = DirtyXMLReader(encoding, self.schema_root,
                        buffersize=buffersize)
            else:
                log.debug("Starting DirtyXMLReader in fast mode")
                self.reader = DirtyXMLReader(encoding, self.schema_root,
                        buffersize=buffersize, mode='fast')

        else:
            msg = "The input type: '%s' " % self.input_type
            msg += "of this descriptor schema is unknown"
            log.error(msg)
            raise ValueError('unsupported input type: %s' % self.input_type)

    def read(self, source):
        """reads the source and returns InputItems instances
        @param source: the source stream to read from
        @type source: a file like object
        """
        return self.__read(source)

    def __read(self, source):
        """the generator that yields items for real
        @param source: the source stream to read from
        @type source: a file like object
        """
        items = self.reader.read(source)
        for item in items:
            yield item
            
    def get_record_count(self, source):
        """ asks the reader to pre-read the file to get the record count.
        Then, it does a seek(0) on the file to give a fresh file """
        if hasattr(self.reader, 'get_record_count'):
            return self.reader.get_record_count(source)
        else:
            return None

