import os
import sys
import struct
import socket
import traceback
from time import mktime
from copy import deepcopy
from select import select
from warnings import warn
from threading import RLock
from datetime import datetime
from StringIO import StringIO
from SocketServer import TCPServer, UDPServer, StreamRequestHandler, DatagramRequestHandler

PROTLIB_DEFAULT_TIMEOUT = 5
if socket.getdefaulttimeout() is None:
    socket.setdefaulttimeout(PROTLIB_DEFAULT_TIMEOUT)

BYTE_ORDER = "!"

def get_default(val):
    return val() if hasattr(val, "__call__") else deepcopy(val)

def fileize(x):
    return StringIO(x) if isinstance(x, basestring) else x

class CError(Exception): pass
class CWarning(Warning): pass

class CType(object):
    instances = []
    
    def __init__(self, **settings):
        self.always = self.default = self.length = None
        extra = [name for name,val in settings.items() if not hasattr(self, name)]
        if extra:
            warn("{0} settings do not include {1}".format(self.__class__.__name__, ", ".join(extra)), CWarning)
        
        self.__dict__.update(settings)
        if self.length is not None and not isinstance(self, (CString, CArray)):
            warn("length has no meaning for {0} objects".format(self.__class__.__name__), CWarning)
        if isinstance(self, CString) and (not isinstance(self.length, int) or self.length <= 0):
            raise CError("CString objects require a length attribute")
        if self.__class__ is CType:
            raise CError("CType may not be directly instantiated; use a subclass such as CInt, CString, etc")
        
        self.instances.append(self)
    
    @property
    def struct_format(self):
        return {
            "CChar":   "b",
            "CUChar":  "B",
            "CShort":  "h",
            "CUShort": "H",
            "CInt":    "i",
            "CUInt":   "I",
            "CLong":   "l",
            "CULong":  "L",
            "CFloat":  "f",
            "CDouble": "d",
            "CString": "{0}s".format(self.length)
        }[self.__class__.__name__]
    
    @property
    def sizeof(self):
        return struct.calcsize(BYTE_ORDER + self.struct_format)
    
    def parse(self, f):
        buf = fileize(f).read(self.sizeof)
        val = struct.unpack(BYTE_ORDER + self.struct_format, buf)[0]
        return val.rstrip("\x00") if isinstance(val, str) else val
    
    def serialize(self, val):
        return struct.pack(BYTE_ORDER + self.struct_format, val)

class CChar(CType): pass
class CUChar(CType): pass
class CShort(CType): pass
class CUShort(CType): pass
class CInt(CType): pass
class CUInt(CType): pass
class CLong(CType): pass
class CULong(CType): pass
class CFloat(CType): pass
class CDouble(CType): pass
class CString(CType): pass

class CArray(CType):
    def __init__(self, length, ctype, **params):
        if type(ctype) is type and issubclass(ctype, CType):    # CArray(10, CInt) and CArray(10, CInt()) are both allowed
            if issubclass(ctype, CStruct):                      # CArray(10, MyStruct) and CArray(10, MyStruct.get_type()) are both allowed
                ctype = ctype.get_type()
            else:
                ctype = ctype()
        
        if not isinstance(ctype, CType):
            raise CError("Second argument to CArray must be a CType e.g. CInt, CFloat, etc")
        elif isinstance(ctype, CStruct):
            ctype = ctype.__class__
            warn("Second argument to CArray should just be the class {0} rather than an instance of that class".format(ctype.__name__), CWarning)
        
        self.ctype = ctype
        
        for param in ["default","always"]:
            if param not in params and getattr(self.ctype, param, None) is not None:
                params[param] = [get_default(getattr(self.ctype, param)) for i in range(length)]
        
        CType.__init__(self, length=length, **params)
    
    @property
    def struct_format(self):
        return self.ctype.struct_format * self.length
    
    def parse(self, f):
        f = fileize(f)
        return [self.ctype.parse(f) for i in range(self.length)]
    
    def serialize(self, xs):
        if len(xs) > self.length:
            warn("CArray has length {0} and but was given {1} elements".format(self.length, len(xs)), CWarning)
        elif len(xs) < self.length:
            if self.default is None:
                raise CError("CArray has length {0} and was only given {1} elements".format(self.length, len(xs)))
            else:
                xs = xs + self.default[len(xs):]    # avoid += to not mutate the original list
        return "".join(self.ctype.serialize(x) for x in xs)

class CStructType(CType):
    def __init__(self, subclass, **params):
        self.subclass = subclass
        CType.__init__(self, **params)
    
    @property
    def struct_format(self):
        return "".join(ctype.struct_format for name,ctype in self.subclass.get_fields())
    
    def parse(self, f):
        buf = fileize(f).read(self.sizeof)
        f = StringIO(buf)
        if len(buf) < self.sizeof:
            raise CError("{0} requires {1} bytes and was only given {2} ({3!r})".format(self.subclass.__name__, self.sizeof, len(buf), buf))
        
        params = {}
        for name,ctype in self.subclass.get_fields():
            val = ctype.parse(f)
            params[name] = val
            if ctype.always is not None and ctype.always != val:
                warn("{0} should always be {1}".format(name, ctype.always), CWarning)
        return self.subclass(**params)
    
    def serialize(self, inst):
        serialized = ""
        for name,ctype in self.subclass.get_fields():
            val = getattr(inst, name, None)
            if val is None or isinstance(val, CType) and not isinstance(val, CStruct):
                raise CError(name + " not set")
            elif ctype.always is not None and ctype.always != val:
                warn("{0} should always be {1}".format(name, ctype.always), CWarning)
            serialized += ctype.serialize(val)
        return serialized

class CStruct(CType):
    def __init__(self, *args, **values):
        if self.__class__ is CStruct:
            raise CError("CStruct may not be instantiated directly; define a subclass instead")
        
        fields = self.get_fields()
        if not fields:
            raise CError("{0} struct contains no CType fields".format(self.__class__.__name__))
        
        field_names = zip(*fields)[0]
        for i,arg in enumerate(args):
            name = field_names[i]
            if name in values and values[name] != arg:
                raise CError("{0} was given a value of {1!r} as a positional argument and {2!r} as a keyword argument".format(name, arg, values[name]))
            values[name] = arg
        
        non_fields = [name for name,value in values.items() if name not in field_names]
        if non_fields:
            warn("{0} fields ({1}) do not include {2}".format(self.__class__.__name__, ", ".join(field_names), ", ".join(non_fields)), CWarning)
        
        for name,ctype in fields:
            maybe = ctype.always if ctype.always is not None else ctype.default
            if maybe is not None:
                setattr(self, name, get_default(maybe))
        self.__dict__.update(values)
    
    @classmethod
    def get_fields(cls):
        if "_fields" not in cls.__dict__:   # avoid hasattr because of subclasses
            uninstantiated = [ctype for name,ctype in cls.__dict__.items() 
                                    if type(ctype) is type and issubclass(ctype,CType)]
            if uninstantiated:
                raise CError("Use {0}{2} instead of {0} when declaring a field in your {1} struct".format(uninstantiated[0].__name__, cls.__name__, ".get_type()" if issubclass(uninstantiated[0],CStruct) else "()"))
            
            directly = [cstruct for name,cstruct in cls.__dict__.items() 
                                if isinstance(cstruct, CStruct)]
            if directly:
                raise CError("Use {0}.get_type() instead of {0}() when declaring a field in your {1} struct".format(directly[0].__class__.__name__, cls.__name__))
            
            top = cls
            while CStruct not in top.__bases__:
                for base in top.__bases__:
                    if issubclass(top, CStruct):
                        top = base
                    break
            
            if top is cls:
                fields = [[name,ctype] for name,ctype in cls.__dict__.items() 
                                       if isinstance(ctype, CType)]
                fields.sort(key = lambda pair: CType.instances.index(pair[1]))
                
                positions = [(CType.instances.index(ctype),name,ctype) for name,ctype in fields]
                for i in range(1, len(positions)):
                    if positions[i][0] == positions[i-1][0]:
                        warn("{0} and {1} were declared with the same {2} object; the order of such fields is undefined".format(positions[i-1][1], positions[i][1], positions[i][2].__class__.__name__), CWarning)
                        break
            else:
                fields = deepcopy( top.get_fields() )
                for pair in fields:
                    final = getattr(cls, pair[0])
                    if not isinstance(final, CType):
                        raise CError("{0} field overridden by non-CType {1!r}".format(pair[0], final))
                    elif final.sizeof != pair[1].sizeof:
                        raise CError("{0[0]} field of type {0[1]} was overridden by differently-sized type {1}".format(pair, final.__class__.__name__))
                    pair[1] = final
            
            cls._fields = fields
        return cls._fields
    
    @classmethod
    def get_type(cls, cached=False, **params):
        if not ("_type" in cls.__dict__ and cached):    # avoid hasattr because of subclasses
            cls._type = [CStructType(cls, **params)]    # stored in a list so that isinstance(self._type, CType) will evaluate to false
        return cls._type[0]
    
    @classmethod
    def parse(cls, f):
        return cls.get_type(cached=True).parse(f)
    
    @classmethod
    def sizeof(cls):
        return cls.get_type(cached=True).sizeof
    
    @classmethod
    def struct_format(cls):
        return cls.get_type(cached=True).struct_format
    
    def serialize(self):
        return self.get_type(cached=True).serialize(self)
    
    @property
    def hashable(self):
        if not hasattr(self, "_hashable"):
            xs = [getattr(self, name, None) for name,ctype in self.get_fields()]
            self._hashable = tuple(tuple(x) if isinstance(x, list) else x for x in xs)
        return self._hashable
    def __hash__(self):
        return hash(self.hashable)
    def __eq__(self, other):
        return self.hashable == getattr(other, "hashable", None)
    def __ne__(self, other):
        return not (self == other)  # Python is stupid for making me do this
    
    def __repr__(self):
        params = ["{0}={1!r}".format(name, getattr(self,name))
                  for name,ctype in self.get_fields() if hasattr(self,name)]
        return "{0}({1})".format(self.__class__.__name__, ", ".join(params))
    
    __str__ = serialize
    def __getitem__(self, key):
        return self.serialize()[key]



def underscorize(camelcased):
    underscored, prev = "", ""
    for i,c in enumerate(camelcased):
        if (prev and not c.islower() and c != "_"
                 and (prev.islower() and not c.isdigit() 
                      or c.isupper() and camelcased[i+1:i+2].islower())):
            underscored += "_"
        underscored += c.lower()
        prev = c
    return underscored

def hexdump(data):
    hexed = [hex(ord(char))[2:].rjust(2,"0") for char in data]
    lines = ["     0  1  2  3  4  5  6  7"]
    for i in range(0, len(hexed), 8):
        lines.append("%3i  " % i + " ".join(hexed[i:i+8]))
    return "\n".join(lines)

class Parser(object):
    def __init__(self, module=None, logger=None):
        self.logger = logger
        
        if not module:
            globs = sys._getframe().f_back.f_globals
        else:
            if isinstance(module, basestring):
                module = __import__(module)
            globs = module.__dict__
        
        self.structs = [cstruct for name,cstruct in globs.items()
                        if type(cstruct) is type and issubclass(cstruct,CStruct) and cstruct is not CStruct]
        self.codes = []
        for cstruct in self.structs:
            first = cstruct.get_fields()[0][1]
            if first.always is not None:
                self.codes.append( (first.serialize(first.always), cstruct) )
        self.codes.sort(key = lambda code: len(code[0]))
        if not self.codes:
            raise CError("No structs defined in module " + (module.__name__ if module else "where you instantiated Parser"))
        
        bufs = zip(*self.codes)[0]
        while bufs:
            matches = [b for b in bufs if bufs[0] == b[:len(bufs[0])]]
            if len(matches) > 1:
                structs = ", ".join(cstruct.__name__ for buf,cstruct in self.codes if buf in matches)
                warn("{0} structs exist which always begin with {1!r}: {2}".format(len(matches), bufs[0], structs), CWarning)
            bufs = [b for b in bufs if b not in matches]
    
    def parse(self, f):
        f = fileize(f)
        buf = ""
        for code,cstruct in self.codes:
            diff = len(code) - len(buf)
            if diff:
                buf += f.read(diff)
                if len(buf) < len(code):
                    return buf
            
            if code == buf:
                bufsize = cstruct.sizeof()
                buf += f.read(bufsize - len(buf))
                if self.logger:
                    self.logger.log_raw(buf, "received")
                
                if len(buf) < bufsize:
                    if self.logger:
                        self.logger.log_error("{0} struct requires {1} bytes, received {2} ({3!r})", cstruct.__name__, bufsize, len(buf), buf)
                    return
                else:
                    inst = cstruct.parse(buf)
                    if self.logger:
                        self.logger.log_struct(inst, "received")
                    return inst
        
        return buf + f.read()

class Logger(object):
    LOG_LOCK = RLock()
    LOGS = ["struct_log","raw_log","error_log","stack_log"]
    
    def __init__(self, log_dir=".", hex_logging=False, also_print=False, suppress_logging=False):
        self.also_print = also_print
        self.hex_logging = hex_logging
        for log in self.LOGS:
            if suppress_logging:
                setattr(self, log, StringIO())
            else:
                fname = os.path.join(log_dir, sys.argv[0].split(".")[0] + "." + log)
                setattr(self, log, open(fname,"a"))
    
    def log_raw(self, data, trans_type="received"):
        message = trans_type + " " + repr(data)
        if self.hex_logging:
            message += "\n" + hexdump(data)
        self.log("raw_log", message)
    
    def log_struct(self, inst, trans_type="received"):
        self.log("struct_log", trans_type + " " + repr(inst))
    
    def log_stacktrace(self):
        self.log("stack_log", traceback.format_exc())
    
    def log_error(self, message, *args, **kwargs):
        self.log("error_log", message.format(*args, **kwargs))
    
    def log_and_write(self, f, inst):
        raw = inst.serialize()
        self.log_struct(inst, "sending")
        self.log_raw(raw, "sending")
        f.write(raw)
    
    def log(self, log_name, message):
        message = "{0}: {1}".format(datetime.now(), message)
        with self.LOG_LOCK:
            try:
                getattr(self, log_name).write(message + "\n")
                getattr(self, log_name).flush()
                if self.also_print:
                    print(message)
            except:
                traceback.print_exc()

class ProtHandler(Logger):
    LOG_DIR = "."
    HEX_LOGGING = LOG_TO_SCREEN = STRUCT_MOD = False
    
    def __init__(self, server=None):
        Logger.__init__(self, log_dir=self.LOG_DIR, hex_logging=self.HEX_LOGGING, also_print=self.LOG_TO_SCREEN,
                        suppress_logging = server.__class__ not in [LoggingTCPServer, LoggingUDPServer])
        self.parser = Parser(logger=self, module=self.STRUCT_MOD or self.__class__.__module__)
        
        for buf,cstruct in self.parser.codes:
            if underscorize(cstruct.__name__) in dir(TCPHandler):
                raise CError("You can't name your struct {0} because that's also the name of a standard handler method".format(cstruct.__name__))
        
        self.handled = 0
        self.prefix = int(mktime( datetime.now().timetuple() ))
    
    def log(self, log_name, message):
        message = "({0}_{1}) {2}".format(self.prefix, self.handled, message)
        Logger.log(self, log_name, message)
    
    def dispatch(self, data):
        if isinstance(data, basestring):
            return self.raw_data(data)
        
        codename = underscorize(data.__class__.__name__)
        if not hasattr(self, codename):
            self.log_error("{0} handler not defined", codename)
        else:
            return getattr(self, codename)(data)
    
    def reply(self, data):
        if isinstance(data, CStruct):
            self.log_struct(data, "sending")
            data = data.serialize()
        self.log_raw(data, "sending")
        self.wfile.write(data)
        self.wfile.flush()
    
    def raw_data(self, data):
        if data:
            self.log_error("unable to resolve {0!r} to a struct", data)
    
    def handle(self, only_one=False):
        try:
            data = self.parser.parse(self)
            while data:
                response = self.dispatch(data)
                if response:
                    self.reply(response)
                
                self.handled += 1
                if only_one:
                    break
                data = self.parser.parse(self)
        except:
            self.log_stacktrace()

class TCPHandler(ProtHandler, StreamRequestHandler):
    def __init__(self, request, client_addr, server):
        ProtHandler.__init__(self, server)
        StreamRequestHandler.__init__(self, request, client_addr, server)
    
    def read(self, n=None):
        buf = ""
        while True:
            r,w,exc = select([self.rfile], [], [], socket.getdefaulttimeout() or PROTLIB_DEFAULT_TIMEOUT)
            c = r[0].read(1) if r else ""
            buf += c    # shlemiel the painter
            if not r or not c or n and len(buf) >= n:
                break
        return buf

class UDPHandler(ProtHandler, DatagramRequestHandler):
    def __init__(self, request, client_addr, server):
        ProtHandler.__init__(self, server)
        DatagramRequestHandler.__init__(self, request, client_addr, server)
    
    def read(self, n=-1):
        return self.rfile.read(n)

class LoggingUDPServer(UDPServer):
    allow_reuse_address = True

class LoggingTCPServer(TCPServer):
    allow_reuse_address = True
