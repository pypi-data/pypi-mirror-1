import debug_globals
def read_hook(prefix):
    def __(string):
        debug_globals._READ("%s %s" % (prefix, string))
    return __
def write_hook(prefix):
    def __(string):
        debug_globals._WRITE("%s %s" % (prefix, string))
    return __
