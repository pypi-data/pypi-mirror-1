from setuptools import setup, find_packages

setup(
    name = "protlib",
    version = "1.0",
    py_modules = ["protlib"],
    
    author = "Eli Courtwright",
    author_email = "eli@courtwright.org",
    description = "library for implementing binary network protocols",
    license = "PSF",
    url = "http://courtwright.org/protlib/",
    
    download_url = "http://courtwright.org/protlib/protlib.tar.gz",
    
    long_description = """
protlib makes it easy to implement binary network protocols. It uses
the struct and SocketServer modules from the standard library. It
provides support for default and constant struct fields, nested structs, 
arrays of structs, better handling for strings and arrays, struct 
inheritance, and convenient syntax for instantiating and using your 
custom structs.

protlib requires Python 2.6 or any later version in the 2.x line.
""",
    
    keywords = ["networking", "protocols", "structs"],
    
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking"
    ]   
)
