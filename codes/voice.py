from soc import TCPModule
from data import dataModule 
from firebase_admin import db

#voice
import os, time
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound

flag = 0
voiceOnoff = 1
isSpeak = 0
category = ''


dir = None
pic_flag = False
hangers = []

dirSize = 4
dt = dataModule()

def take_pic():
    global pic_flag
    return pic_flag

def change_pic_flag(b):
    global pic_flag
    pic_flag = b

def get_available_hanger():
    global hangers
    for i in range(1,16):
        if i not in hangers: 
            hangers.append(i)
            return i
    return -999 # hanger full

def update_dirSize(_n):
    global dirSize
    dirSize = _n

def is_registering():
    global flag
    if flag >=2:
        return True
    else: return False
    
def exeRegisterMode(input_text):
    global flag
    global voiceOnoff
    global dirSize
    global category

    voiceWord = ''
    
    if '등록' in input_text and '모드' in input_text and '종료' in input_text:
        flag = 1
        speak('등록 모드를 종료합니다.')

    if flag == 2:
        if '아니' in input_text:
            flag = 1
            speak('등록 모드를 종료합니다.')   
        elif '예' in input_text or '네' in input_text or '응' in input_text:
            if flag != 1:
                speak('등록할 옷을 80cm 거리를 두고 카메라에 보여주세요.')
            if flag != 1:
                time.sleep(5)
                change_pic_flag(True)
                speak('사진 등록이 완료되었습니다.') 
            if flag != 1:
                speak('옷의 카테고리를 말씀해주세요. 상의 하의 외투 기타')
            if flag != 1:
                flag += 1  
        else:
            speak('다시 말씀해주세요')
        if voiceOnoff == 0:
            flag = 0     
    elif flag == 3:
        if '상의' in input_text:
            category = '상의'
            if flag != 1:
                speak('상의로 등록되었습니다.')
            if flag != 1:
                speak('보이스워드를 등록하시겠습니까?')
            if flag != 1:
                flag += 1
        elif '하의' in input_text:
            category = '하의'
            if flag != 1:
                speak('하의로 등록되었습니다.')
            if flag != 1:
                speak('보이스워드를 등록하시겠습니까?')
            if flag != 1:
                flag += 1    
        elif '외투' in input_text:
            category = '외투'
            if flag != 1:
                speak('외투로 등록되었습니다.')
            if flag != 1:
                speak('보이스워드를 등록하시겠습니까?')
            if flag != 1:
                flag += 1    
        elif '기타' in input_text:            
            category = '기타'
            if flag != 1:
                speak('기타로 등록되었습니다.')
            if flag != 1:
                speak('보이스워드를 등록하시겠습니까?')
            if flag != 1:
                flag += 1    
        else:
            speak('다시 말씀해주세요. 상의 하의 외투 기타')
        if voiceOnoff == 0:
            flag = 0

                           
    elif flag == 4:
        if '예' in input_text or '네' in input_text or '응' in input_text:
            if flag != 1:
                speak('등록할 보이스워드를 말씀해주세요.')
            if flag != 1:
                flag += 1
        elif '아니' in input_text:
            if flag != 1: 
                hangerNum = get_available_hanger()
                if hangerNum == -999:
                    speak('옷장이 가득 찼습니다.')
                
                #insert pic
                id = dirSize - 1
                filename = 'clothes'+str(id+1)+'-2.jpg'
                
                #insert DB
                from data import dataModule
                d = dataModule()
                d.picUpload(id+1, filename)
                d.insertData(id,category,hangerNum,filename,voiceWord)
                speak('옷 등록이 완료되었습니다.')

                d.moveCloset(hangerNum)
                speak('옷을 자리에 걸어주세요.')
            if flag != 1:
                speak('또 다른 옷을 등록하시겠습니까?')
            if flag != 1:
                flag = 2
        else:
            speak('다시 말씀해주세요. 보이스워드를 등록하시겠습니까?')
        if voiceOnoff == 0:
            flag = 0
                           
    elif flag == 5:
        voiceWord = findByVoiceWord(input_text,0)
        if voiceWord == "":
            if flag != 1:
                voiceWord = input_text 
                speak(input_text + '으로 등록되었습니다.')
            
            if flag != 1:
                hangerNum = get_available_hanger()
                if hangerNum == -999:
                    speak('옷장이 가득 찼습니다.')
                
                #insert pic
                id = dirSize - 1

                filename = 'clothes'+str(id + 1)+'-2.jpg'
               
                #insert DB
                from data import dataModule
                d = dataModule()
                d.picUpload(id+1, filename)

                print(category)
                d.insertData(id,category,hangerNum,filename,voiceWord)
                speak('옷 등록이 완료되었습니다.')

                d.moveCloset(hangerNum)
                d.currentHangerNum = hangerNum
                speak('옷을 자리에 걸어주세요.')

            
            if flag != 1:
                speak('또 다른 옷을 등록하시겠습니까?')

            if flag != 1:
                flag = 2
            
        else:
            speak('사용할 수 없는 보이스워드입니다. 다시 말씀해주세요')

        if voiceOnoff == 0:
            flag = 0


def findByVoiceWord(text, f):
    global dirSize

    i = 1
    voiceWord = ""
    hangerNum = 0
    dir = db.reference('closet/clothes')

    print(dirSize)
    while i < dirSize - 1:

        vw = dir.child(str(i)).child('voiceWord').get()
        if vw in text:
            if vw != "":
                voiceWord = dir.child(str(i)).child('voiceWord').get()
                print('voiceWord: ' + voiceWord)
                hangerNum = dir.child(str(i)).child('hangerNum').get()
                # print('hangerNum: ' + str(hangerNum))

        if f == 0:
            if text in vw:
                if vw != '':
                  voiceWord = dir.child(str(i)).child('voiceWord').get()
                  print('voiceWord: ' + voiceWord)
                  hangerNum = dir.child(str(i)).child('hangerNum').get()
                # print('hangerNum: ' + str(hangerNum))

        i += 1

    if f == 1:
        global dt
        dt.moveCloset(hangerNum)

    return voiceWord


def listen():
    global flag
    global voiceOnoff

    print("#############################")

    if voiceOnoff == 0:
        flag = 0
        return

    r = sr.Recognizer()
    m = sr.Microphone()

    while True:
      with m as source:
          r.adjust_for_ambient_noise(source)
          audio = r.listen(source)

      try:
            print("#############################")
            text = r.recognize_google(audio, language = 'ko')
            print('[사용자] ' + text)

            if '안녕'in text and '스마트' in text and '옷장' in text:
                flag = 1

            if flag == 1:
                answer(text)
            elif flag >= 2:
                exeRegisterMode(text)

      except sr.UnknownValueError:
            print('voice recognition failed')

      except sr.RequestError as e:
            print('Request actual loss: {0}'.format(e))


def answer(input_text):

    global flag
    global findByVoiceWord

    answer_text = ''

    if '안녕'in input_text and '스마트' in input_text and '옷장' in input_text:
        speak('안녕하세요. 반가워요.')
    elif '등록' in input_text and '모드' in input_text and '실행' in input_text:
        speak('등록모드를 실행하시겠습니까?')
        flag = 2
    elif '오른쪽' in input_text:
        dt.moveCloset(-1)
    elif '왼쪽' in input_text:
        dt.moveCloset(-2)
    elif '찾아' in input_text:
        voiceWord = findByVoiceWord(input_text, 1)
        print('find ' + voiceWord)

        if voiceWord == "":
            answer_text = '찾으시는 옷이 없습니다. 보이스워드를 다시 확인해주세요'
        else:
            answer_text = voiceWord +' 찾습니다.'

        speak(answer_text)

    elif '다음에 또 만나' in input_text:
        flag = 0
        speak( '스마트 옷장을 종료합니다.다음에 또 만나요.')

    else:
        speak('무슨 말인지 못 알아들었어요. 다시 말씀해주세요.')


def speak(text):
    global isSpeak
    global voiceOnoff
    global flag

    if voiceOnoff == 0:
        flag = 0
        return

    while isSpeak == 1:
        pass
        
    isSpeak = 1
    print('[스마트옷장] ' + text)
    file_name = 'voice.mp3'
    tts = gTTS(text = text, lang = 'ko')
    tts.save(file_name)
    playsound(file_name)
    
    if os.path.exists(file_name):
        os.remove(file_name)

    isSpeak = 0


def listener(event):
    global voiceOnoff

    voiceOnoff = event.data
    print(event.data)


def update_dir(d):
    global dir
    dir= d