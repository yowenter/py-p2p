#P2P connection example by python

##Support UDP


### 原理:  
- 每个节点先中介服务器，并告诉自己的内网ip .  

- 中介服务器接收到每个节点的内网ip ，并广播给所有节点 其他节点的外网ip 和内网ip 。

- 每个节点接收到其他节点的内网ip，外网ip 之后，分别发送信息。

###reference
p2pnat[http://www.bford.info/pub/net/p2pnat/]







