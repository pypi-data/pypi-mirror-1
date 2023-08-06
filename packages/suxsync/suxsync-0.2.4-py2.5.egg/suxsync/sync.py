import config
from digest import AudioDigest, digestedFile
from download import downloadRequest, suckyDownloader
import urllib2, urllib, csv, Queue, logging, sys, os

class SuckySync(object):
    """
    Perform a sync
    """
    def __init__(self, root, remoteRoot, threads=1):
        self._root = root
        self._remote = remoteRoot
        self._digests = AudioDigest( self._root )
        self._threads = threads
        self._logger = logging.getLogger( self.__class__.__name__ )
    
    
    def getRemoteDigests(self):
        digestUrl = "%s/%s" % ( self._remote, config.digestFileName )
        
        try:
            digestStream = urllib2.urlopen( digestUrl )
        except urllib2.HTTPError, hte:
            self._logger.critical("Could not download digest %s" % digestUrl )
            sys.exit(1)
            
        csvSource=csv.DictReader( digestStream, fieldnames=config.digestFields )
        for row in csvSource:
            yield row
         
    def __call__(self):
        # Do the magic
        self._logger.info('Sync started. PID: %i' % os.getpid() )
        remoteDigests={}
        
        # Make our own digest
        self._digests()
        
        # Do the sync
        for item in self.getRemoteDigests():
            remoteDigests[item['rel']] = item['md5']
        
        local = self._digests._files.keys() 
        remote = remoteDigests.keys() 
        
        delete = [a for a in local if not a in remote]
        download = [a for a in remote if not a in local]
        check = [a for a in local if a in remote]
        
        for item in check:
            localDigest = self._digests._files[ item ]._md5
            remoteDigest = remoteDigests[ item ]
            if localDigest != remoteDigest:
                self._logger.warn( "File has differed: %s" % item )
                delete.append( item )
                download.append( item )
        
        for toDelete in delete:
            digestedFile = self._digests._files[ toDelete ]
            digestedFile.delete()
        
        downloadQueue = Queue.Queue()
        
        for item in download:
            # Make a download queue
            downloadUrl = "%s/%s" % ( self._remote, urllib.quote( item ) )
            remoteDigest = remoteDigests[ item ]
            downloadItem = downloadRequest( remote=downloadUrl, root=self._root, rel=item, digest=remoteDigest )
            downloadQueue.put( downloadItem )
            
        downloader = suckyDownloader( downloadQueue, threads = self._threads )
        downloader()
            
        # Re-digest
        self._digests()
        