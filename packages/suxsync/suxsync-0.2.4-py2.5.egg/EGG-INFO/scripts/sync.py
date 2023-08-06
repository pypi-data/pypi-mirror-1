#!/Library/Frameworks/Python.framework/Versions/2.5/Resources/Python.app/Contents/MacOS/Python
import optparse, user, os
from suxsync.sync import SuckySync

if __name__ == "__main__":
    parser = optparse.OptionParser()
    
    parser.add_option("-r", "--root", dest="root", metavar="DIRECTORY", 
                  help="Root of your synchronised filesystem")
    
    parser.add_option("-u", "--url", dest="remoteRoot", metavar="URL", 
                  help="A url for the remote site that we need to sync against.")
                  
    parser.add_option("-t", "--threads", dest="threads", metavar="NUMBER", default=3, type='int', 
                  help="How many download threads should we run at once?.")
    
    (options, args) = parser.parse_args()
    
    try:
        assert options.root
        assert options.remoteRoot
    except AssertionError, ae:
        parser.print_help()
        parser.error("Missing value.")
    
    fod = SuckySync( root=os.path.abspath( options.root ), remoteRoot=options.remoteRoot, threads=options.threads )
    
    fod()
    