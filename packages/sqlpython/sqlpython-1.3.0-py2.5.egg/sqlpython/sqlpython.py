#
# SqlPython V1.3
# Author: Luca.Canali@cern.ch, Apr 2006
# Rev 18-Oct-07
#
# A python module to reproduce Oracle's command line 'sqlplus-like' within python
# Intended to allow easy customizations and extentions 
# Best used with the companion modules sqlpyPlus and mysqlpy 
# See also http://twiki.cern.ch/twiki/bin/view/PSSGroup/SqlPython

import cmd,getpass,binascii,cx_Oracle,re
import pexpecter
    
    # complication! separate sessions ->
    # separate transactions !!!!!
    # also: timeouts, other session failures
	    
class sqlpython(cmd.Cmd):
    '''A python module to reproduce Oracle's command line with focus on customization and extention'''
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = 'SQL.No_Connection> '
        self.prompt2 = ' > '
        self.terminator = ';'
        self.maxfetch = 1000
        self.failoverSessions = []
        self.timeout = 30
    
    def do_select(self, arg):
        '''executes select statements and prints the result set'''
        self.query = self.GetStmt('select '+arg)
        try:
            self.curs.execute(self.query)
            self.rows = self.curs.fetchmany(self.maxfetch)
            self.desc = self.curs.description
            self.rc = self.curs.rowcount
            if self.rc > 0:
                print '\n' + pmatrix(self.rows,self.desc)
            if self.rc == 0:
                print '\nNo rows Selected.\n'
            elif self.rc == 1: 
                print '\n1 row selected.\n'
            elif self.rc < self.maxfetch:
                print '\n%d rows selected.\n' % self.rc
            else:
                print '\nSelected Max Num rows (%d)' % self.rc                 
        except Exception, e:
            print e
    
    def do_connect(self, arg):
        '''Opens the DB connection'''
        try:
            if arg.find('/') == -1:
                orapass = getpass.getpass('Password: ')
                orauser = arg.split('@')[0]
                oraserv = arg.split('@')[1]
                self.orcl = cx_Oracle.connect(orauser,orapass,oraserv)
                arg = '%s/%s@%s' % (orauser, orapass, oraserv)
            else:
                self.orcl = cx_Oracle.connect(arg)
            self.curs = self.orcl.cursor()
            self.prompt = 'SQL.'+self.orcl.tnsentry+'> '
            self.failoverSessions = [f for f in [fbs(arg) for fbs in pexpecter.available] if f.available]

        except Exception, e:
            print e
        
    def emptyline(self):
        pass
    
    def do_quit(self, arg):
        return 1
    
    def fail(self, arg, do_everywhere=False):
        if self.failover:
            success, result = False, ''
            for fbs in self.failoverSessions:
                success, result = fbs.attempt(arg)
                if success:
                    print result
                    if not do_everywhere:
                        return True
            print result 
        return False
                
    def designated_session(self, arg, sesstype):
        for fbs in self.failoverSessions:
            if fbs.valid and fbs.__class__ == sesstype:
                success, result = fbs.attempt(arg)
                print result
                return
        print 'Valid %s not found' % (sesstype.__name__)
        
    def do_yasql(self, arg):
        '''Sends a command to a YASQL session (http://sourceforge.net/projects/yasql/)'''
        self.designated_session(arg, pexpecter.YASQLSession)
    do_y = do_yasql
    def do_sqlplus(self, arg):
        '''Sends a command to a SQL*Plus session'''
        self.designated_session(arg, pexpecter.SqlPlusSession)
    do_sqlp = do_sqlplus
    def do_senora(self, arg):
        '''Sends a command to a Senora session (http://senora.sourceforge.net/)'''
        self.designated_session(arg, pexpecter.SenoraSession)
    do_sen = do_senora       
        
    def default(self, arg, do_everywhere = False):
        self.query = self.GetStmt(arg)
        try:
            self.curs.execute(self.query)
            print '\nExecuted\n'
            if do_everywhere:
                self.fail(arg, do_everywhere = True )
        except Exception, e:
            result = self.fail(arg)
            if not result:
                print str(e)
            
    def do_commit(self, arg):
        self.default('commit %s' % (arg), do_everywhere=True)
    def do_rollback(self, arg):
        self.default('rollback %s' % (arg), do_everywhere=True)        
        
    def GetStmt(self, firstline):
     v_Lines = []
     v_Line = firstline
     v_Offset = - len(self.terminator)
     while 1:
       v_Line = v_Line.rstrip()
       if v_Line.endswith(self.terminator):
          v_Line = v_Line[:v_Offset]
          if v_Line:
            v_Lines.append(v_Line)
          break
       v_Lines.append(v_Line)
       v_Line = raw_input(self.prompt2)
     return '\n'.join(v_Lines)
        
    # shortcuts
    do_q = do_quit
    do_exit = do_quit


def pmatrix(rows,desc,maxlen=30):
    '''prints a matrix, used by sqlpython to print queries' result sets'''
    names = []
    maxen = []
    toprint = []
    for d in desc:
        n = d[0]
        names.append(n)      # list col names
        maxen.append(len(n)) # col length
    rcols = range(len(desc))
    rrows = range(len(rows))
    for i in rrows:          # loops for all rows
        rowsi = map(str, rows[i]) # current row to process
        split = []                # service var is row split is needed
        mustsplit = 0             # flag 
        for j in rcols:
            if str(desc[j][1]) == "<type 'cx_Oracle.BINARY'>":  # handles RAW columns
                 rowsi[j] = binascii.b2a_hex(rowsi[j])
            maxen[j] = max(maxen[j], len(rowsi[j]))    # computes max field length
            if maxen[j] <= maxlen:
                split.append('')
            else:                    # split the line is 2 because field is too long
                mustsplit = 1   
                maxen[j] = maxlen
                split.append(rowsi[j][maxlen-1:2*maxlen-1])
                rowsi[j] = rowsi[j][0:maxlen-1] # this implem. truncates after maxlen*2
        toprint.append(rowsi)        # 'toprint' is a printable copy of rows
        if mustsplit != 0:
            toprint.append(split)
    sepcols = []
    for i in rcols:
        maxcol = maxen[i]
        name = names[i]
        sepcols.append("-" * maxcol)  # formats column names (header)
        names[i] = name + (" " * (maxcol-len(name))) # formats separ line with --
        rrows2 = range(len(toprint))
        for j in rrows2:
            val = toprint[j][i]
            if str(desc[i][1]) == "<type 'cx_Oracle.NUMBER'>":  # right align numbers
                toprint[j][i] = (" " * (maxcol-len(val))) + val
            else:
                toprint[j][i] = val + (" " * (maxcol-len(val)))
    for j in rrows2:
        toprint[j] = ' '.join(toprint[j])
    names = ' '.join(names)
    sepcols = ' '.join(sepcols)
    toprint.insert(0, sepcols)
    toprint.insert(0, names)
    return '\n'.join(toprint)

