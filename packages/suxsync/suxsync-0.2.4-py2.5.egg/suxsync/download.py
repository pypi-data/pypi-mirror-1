import logging, urllib2, threading, os
from digest import digestedFile
import Queue
import config

opener = urllib2.build_opener()
opener.addheaders = [('User-agent', '%s/%s' % ( config.agentString, config.versionString ))]

class downloadThread( threading.Thread ):
    def __init__(self, downloadQueue):
        threading.Thread.__init__( self )
        self.dc = downloadQueue
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def run(self):
        self.logger.info( "Thread %s starting." % self.getName() )
        try:
            while True:
                di = self.dc.get(block=False)
                result = di.download()
        except Exception, e:
                    self.logger.exception( repr(e) )            
                    import pdb
                    pdb.set_trace()
                    raise
                    
        self.logger.info("Thread %s has ended." % self.getName() )

class downloadRequest( object ):
    def __init__(self, remote, root, rel, digest):
        self._remote = remote
        self._root = os.path.abspath( root )
        self._rel = rel
        self._local = os.path.join( self._root, *( self._rel.split( os.sep ) ) )
        self._digest = digest
        self._logger = logging.getLogger( self.__class__.__name__ )

    def mkDir( self, localDir ):
        if os.path.exists( localDir ) and os.path.isdir( localDir ):
            return
        else:
            parentPath, dirName = os.path.split( localDir )
            self.mkDir( parentPath )
            os.mkdir( localDir )
    
    def download( self ):
        url="%s?%s" % (self._remote, config.queryString)
        
        try:
            dowloadStream = opener.open( url )
        except urllib2.HTTPError, hte:
            self._logger.warn( "Failure to open %s" % url ) 
            raise
        
        localDir = os.path.dirname( self._local )
        self.mkDir( localDir )
        
        self._logger.info( "Downloading from %s." % url )
        localFile = file( self._local, 'wb' ).write( dowloadStream.read() )
        fullPath = os.path.join( self._root, *self._rel.split( os.sep ) )
        self._digested = digestedFile( self._root, fullPath )
        assert self._digested._md5 == self._digest
        self._logger.info( "Saved " )
        
        # Return a digested thing.
        return self._digested
        
        
class suckyDownloader( object ):
    def __init__(self, downloadQueue, threads=1):
        self.downloadQueue = downloadQueue
        self.downloadThreads = []
        self.threadcount = threads
        self._logger = logging.getLogger(self.__class__.__name__)
        
        
    def __call__(self):
        if self.threadcount > 0:
            self.threadedDownload()
        else:
            self.nonThreadedDownload()
            
    def nonThreadedDownload(self):
        try:
            while True:
                downloadItem = self.downloadQueue.get( block=False )
                downloadItem.download()
        except Queue.Empty, qe:
            self._logger.info("No more items to download.")
        
    def threadedDownload(self):
        for threadNo in range(0, self.threadcount):
            newThread = downloadThread( downloadQueue=self.downloadQueue )
            newThread.setName( "Download %i" % threadNo )
            self.downloadThreads.append( newThread )
            
        for thread in self.downloadThreads:
            thread.start()
            
        for thread in self.downloadThreads:
            thread.join()
        
        
        
        
         
        
        