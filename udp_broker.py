import socket
import json
import time

class Registry:
    def __init__(self,_socket=None):
        self._addrs=[]
        self._socket=_socket
    
    def notify_all(self,data):
        for i,r in enumerate(self._addrs):
            try:
                self._socket.sendto(data,r)
            except Exception as e:
                print "notify address failure",r,str(e)
                self._addrs.pop(i)
                
                    
    

                
    def add_node(self,address):
        _node=self.find_node(address)
        if _node:
            return

        print "new node added .",address
        self._addrs.append(address)
        
    
    def find_node(self,address):
        for r in self._addrs:
            if r[0]==address[0] and r[1]==address[1]:
                return r
             

class MyUDPBroker:
    def __init__(self,host,port,registry):
        self._socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self._socket.bind((host,port))
        self.registry=registry
        self.registry._socket=self._socket
        
    def run(self):
        while True:
            data,address=self._socket.recvfrom(1024)
            self.registry.add_node(address)
            self._socket.sendto(json.dumps({"data":"pong","from":"server"}),address)
            time.sleep(3)
            notification={"address":list(address),"from":"node","data":data}
            self.registry.notify_all(json.dumps(notification))
            time.sleep(3)
            nodes={"nodes":[list(r) for r in self.registry._addrs]}
            self.registry.notify_all(json.dumps(nodes))
            
            
            
if __name__=='__main__':
    server_port=8001
    print "Starting Listen...",server_port
    udp_broker=MyUDPBroker('',server_port,Registry())
    udp_broker.run()
    

    
            
        
        