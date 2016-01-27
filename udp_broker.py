#-*-encoding:utf-8-*-
import logging
import socket
import json
import time
import gevent.monkey

gevent.monkey.patch_all()
logger = logging.getLogger('udp_broker')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('udp_broker.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


class Registry:
    def __init__(self,_socket=None):
        self._nodes=[]
        self._socket=_socket
    
    def notify_all(self,data):
        for n in self._nodes:
            self._socket.sendto(data,n['public'])
            
    
    def is_node_alive(self,public_address):
        i=self.find_node_index(public_address)
        if i is not None:
            node=self._nodes[i]
            if int(time.time())-node.get("latest_heartbeat",0) <3600:
                return True
            else:
                self._nodes.pop(i)
                print "node dead",node
                return False
        return False
    
    def heartbeat_node(self,public_address):
        i=self.find_node_index(public_address)
        if i is not None:
            self._nodes[i]['latest_heartbeat']=int(time.time())
             
                
    def add_node(self,public_address,private_address=None):
        _node=self.find_node_index(public_address)
        if _node is not None:
            self.heartbeat_node(public_address)
            return

        logger.info( "new node added .%s %s",public_address,private_address)
        self._nodes.append({"public":public_address,'private':private_address,"latest_heartbeat":int(time.time())})
        
    
    def find_node_index(self,public_address):
        for i,r in enumerate(self._nodes):
            if str(r['public'][0])==str(public_address[0]) and str(r['public'][1])==str(public_address[1]):
                return i
            
    def update_node(self,public,private_addr):
        i=self.find_node_index(public)
        self._nodes[i]['private']=tuple(private_addr)
        logger.info("Node updated %s",self._nodes[i])
        self.heartbeat_node(public)
             

class MyUDPBroker:
    def __init__(self,host,port,registry):
        self._socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self._socket.bind((host,port))
        self.registry=registry
        self.registry._socket=self._socket
        
    def run(self):
        gevent.spawn(lambda:ping_to_nodes(self))
#         gevent.spawn(lambda:publish_nodes(self))
        
        while True:
            data,address=self._socket.recvfrom(1024)
            self._socket.sendto(json.dumps({"data":"pong","from":"server","address":address}),address)
            self.registry.heartbeat_node(address)
            try:
                d=json.loads(data)
                if d.get("data")=='join' and d.get("from")=='node':
                    self.registry.add_node(address)
                    nodes={"nodes": self.registry._nodes}
                    self.registry.notify_all(json.dumps(nodes)) 
                if d.get("private"):
                    self.registry.update_node(address,d['private'])
            except Exception as e:
                logger.error("received data not json ,parse failure.%s %s",data,str(e))
                

            

def ping_to_nodes(broker):
    logger.info("Start to ping nodes every few seconds.")
    while True:
        broker.registry.notify_all(json.dumps({"from":"server","data":"ping"}))
        time.sleep(6)
     
# def publish_nodes(broker):
#     print "start publish nodes every few seconds"
# #     while True:
#     nodes={"nodes": broker.registry._nodes}
#     broker.registry.notify_all(json.dumps(nodes)) 
# #     time.sleep(60)
#        
            
if __name__=='__main__':
    server_port=8001
    logger.info("开始监听...%s",server_port)
    udp_broker=MyUDPBroker('',server_port,Registry())
    udp_broker.run()
    

    
            
        
        
