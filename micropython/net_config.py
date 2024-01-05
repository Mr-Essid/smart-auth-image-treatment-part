import network
import time
from time import sleep

net = network.WLAN(network.STA_IF)

"""
    THIS script CONTAINE ( (connect) function that connect to wifi, (net) instance of WLAN )   
"""



class NetworkNotFound(RuntimeError):
    def __init__(self, message = "network not found!"):
        self.message = message
        super().__init__(message)
        
        
        
        
class ConnectionRefaused(RuntimeError):
    def __init__(self, message='connection refaused'):
        self.message = message
        super().__init__(message)
        
        

def connect(ssid, password):
    net.active(False)
    net.active(True)
    
    exists = False
    while not exists:
        list_networks = net.scan()
        print('try to find the network')
        for net_ in list_networks:
            if ssid == net_[0].decode('utf-8'):
                exists = True
        sleep(0.5)
        
    
    net.connect(ssid, password)
    time_out = 8 # 8 seconds
    print('connecting', end=' ')
    while not net.isconnected():
        time.sleep(1)
        time_out -= 1
        print('.', end= '')
        if time_out == 0:
            raise  ConnectionRefaused
    
    print('\nconnected')
    print(net.ifconfig())
    
    


if __name__ == '__main__':
    #connect('test', '00000000')
    pass
        
        
        
        
        
    
    
    
    
    