#! /usr/bin/python

STRINGTYPES = (str, type(u""))

def readHook(string):
    pass
def writeHook(string):
    pass

import pgdb
import types
_repr = repr

def __repr(string):
    t = _repr(string)
    if t[0] == "u":
        t = t[1:]
    if t[0] == '"':
        t = t.replace("'", "''")
        t = t.replace('"', "'")
    return t
repr = __repr
class dbDate(str):
    """Thin wrapper to change the type of a Date field, so that dbList can alter it later
    similar hax to dbListM"""
DBDATE = dbDate()
class dbList(list):
    """dbList is a list derivative, basically a wrapper to kludge data into"""
    """a pg format dolphin can use, this way the api is consistent"""
    dbDate = type(dbDate())
    __list__ = []
    def __init__(self, *args, **kwds):
        list.__init__(self)
        if len(args) == 0:
            return
#       Smash our first arg into args if it's an array type
        if type(args[0]) in (list, tuple):
            args = args[0]
        for i in args:
            self.append(i)
    #def __setitem__(self, index, value):
    #    self.__list__[index] = repr(str(value))
    #def __getitem__(self, index):
    #    return self.__list__[index]

    def append(self, item):
        # More sweet kludges
#       XXX Kludge. I'z not decided what I want to do here, ints probably need to stay
#       ints for db purposes, although pg does seem to let:
#       'INSERT INTO table (someIntColumn) VALUES ("123")' => SELECT someIntColumn FROM table => 123

        if type(item) in STRINGTYPES:
            tmp = ""
            for i in item:
                j = ord(i)
                if (j <= 122 and j >= 39) or j in (32,):
                    tmp += i
            proc = repr(tmp)
            if "\\" in proc and self.__class__ == dbList:
                proc = "E" + proc
            list.append(self, proc)
        elif type(item) == long:
            list.append(self, int(item))
        elif type(item) == dbDate: # HACK
            year, month, date= item.split("-")
            list.append(self, repr("%s/%s/%s" % (date, month, year)))
        elif type(item) == float:
            list.append(self, item)
        elif type(item) == types.NoneType:
            list.append(self, "NULL")
        else:
            list.append(self, item)
    def getFormat(self):
        outPut = []
        for i in self:
            if type(i) in STRINGTYPES:
                outPut.append("%s")
            elif type(i) in (int, long):
                outPut.append("%d")
            elif type(i) == float:
                outPut.append("%.2f")
            elif type(i) == dbDate:
                outPut.append("%s")
            else:
                raise Exception ("Didn't match format for parameter %s of type %s" % (i, str(type(i))))
        return ", ".join(outPut)
class dbListM(dbList):
    """This wraps dbList but supplies data appropriately for myob
    The mad hax to wrap it let me develop them both inline"""
    pass
class Connect(object):
#   TODO
#   -> Add ReadHook and WriteHook as parameterised values to remove dependency
#   on debug_globals and debug_decs
    """XXX Clean up this API. No need to avoid breakage anymore
    Internal methods should handle their own cursors"""
    def __init__(self, host, username, password, database):
        try:
            self.dbObj = pgdb.connect("%s:%s:%s:%s" % (host, database, username, password) )
        except pgdb.InternalError as e:
            print ("Postgres Connection failed. Check details in config.ini\n")
            self.dbObj = None
    def _dbok(self):
        """Internal method, returns void. No need to test it's value, just catch exceptions if you want to recover"""
        if self.dbObj is None:
            raise NotConnectedError
    def ReadExecute(self, query, *args):
        readHook(query)
        """Thin wrapper around execute() but allows finer grained control than trying to do
        something clever based on a stupid boolean parameter, just use the correct
        function"""
        tmpCurs = self.dbObj.cursor()
        def getIndexes():
            rows = {}
            j = 0
            for i in tmpCurs.description:
                rows[i[0]] = j
                j += 1
            return rows
        tmpCurs.getIndexes = getIndexes

        if args:
            tmpCurs.execute(query, *args)
        else:
            tmpCurs.execute(query)
        tmpCurs.ColumnNames = []
        for i in tmpCurs.description:
            tmpCurs.ColumnNames.append(i[0])
        return tmpCurs
    def WriteExecute(self, query, *args, **kwargs ):
        writeHook(query)
        """Thin wrapper around execute() but allows finer grained control than trying to do
        something clever based on a stupid boolean parameter, just use the correct
        function"""
# Gah hax
        if "disable_triggers" in kwargs:
            disable_triggers = kwargs['disable_triggers'] 
        else:
            disable_triggers = None
        #with self.cursor() as tmpCurs:
        disabled = {}
        try:
            tmpCurs = self.cursor()
            if disable_triggers:
                print disable_triggers
                disabled = self.sub_triggers("DISABLE", disable_triggers, tmpCurs)
            if args:
                tmpCurs.execute(query, *args)
            else:
                tmpCurs.execute(query)
            tmpCurs.close()
            self.dbObj.commit()
        except:
            raise
        finally:
            if disabled:
                self.sub_triggers("ENABLE", disabled, tmpCurs)
            del tmpCurs
    @staticmethod
    def sub_triggers(action, tables, tmpCurs):
        print tables
        print ("sub_triggers called")
        disabled = {}
        for table in tables:
            print ("%s'ing %s on %s" % (action, tables[table], table))
            tmpCurs.execute("""ALTER TABLE %s %s TRIGGER "%s";""" % (table, action, tables[table]))
            disabled[table] = tables[table]
        return disabled
    def execute(self, queryString, returnCurs = False):
        """Further examination of this method makes me think it's stupid.
        Created the wrappers ReadExecute and WriteExecute. Use them instead"""
        if self.dbObj is None: return None
        tmpCurs = self.dbObj.cursor()
        try:
            tmpCurs.execute(queryString)
            if returnCurs:
                return tmpCurs
        except pgdb.DatabaseError as e:
            print ("Database error: %s" % (repr(e)))
            self.rollback()
            tmpCurs.close()
            raise
            # XXX WTF? vv
            return False
        self.commit()
        tmpCurs.close()
        return True
    def query(self, queryString, fieldnames):
        """This originally did some clever matching up to make sure that the fieldnames
        mentioned at compiletime for the query matched up to the returned resultset

        However that functionality was broken, and in many ways should be removed.
        XXX DEPRECATED
        """
        tmpCurs = self.dbObj.cursor()
        tmpCurs.execute(queryString)
        tmpCurs.curFields = fieldnames
        return tmpCurs
    def cursor(self):
        self._dbok()
        def exitHook():
#           The first attempt at this had flawed logic. __exit__ is called regardless
#           of failure, and so this should only rollback() after having a crack at a 
#           commit()
            self.parent.commit()
        def enterHook():
            pass
        tmp = self.dbObj.cursor()
        tmp.__exit__ = exitHook
        tmp.__enter__ = enterHook
        tmp.parent = self
        return tmp
    def commit(self):
        self.dbObj.commit()
    def rollback(self):
        self.dbObj.rollback()
    def close(self):
        self.dbObj.close()
    def Disconnect(self):
        """ For CTAPI compatibility """ 
        self.close()
def ConnectS(string):
    return Connect(*string.split(":"))

# Support old API
postgreConnect = Connect
