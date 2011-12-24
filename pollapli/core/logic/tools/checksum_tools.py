import hashlib
from twisted.internet import reactor, defer
from twisted.python import log,failure

class ChecksumTools(object):
    
    @staticmethod
    def generate_hash(filePath,chunkSize=128):
        """generate an md5 hash for given file name"""
        def _generate(*args,**kwargs):
            inputFile = open(filePath, "rb")
            md5 = hashlib.md5()
            while True:
                data = inputFile.read(chunkSize)
                if not data:
                    break
                md5.update(data)
            inputFile.close()
            digest = md5.hexdigest()
            return digest

        return defer.maybeDeferred(_generate)
    
    @staticmethod
    def compare_hash(hash,filePath,chunkSize=128):
        def _compare(*args,**kwargs):
            f = open(filePath, "rb")
            md5 = hashlib.md5() 
            while True:
                data = f.read(chunkSize)
                if not data:
                    break
                md5.update(data)
            f.close()
            digest = md5.hexdigest()
            return hash == digest
        return  defer.maybeDeferred(_compare)