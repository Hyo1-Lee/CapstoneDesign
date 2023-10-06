import socket, datetime, time
from threading import Thread, Lock

import re, subprocess

lock = Lock()
client = {}
PORT = 5003
    
def echo(sock, ip):
      sock.sendall(b'HELLO00000')
      time.sleep(0.2)
      while True:
           print('############33')
           data = sock.recv(1024)
           time.sleep(0.5)
            
           if not data:
                print('break#############')
                break
                
           msg = data.decode('ascii')
           print(datetime.datetime.now(), msg)
           
           from data import dataModule
           d = dataModule()        
           d.recvSignal(msg)
            
def run_socket():
     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
         t =  TCPModule()
         s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
         PORT = 5003
         print(PORT)
         
         server_address = (t.jetsonIP, PORT) 
         s.bind(server_address)
                    
         while True:
             print('listening')
             s.listen()
             print('waiting')
             conn, (ip, PORT) = s.accept()
                        
             lock.acquire()
             client[ip] = conn
             lock.release()
             t = Thread(target = echo, args = (conn, ip,))
             t.start()

def get_IP_address():
    result = subprocess.run('ifconfig wlan0',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    output = result.stdout
    pattern = r'inet\s(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    match = re.search(pattern,output)

    if match:
        inet_address = match.group(1)
        return inet_address

    return None

class TCPModule():
    def __init__(self):
        self.jetsonIP = get_IP_address()
        
    def create_TCPThread(self): #TCP start
        socket_thread = Thread(target = run_socket)
        socket_thread.start()
