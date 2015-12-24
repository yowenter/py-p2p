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
                self._socket.sendto(data,r['public'])
            except Exception as e:
                print "notify address failure",r,str(e)
                self._addrs.pop(i)
                
                    
    

                
    def add_node(self,public_address,private_address=None):
        _node=self.find_node(public_address)
        if _node:
            return

        print "new node added .",public_address,private_address
        self._addrs.append({"public":public_address,'private':private_address})
        
    
    def find_node(self,address):
        for i,r in enumerate(self._addrs):
            if r['public'][0]==address[0] and r['public'][1]==address[1]:
                return i
    def update_node(self,public,private_addr):
        i=self.find_node(public)
        self._addrs[i]['private']=tuple(private_addr)
        
             

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
            self._socket.sendto(json.dumps({"data":"pong","from":"server","your_address":list(address)}),address)
            try:
                d=json.loads(data)
                if d.get("private"):
                    self.registry.update_node(address,d['private'])
            except Exception as e:
                print "parse received data failure",data,str(e)
                
                
            time.sleep(3)
            nodes={"nodes": self.registry._addrs}
            self.registry.notify_all(json.dumps(nodes))
            
            
            
if __name__=='__main__':
    server_port=8001
    print "Starting Listen...",server_port
    udp_broker=MyUDPBroker('',server_port,Registry())
    udp_broker.run()
    

    
            
        
        