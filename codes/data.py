from firebase_admin import db, storage
from uuid import uuid4
from blue import BlueModule
import time
from queueModule import shared_queue
import os 

BASEDIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
new_token = 0
BT = None
current_hangerNum = 1

#insert new data
#dir.update({2:
 #           {"id":2, 
  #           "category":"coat", 
  #           "hangerNum":0, 
  #           'pic':'gs://smartcloset-bc3a3.appspot.com/003.png', 
  #           'setNum':0, 
  #           'voiceWord':'',
   #          "writeDate":'2023-04-30 14:17:30'}})
#############################################################

def bt():
    global BT
    BT = BlueModule()
    BT.connect_dev()

class dataModule():
    dir = None
    bk = None
    voiceOnoff = ''

    def updateIP(self):
        from soc import TCPModule
        t = TCPModule()
        print('jetsonIP: ' + str(t.jetsonIP))
        db.reference('closet').update({'jetsonIP' : t.jetsonIP})

    def picUpload(self, id, filename):
        global new_token
        self.bk = storage.bucket()
        print("bk: "+str(self.bk))

        blob = self.bk.blob(filename)
        new_token = uuid4()
        metadata = {'firebaseStorageDownloadTokens':new_token}
        blob.metadata = metadata
        dir_path = BASEDIR + "/data/support/"
        blob.upload_from_filename(filename=dir_path+str(id)+'/'+filename, content_type='image/jpg')

    def insertData(self, id,category,hangerNum,picname,voiceWord):
        global new_token

        self.dir = db.reference('closet/clothes')
        self.dir.update({id:
           {"id":id, 
            "category":category, 
            "hangerNum":hangerNum, 
            'picPath':'https://firebasestorage.googleapis.com/v0/b/smartcloset-bc3a3.appspot.com/o/'+picname+'?alt=media'+'&token='+str(new_token),
            'setNum':0, 
            'voiceWord':voiceWord,
            "writeDate":''}})

    def recvSignal(self, data): #TCP with app
        r = data.split()
        if r[0] == 'insertData':
            if r[1] == 'exe':
                shared_queue.put('등록 모드 실행')
            else:
                if r[1] == 'end':
                    shared_queue.put('등록 모드 종료')           
        else:
            if r[0] == 'hanger':
                self.moveCloset(int(r[1]))

    def moveCloset(self, hangerNum):
            global current_hangerNum

            if hangerNum == 0:
                pass
                
            elif hangerNum == -1:
                BT.transmit('R')
                BT.transmit('1')
                print('to the right')
                
            elif hangerNum == -2:
                BT.transmit('L')
                BT.transmit('1')
                print('to the left')
                
            else:
                num = current_hangerNum-hangerNum
                print("cur_hag:", current_hangerNum)

                if abs(num) > 7:
                    num = (15 - abs(num))*(num//abs(num))*-1
                print("num is : ",num)
                current_hangerNum = hangerNum
                if num > 0:
                    BT.transmit('R')
                    time.sleep(0.5)
                    BT.transmit(chr(ord('a') + abs(num)))
                    print('move to hanger' + str(hangerNum))
                elif num < 0:
                    BT.transmit('L')
                    time.sleep(0.5)
                    BT.transmit(chr(ord('a') + abs(num)))
                    print('move to hanger' + str(hangerNum))

                