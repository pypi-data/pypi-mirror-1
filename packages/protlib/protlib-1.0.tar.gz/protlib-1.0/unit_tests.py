from protlib import *

import os
from glob import glob
from time import sleep
from threading import Thread

import unittest
from unittest import TestCase

import warnings
warnings.simplefilter("error", CWarning)

socket.setdefaulttimeout(0.1)

class NamedPoint(CStruct):
    code = CShort(always = 0x1234)
    x    = CInt()
    y    = CInt()
    name = CString(length=15, default="unnamed")
NP_BUF = "\x124\x00\x00\x00\x05\x00\x00\x00\x06unnamed\x00\x00\x00\x00\x00\x00\x00\x00"

class RenamedPoint(NamedPoint):
    code = CShort(always = 0x4321)

class NamedOrigin(NamedPoint):
    y = CInt(always = 0)            # field order can be different in subclasses
    code = CShort(always = 0x2332)
    x = CInt(always = 0)

SERVER_ADDR = ("127.0.0.1", 7357)
CLIENT_ADDR = ("127.0.0.1", 5737)

class TestHandler(object):
    def named_point(self, np):
        return RenamedPoint(x=np.x, y=np.y)
    
    def renamed_point(self, rp):
        return "Hello World!\n"

class TCPTestHandler(TCPHandler, TestHandler): pass
class UDPTestHandler(UDPHandler, TestHandler): pass

class CTypeTests(TestCase):
    def test_valid_basic(self):
        for always in [None, 5]:
            for default in [None, 6]:
                for ctype in [CChar,  CShort,  CInt,  CLong,
                              CUChar, CUShort, CUInt, CULong,
                              CFloat, CDouble]:
                    ctype(always=always, default=default)
                CString(length=5, always=always and str(always), default=default and str(default))
    
    def test_invalid_basic(self):
        self.assertRaises(CWarning, CInt,    length=5)
        self.assertRaises(CWarning, CInt,    something=6)
        self.assertRaises(CError,   CString, length=None)
        self.assertRaises(CError,   CType)
    
    def test_array_instantiation(self):
        class Point(CStruct):
            x = CInt()
            y = CInt()
        
        CArray(10, CInt)
        CArray(10, CInt())
        CArray(10, Point)
        CArray(10, Point.get_type())
    
    def test_valid_array_packing(self):
        xs = CArray(2, CInt, default=[0,6])
        buf = "\x00\x00\x00\x05\x00\x00\x00\x06"
        self.assertEqual(xs.serialize([5,6]), buf)
        self.assertEqual(xs.serialize([5]), buf)
        self.assertEqual([5,6], xs.parse(buf))
    
    def test_array_defaults(self):
        class Point(CStruct):
            xy = CArray(2, CInt, default=[5,6])
        self.assertEqual(Point().xy, [5,6])
        
        class Point(CStruct):
            xy = CArray(2, CInt(default=0))
        self.assertEqual(Point().xy, [0,0])
        
        class Point(CStruct):
            xy = CArray(2, CInt, default=lambda: [5,6])
        self.assertEqual(Point().xy, [5,6])
    
    def test_invalid_arrays(self):
        self.assertRaises(CError, CArray, 10, int)
        self.assertRaises(CWarning, CArray, 10, NamedPoint())
        self.assertRaises(CWarning, CArray(2,CInt).serialize, [5,6,11])
    
    def test_struct_equality(self):
        np   = NamedPoint(x=5, y=6)
        same = NamedPoint(x=5, y=6)
        diff = NamedPoint(x=0, y=0)
        
        self.assertTrue(np == same)
        self.assertFalse(np != same)
        self.assertEqual(hash(np), hash(same))
        self.assertEqual([np.code, np.name, np.x, np.y], [same.code, same.name, same.x, same.y])
        
        self.assertTrue(np != diff)
        self.assertFalse(np == diff)
        self.assertNotEqual(hash(np), hash(diff))
        self.assertEqual([np.code, np.name, np.x, np.y], [same.code, same.name, same.x, same.y])
    
    def test_valid_structs(self):
        np = NamedPoint(x=5, y=6)
        buf = np.serialize()
        pos = NamedPoint(0x1234, 5, 6)
        dup = NamedPoint(0x1234, 5, 6, x=5, y=6)
        parsed = NamedPoint.parse(buf)
        evaled = eval( repr(np) )
        from_file = NamedPoint.parse( StringIO(NP_BUF) )
        
        self.assertEqual(buf, NP_BUF)
        self.assertEqual(np, pos)
        self.assertEqual(np, dup)
        self.assertEqual(np, parsed)
        self.assertEqual(np, evaled)
        self.assertEqual(np, from_file)
    
    def test_nested_structs(self):
        class Segment(CStruct):
            p1 = NamedPoint.get_type()
            p2 = NamedPoint.get_type()
        Segment(p1=NamedPoint(x=5,y=6), p2=NamedPoint(x=11,y=42))
        Segment.parse(NP_BUF * 2)
        Segment.parse(NP_BUF * 2 + "extra data in buffer")
    
    def test_invalid_struct_instances(self):
        self.assertRaises(CError, CStruct)
        self.assertRaises(CWarning, NamedPoint, x=5, y=6, z=12)
        self.assertRaises(CError, NamedPoint, 0x1234, 5, x=6)
        self.assertRaises(CError, NamedPoint(x=5).serialize)
        self.assertRaises(CWarning, NamedPoint(code=0x4321, x=5, y=6).serialize)
        self.assertRaises(CWarning, NamedPoint.parse, "!C\x00\x00\x00\x05\x00\x00\x00\x06unnamed\x00\x00\x00\x00\x00\x00\x00\x00")
    
    def test_invalid_structs(self):
        self.assertRaises(CError, NamedPoint.parse, "not enough data")
        
        class Point(CStruct):
            pass
        self.assertRaises(CError, Point)
        
        class Point(CStruct):
            x = CInt
        self.assertRaises(CError, Point)
        self.assertRaises(CError, Point.parse, "\x00\x00\x00\x00")
        
        class Segment(CStruct):
            p1 = NamedPoint
            p2 = NamedPoint
        self.assertRaises(CError, Segment)
        self.assertRaises(CError, Segment.parse, NP_BUF * 2)
        
        class Segment(CStruct):
            p1 = NamedPoint()
            p2 = NamedPoint()
        self.assertRaises(CError, Segment)
        self.assertRaises(CError, Segment.parse, NP_BUF * 2)
    
    def test_duplicate_fields(self):
        class Point(CStruct):
            x = y = CInt()
        self.assertRaises(CWarning, Point)
    
    def test_valid_inheritance(self):
        class Origin(NamedPoint):
            x = y = CInt(always = 0)
        orig = Origin()
        self.assertEqual([orig.x, orig.y], [0, 0])
        self.assertRaises(CWarning, Origin.parse, NP_BUF)
    
    def test_invalid_inheritance(self):
        class Origin(NamedPoint):
            x = y = CChar(always = 0)
        self.assertRaises(CError, Origin)
        
        class Origin(NamedPoint):
            x = y = 0
        self.assertRaises(CError, Origin)

class BadHandlerTests(TestCase):
    def test_no_structs(self):
        class EmptyHandler(ProtHandler):
            class STRUCT_MOD:
                pass
        self.assertRaises(CError, EmptyHandler)
    
    def test_duplicate_starts(self):
        class DupHandler(ProtHandler):
            class STRUCT_MOD:
                class Foo(CStruct):
                    code = CInt(always = 1)
                class Bar(CStruct):
                    code = CInt(always = 1)
        self.assertRaises(CWarning, DupHandler)
    
    def test_bad_struct_name(self):
        class BadNameHandler(ProtHandler):
            class STRUCT_MOD:
                class Handle(CStruct):
                    code = CInt(always = 1)
        self.assertRaises(CError, BadNameHandler)

class ServerTests:
    def setUp(self):
        self.delete_logs()
        
        self.server = self.ServerClass(SERVER_ADDR, self.HandlerClass)
        t = Thread(target=self.server.serve_forever)
        t.daemon = True
        t.start()
        
        self.client_setup()
        
        self.np = NamedPoint(x=5, y=6)
        self.rp = RenamedPoint(x=5, y=6)
    
    def tearDown(self):
        self.sock.close()
        self.server.shutdown()
        self.server.socket.close()
        self.delete_logs()
    
    def client_teardown(self):
        self.sock.close()
    
    def delete_logs(self):
        for name in glob(sys.argv[0].split(".")[0] + ".*_log"):
            os.remove(name)
    
    def read_log(self, name):
        with open("unit_tests." + name) as f:
            return f.read()
    
    def test_struct_response(self):
        self.send(self.np)
        rp = RenamedPoint.parse(self.f)
        self.assertEqual(rp, self.rp)
    
    def test_string_response(self):
        self.send(self.rp)
        self.assertEqual(self.f.readline(), "Hello World!\n")
    
    def test_too_short(self):
        self.send( self.np.serialize()[:5] )
        sleep(0.2)
        self.assertTrue("struct requires" in self.read_log("error_log"))
    
    def test_no_handler(self):
        self.send( NamedOrigin() )
        sleep(0.2)
        self.assertTrue("handler not defined" in self.read_log("error_log"))
    
    def test_unknown(self):
        self.send("raw data")
        sleep(0.2)
        self.assertTrue("unable to resolve" in self.read_log("error_log"))
    
    def test_multiple_clients(self):
        self.test_struct_response()
        self.client_teardown()
        self.client_setup()
        self.test_struct_response()

class TCPServerTests(ServerTests, TestCase):
    ServerClass = LoggingTCPServer
    HandlerClass = TCPTestHandler
    
    def client_setup(self):
        self.sock = socket.create_connection(SERVER_ADDR)
        self.f = self.sock.makefile("r+b", bufsize=0)
    
    def send(self, data):
        self.f.write(data)
        self.f.flush()

class UDPServerTests(ServerTests, TestCase):
    ServerClass = LoggingUDPServer
    HandlerClass = UDPTestHandler
    
    def client_setup(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(CLIENT_ADDR)
        self.f = self.sock.makefile("rb")
    
    def send(self, data):
        self.sock.sendto(str(data), SERVER_ADDR)

if __name__ == "__main__":
    unittest.main()
