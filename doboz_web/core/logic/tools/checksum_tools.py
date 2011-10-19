import hashlib
from twisted.internet import reactor, defer
from twisted.python import log,failure

def generate_hash(filePath,chunkSize=128):
    d=defer.Deferred()
    def _generate(*args,**kwargs):
        f = open(filePath,"rb")
        md5 = hashlib.md5()
        while True:
            data=f.read(chunkSize)
            if not data:
                break
            md5.update(data)
        f.close()
        digest=md5.hexdigest()
        
        return digest
    
    d.addCallback(_generate)
    return d
    
def compare_hash(result,hash,filePath,chunkSize=128):
    
    def _compare(*args,**kwargs):
        f = open(filePath,"rb")
        md5 = hashlib.md5()
        while True:
            data=f.read(chunkSize)
            if not data:
                break
            md5.update(data)
        f.close()
        digest=md5.hexdigest()
        if hash==digest:
            return True
        else:
            raise Exception("MD5 checksum mismatch")
    d=defer.succeed(_compare())
    return d