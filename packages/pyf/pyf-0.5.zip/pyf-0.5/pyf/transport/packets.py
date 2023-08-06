from simplejson.encoder import JSONEncoder
from simplejson import loads
import operator
import datetime
import decimal
from dateutil import parser as dateparser
from itertools import imap, izip

from pyf.splitter.inputsplitter import input_item_separator, tokenize,\
    EndOfFileError

class Packet(object):
    def __init__(self, data=None, data_type="simple"):
        super(Packet, self).__init__()
        
        if data is None:
            self.__data = dict()
        else:
            if data_type == "simple":
                self.__data = self.prepare_data_dict(data)
            elif data_type == "serialized":
                self.__data = self.unserialize_data_dict(data)
            elif data_type == "prepared":
                self.__data = data
            
        self.__initialised = True
        
    def itervalues(self):
        return imap(operator.itemgetter('value'), self.__data.itervalues())
    
    def iterkeys(self):
        return self.__data.iterkeys()
    __iter__ = iterkeys
            
    def iteritems(self):
        return izip(self.iterkeys(), self.itervalues())
    
    def keys(self):
        return list(self.iterkeys())
    
    properties = property(keys)
    
    def values(self):
        return list(self.itervalues())
    
    def prepare_data_dict(self, data):
        data_dict = dict()
        for key, value in data.iteritems():
            value, metas = self.__get_bare_metadata(value)
            
            data_dict[key] = dict(value = value,
                                  metadata = metas)
        return data_dict
    
    def unserialize_data_dict(self, data):
        data_dict = dict()
        for key, value_dict in data.iteritems():
            metadata = value_dict.get('metadata', dict())
            value = value_dict.get('value')
            
            value = self.unserialize_value(value, metadata)
                
            data_dict[key] = dict(value = value,
                                  metadata = self.__get_bare_metadata(value))
        return data_dict
                
    def __setitem__(self, attribute, value):
        self.__data[attribute] = dict()
        self.__data[attribute]['metadata'] = dict()
        self.__data[attribute]['value'] = value
        
        self.__generate_bare_metadata(attribute)
                
    def __setattr__(self, attribute, value):
        if not self.__dict__.has_key('_Packet__initialised'):
            return object.__setattr__(self, attribute, value)
        elif self.__dict__.has_key(attribute):
            object.__setattr__(self, attribute, value)
        else:
            self.__setitem__(attribute, value)
    
    def __generate_bare_metadata(self, field):
        value = self.__data[field]['value']
        value, metas = self.__get_bare_metadata(value)
        self.__data[field]['value'] = value
        for key, value in metas.iteritems():
            self.set_metadata(field, key, value)
        
    def __get_bare_metadata(self, value):
        metas = dict()
        
        metas['multi_values'] = False
        metas['compound'] = False
        
        if isinstance(value, str) or isinstance(value, unicode):
            metas['type'] = 'string'
        elif isinstance(value, datetime.datetime):
            metas['type'] = 'datetime'
        elif isinstance(value, decimal.Decimal):
            metas['type'] = 'decimal'
        elif isinstance(value, datetime.date):
            metas['type'] = 'date'
        elif isinstance(value, list):
            metas['multi_values'] = True
            metas['type'] = 'unknown'
            
        elif isinstance(value, dict):
            metas['multi_values'] = True
            metas['compound'] = True
            metas['type'] = 'packet'
            value = Packet(value, data_type="simple")
            
        elif isinstance(value, Packet):
            metas['multi_values'] = True
            metas['compound'] = True
            metas['type'] = 'packet'
        
        else:
            metas['type'] = 'unknown'
            
        return value, metas
    
    def __hasattr__(self, attribute):
        return bool(attribute in self.__data) or bool(attribute in self.__dict__)
    
    def __getitem__(self, attribute):
        return self.__getattr__(attribute)
    
    def get(self, key, default=None):
        return self.__data.get(key, dict()).get('value', default)
    
    def __getattr__(self, attribute):
        if not attribute in self.__data:
            raise AttributeError, "'packet' object has no attribute '%s'" % attribute
        
        return self.__data[attribute].get('value')
    
    def __delitem__(self, key):
        del self.__data['key']
        
    def set_metadata(self, field, key, value):
        self.__data[field]['metadata'][key] = value
        
    def get_metadata(self, field, key=None):
        if key is not None:
            return self.__data[field].get('metadata', dict()).get(key)
        else:
            return self.__data[field].get('metadata', dict())
    
    def serialize_value(self, value, metadata):
        if metadata['type'] == 'date':
            value = value.isoformat()
        elif metadata['type'] == 'datetime':
            value = value.isoformat('T')
        elif metadata['type'] == 'decimal':
            value = str(value)
        elif metadata['type'] == 'packet':
            value = value.serialized
        elif metadata['multi_values']:
            md = metadata.copy()
            md['multi_values'] = False
            value = [self.serialize_value(oneval, md) for oneval in value]
            
        elif metadata['type'] == 'unknown':
            # do some guessing work there, just in case...
            found = True
            
            if isinstance(value, datetime.date):
                metadata['type'] = 'date'
            elif isinstance(value, datetime.datetime):
                metadata['type'] = 'datetime'
            else:
                found = False
                
            if found:
                # if we found a simple 
                return self.serialize_value(value, metadata)
        
        return dict(value=value, metadata=metadata)
    
    def unserialize_value(self, value, metadata):
        if metadata['type'] == 'date':
            value = dateparser.parse(value).date()
        elif metadata['type'] == 'datetime':
            value = dateparser.parse(value)
        elif metadata['type'] == 'decimal':
            value = decimal.Decimal(value)
        elif metadata['type'] == 'packet':
            value = Packet(value, data_type="serialized")
        elif metadata.get('multi_values', False):
            value = [self.unserialize_value(val.get('value'),
                                            val.get('metadata'))\
                     for val in value]
            
        return value
    
    @property
    def serialized(self):
        output_dict = dict()
        for key, key_dict in self.__data.iteritems():
            value = key_dict['value']
            metadata = key_dict['metadata']
            value = self.serialize_value(value, metadata)
            output_dict[key] = value
        
        return output_dict
    
    def __str__(self):
        return str(dict(self.iteritems()))
    
    def __repr__(self):
        return repr(dict(self.iteritems()))
    
    def __contains(self, key):
        return bool(key in self.__data)
                
    
class PacketEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Packet) or hasattr(o, 'serialized'):
            return o.serialized
            
        return JSONEncoder.default(self, o)
    
def encode_packet_flow(object_flow,
                       separator=input_item_separator,
                       iterencode=False,
                       compress=False):
    encoder = PacketEncoder()
    for i, o in enumerate(object_flow):
        if iterencode:
            if compress:
                raise NotImplementedError,\
                      "Can't use iterencode with compress in encode_packet_flow"
            
            for chars in encoder.iterencode(o):
                yield chars
                
        else:
            val = encoder.encode(o)
            if compress:
                import zlib
                val = zlib.compress(val)
            
            yield val
        
        yield separator

def decode_packet_flow(source, buffersize=16384,
                       separator=input_item_separator,
                       decompress=False):
    buffer = ""
    
    newdata = "dummy"
    while newdata:
        if hasattr(source, 'read'):
            newdata = source.read(buffersize)
        else:
            try:
                newdata = source.next()
            except StopIteration:
                newdata = ""
                
        buffer += newdata
        items, buffer = tokenize(buffer, separator)
        for item in items:
            if decompress:
                import zlib
                item = zlib.decompress(item)
                
            yield Packet(data=loads(item), data_type="serialized")

    if buffer:
        raise EndOfFileError(
                'Bad file content: EOF reached but buffer not empty')