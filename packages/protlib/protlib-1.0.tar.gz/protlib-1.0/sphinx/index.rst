.. toctree::
   :maxdepth: 2


protlib - Easily implement binary network protocols
===================================================

protlib builds on the
`struct <http://docs.python.org/library/struct.html>`_
and
`SocketServer <http://docs.python.org/library/socketserver.html>`_
modules in the standard library to make it easy to implement binary 
network protocols. It provides support for default and constant struct 
fields, nested structs, arrays of structs, better handling for strings 
and arrays, struct inheritance, and convenient syntax for instantiating 
and using your custom structs.

Here's an example of defining, instantiating, writing, and reading a struct using file i/o:

.. code-block:: python

    from protlib import *
    class Point(CStruct):
        x = CInt()
        y = CInt()
    
    p1 = Point(5, 6)
    p2 = Point(x=5, y=6)
    p3 = Point(y=6, x=5)
    assert p1 == p2 == p3

    with open("point.dat", "wb") as f:
        f.write( p1.serialize() )
    
    with open("point.dat", "rb") as f:
        p4 = Point.parse(f)
    
    assert p1 == p4

You may use the
`socket.makefile <http://docs.python.org/library/socket.html#socket.socket.makefile>`_
method to use this file i/o approach for sockets.



Installation
============
protlib requires Python 2.6 and will presumably work with Python 2.7 although this hasn't
been tested.  It has no other dependencies.

You may `click here <http://courtwright.org/protlib/protlib.tar.gz>`_ to download protlib.
You may also run ``easy_install protlib`` if you have 
`EasyInstall <http://peak.telecommunity.com/DevCenter/EasyInstall>`_ on your system.  The
project page for protlib in the Cheese Shop (aka the Python Package Index or PyPI) may
be found `here <http://pypi.python.org/pypi/protlib/>`_.

You may also check out the development version of protlib with this command:

``svn checkout http://courtwright.org/svn/protlib``



Data Types
==========

.. class:: CType(**kwargs)
    
    This is the root class of all classes representing C data types
    in the protlib library.  It may not be directly instantiated; you
    must always use one of its subtypes instead.  There are three
    optional arguments which you may pass to a CType:
    
    :param length: only valid for the ``CString`` and ``CArray`` data types, for which 
                   it is required
    
    :param always: Use this to set a constant value for a field.  You won't need to specify
                   this value, and a warning will be raised if the value differs from this
                   parameter when the struct is parsed or serialized.  For example:
                   
                   >>> from protlib import *
                   >>> class OriginPoint(CStruct):
                   ...     x = CInt(always = 0)
                   ...     y = CInt(always = 0)
                   ... 
                   >>> op1 = OriginPoint()
                   >>> op1
                   OriginPoint(x=0, y=0)
                   >>> op1.x = 5
                   >>> with open("origin.dat", "wb") as f:
                   ...     f.write( op1.serialize() )
                   ...
                   protlib.py:159: CWarning: x should always be 0
                     warn("{0} should always be {1}".format(name, ctype.always), CWarning)
                   >>>
                   >>> with open("origin.dat", "rb") as f:
                   ...     op2 = OriginPoint.parse(f)
                   ...
                   protlib.py:149: CWarning: x should always be 0
                     warn("{0} should always be {1}".format(name, ctype.always), CWarning)
                   >>>
                   >>> assert op1 == op2

    :param default: Like the ``always`` parameter, except that no warnings are raised when a 
                    different value is parsed or serialized.  Also, a ``default`` parameter
                    may be either a value or a ``callable`` object.  For example:
                    
                    >>> from protlib import *
                    >>> class Point(CStruct):
                    ...     x = CInt(default = 0)
                    ...     y = CInt(default = lambda: 5)
                    ...
                    >>> p = Point()
                    >>> p
                    Point(x=0, y=5)
    
    .. attribute:: sizeof

        The size of the packed binary data representing this ``CType``.
        Note that this is a ``classmethod`` for subclasses of ``CStruct``.

    .. attribute:: struct_format

        The format string used by the underying
        `struct module <http://docs.python.org/library/struct.html>`_
        to represent the packed binary data format.
        Note that this is a ``classmethod`` for subclasses of ``CStruct``.

    .. method:: parse(f)

        Accepts either a string or a file-like object (anything with a ``read`` method)
        and returns a Python object with the appropriate value.

        >>> raw = "\x00\x00\x00\x05"
        >>> i = CInt().parse(raw)
        >>> assert i == 5

        Note that unlike the struct module, strings are stripped of trailing null
        bytes when they're parsed.  For example:

        >>> raw = "foo\x00\x00"
        >>> import struct
        >>> s = struct.unpack("5s", raw)[0]
        >>> assert s == "foo\x00\x00"
        >>> 
        >>> from protlib import *
        >>> s = CString(length = 5).parse(raw)
        >>> assert s == "foo"
    
        Note that this is a ``classmethod`` on subclasses of ``CStruct``.

    .. method:: serialize(x)
    
        Serializes the value according to the specific ``CType`` class.
        Note that this takes no argument when called on a ``CStruct``
        instance.


Basic Data Types
----------------

Because protlib is built on top of struct module, each basic data type
in protlib uses a struct format string.  The list of struct format strings 
`may be found here <http://docs.python.org/library/struct.html#struct.calcsize>`_
and the protlib types which use them are listed below:

+----------------+---------------+--------------------------+
| C data type    | protlib class | struct format string     |
+================+===============+==========================+
| char           | CChar         | b                        |
+----------------+---------------+--------------------------+
| unsigned char  | CUChar        | B                        |
+----------------+---------------+--------------------------+
| short          | CShort        | h                        |
+----------------+---------------+--------------------------+
| unsigned short | CUShort       | H                        |
+----------------+---------------+--------------------------+
| int            | CInt          | i                        |
+----------------+---------------+--------------------------+
| unsigned int   | CUInt         | I                        |
+----------------+---------------+--------------------------+
| long           | CLong         | l                        |
+----------------+---------------+--------------------------+
| unsigned long  | CULong        | L                        |
+----------------+---------------+--------------------------+
| float          | CFloat        | f                        |
+----------------+---------------+--------------------------+
| double         | CDouble       | d                        |
+----------------+---------------+--------------------------+
| char[]         | CString       | Xs (e.g. 5s for char[5]) |
+----------------+---------------+--------------------------+


Arrays
------

.. class:: CArray(length, ctype)

    You can make an array of any ``CType``.  Arrays pack and unpack to and
    from Python lists.  For example:
    
    >>> ca = CArray(5, CInt)
    >>> raw = ca.serialize( [5,6,7,8,9] )
    >>> xs = ca.parse(raw)
    >>> assert xs == [5,6,7,8,9]
    
    Arrays may either be given default/always values themselves or use the
    default/always values of the ``CType`` they are given.  For example:
    
    >>> class Triangle(CStruct):
    ...     xcoords = CArray(3, CInt(default=0))
    ...     ycoords = CArray(3, CInt, default=[0,0,0])
    ...
    >>> tri = Triangle()
    >>> assert tri.xcoords == tri.ycoords == [0,0,0]


Custom Structs
--------------

.. class:: CStruct

    This should never be instantiated directly.  Instead, you should subclass
    this when defining a custom struct.  Your subclass will be given a
    constructor which takes the fields of your struct as positional and/or
    keyword arguments.  However, you don't have to provide values for your
    fields at this time.  For example:
    
    >>> class Point(CStruct):
    ...     x = CInt()
    ...     y = CInt()
    ...
    >>> p1 = Point(5, 6)
    >>> p2 = Point()
    >>> p2.x = 5
    >>> p2.y = 6
    >>> assert p1 == p2
    
    .. classmethod:: sizeof()
    
        Returns the size of the packed binary data needed to hold this
        ``CStruct``
    
    .. classmethod:: struct_format()
    
        Returns the format string used by the underlying struct module to
        represent this ``CStruct``
    
    .. classmethod:: parse(f)
        
        Accepts a string or file-like object and returns an instance of
        this ``CStruct``.
    
    .. method:: serialize()
    
        Returns the packed binary data representing the values of
        this ``CStruct``.  This is what should be written to files and sockets.
    
    .. method:: __repr__()
    
        Returns a literal representation of the ``CStruct``.  For example:
        
        >>> class Point(CStruct):
        ...     x = CInt()
        ...     y = CInt()
        ...
        >>> p = Point(x=5, y=6)
        >>> p
        Point(x=5, y=6)

    .. classmethod:: get_fields()
    
        Returns a list of the ``CType`` objects which define the fields of 
        this struct in the order in which they were declared.
    
    .. classmethod:: get_type(**kwargs)
    
        Returns an objects which may be used to declare a ``CStruct`` as a
        field in another ``CStruct``.  This accepts the same ``default``
        and ``always`` parameters as the ``CType`` constructor.  For example:
        
        >>> class Point(CStruct):
        ...     x = CInt()
        ...     y = CInt()
        ...
        >>> class Vector(CStruct):
        ...     p1 = Point.get_type()
        ...     p2 = Point.get_type(default = Point(0,0))
        ...
        >>> v = Vector(p1 = Point(5,6))


.. warning::

    The order of struct fields is defined by the order in which the ``CType``
    subclasses for those fields were instantiated.  In other words, if you say

    .. code-block:: python

       from protlib import *

       y_field = CInt()
       x_field = CInt()

       class Point(CStruct):
           x = x_field
           y = y_field

    then when you serialize your struct, the ``y`` field will come **before**
    the ``x`` field because its ``CInt`` value was instantiated first.  Similarly,
    if you say

    .. code-block:: python

        from protlib import *

        class Point(CStruct):
            x = y = CInt()

    then the order of the x and y fields is undefined since they share the same
    ``CInt`` instance.  In this second case, a warning will be raised,
    but the first case is not automatically detected by the protlib library.



Protocol Handlers
=================

protlib also provides a convenient framework for implementing servers which receive and 
return ``CStruct`` objects.  This makes it easy to implement custom binary protocols in 
which structs are passed back and forth over socket connections.  This is based on
`the SocketServer module <http://docs.python.org/library/socketserver.html>`_
in the Python standard library.

In order to use these examples, you must do only two things.

* First, make sure that each struct which represents a message begins with a constant 
  value which uniquely identifies that struct.
* Second, define a subclass of the appropriate handler class, either ``TCPHandler`` or
  ``UDPHandler``, and define a handler method for each message type you wish to respond to.


An example client/server
------------------------

Let's walk through a simple example.  We'll define several structs to represent geometric 
concepts: a Point, a Vector, and a Rectangle.  Each of these structs is a message which 
can be sent between the client and server. We'll also define a variable-length message 
called PointGroup; this struct contains the number of Point messages which immediately 
follow the PointGroup struct in the message.

Note that first field in each of these messages is a constant value that uniquely 
identifies the message.

This entire example can be found in the ``examples/geocalc`` directory.  Here's the 
``common.py`` file, which is imported by both the ``server.py`` and ``client.py`` programs:

.. literalinclude:: ../examples/geocalc/common.py

For our server, we define a handler class with a handler method for each message we wish 
to accept.  The name of each handler method should be the name of the message class in 
lower case with the words separated by underscores.  For example, the ``Vector`` class 
is handled by the ``vector`` method, and the ``PointGroup`` class is handled by the 
``point_group`` method.  Each of these handler methods takes a single parameter other 
than ``self`` which is the actual message read and parsed from the socket.

Here's the ``server.py`` file which uses our subclasses of
`the SocketServer module <http://docs.python.org/library/socketserver.html>`_
classes to accept and handle incoming messages:

.. literalinclude:: ../examples/geocalc/server.py

To test this server, we have a simple client which sends a series of messages to the 
server and then reads back the responses, logging everything with our ``protlib.Logger`` 
class.  Here's our ``client.py`` script:

.. literalinclude:: ../examples/geocalc/client.py

Our server does all of our logging automatically, but we need to manually invoke the 
logger on the client.  The logs created and their format are explained below.


Logging
-------

If you use the ``LoggingTCPServer`` and ``LoggingUDPServer`` classes, then everything is
logged for us.  There are 4 logs created, a `struct_log`, a `raw_log`, an `error_log`, and 
a `stack_log`.  The log prefix is the name of the script being executed.  So if we're 
executing ``server.py`` then our log files will be ``server.struct_log``, ``server.raw_log``, 
etc.  All logs are opened in append mode.

Each log message contains a timestamp followed by a unique identifier which indicates the 
specific message being received.  This makes it easy to match the log messages in the 
different files to one another, since the unique message identifier will be present in 
each of the 4 logs.

Here's a description of each log:

.. attribute:: struct_log
    
    This contains the literal representation of each request and response, for example:
    
    .. code-block:: none
        
        2010-01-14 11:14:37.771015 (1263485677_0): received Vector(code=2, p1=Point(code=1, x=31.0, y=24.0), p2=Point(code=1, x=12.0, y=52.0))
        2010-01-14 11:14:37.771170 (1263485677_0): sending Point(code=1, x=21.5, y=38.0)
    
    This is convenient because the structs are logged with the Python code which represents 
    them.  Therefore we can paste them directly into a Python command prompt to inspect and 
    play around with them:
    
    >>> from common import *
    >>> p = Point(code=1, x=21.5, y=38.0)
    >>> p
    Point(code=1, x=21.5, y=38.0)
    
.. attribute:: raw_log
    
    This contains the raw data in the form of a Python string of each request and response, 
    for example:
    
    .. code-block:: none
    
        2010-01-14 11:14:37.770419 (1263485677_0): received '\x00\x02\x00\x01A\xf8\x00\x00A\xc0\x00\x00\x00\x01A@\x00\x00BP\x00\x00'
        2010-01-14 11:14:37.771247 (1263485677_0): sending '\x00\x01A\xac\x00\x00B\x18\x00\x00'
    
    This is convenient because we can paste these strings into a Python command prompt 
    and play around with them.  If they are valid then we can parse them into structs, and 
    if they aren't then we can examine exactly why; this log will always log what we receive 
    even in the case of unparsable binary data:
    
    >>> from common import *
    >>> s = '\x00\x01A\xac\x00\x00B\x18\x00\x00'
    >>> p = Point.parse(s)
    >>> p
    Point(code=1, x=21.5, y=38.0)
    >>> 
    >>> s = "bad"
    >>> p = Point.parse(s)
    >>> Point.parse(s)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "protlib.py", line 230, in parse
        return cls.get_type(cached=True).parse(f)
      File "protlib.py", line 141, in parse
        raise CError("{0} requires {1} bytes and was only given {2} ({3!r})".format(self.subclass.__name__, self.sizeof, len(buf), buf))
    protlib.CError: Point requires 10 bytes and was only given 3 ('bad')
    >>> 
    >>> s = "invalid but with enough data"
    >>> p = Point.parse(s)
    ../../protlib.py:148: CWarning: code should always be 1
      warn("{0} should always be {1}".format(name, ctype.always), CWarning)
    >>> p
    Point(code=26990, x=1.1430328245747994e+33, y=1.1834294514326081e+22)
    
.. attribute:: error_log

    This contains messages for common errors, such as when a message is too short, or 
    when we have no handler to match a message we've received, etc.  These messages 
    contain as much information as possible to help reconstruct the problem, which 
    usually includes the raw data involved (also present in the ``raw_log``).

.. attribute:: stack_log

    This contains any stack traces which occur while the server is running.  This is 
    useful for diagnosing problems in your handler methods.


Protocol Handler Classes
------------------------

.. class:: ProtHandler

    The user does not instantiate this class or any of its subclasses directly.  Instead, 
    you declare your own handler class which subclasses either ``TCPServer`` or 
    ``UDPServer``, which are themselves subclasses of ``ProtHandler``.  They also extend
    `the StreamRequestHandler and DatagramRequestHandler classes <http://docs.python.org/library/socketserver.html#requesthandler-objects>`_
    of the SocketServer module, respectively.
    
    Here are all fields and methods which the user is expected to call and/or override:
    
    .. attribute:: STRUCT_MOD
    
        By default, your handler will detect all messages present in the same module 
        where the handler class itself is defined.  So you can either define your handler 
        in the same module where your structs are  defined, or you can import those 
        structs into the handler module.  This is the recommended way to integrate your 
        handlers with your struct definitions.
        
        However, you may instead set the STRUCT_MOD field to the module where the structs 
        are declared. (Technically you can set this to anything with ``__dict__`` and 
        ``__name__`` fields.)  You may also set this to a string which is the name of 
        the module where they are declared.  For example:
        
        .. code-block:: python
        
            import module_with_structs
            
            class SomeHandler(TCPHandler):
                STRUCT_MOD = module_with_structs
                
                # handler methods go here
            
            class AnotherHandler(UDPHandler):
                STRUCT_MOD = "module_with_structs"
                
                # handler methods go here
    
    .. attribute:: LOG_DIR
    
        This is ``"."`` by default and determines the location of the log files.
    
    .. attribute:: LOG_TO_SCREEN
    
        This is ``False`` by default, but if set to ``True``, every log message will be 
        printed to the screen in addition to being written to the appropriate log.
    
    .. attribute:: HEX_LOGGING
    
        This is ``False`` but default, but if set to ``True``, the ``raw_log`` will 
        contain a nicely formatted hex dump of the binary data sent and received.  
        For example:
        
        .. code-block:: none
            
            2010-01-14 13:47:37.237310 (1263494857_2): sending '\x00\x04\x00\x01A\x98\x00\x00AP\x00\x00\x00\x01A\x98\x00\x00B\xae\x00\x00\x00\x01B\xc2\x00\x00AP\x00\x00\x00\x01B\xc2\x00\x00B\xae\x00\x00'
                 0  1  2  3  4  5  6  7
              0  00 04 00 01 41 98 00 00
              8  41 50 00 00 00 01 41 98
             16  00 00 42 ae 00 00 00 01
             24  42 c2 00 00 41 50 00 00
             32  00 01 42 c2 00 00 42 ae
             40  00 00
        
        These are best set where your custom handler class is defined, for example:
        
        .. code-block:: python
        
            class Handler(TCPHandler):
                HEX_LOGGING = LOG_TO_SCREEN = True
                
                # handler methods would go here

    .. method:: raw_data(data)
    
        This is the default handler for any message for which no struct has been 
        defined.  By default this logs an error message and sends no reply.  Override 
        this if you wish to have your own handler for unclassified binary messages; 
        the ``data`` parameter is a string containing the binary data of the message.
    
    .. method:: reply(data)
    
        Anything you return a handler method is sent back to the client, whether it's 
        a struct or just binary data in a string.  However, sometimes you may need to 
        send multiple messages back to the client.  You can manually concatenate the 
        binary data strings, or you can use the ``reply`` method, for example:
        
        .. code-block:: python
            
            class RepeatRequest(CStruct):
                code = CShort(always = 1)
                name = CString(length = 25)
                repititions = CInt()
            
            class Handler(TCPHandler):
                def repeat_request(self, rr):
                    for i in range(rr.repititions):
                        self.reply("Hello " + sm.name + "!\n")


.. class:: LoggingTCPServer(addr, handler_class)
.. class:: LoggingUDPServer(addr, handler_class)

    These classes extend the 
    `TCPServer <http://docs.python.org/library/socketserver.html#socketserver-tcpserver-example>`_
    and the
    `UDPServer <http://docs.python.org/library/socketserver.html#socketserver-udpserver-example>`_
    classes from the SocketServer module, respectively.  You should use these to get the 
    automated logging described above.  However, you may simply use the ``TCPServer`` 
    and ``UDPServer`` classes instead if you'd prefer to do your own logging.

.. class:: Logger([log_dir="."[, hex_logging=False[, also_print=False]]])

    A logging object which creates the 4 logs listed above.  If ``prefix`` is omitted, then
    all log messages are printed to standard output and no files are created.
    
    If you use the logging servers listed above then the logging is done automatically, but 
    if you're implementing a client program, then you can use this class to perform 
    the same type of logging.
    
    :param log_dir: the directory where the logfiles will be written
    :param hex_logging: whether to print a hexdump as part of each ``raw_log`` message
    :param also_print: whether to also print log messages to the screen

    .. method:: log_struct(inst[, trans_type="received"])
    
        Logs the ``repr`` of an instance of a ``CStruct`` subclass to the ``struct_log``.
        
        :param inst: the instance of the struct to be logged
        :param trans_type: a prefix to the log message, generally this should be either
                           ``"sending"`` or ``"received"``
    
    .. method:: log_raw(data[, trans_type="received"])
    
        Logs the ``repr`` of the packed binary data to the ``raw_log``.  If hex logging
        is enabled, this will also log a nicely formatted table of the hexadecimal
        values of this data immediately after the log message.
        
        :param data: the packed binary data, such as what's produced by calling
                     ``s.serialize()`` on an instance of a ``CStruct`` subclass
        :param trans_type: a prefix to the log message, generally this should be either
                           ``"sending"`` or ``"received"``
    
    .. method:: log_error(message, *args, **kwargs)
    
        Logs the message to the ``error_log``.  The ``message`` parameter should be
        a string, and the ``*args`` and ``**kwargs`` to this method are used as the
        parameters to `str.format <http://docs.python.org/library/stdtypes.html#str.format>`_

    .. method:: log_stacktrace()
    
        Logs the value of `traceback.format_exc() <http://docs.python.org/library/traceback.html#traceback.format_exc>`_
        to the ``stack_log``.

.. class:: Parser([module[, logger]])

    If you know what struct you want, then you can use the ``CStruct.parse`` classmethod
    to read an instance of that struct from a file, e.g. ``p = Point.parse(f)``.  However, 
    in some cases you want to read some data from a file or socket but aren't sure what 
    message is coming across.  This class's ``parse`` method figures out which message 
    is being read and returns an instance of the correct struct.
    
    :param module: This is exactly the same as the ``ProtHandler.STRUCT_MOD`` field;
                   if present then it indicates which module contains the struct classes
                   you want to use.  If omitted, then the module where this class is
                   instantiated is used.
    :param logger: The instance of the ``Logger`` class to use to perform logging.  If
                   omitted, no logging will be performed.
    
    .. method:: parse(f)
    
        This method accepts a string or file and returns an instance of the struct
        it reads from that string/file.  If the data it finds cannot be parsed into
        a struct, then it just returns all of the data it is able to read.  This
        may be an empty string if no data is available.
        
        ``None`` will be returned in the case of an incomplete message.  In this case
        a message will be written to the ``error_log`` if a logger was provided.


Struct Inheritance
------------------

Many binary protocols have many message types, but every message has exactly the same
fields, even if those fields have different lengths.  It would be annoying if you had
to write a bunch of mostly-identical struct definitions, so protlib lets you subclass
your custom structs and only override the fields which are different in some way,
such as having a default value in some subclasses but not others, etc.

Let's walk through a simple example, which is available in the ``examples/struct_inheritance``
directory.  First, we define our messages in ``common.py``:

.. literalinclude:: ../examples/struct_inheritance/common.py

In this case we have a standard message format, and the only thing that varies is
the value of the ``code`` field, so we need only specify that field in our subclasses.
If we needed to override other fields, we could do so in any order; the order of
fields would remain as however they were declared in the parent class.

Since these messages all have different constant values in their first field, we can
write a normal handler class in our ``server.py``:

.. literalinclude:: ../examples/struct_inheritance/server.py

Since our handler can return different types of messages depending on whether our lookup
was successful, our ``client.py`` uses the ``Parser`` class to parse all incoming messages:

.. literalinclude:: ../examples/struct_inheritance/client.py



Miscellaneous classes, methods, and constants
=============================================

.. class:: CError
.. class:: CWarning

    All exceptions and warnings raised by the protlib module will be instances of these classes.
 
.. function:: underscorize(name)

    This is the function used to convert between ``camelCased`` and 
    ``separated_with_underscores`` names.  Pass it a string and it returns an 
    all-lower-case string with underscores inserted in the appropriate places.  You 
    never have to call this method yourself, but you can use it as a test if you're 
    unsure of the correct handler method name for one of your ``CStruct`` class.  To 
    make it even clearer, here are some examples:
    
    .. code-block:: none
    
        SomeStruct   -> some_struct
        SSNLookup    -> ssn_lookup
        RS485Adaptor -> rs485_adaptor
        Rot13Encoded -> rot13_encoded
        RequestQ     -> request_q
        John316      -> john316
    
    If your struct names are already lower case then this function will just return the
    original string, whether or not you are already using underscores.
    So the ``rs485adaptor`` struct would be handled by the ``rs485adaptor`` handler 
    method, and the ``rot13_encoded`` struct would be handled by the ``rot13_encoded`` 
    handler method, etc.

.. function:: hexdump(data)

    Takes a string and returns a string containing a nicely formatted table of the 
    hexadecimal values of the data in that string.  For example:

    >>> from protlib import *
    >>> print hexdump("Hello World!")
         0  1  2  3  4  5  6  7
      0  48 65 6c 6c 6f 20 57 6f
      8  72 6c 64 21

.. attribute:: BYTE_ORDER

    The first character of the format string passed to
    `the struct module <http://docs.python.org/library/struct.html>`_
    which determines the byte order used to parse and serialize our structs.  By default
    this is set to ``"!"``, which indicates network byte order.  You may change it to
    any of the options availbale in the struct module.

.. attribute:: PROTLIB_DEFAULT_TIMEOUT

    When protlib is imported, it checks whether anyone has set a default socket timeout
    with the `socket.setdefaulttimeout <http://docs.python.org/library/socket.html#socket.setdefaulttimeout>`_
    method and if a default does not already exist, it sets the timeout to this value, 
    which is 5 seconds.
    
    Even if you unset the default timeout, this value will still be used in calls to
    `select <http://docs.python.org/library/select.html#select.select>`_
    by the ``TCPHandler`` class.

