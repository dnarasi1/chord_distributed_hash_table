import sys
import glob
import hashlib
sys.path.append('gen-py')
sys.path.insert(0, glob.glob('/home/yaoliu/src_code/local/lib/lib/python2.7/site-packages')[0])

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from chord import FileStore
from chord.ttypes import SystemException, RFile,  RFileMetadata, NodeID 

def main():
    transport = TSocket.TSocket(sys.argv[1], int(sys.argv[2]))
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = FileStore.Client(protocol)
    transport.open()

    wFile = RFile()    
    wFileMeta =  RFileMetadata()
    wFileMeta.filename = "sample.txt"
    sha256file = hashlib.sha256(wFileMeta.filename.encode())
    wFileMeta.contentHash = sha256file.hexdigest()
    wFile.meta = wFileMeta
    wFile.content = "what now?"
    #print('dddddddddddddddd : ',sha256file.hexdigest() ) 
    client.writeFile(wFile)

    rFile = RFile()
    rFile = client.readFile('aaa.txt')
    print('sha256: ', rFile.meta.contentHash)
    print('content: ', rFile.content)

    nodeID = NodeID()
    #nodeID = client.getNodeSucc()
    #keey = '69c9b6900f19eeddc1c9c99928410ddf045adb877f565487546c9cf05c9e2fd2'
    #nodeID = client.findPred(sha256file.hexdigest())
    #print('node', nodeID)

        

    transport.close()


if __name__ == '__main__':
        main()
