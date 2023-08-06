try:
    import version
except ImportError: #We're not part of the myob suit
    import os as version
    version._RELEASE = False
    version._DEBUG = False
import sys
import time
def time_date():
    return time.strftime("%d-%m-%y")
def time_date_rev():
    return time.strftime("%Y-%m-%d")
def time_time():
    return time.strftime("%H:%M")
# XXX I _BELIEVE_ this will work if sys.stdout is redirected elsewhere.
__all__ = ['_DEBUG', '_ERROR', '_NOTICE', '_QUERY', '_', '_READ', '_WRITE']
LOGFILE = sys.stdout
APPLOG = open("dolphin_myob_log-%s.log" % (time_date_rev()), "a") 
def LOGFILEwrite(string): # Note no .
    if string[-1] != "\n":
        string += "\n"
    LOGFILE.write(string)
    

# Don't pester the user if we've made noise in a release
def _LOG(string):
    APPLOG.write(string + "\n")
if version._RELEASE and hasattr(sys, "frozen"):
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
