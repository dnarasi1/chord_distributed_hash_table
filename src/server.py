import glob
import sys
import hashlib
import socket

sys.path.append('gen-py')
sys.path.insert(0, glob.glob('/home/yaoliu/src_code/local/lib/lib/python2.7/site-packages')[0])

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from chord import FileStore
from chord.ttypes import SystemException, RFile, RFileMetadata, NodeID

class chordfunc:
    
    def __init__(self, port,ip):
        self.log = {}
        self.port = port
        self.ip = ip
        self.id = ip + ":"+str(port)
        

    def writeFile(self, inputF):
        #print('--------------------------------------------------')
        ipAddress = socket.gethostbyname(socket.gethostname())
        self.file = ipAddress + ':'+str(port)
        sha256file = hashlib.sha256(self.file.encode())
        self.sha256ID = sha256file.hexdigest()
        #print ('IP and port ', file)	
        filename = inputF.meta.filename
        contentHash = inputF.meta.contentHash
        checkNode = NodeID()
        checkNode = self.findSucc(contentHash)
        
        #print('checknode id:', checkNode.id, 'self: ',self.sha256ID)
        if self.sha256ID == checkNode.id: 


            if self.sha256ID in self.log:
                #x = self.log[self.sha256ID].meta.version
                #self.log[self.sha256ID].meta.version = x+1
                     
                #self.log[self.sha256ID].content = inputF.content
                
                #x = RFile()
                #x1 =  RFileMetadata()
                #x1 = self.log[self.sha256ID].meta
                #x1.version = x1.version + 1
                #self.log[self.sha256ID].meta = x1

                self.version = self.version+1
                self.content = inputF.content

                #x = self.log[self.sha256ID]
                #x.meta = RFileMetadata()
                #x.meta.version = x.meta.version + 1
                #x1 = x.meta
                #x1.version = x.meta.version + 1
                #x.RFileMetadata = x1 
               
                #x.meta.version = x.meta.version+1
                #x.content = inputF.content
                #self.log[self.sha256ID] = x
                
                #self.log[sha256ID].meta.version = x+1
                #self.log[sha256ID].content = inputF.content
            
                #x = serverFile.meta.version
                #serverFile.meta.version = x+1
                #serverFile.meta.contentHash = inputF.meta.contentHash
                #serverFile.content = inputF.content
                file = open(inputF.meta.filename, "w+")
                file.write(inputF.content)

            else:
            
                serverFile = RFile()          
                sMeta = RFileMetadata()
                file = open(filename, "w+")
                file.write(inputF.content)
                sMeta.filename = filename
                sMeta.version = 0
                self.version = sMeta.version
                sMeta.contentHash = contentHash
                serverFile.content = inputF.content
               
                self.content = serverFile.content
                serverFile.RFileMetadata = sMeta
                self.log[self.sha256ID] = serverFile
                file.close()
        else:
            y = SystemException()
            y.message = "Rserver is not the file’s successor"
            raise y

    def readFile(self,fileC):
        ipAddress = socket.gethostbyname(socket.gethostname())
        file = ipAddress + ':'+str(port)


        sha256key = hashlib.sha256(file.encode())
        sHash = sha256key.hexdigest()
        sha256val = hashlib.sha256(fileC.encode())
        contentHash = sha256val.hexdigest()
        checkNode = NodeID()
        checkNode = self.findSucc(contentHash)

        if self.sha256ID == checkNode.id:

            if sHash in self.log: 

                #sha256val = hashlib.sha256(fileC.encode())
                #sHashfile = sha256val.hexdigest()

                sFile = RFile()
                sFileMeta = RFileMetadata()
                sFileMeta.filename = fileC

                sFileMeta.version = self.version
                sFileMeta.contentHash = contentHash
                file = open(fileC, "r")
                sFile.content = file.read()
           
                print(sFile.content)
                sFile.meta = sFileMeta
            else:
                x = SystemException()
                x.message = "File Is not Present in server"
                raise x
            return sFile
        else:
            z = SystemException()
            z.message = "server is not the file’s successor"
            raise z

    def setFingertable(self,node_list):
        self.fTable = list(node_list)
        #print(*self.fTable, sep = "\n")
    
    def getNodeSucc(self):
        if not self.fTable:
            z = SystemException()
            z.message = "no fTable"
            raise z
        return self.fTable[0]
  
    def findSucc(self, key):
        qnode = NodeID()
        qnode.id = self.sha256ID
        qnode.ip = self.ip
        qnode.port = self.port
            
        nNode = NodeID()
        nNode = self.findPred(key)
      
        #print('predNode: ', nNode.id)

        if qnode.id == key:
            return qnode

        else:       

            if nNode.id == qnode.id:
                return self.getNodeSucc()
            else:
                ttransport = TSocket.TSocket(nNode.ip, nNode.port)
                ttransport.open()
                pprotocol = TBinaryProtocol.TBinaryProtocol(ttransport)
                client = FileStore.Client(pprotocol)
                cNode = NodeID()
                cNode = client.getNodeSucc()
                #ttransport.close()
                return cNode

    def findPred(self, key):
        cNode = NodeID()
        sha256id = hashlib.sha256(self.id.encode())
        cNode.id = sha256id.hexdigest()
        cNode.ip = self.ip
        cNode.port = self.port
        tempNode = NodeID()

        if not self.fTable:
            z = SystemException()
            z.message = "no fTable"
            raise z
            
        

        tempNode = self.fTable[0] 
        x = self.checkInRange(key, cNode.id, tempNode.id)
        #print('x:', x)
        while not x:
            for i in range(len(self.fTable)-1, 0,-1):
                temp = NodeID()
                temp = self.fTable[i]
                y = self.checkInRange(temp.id,cNode.id, key)
                #print('temp.id: ', temp.id, '\n', 'cNode.id:', cNode.id, '\n', 'key:', key )
                #print('y',y)
                if y:
                    ttransport = TSocket.TSocket(temp.ip, temp.port)
                    #ttransport = TTransport.TBufferedTransport(ttransport)
                    ttransport.open()
                    pprotocol = TBinaryProtocol.TBinaryProtocol(ttransport)
                    client = FileStore.Client(pprotocol)
                    #ttransport.open()
                    sNode = NodeID()
                    sNode = client.findPred(key)
                    
                   
                    ttransport.close()
                    return sNode
            break
        return cNode
                    
        
        
    def checkInRange(self, key, n, n1):
        if key>n and key<n1:
            return True
        elif n>n1:
            if key<n and key>n1:
                return True
            else:
                return False
        else:
            return False	


if __name__ == '__main__':
    sipAddress = socket.gethostbyname(socket.gethostname())
    port = int(sys.argv[1])
    chord = chordfunc(port, sipAddress)
    processor = FileStore.Processor(chord)
    transport = TSocket.TServerSocket(port = int(sys.argv[1]))
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    print('Starting the server...')
    #sipAddress = socket.gethostbyname(socket.gethostname())
    print('server IP', sipAddress, ' ,''port: ', port)
    server.serve()
	
