import SocketServer
import threading
import socket
from configobj import ConfigObj

Ini_Filename = "echo.ini"

def readConfig(settings_path):
    configs = []
    config_file = ConfigObj(settings_path)
    
    configs_names = config_file['configs']
    for name in configs_names:
        inner_config_names = config_file[name]['send_list']
        configs.append( {'name': name,
                         'recive_ip': config_file[name]['recive_ip'],
                         'recive_port': config_file[name]['recive_port'], 
                         'send_list': []
                         })
       
        inner_config_names = config_file[name]['send_list']
        for inner_name in inner_config_names:
            send_item = { 'name':inner_name, 
                          'send_ip': config_file[name][inner_name]['send_ip'],
                          'send_port': config_file[name][inner_name]['send_port']
                        }       
            configs[len(configs) - 1]['send_list'].append(send_item)
    return configs

def ByteToHex( byteStr ):
    """
    Convert a byte string to it's hex string representation e.g. for output.
    """
    
    # Uses list comprehension which is a fractionally faster implementation than
    # the alternative, more readable, implementation below
    #   
    #    hex = []
    #    for aChar in byteStr:
    #        hex.append( "%02X " % ord( aChar ) )
    #
    #    return ''.join( hex ).strip()        

    return ''.join( [ "%02X " % ord( x ) for x in byteStr ] ).strip()

class ThreadedUDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    pass

    
class MyUDPHandler(SocketServer.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print "%s:%i wrote:" % (self.client_address[0], self.client_address[1])
        print ByteToHex(data)
        own_port = self.server.server_address[1]
        #TODO send data to right ports
        send_list =[x['send_list'] for x in config if int(x['recive_port']) == own_port ]
        for i in send_list:
            for address in i:
                print "Sendind to: ", address
                socket.sendto(data, (address['send_ip'] , int(address['send_port']) ) )
        
def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((ip, port))
    sock.send(message)
    print "sending :" , message
    sock.close()
    
def StartListening(config):
    servers_thread_list = []
    servers_list = []
    num_of_servers = -1
    for i, con in enumerate(config):
        ip, port = con['recive_ip'] , int(con['recive_port'])
        server = ThreadedUDPServer((ip, port), MyUDPHandler)
        servers_thread_list.append(threading.Thread(target=server.serve_forever) )
        servers_list.append( server )   
        num_of_servers = i + 1
    
    print num_of_servers 
    
    for server in servers_thread_list:
        server.setDaemon(True)
        server.start()
        
    #TODO, wait for something
    while True:
        s = raw_input('--> ')
        if s == 'exit':
            break
        elif s == 'test':
            client('127.0.0.1', 1111, "Hello world")
        elif s == 'config':
            print config
    
    s = raw_input('--> ')
    #close all servers
    #for server in servers_thread_list:
    #    server.shutdown()

if __name__ == "__main__":
   global config 
   config = readConfig(Ini_Filename)
   StartListening(config)
