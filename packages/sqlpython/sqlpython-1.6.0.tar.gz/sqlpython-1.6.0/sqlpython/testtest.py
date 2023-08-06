import pyparsing

class Ob2(object):
    continuationPrompt = '> '
    prompt = 'testdata@eqdev> '
    
def transcriptReader(cmdapp, filename='test_cmd2.txt'):
    '''Usage: result = transcriptReader(cmdapp, filename)
    Assists in writing unit test suites for an instance of cmd2 (cmdapp) 
    by reading the transcript of an interactive session (filename)
    and returning a list of {command, response} dictionaries.
    '''
    
    tfile = open(filename)
    txt = tfile.read()
    tfile.close()
    currentpos = 0
    while True:
        prompt = pyparsing.Suppress(pyparsing.lineStart + cmdapp.prompt)
        continuationPrompt = pyparsing.Suppress(pyparsing.lineStart + cmdapp.continuationPrompt)
        cmdtxtPattern = (prompt + pyparsing.restOfLine + pyparsing.ZeroOrMore(
            pyparsing.lineEnd + continuationPrompt + pyparsing.restOfLine))("command")
        (thiscmd, startpos, endpos) = cmdtxtPattern.scanString(txt[currentpos:], maxMatches=1).next()
        # we can't scan all at once, unfortunately, because prompt may change during session
        yield {'command': ''.join(thiscmd.command), 
               'response': txt[currentpos+endpos:],
               'lineNum': txt.count('\n', 0, currentpos+startpos) + 1}
        currentpos += endpos
        
class TranscriptReader(object):
    def __init__(self, cmdapp, filename='test_cmd2.txt'):
        self.cmdapp = cmdapp
        tfile = open(filename)
        self.transcript = tfile.read()
        tfile.close()
        self.bookmark = 0
    def refreshCommandFinder(self):
        prompt = pyparsing.Suppress(pyparsing.lineStart + self.cmdapp.prompt)
        continuationPrompt = pyparsing.Suppress(pyparsing.lineStart + self.cmdapp.continuationPrompt)
        self.cmdtxtPattern = (prompt + pyparsing.restOfLine + pyparsing.ZeroOrMore(
            pyparsing.lineEnd + continuationPrompt + pyparsing.restOfLine))("command")        
    def inputGenerator(self):
        while True:
            self.refreshCommandFinder()
            (thiscmd, startpos, endpos) = self.cmdtxtPattern.scanString(self.transcript[self.bookmark:], maxMatches=1).next()
            lineNum = self.transcript.count('\n', 0, self.bookmark+startpos) + 2
            self.bookmark += endpos
            yield (''.join(thiscmd.command), lineNum)
    def nextExpected(self):
        self.refreshCommandFinder()
        try:
            (thiscmd, startpos, endpos) = self.cmdtxtPattern.scanString(self.transcript[self.bookmark:], maxMatches=1).next()
            result = self.transcript[self.bookmark:self.bookmark+startpos]
            self.bookmark += startpos
            return result
        except StopIteration:
            return self.transcript[self.bookmark:]
    
reader = TranscriptReader(Ob2(), 'test_sqlpyPlus.txt')
g = reader.inputGenerator()
g.next()