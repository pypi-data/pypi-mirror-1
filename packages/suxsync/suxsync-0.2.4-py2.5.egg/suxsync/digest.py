"""
Does digesting.
"""
import os, md5, optparse, logging, csv, dircache, user, re, UserDict, datetime, math, random
import config
import util

MATCHRE = re.compile( ".*\.(ogg|mp3)$" )

OLD_FILE_AGE = datetime.timedelta(hours = 1)

class digestedFile( object ):
    
    _logger = logging.getLogger( __name__ )
    
    def __init__(self, root, filePath, clear=False ):
        self._clear = clear
        self._root = os.path.abspath( root )
        self._filePath = os.path.abspath( filePath )
        
        rootLength = len( self._root.split( os.sep ) )
        
        relParts = self._filePath.split(os.sep)[rootLength:]

        if len(relParts) == 0:
            import pdb
            pdb.set_trace()

        
        self._rel = os.path.join( *relParts )
        
        self._digestFilePath = "%s.md5" % filePath        
        self._deleted = False
        
        self.__check()
        
    def __repr__(self):
        return "<%s %s:%s>" % (self.__class__.__name__, self._rel, self._md5 )
        
    
    def delete(self):
        self._logger.warn( "Deleting the file %s" % self._filePath )
        fileDir = os.path.dirname( self._filePath )
        os.remove( self._filePath )
        os.remove( self._digestFilePath )
        if len( os.listdir( fileDir ) ) == 0:
            self._logger.warn( "Deleting the directory %s" % fileDir )
            os.rmdir( fileDir )
            
        self._deleted = True
        
    def mkRow(self):
        return (self._rel, self._md5)
    
    def souldNotRefresh(self, digestDate, fileDate ):
        """
        Should we force a refresh?
        If the digest is newer than the original file then it's probably time to
        refresh... but that isnt all.
        """
        if self._clear:
            # If we are in clear mode, allways refresh.
            return False
        
        if digestDate > fileDate:
            # Find the age of the file
            fileAge =  datetime.datetime.now() - datetime.datetime.fromtimestamp(fileDate)
            
            # How many half-lifes old is this file?
            hl = util.timeDeltaToSeconds(fileAge) / util.timeDeltaToSeconds(OLD_FILE_AGE)
            assert hl > 0
            
            self._logger.info("File is %f half-lives old" % hl )
            
            refreshProb = math.e ** ( 0 - hl )
            randomNumber = random.random()
            
            if randomNumber < refreshProb:
                return False         
            return True
        return True
    
    def __check(self):
        assert os.path.exists( self._filePath )
        if not os.path.exists( self._digestFilePath ):
            # Digest does not exist
            self._logger.warn("Making digest for %s." %  self._filePath )
            dig = md5.new()
            dig.update( file(self._filePath,'rb').read() )
            self._md5 = dig.hexdigest()
            file( self._digestFilePath, 'wb' ).write( self._md5 )
            return
        else:
            digestData = os.stat( self._digestFilePath )
            fileData = os.stat( self._filePath )
            
            if self.souldNotRefresh( digestData[8], fileData[8] ):
                # Digest is older than file
                self._md5 = file( self._digestFilePath, 'rb' ).read()
                return
                
            else:
                # File is newer than digest
                os.remove( self._digestFilePath )
                self.__check()


class AudioDigest(object):
    def __init__( self, rootPath, clear=False ):
        self._root = rootPath
        assert clear in [True, False]
        self.clear = clear
        self._csvFileName = os.path.join( rootPath, config.digestFileName )
        self._csvFile = open( self._csvFileName, 'w' )
        self._csv = csv.writer( self._csvFile )
        self._files = {}

        
    def generateFileObjects(self, root ):
        files = os.walk( root, topdown=True )
        for item in files:
            for fileName in item[2]:
                filePath = os.path.join( item[0], fileName )
                if MATCHRE.match( filePath ):
                    yield digestedFile( root, filePath, clear=self.clear )
            
    
    def __call__(self):
        for fileObj in self.generateFileObjects( self._root ):
            self._csv.writerow( fileObj.mkRow() )
            self._files[ fileObj._rel ] = fileObj