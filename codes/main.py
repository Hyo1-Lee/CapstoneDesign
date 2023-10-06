import os, sys, cv2, time

from dataloader import load_support, load_query
from camera_loader import gstreamer_pipeline
from test import Inference

#firebase
import firebase_admin
from firebase_admin import credentials, db, storage
from threading import Thread

from soc import TCPModule
from data import dataModule 
from data import bt

from voice import listener, speak, listen, answer, exeRegisterMode, update_dir, take_pic, change_pic_flag, update_dirSize, is_registering
from queueModule import shared_queue

sys.path.append(os.path.dirname(os.path.realpath(os.path.dirname(__file__))))
BASEDIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

db_url = 'https://smartcloset-bc3a3-default-rtdb.firebaseio.com/'
cred = credentials.Certificate('./smartcloset-bc3a3-firebase-adminsdk-dffau-ffe7840dc6.json')
dafault_app = firebase_admin.initialize_app(cred, {'databaseURL':db_url,
    #gs://smartcloset-bc3a3.appspot.com 
    'storageBucket':f"smartcloset-bc3a3.appspot.com"})   

def main():
    TCP_Module = TCPModule()
    bt()
    data_Module = dataModule()

    firebase_admin.db.reference('closet/voiceOnoff').listen(listener)
    data_Module.dir = db.reference('closet/clothes')
    data_Module.bk = storage.bucket()
    update_dir(data_Module.dir)

    TCP_Module.create_TCPThread()
    data_Module.updateIP()
   
    listen_thread = Thread(target = listen)
    listen_thread.start()
    
    inf = Inference()
    args = inf.args
    model = inf.model
    embedding = inf.embedding

    q_id = 0
    s_id = 0
    c_num = args["num_classes"]+1
    last_cloth = []
    inf_que = []
    last_idx=0
    init_flag = True
    data=''
    
    print(gstreamer_pipeline(flip_method=0))
    video_capture = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
    speak('스마트 옷장이 켜졌습니다.')
    if video_capture.isOpened():
        try:
            while True:
                time.sleep(0.1)
                _, frame = video_capture.read()\

                if init_flag:
                    while True:
                        dir_path = BASEDIR + "/data/support/1/"
                        if not os.path.exists(dir_path):
                            os.mkdir(dir_path)  
                        cv2.imwrite(dir_path + "1-%d.jpg"%s_id, frame)
                        time.sleep(0.1)
                        s_id += 1
                        if s_id == args['num_support']:
                            s_id = 0
                            init_flag = False
                            break
                    support = load_support(args)
                    update_dirSize(c_num)

                if not shared_queue.empty():
                    data = shared_queue.get()
                    if data == '등록 모드 실행':
                        answer('등록 모드 실행')
                        
                    elif data == '등록 모드 종료':
                       exeRegisterMode('등록 모드 종료')

                else:
                    if is_registering() == True:
                        if(take_pic()):
                                dir_path = BASEDIR + "/data/support/%d/"%c_num
                                if not os.path.exists(dir_path):
                                    os.mkdir(dir_path)  
                                cv2.imwrite(dir_path + f"clothes{c_num}-{s_id}.jpg", frame)
                                s_id += 1
                                if s_id == args['num_support']:
                                    s_id = 0
                                    args["num_classes"] += 1
                                    support = load_support(args)
                                    update_dirSize(c_num)
                                    c_num+=1
                                    change_pic_flag(False)
                    else:
                        cv2.imwrite(BASEDIR + "/data/query/%d.jpg"%q_id, frame)
                        q_id = q_id + 1

                        if q_id == args["num_query"] and support != None:
                            print("---------------Test Result---------------")

                            query = load_query(args)
                            if len(inf_que) < 3:
                                inf_que.append(inf.test(support, query, model, embedding))
                                q_id = 0
                            else:
                                inf_que.pop(0)
                                inf_que.append(inf.test(support, query, model, embedding))
                                q_id = 0

                            if inf_que.count(inf_que[-1]) == 3 and inf_que[-1] != 1 and inf_que[-1] not in last_cloth:
                                speak('%d번 옷을 넣습니다.'%inf_que[-1])
                                data_Module.moveCloset(inf_que[-1])

                                if len(last_cloth) < 1:
                                    last_cloth.append(inf_que[-1])
                                else:
                                    last_cloth.pop(0)
                                    last_cloth.append(inf_que[-1])
                                    print(last_cloth)
                                last_idx = (last_idx + 1) % 1
                
        finally:
            video_capture.release()
            cv2.destroyAllWindows()
    else:
        print("Error: Unable to open camera")
        

if __name__ == '__main__':
    main()