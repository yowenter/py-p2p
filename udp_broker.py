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
        _node=self.find_node_index(public_address)
        if _node is not None:
            return

        print "new node added .",public_address,private_address
        self._addrs.append({"public":public_address,'private':private_address})
        
    
    def find_node_index(self,public_address):
        for i,r in enumerate(self._addrs):
            if str(r['public'][0])==str(public_address[0]) and str(r['public'][1])==str(public_address[1]):
                return i
            
    def update_node(self,public,private_addr):
        i=self.find_node_index(public)
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
            self._socket.sendto(json.dumps({"data":"pong","from":"server","address":address}),address)
            try:
                d=json.loads(data)
                if d.get("data")=='join' and d.get("from")=='node':
                    self.registry.add_node(address)
                if d.get("private"):
                    self.registry.update_node(address,d['private'])
            except Exception as e:
                print "received data not json ,parse failure.",data,str(e)
                
                
            time.sleep(3)
            nodes={"nodes": self.registry._addrs}
            self.registry.notify_all(json.dumps(nodes))
            
            
            
if __name__=='__main__':
    server_port=8001
    print "Starting Listen...",server_port
    udp_broker=MyUDPBroker('',server_port,Registry())
    udp_broker.run()
    

    
            
        
        