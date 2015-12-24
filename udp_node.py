import socket
import os
import json
import time
SERVER_IP=os.getenv("SERVER_IP")
SERVER_PORT=os.getenv("SERVER_PORT")


class Node:
    def __init__(self,broker_ip,broker_port,local_port):
        self._socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._broker_address=(broker_ip,broker_port)
        self._socket.bind(('',local_port))
        self._public_address=None
        self._local_address=(self._get_ip(),local_port)
        self._connect_another_node=False
        
    def _get_ip(self):
        public_host=socket.gethostbyname('github.com')
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((public_host,80))
        return s.getsockname()[0]
   
        
    
    def connect_server(self):
        while True:
            if not self._connect_another_node:
                self._socket.sendto(json.dumps({"from":"node","data":"ping"}),self._broker_address)
                
                self._socket.sendto(json.dumps({"from":"node","private":self._local_address}),self._broker_address)
            
            data,address=self._socket.recvfrom(2048)
            if address[0]==self._broker_address[0]:
                print "received from server",data
                try:
                    data=json.loads(data)
                except:
                    print "data not json "
                    
                if isinstance(data,dict):
                    if data.get("your_address") and not self._public_address:
                        self._public_address=tuple(data['your_address'])

                    if data.get("nodes"):
                        if len(data['nodes'])>1:
                            print "nodes more than one",data['nodes']
                            for n in data['nodes']:
                                if not self._public_address:
                                    print "self public address not fetch."
                                    continue
                                if str(n['public'])!=str(list(self._public_address)):
                                    self._socket.sendto("Nice to meet U!- %s:%s"%(str(self._local_address),str(self._public_address)),tuple(n['public']))
                                    self._socket.sendto("Nice to meet U!- %s:%s"%(str(self._local_address),str(self._public_address)),tuple(n['private']))                                        
                                                
                        else:
                            time.sleep(5)
                            continue
                        
                                
            else:
                print "connected to another node!!! received",data
                while True:

                    self._socket.sendto("Nice to meet U!- %s:%s"%(str(self._local_address),str(self._public_address)),address)

                    time.sleep(3)
                    data,address=self._socket.recvfrom(1024)
                    print "received ",data,address
                    self._connect_another_node=True

if __name__=='__main__':
    n=Node(SERVER_IP,SERVER_PORT,7082)   
    n.connect_server()       
                    
            
