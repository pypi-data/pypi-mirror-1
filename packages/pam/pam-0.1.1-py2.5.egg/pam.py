# (c) 2007 Chris AtLee <chris@atlee.ca>
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php
"""
PAM module for python

Provides an authenticate function that will allow the caller to authenticate
a user against the Pluggable Authentication Modules (PAM) on the system.

Implemented using ctypes, so no compilation is necessary.
"""
__all__ = ['authenticate']

from ctypes import *

libpam = CDLL("libpam.so")
libc = CDLL("libc.so.6")

calloc = libc.calloc
calloc.restype = c_void_p
calloc.argtypes = [c_uint, c_uint]

strdup = libc.strdup
strdup.argstypes = [c_char_p]
strdup.restype = POINTER(c_char) # NOT c_char_p !!!!

# Various constants
PAM_PROMPT_ECHO_OFF = 1
PAM_PROMPT_ECHO_ON = 2
PAM_ERROR_MSG = 3
PAM_TEXT_INFO = 4

class pam_handle(Structure):
    _fields_ = [
            ("handle", c_void_p)
            ]

    def __init__(self):
        self.handle = 0

class pam_message(Structure):
    _fields_ = [
            ("msg_style", c_int),
            ("msg", c_char_p),
            ]

    def __repr__(self):
        return "<pam_message %i '%s'>" % (self.msg_style, self.msg)

class pam_response(Structure):
    _fields_ = [
            ("resp", c_char_p),
            ("resp_retcode", c_int),
            ]

    def __repr__(self):
        return "<pam_response %i '%s'>" % (self.resp_retcode, self.resp)

conv_func = CFUNCTYPE(c_int,
        c_int, POINTER(POINTER(pam_message)),
               POINTER(POINTER(pam_response)), c_void_p)

class pam_conv(Structure):
    _fields_ = [
            ("conv", conv_func),
            ("appdata_ptr", c_void_p)
            ]

pam_start = libpam.pam_start
pam_start.restype = c_int
pam_start.argtypes = [c_char_p, c_char_p, POINTER(pam_conv), POINTER(pam_handle)]

pam_authenticate = libpam.pam_authenticate
pam_authenticate.restype = c_int
pam_authenticate.argtypes = [pam_handle, c_int]

def authenticate(username, password, service='login'):
    """Returns True if the given username and password authenticate for the
    given service.  Returns False otherwise
    
    ``username``: the username to authenticate
    
    ``password``: the password in plain text
    
    ``service``: the PAM service to authenticate against.
                 Defaults to 'login'"""
    @conv_func
    def my_conv(nMessages, messages, pResponse, appData):
        # Create an array of nMessages response objects
        addr = calloc(nMessages, sizeof(pam_response))
        pResponse[0] = cast(addr, POINTER(pam_response))
        for i in range(nMessages):
            if messages[i].contents.msg_style == PAM_PROMPT_ECHO_OFF:
                p = strdup(password)
                pResponse.contents[i].resp = cast(p, c_char_p)
                pResponse.contents[i].resp_retcode = 0
        return 0

    handle = pam_handle()
    c = pam_conv(my_conv, 0)
    retval = pam_start(service, username, pointer(c), pointer(handle))

    if retval != 0:
        # TODO: This is not an authentication error, something
        # has gone wrong starting up PAM
        return False

    retval = pam_authenticate(handle, 0)
    return retval == 0

if __name__ == "__main__":
    import getpass
    print authenticate(getpass.getuser(), getpass.getpass())
