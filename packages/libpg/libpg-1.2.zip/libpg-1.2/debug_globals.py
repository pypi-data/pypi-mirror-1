import sys
import os
try:
    import version
except ImportError: #We're not part of the myob suit
    import os as version
    version._RELEASE = True
    version._DEBUG = True
    sys.frozen = True
    # Hax

import time
def time_date():
    return time.strftime("%d-%m-%y")
def time_date_rev():
    return time.strftime("%Y-%m-%d")
def time_time():
    return time.strftime("%H:%M")
# XXX I _BELIEVE_ this will work if sys.stdout is redirected elsewhere.
__all__ = ['_DEBUG', '_ERROR', '_NOTICE', '_QUERY', '_LOG',
            '_', '_READ', '_WRITE', 'nullwrite', 'fakestderr',
            'time_date', 'time_date_rev', 'time_time' ]
LOGFILE = sys.stdout
def nullwrite(string):
    """Override any of the functions here (probably _DEBUG) with nullwrite
    to have it STFU (useful for shutting up a particular module"""
    pass
try:
    APPLOG = open("dolphin_myob_log-%s.log" % (time_date_rev()), "a") 
except IOError:
    APPLOG = open(os.devnull, "w")
def LOGFILEwrite(string): # Note no .
    if string[-1] != "\n":
        string += "\n"
    LOGFILE.write(string)
    APPLOG.write(string)
    

def _LOG(string):
    APPLOG.write(string + "\n")
#
# Don't pester the user if we've made noise in a release
if not version._DEBUG:
    silent = True
    def _DEBUG(string): pass
    def _ERROR(string): pass
    def _NOTICE(string): pass
    def _QUERY(string): pass
    def _READ(string): pass
    def _WRITE(string): pass
else:
    silent = False
    def _DEBUG(string):
        LOGFILEwrite( "[+] " + string)
    def _ERROR(string):
        LOGFILEwrite( "[*] " + string)
    def _NOTICE(string):
        LOGFILEwrite( "[o] " + string)
    def _QUERY(string):
        LOGFILEwrite( "[q] " + string)
    def _READ(string):
        LOGFILEwrite( "[r] " + string)
    def _WRITE(string):
        LOGFILEwrite( "[w] " + string)
_ = _NOTICE
class fakestderr(object):
    LOGWIDTH = 100
    TIMEFORMAT = " [%s]"
    TIMEWIDTH = 8
    def write(self, string):
        string = string.replace("\r", "\n")
        string = string.replace("\n\n", "\n")
        for i in string.split("\n"):
            padding = self.LOGWIDTH - (len(i) + self.TIMEWIDTH)
            _ERROR(self.pad_msg(i, padding))
    def pad_msg(self, string, padding):
        return string + " " * padding + self.TIMEFORMAT % (time_time())
