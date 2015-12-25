import socket
import os
import json
import time
import gevent
import random
import gevent.monkey

gevent.monkey.patch_all()

SERVER_IP=os.getenv("SERVER_IP","107.170.255.192")
SERVER_PORT=os.getenv("SERVER_PORT",8900)


class Node:
    def __init__(self,broker_ip,broker_port,local_port):
        self._socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._broker_address=(broker_ip,broker_port)
        self._socket.bind(('',local_port))
        self._public_address=None
        self._local_address=(self._get_ip(),local_port)
        self._connect_another_node=False
        print "Node init finished.",self._broker_address,self._local_address
        
    def _get_ip(self):
        public_host=socket.gethostbyname('baidu.com')
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((public_host,80))
        return s.getsockname()[0]
   
        
    
    def connect_server(self):
        gevent.spawn(lambda :ping_to_server(self))
        
        while True:
            if not self._connect_another_node:
                print "Trying to join p2p..."
                self._socket.sendto(json.dumps({"from":"node","data":"join"}),self._broker_address)
                
                self._socket.sendto(json.dumps({"from":"node","private":self._local_address}),self._broker_address)
                time.sleep(5)
            data,address=self._socket.recvfrom(2048)
            if address[0]==self._broker_address[0]:
                try:
                    data=json.loads(data)
                except:
                    print "data not json ",data
                    
                if isinstance(data,dict):
                    if data.get("data")=="ping":
                        print "received server ping"
                        
                    if data.get("address") and not self._public_address:
                        print "Get self public address",data['address']
                        self._public_address=tuple(data['address'])

                    if data.get("nodes"):
                        
                        if len(data['nodes'])>1:
                            print "Get nodes:",data['nodes']
                            for n in data['nodes']:
                                if not self._public_address:
                                    print "self public address not init."
                                    continue
                                
                                if str(n['public'])!=str(list(self._public_address)):
                                    self._socket.sendto("To %s,\nNice to meet U! \n-From %s:%s"%(str(address),str(self._local_address),str(self._public_address)),tuple(n['public']))
                                if n['private'] and n['private']!=str(list(self._local_address)): 
                                    self._socket.sendto("To %s,\nNice to meet U! \n-From %s:%s"%(str(address),str(self._local_address),str(self._public_address)),tuple(n['private']))        
                                                                    
                                                
                        else:
                            continue
                        
                                
            else:
                print "Received %s,%s\n"%(str(address),data)

                self._socket.sendto("Nice to hear from U . \nFrom %s:%s"%(str(self._local_address),str(self._public_address)),address)
                self._connect_another_node=True
                time.sleep(3)
            
            


def ping_to_server(node):
    print "Start to  ping server every few seconds."
    while True:
        node._socket.sendto(json.dumps({"from":"node","data":"ping"}),node._broker_address)
        time.sleep(6)
        
        
        
if __name__=='__main__':
    local_port=random.randint(2048,60000)
    print "start node",local_port
    n=Node(SERVER_IP,SERVER_PORT,local_port)   
    n.connect_server()       
                    
            
