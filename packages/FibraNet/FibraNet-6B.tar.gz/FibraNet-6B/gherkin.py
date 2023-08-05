from types import IntType,TupleType,StringType,FloatType,LongType,ListType,DictType,NoneType,BooleanType,UnicodeType

from struct import pack, unpack
from cStringIO import StringIO

SIZEOF_INT = 4
SIZEOF_FLOAT = 8
UNICODE_CODEC = 'utf-8'

def memoize(func):
    cache = {}
    def check_memo(*args):
        if args in cache:
            return cache[args]
        else:
            return cache.setdefault(args, func(*args))
    return check_memo

class Gherkin(object):
    def __init__(self):
        self.strings = {}
        self.header = 'GHE'
        self.version = 0
        self.protocol = {
            TupleType:"T",
            ListType:"L",
            DictType:"D",
            LongType:"B",
            IntType:"I",
            FloatType:"F",
            StringType:"S",
            NoneType:"N",
            BooleanType:"b",
            UnicodeType:"U"
        }

        self.int_size = SIZEOF_INT
        self.float_size = SIZEOF_FLOAT

        self.encoder = {
            DictType:self.enc_dict_type,
            ListType:self.enc_list_type,
            TupleType:self.enc_list_type,
            IntType:memoize(self.enc_int_type),
            FloatType:memoize(self.enc_float_type),
            LongType:memoize(self.enc_long_type),
            UnicodeType:memoize(self.enc_unicode_type),
            StringType:memoize(self.enc_string_type),
            NoneType:self.enc_none_type,
            BooleanType:memoize(self.enc_bool_type)
        }

        self.decoder = {
            self.protocol[TupleType]:self.dec_tuple_type,
            self.protocol[ListType]:self.dec_list_type,
            self.protocol[DictType]:self.dec_dict_type,
            self.protocol[LongType]:self.dec_long_type,
            self.protocol[StringType]:self.dec_string_type,
            self.protocol[FloatType]:self.dec_float_type,
            self.protocol[IntType]:self.dec_int_type,
            self.protocol[NoneType]:self.dec_none_type,
            self.protocol[BooleanType]:self.dec_bool_type,
            self.protocol[UnicodeType]:self.dec_unicode_type
        }

    def enc_dict_type(self, obj):
        data = "".join([self.encoder[type(i)](i) for i in obj.items()])
        return "%s%s%s" % (self.protocol[DictType], pack("!L", len(data)), data)

    def enc_list_type(self, obj):
        data = "".join([self.encoder[type(i)](i) for i in obj])
        return "%s%s%s" % (self.protocol[type(obj)], pack("!L", len(data)), data)

    def enc_int_type(self, obj):
        return "%s%s" % (self.protocol[IntType], pack("!i", obj))

    def enc_float_type(self, obj):
        return "%s%s" % (self.protocol[FloatType], pack("!d", obj))

    def enc_long_type(self, obj):
        obj = hex(obj)
        if obj[0] == "-":
            pre = "-"
            obj = obj[3:-1]
        else:
            pre = "+"
            obj = obj[2:-1]
        return "%s%s%s%s" % (self.protocol[LongType], pre, pack("!L", len(obj)), obj)

    def enc_unicode_type(self, obj):
        obj = obj.encode(UNICODE_CODEC)
        return "%s%s%s" % (self.protocol[UnicodeType], pack("!L", len(obj)), obj)

    def enc_string_type(self, obj):
        return "%s%s%s" % (self.protocol[StringType], pack("!L", len(obj)), obj)

    def enc_none_type(self, obj):
        return self.protocol[NoneType]

    def enc_bool_type(self, obj):
        return self.protocol[BooleanType] + str(int(obj))

    def dumps(self, obj):
        """
        Return the string that would be written to a file by dump(value, file). The value must be a supported type. Raise a ValueError exception if value has (or contains an object that has) an unsupported type.
        """
        options = "".join((hex(self.version)[2:],hex(SIZEOF_INT)[2:],hex(SIZEOF_FLOAT)[2:]))
        assert len(options) == 3
        try:
            data = self.encoder[type(obj)](obj)
        except KeyError, e:
            raise ValueError, "Type not supported. (%s)" % e
        header = "".join((self.header, options))
        assert len(header) == 6
        return "".join((header, data))

    def dump(self, obj, file):
        """
        Write the value on the open file. The value must be a supported type. The file must be an open file object such as sys.stdout or returned by open() or posix.popen(). It must be opened in binary mode ('wb' or 'w+b').
        If the value has (or contains an object that has) an unsupported type, a ValueError exception is raised
        """
        return file.write(self.dumps(obj))

    def build_sequence(self, data, cast=list):
        size = unpack('!L', data.read(SIZEOF_INT))[0]
        items = []
        data_tell = data.tell
        items_append = items.append
        self_decoder = self.decoder
        data_read = data.read
        start_position = data.tell()
        while (data_tell() - start_position) < size:
            T = data_read(1)
            value = self_decoder[T](data)
            items_append(value)
        return cast(items)

    def dec_tuple_type(self, data):
        return self.build_sequence(data, cast=tuple)

    def dec_list_type(self, data):
        return self.build_sequence(data, cast=list)

    def dec_dict_type(self, data):
        return self.build_sequence(data, cast=dict)

    def dec_long_type(self, data):
        pre = data.read(1)
        size = unpack('!L', data.read(self.int_size))[0]
        value = long(data.read(size),16)
        if pre == "-": value = -value
        return value

    def dec_string_type(self, data):
        size = unpack('!L', data.read(self.int_size))[0]
        value = str(data.read(size))
        return value

    def dec_float_type(self, data):
        value = unpack('!d', data.read(self.float_size))[0]
        return value

    def dec_int_type(self, data):
        value = unpack('!i', data.read(self.int_size))[0]
        return value

    def dec_none_type(self, data):
        return None

    def dec_bool_type(self, data):
        value = int(data.read(1))
        return bool(value)

    def dec_unicode_type(self, data):
        size = unpack('!L', data.read(self.int_size))[0]
        value = data.read(size).decode(UNICODE_CODEC)
        return value

    def loads(self, data):
        """
        Convert the string to a value. If no valid value is found, raise EOFError, ValueError or TypeError. Extra characters in the string are ignored.
        """
        self.strings = {}
        buffer = StringIO(data)
        header = buffer.read(len(self.header))
        assert header == self.header
        self.version = int(buffer.read(1), 10)
        self.int_size = int(buffer.read(1), 10)
        self.float_size = int(buffer.read(1), 10)
        try:
            value = self.decoder[buffer.read(1)](buffer)
        except KeyError, e:
            raise ValueError, "Type prefix not supported. (%s)" % e
        return value

    def load(self, file):
        """
        Read one value from the open file and return it. If no valid value is read, raise EOFError, ValueError or TypeError. The file must be an open file object opened in binary mode ('rb' or 'r+b').
        """
        return self.loads(file.read())


__gherk = Gherkin()
dumps = __gherk.dumps
loads = __gherk.loads
dump = __gherk.dump
load = __gherk.load

if __name__ == "__main__":
    def test():
        import time
        alist = []
        value = 1000,-1000,34444444444444444444444444444444444444444,-33333333333333333333333333333334444444444444,3.14,"test string",-22.7332342,{1:2,3:"x"},(1,2,[3,4])
        print "Data (x100000):", value
        value = value * 100
        t = time.clock()
        data = dumps(value)
        print "Dump time:", time.clock() - t
        print "Dump size:", len(data)
        t = time.clock()
        new_value = loads(data)
        print "Load time:", time.clock() - t
        assert value == new_value
    test()


