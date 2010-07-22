from socket import *

data = "python is sending a TCP packet\n"

testsocket=socket(AF_INET,SOCK_STREAM)

testsocket.connect(('192.168.0.223',55))

testsocket.send(data)

testsocket.close()

