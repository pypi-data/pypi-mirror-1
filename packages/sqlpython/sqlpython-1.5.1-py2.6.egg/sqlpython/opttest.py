import optparse
parser = optparse.OptionParser()
parser.add_option(optparse.make_option('-a',action='store_const',const=('fish',),dest='opts',default=('a','b')))

(options, args) = parser.parse_args()
print options