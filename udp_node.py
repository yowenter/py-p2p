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

    
    def connect_server(self):
        while True:
            
            self._socket.sendto(json.dumps({"from":"node","data":"ping"}),self._broker_address)
            self._local_address=self._socket.getsockname()
            self._public_address=None
            self._socket.sendto(json.dumps({"from":"node","private_ip_port":str(self._local_address)}),self._broker_address)
            data,address=self._socket.recvfrom(2048)
            if address[0]==self._broker_address[0]:
                print "received from server",data
                try:
                    data=json.loads(data)
                except:
                    print "data not json "
                if isinstance(data,dict):
                    if data.get("address") and data.get("from")=='node' and data.get("data") is not None:
                        print "broker transport another node data",data
                        node_data=None
                        try:
                            node_data=json.loads(data['data'])
                        except:
                            print "another node send no json"
                        if isinstance(node_data, dict):
                            if str(node_data.get("private_ip_port"))==str(self._local_address):
                                self._public_address=data["address"]
                                print "another node is yourself,continue"
                    if data.get("nodes"):
                        if len(data['nodes'])>1:
                            print "nodes more than one",data['nodes']
                            for n in data['nodes']:
                                if str(n)!=str(self._public_address):
                                    try:
                                        
                                        self._socket.sendto("Nice to meet U!- %s:%s"%(str(self._local_address),str(self._public_address)))
                                    except Exception as e:
                                        print "connect another node failure",str(e)
                                        
                        else:
                            continue
                        
                                
     
            else:
                print "connected to another node, received",data
                while True:
                    try:
                        
                        self._socket.sendto("Nice to meet U!- %s:%s"%(str(self._local_address),str(self._public_address)),address)
                    except Exception as e:
                        print "send to another node failure",str(e)
                        
                    time.sleep(3)
                    data,address=self._socket.recvfrom(1024)
                    print "received ",data,address
                    
                    
            