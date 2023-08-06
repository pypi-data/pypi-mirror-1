#!/usr/bin/python
from distutils.core import setup
from distutils.extension import Extension

from Cython.Distutils import build_ext

setup(
    name = "pyusblcd",
    version = "1.1",
    url = "http://pypi.python.org/pypi/pyusblcd",
    description = """Python interface for the picoLCD driver""",
    long_description =
        """
        Python interface for the picoLCD driver
        =======================================
        
        This is a set of python bindings for the picoLCD display driver
        (usblcd). To use this you will need libpicoLCD 0.1.8 (previously
        called libusblcd) installed. You can find more information about the
        picoLCD displays and download drivers and SDK from the mini-box
        website `www.mini-box.com <http://www.mini-box.com>`_.
        
        This set of python bindings tries to keep as close as possible to
        the original libusblcd/libpicoLCD API but in some cases uses more
        natural and easier python styles (eg. for the method read_events it
        returns a tuple containing the event data rather than creating an
        event object).
        """,
    author = "Michael Whapples",
    author_email = "mwhapples@users.berlios.de",
    cmdclass = {"build_ext": build_ext},
    ext_modules = [Extension("pyusblcd", ["pyusblcd.pyx"], libraries=["picoLCD"])],
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Artistic License",
        "Intended Audience :: Developers",
        "Topic :: System :: Hardware",
        "Operating System :: POSIX"
    ]
)
