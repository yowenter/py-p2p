import socket
import os
import json
SERVER_IP=os.getenv("SERVER_IP")
SERVER_PORT=os.getenv("SERVER_PORT")




class Node:
    def __init__(self,server_ip,server_port,local_port):
        self._server_ip=server_ip
        self._server_port=server_port
        self._local_port=local_port
        
        self._server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT,1)
        self._server_socket.bind(('',self._local_port))
        
        
    def connect_to_server(self):
        self._server_socket.connect((self._server_ip,self._server_port))
        local_ip_port=self._server_socket.getsockname()
        data=json.dumps({"from":"node","data":str(local_ip_port)})
        self._server_socket.sendall(data)
        
    def listen(self):
        self._local_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self._local_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._local_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT,1)
        self._local_socket.bind(('',self._local_port))
        self._local_socket.listen(5)
        
        