#!/Library/Frameworks/Python.framework/Versions/2.5/Resources/Python.app/Contents/MacOS/Python

import optparse
from suxsync.digest import AudioDigest
            
if __name__ == "__main__":
    parser = optparse.OptionParser()
    
    parser.add_option("-r", "--root", dest="root", metavar="DIRECTORY", 
                  help="Root of your synchronised filesystem")
    
    parser.add_option("-l", "--clear", dest="clear", metavar="CLEAR",
                      action="store_true",
                      default=False, 
                      help="Rebuild all digests, regardless of age. This may take a long time.")
    
    (options, args) = parser.parse_args()
    
    try:
        assert options.root != None
    except AssertionError, ae:
        parser.error('You must provide a root path.')
    
    foo = AudioDigest(rootPath = options.root, clear=options.clear )
    foo()
    
    
            
        