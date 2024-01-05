import socket, camera, sys
from net_config import net, connect
import struct
import io
from time import sleep
from machine import SoftI2C, Pin
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
import _thread
import machine

'''
socket AP_INET, SOCK_STREAM
'''
SERVER_ADDRESS = ('4.tcp.eu.ngrok.io', 15424)
SYNC = 'CLIENT_CAM'.encode()
GOT_FRAME = 'GOT_FRAME'
SSID = 'test'
PASSWORD = '00000000'





relayPin = Pin(13, Pin.OUT)
relayPin.value(0)



#apiKey = "HelloWorld"


if not net.isconnected():
    connect(SSID, PASSWORD)


client_socket = socket.socket()
#client_socket.settimeout(10) # 10 seconds will throw exception cause of wait 

payload_size = struct.calcsize(">L")
is_init_ = camera.init()
if not is_init_:
    print('Camera Failed To Start')
    sys.exit(-1)
    
camera.framesize(9)


def getName(_socket__: socket.socket):
    while True:
        try: 
            payload = _socket__.recv(1024)
        except Exception as e:
            print(e)
            break
        if payload == b'':
            break
        
        else:
            relayPin.value(1)
            sleep(5)
            relayPin.value(0)
            print('bay')







try:
    client_socket.connect(SERVER_ADDRESS)
    client_socket.send(b'NC')
    
except OSError as e:
    print('run the server!')
    camera.deinit()
    sys.exit(-1)
    


_thread.start_new_thread(getName, (client_socket, ))


file = client_socket.makefile('wb')

print('currently sending frames')
buffer = io.BytesIO()

counter = 0
try:
    while net.isconnected():
        buffer_ = camera.capture()
        len_ = len(buffer_)
        header = struct.pack('<L', len_)
        try:
            file.write(header)
            file.write(buffer_)
        except OSError as e:
            print(str(e))
            try:
                print('reconncting to server.')
                client_socket.close()
                client_socket = socket.socket()
                client_socket.connect(SERVER_ADDRESS)
                client_socket.send(b'NC')
                file = client_socket.makefile('wb')
                counter = 0
            except OSError as e:
                counter += 1
                print(counter)
                sleep(1)
            if counter == 40:
                machine.reset()
                break
        sleep(0.1)
    else:
        print("Try to Reconnect To WiFi")
        connect(SSID, PASSWORD)
        sleep(1)
        

except KeyboardInterrupt as e:
    print(e)
    print('bay')
    
print('release ressources')

camera.deinit()



