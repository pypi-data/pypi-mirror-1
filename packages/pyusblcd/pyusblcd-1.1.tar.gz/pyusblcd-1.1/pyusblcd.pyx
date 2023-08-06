"""Module to access the picoLCD displays

This module provides the python bindings for the picoLCD driver library.
These bindings require libpicoLCD 0.1.8 (previously known as libusblcd)
to be installed. You may get the required drivers and a SDK from the mini-box 
website `www.mini-box.com <http://www.mini-box.com>`_.

This set of bindings tries to keep as close to the original libpicoLCD
API as possible, only making changes where absolutely needed or where it
makes it significantly simpler or easier in python.

The main class to use is UsbLCD, this corresponds to libpicoLCD's
usblcd_operations type. For usage see the docstrings in this module and
documentation with the libpicoLCD SDK.

"""

###############################################################################
# Copyright (C) 2009 Michael Whapples
#
# This module is free software; you
# can redistribute it and/or modify it under the terms of the
# Artistic License 2.0. For details, see the full text of the
# license in the file LICENSE.
#
# This module is distributed in the hope that it will be
# useful, but it is provided "as is" and without any express
# or implied warranties. For details, see the full text of
# the license in the file LICENSE.
###############################################################################

cimport stdlib

cdef extern from "usblcd.h":
    ctypedef struct c_usblcd_event "usblcd_event":
        int type
        int length
        char *data
    ctypedef struct c_usblcd_state "usblcd_state":
        unsigned int usblcd_state
        unsigned int usblcd_cursor
        unsigned int usblcd_cursor_blink
    ctypedef struct c_usblcd_operations "usblcd_operations":
        c_usblcd_state *state
        unsigned int leds
        void (*getversion)(c_usblcd_operations *self)
        void (*backlight)(c_usblcd_operations *self, unsigned int state)
        void (*contrast)(c_usblcd_operations *self, unsigned int level)
        void (*setled)(c_usblcd_operations *self, unsigned int led, unsigned int status)
        void (*set_switch)(c_usblcd_operations *self, unsigned int status)
        void (*set_cursor)(c_usblcd_operations *self, unsigned int status)
        void (*set_cursor_blink)(c_usblcd_operations *self, unsigned int status)
        void (*clear)(c_usblcd_operations *self)
        void (*setchar)(c_usblcd_operations *self, unsigned int x, unsigned int y, char character)
        void (*settext)(c_usblcd_operations *self, unsigned int x, unsigned int y, char *text)
        c_usblcd_event *(*read_events)(c_usblcd_operations *self) nogil
        void (*setfont)(c_usblcd_operations *self, char *filename)
        void (*enter_flasher_mode)(c_usblcd_operations *self)
        void (*exit_flasher_mode)(c_usblcd_operations *self)
        void (*setfontmemory)(c_usblcd_operations *self, int fontlines[], int nrchars)
        void(*setsplash)(c_usblcd_operations *self, char *filename)
        void (*flash)(c_usblcd_operations *self)
        void (*powerstate)(c_usblcd_operations *self)
        void (*keystate)(c_usblcd_operations *self)
        void (*irdata)(c_usblcd_operations *self)
        void (*init)(c_usblcd_operations *self)
        void (*close)(c_usblcd_operations *self)
        void (*debug)(int level)
    c_usblcd_operations *new_usblcd_operations "new_usblcd_operations" ()

cdef int get_int_from_bin(line):
    cdef int result = 0
    cdef int char_id = 0
    for char_id in range(5):
        if line[char_id] != "0":
            result = (result * 2) + 1
    return result
cdef class UsbLCD:
    """
    The main class to be used to access the picoLCD
    
    This class corresponds to the libpicoLCD type usblcd_operations. You
    should be aware that these bindings automatically initialise the display
    (call the init function on creation and automatically call close 
    when you delete an object of this class, so you need not call these).
    NOTE: some of the methods in the original libpicoLCD are
    not complete, so some of the methods here may not work. All exposed
    methods are included here as future versions of libpicoLCD may have
    complete versions of these methods.
    """
    cdef c_usblcd_operations *thisptr
    def __cinit__(self):
        self.thisptr = new_usblcd_operations()
        self.thisptr.init(self.thisptr)
    def __dealloc__(self):
        self.thisptr.close(self.thisptr)
    def debug(self, int level):
        """Set the debugging level"""
        self.thisptr.debug(level)

    def backlight(self, unsigned int state):
        """Set the backlight on state=1 or off state=0"""
        self.thisptr.backlight(self.thisptr, state)
    def contrast(self, unsigned int level):
        """Set the contrast level, should be a value between 0 and 40"""
        self.thisptr.contrast(self.thisptr, level)
    def clear(self):
        """Clear the display"""
        self.thisptr.clear(self.thisptr)
    def setchar(self, unsigned int x, unsigned int y, char character):
        """Set character at position x,y to a given value"""
        self.thisptr.setchar(self.thisptr, x, y, character)
    def settext(self, unsigned int x, unsigned int y, char *text):
        """Set text starting at x,y to a given value"""
        self.thisptr.settext(self.thisptr, x, y, text)
    def setled(self, unsigned int led, unsigned int status):
        """Set the numbered LED to given state (0 for off or 1 for on)"""
        self.thisptr.setled(self.thisptr, led, status)
    def set_cursor(self, unsigned int status):
        """Show or hide the cursor"""
        self.thisptr.set_cursor(self.thisptr, status)
    def set_cursor_blink(self, unsigned int status):
        """Set the blink state of the cursor"""
        self.thisptr.set_cursor_blink(self.thisptr, status)
    def set_switch(self, unsigned int status):
        """Switch LCD screen on or off"""
        self.thisptr.set_switch(self.thisptr, status)
    def read_events(self):
        """
        Read events from the picoLCD device
        
        This method will wait until an event is recieved at which point
        it returns a tuple with the first value being the event type and
        the second value being the data of the event. This saves using
        event type used in libpicoLCD.
        """
        cdef c_usblcd_event *res
        res = NULL
        with nogil:
            while res == NULL:
                res = self.thisptr.read_events(self.thisptr)
        data = res.data[:res.length]
        type = res.type
        return (type, data)
    def getversion(self):
        """Get the version"""
        self.thisptr.getversion(self.thisptr)
    def enter_flasher_mode(self):
        """Enter flasher mode"""
        self.thisptr.enter_flasher_mode(self.thisptr)
    def exit_flasher_mode(self):
        """Exits flasher mode"""
        self.thisptr.exit_flasher_mode(self.thisptr)
    def setfont(self, char *filename):
        """Upload a font file to the picoLCD"""
        self.thisptr.setfont(self.thisptr, filename)
    def setfontmemory(self, list chars):
        cdef int nrchars = len(chars)
        cdef int line_num = 0
        cdef int *line_array = <int *>stdlib.malloc(nrchars * 8 * sizeof(int))
        try:
            for character in chars:
                lines = character.splitlines()
                for line in lines:
                    if len(line) != 5:
                        raise Exception("Invalid line found")
                    line_array[line_num] = get_int_from_bin(line)
                    line_num = line_num + 1
            self.thisptr.setfontmemory(self.thisptr, line_array, nrchars)
        finally:
            stdlib.free(line_array)
    def setsplash(self, char *filename):
        """Set splash screen from a file"""
        self.thisptr.setsplash(self.thisptr, filename)
    def flash(self):
        """Flash the device with firmware in file"""
        self.thisptr.flash(self.thisptr)
    def powerstate(self):
        """Return the power state"""
        self.thisptr.powerstate(self.thisptr)
    def keystate(self):
        """Return the last key presses"""
        self.thisptr.keystate(self.thisptr)
    def irdata(self):
        """Return the IR data last recieved"""
        self.thisptr.irdata(self.thisptr)
    property leds:
        """A list containing the states of the LEDs"""
        def __get__(self):
            ledlist = []
            cdef int i
            for i from 0 <= i < 6:
                bitval = 2**i
                if (bitval & self.thisptr.leds) == bitval:
                    ledlist.append(1)
                else:
                    ledlist.append(0)
            return ledlist
