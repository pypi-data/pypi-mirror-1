"""
pexpecter

Uses pexpect to handle interactive sessions
Create subclass of Session for each type of program to be used
"""
import re, os

try:
    import pexpect
    
    class Session(object):
        available = True
        call = 'theprogram %s'
        errPattern = re.compile('.')
        validPattern = re.compile('Connected to:')
        promptstub = '>'
        def __init__(self, argstring):
            try:
                self.user, self.instance = argstring.split('@')
                self.user, self.pw = self.user.split('/')
                self.sess = pexpect.spawn(self.call)
                self.connect()
                self.sess.expect(self.promptstub)
                self.valid = self.validPattern.search(self.sess.before)
                self.prompt = '[\r\n]%s%s' % (self.sess.before.splitlines()[-1], self.promptstub)
            except Exception:
                self.valid = False
        def success(self, result):
            return not self.errPattern.search(result)
        def attempt(self, command, timeout=30):
            self.sess.sendline(self._pre_attempt(command))
            try:
                self.sess.expect(self.prompt, timeout=timeout)
            except pexpect.TIMEOUT:
                return (False, """Errror: Waited %d seconds with no response from %s.
                To wait longer, set timeout.""" % (timeout, str(self.__class__)))
            result = self.sess.before
            success = self.success(result)
            if success:
                print 'Executed through %s' % (str(self.__class__))
            return (success, result)
        def _pre_attempt(self, command):
            return command
        
    class YASQLSession(Session):
        errPattern = re.compile('\n[A-Z2]{3,4}-\d{4}:\s')
        terminatorPattern = re.compile('(;|\\g|\\i|\/|\\G|\\s|\\S)\s*\d*\s*$')
        call = os.popen('locate -r /yasql$').readline().strip()
        if not call:
            print 'yasql not found; commands cannot failover to YASQL'
            available = False
        def _pre_attempt(self, command):
            if not self.terminatorPattern.search(command):
                return '%s;' % (command)
            return command
        def connect(self):
            self.sess.sendline('%s@%s' % (self.user, self.instance))
            self.sess.sendline(self.pw)
    
    class SQLSession(Session):
        def _pre_attempt(self, command):
            if command.strip()[-1] != ';':
                return '%s;' % (command)
            return command

    class SqlPlusSession(SQLSession):
        call = r'sqlplus'
        errPattern = re.compile('\n[A-Z2]{3,4}-\d{4}:\s')
        def connect(self):
            self.sess.sendline('%s/%s@%s' % (self.user, self.pw, self.instance))
            
    class SenoraSession(SQLSession):
        errPattern = re.compile('(\n[A-Z2]{3,4}-\d{4}:\s)|(\nwhat ? )')
        call = os.popen('locate -r Senora\.pm$ | head -1').readline().strip()
        if call:
            call = 'perl %s' % (call)
        else:
            print 'Senora.pm not found; commands cannot failover to Senora'
            available = False
        def connect(self):
            self.sess.expect(self.promptstub)            
            self.sess.sendline('connect %s/%s@%s' % (self.user, self.pw, self.instance))
    
except ImportError:
    print '''Python's pexpect module is not installed; cannot pass
    commands through to sqlplus, etc.'''    
    class Session(object):
        valid = False    
        available = False
    class YASQLSession(Session):
        pass
    class SqlPlusSession(Session):
        pass
    class SenoraSession(Session):
        pass
        
available = [s for s in [SenoraSession, YASQLSession, SqlPlusSession] if s.available]
