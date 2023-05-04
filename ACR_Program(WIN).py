#-*- coding:utf-8 -*-
#python 3.9
import json
import time
import base64
import hashlib
import hmac
import requests
import os
import sys
import pythoncom
import webbrowser
import winsound

from tkinter import *
import tkinter as tk
from tkinter import filedialog,Entry
from tkinter.font import Font

import threading

from PIL import Image,ImageTk
from io import BytesIO

from ffmpeg import audio
import numpy as np
from scipy.io.wavfile import write

root = tk.Tk()

width = 660
heigh = 550
screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()
root.geometry('%dx%d+%d+%d'%(width, heigh, (screenwidth-width)/2, (screenheight-heigh)/2))

root.resizable(width=0, height=0)
root.title('ACR Recognition')
ico=b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAACRUlEQVR42sWXz0tUURTH3/9U0Q+SGEhq4QgVRUERBC0Kghb9oIVBMERFtYg21UqoRS2CcqMLBxVcCM68GXVm1HH8MTrq6Azq/PSNPr9ePFePzxkdns9358CXd++Zd+75nHPv8LjaqUFoUl4hv1BeCC4pL3O07ObVgJ2BTwiK5QMEgKRBg+QVAPDbCXqeAIomEC+dCIBfACBnJ+jPEvbsfNAxQE6zGzRZZoCWIccAsAVwNQyL3YspBmibhMWexhUD/MvAYm+mFQOkDEpsmPT8OqcQoHWYK+9doeevtEIA3zQlTZSB7/M07swqBOjKUtLfS8D7JI0Hcvx7cwho0l0COC2UqVDSZxPAiwSNJ0rWf8iXOZcAbkYooSnk0YGHYzTPbvA7HRkxrwAXgi4AfJAtjxVpfn2Egc4EyJc2yPcx6QJAjzz17Ys094SwZ81h4MYIz9MV4FzgxACowrVNWvxJnP2VLfLdjgDvZmCxtzM11hG6HwOuDR8CcDdaW6/kgdvYAi7y/opKyf9oHOiWHSpI0NR69Tr9a7xtDMgAdU3PW8mjRfK/npIdkuOSiTpG79sG+DG/H4Ar6sxyh5qCwM9F1LUFowaARz9K1Qfrv/wwlWXFQdmhs4Ha8X+X6b11E3iZqAKwr/YDlX5L1Y+5EgYu6TR2DPB5FhZ7MGor3jlA2xQnL25S65UCPB5ngL5V8ikFuBNlgE9JZwC54wReDgEpg071rcixAfJ8MVEuvph4G3w1a9zlVEgjAFKr3I6Ci0kLMod3N+82PcJ9HGP605gAAAAASUVORK5CYII='
root.tk.call('wm', 'iconphoto', root, PhotoImage(data=ico))

#Объявление переменной под токен
AK=''
SK=''
H=''
TK=''

S=10#Секунды по умолчанию

pathname = os.path.dirname(sys.argv[0])

if not os.path.exists(f'{pathname}/Logs'):
    os.makedirs(f'{pathname}/Logs')

#Загрузка токена или создание файла конфигурации
if os.path.exists(f'{pathname}/Logs/data_file.json'):
    with open(f'{pathname}/Logs/data_file.json', "r") as write_file:
        f=json.load(write_file)
        data_local={
            "AccessKey":f['AccessKey'],
            "SecretKey":f['SecretKey'],
            "Host":f['Host'],
            "Seconds":f['Seconds'],
            "Token":f['Token']
        }
        with open(f'{pathname}/Logs/data_file.json', "w") as write_file:
            json.dump(data_local, write_file)
        AK=data_local['AccessKey']
        SK=data_local['SecretKey']
        H=data_local['Host']
        S=data_local['Seconds']
        TK=data_local['Token']
else:
    data_local={
            "AccessKey":'',
            "SecretKey":'',
            "Host":'',
            "Seconds":'',
            "Token":''
        }
    with open(f'{pathname}/Logs/data_file.json', "w") as write_file:
            json.dump(data_local, write_file)

LeftMenu = Frame(root, bg ="#304156",width=22)
LeftMenu.grid(row=1,rowspan = 10, column = 0, sticky = "nesw")

def on_enter(e):
    e.widget['background'] = e.widget['activebackground']
def on_leave(e):
    e.widget['background'] = '#304156'
def show_hand_cursor(e):
    e.widget.config(cursor='hand2')
def show_xterm_cursor(e):
    e.widget.config(cursor='xterm')
    
#Предупреждение о несоответствие ключей минимальной характеристике
Warn=Label(root,text='Токен не введен\nили введен не верно',bg='#304156',fg='#ff0000',width=25,font=('Microsoft Sans Serif',9))
if(len(TK)<1500):
    Warn.grid(row=1,column=0,sticky='s')

#Переменные для сбора ключей с полей ввода
textTK = StringVar()

#создание доп окон
class windows:
    def FAQ():
        faq=tk.Toplevel(root)
        # faq.grab_set()
        faq.attributes("-topmost",True)
        faq.resizable(width=0, height=0)
        faq.title('Важные моменты пользования')
        
        faq.grid_columnconfigure(0, weight = 1)
        faq.grid_rowconfigure(0, weight = 1)
        faqFrame=Frame(faq,bg="#304156")
        faqFrame.grid(row=0,column=0,sticky = "nesw")

        width = 722
        heigh = 185
        screenwidth = faq.winfo_screenwidth()
        screenheight = faq.winfo_screenheight()
        faq.geometry('%dx%d+%d+%d'%(width, heigh, (screenwidth-width)/2, (screenheight-heigh)/2))

        Rules=Text(faqFrame,state=NORMAL,height=11,width=80,font=('Microsoft Sans Serif',12),bg="#304156",fg="#bfcbd9",wrap='word',borderwidth=0)
        Rules.grid(row=0,column=0,sticky='w')
        text='''1: Ползунком выбирается продолжительность в секундах как для записи, так и для файла.
2: Звук записывается с устройства воспроизведения по умолчанию.
3: При записи звук на устройстве воспроизведения по умолчанию не должен быть выключен.
4: Прямая ссылка на токен для европейского региона: Токен.
Перейдя по ссылке, войдите или зарегистрируйтесь на данном сервисе. После нажмите «Create Token» задайте любое удобное имя, выберите все пункты доступа и после создания нажмите «View» скопируйте строку из 1600 символов и вставьте в соответствующее поле в настройках.
            '''
        Rules.insert(1.0,text)

        Rules.tag_add(f'tok', '4.52', '4.57')
        Rules.tag_config(f'tok', foreground='#409eff', underline=True)
        Rules.tag_bind(f'tok', '<Enter>', show_hand_cursor)
        Rules.tag_bind(f'tok', '<Leave>', show_xterm_cursor)
        Rules.tag_bind(f'tok', '<Button-1>', lambda e: webbrowser.open_new(r"https://console.acrcloud.com/account?region=eu-west-1#/developer"))

        root.update()
        Rules.configure(state=DISABLED)

    #ввод ключей
    def setting():
        settings=tk.Toplevel(root)
        settings.bind("<Key>", _onKeyRelease, "+")
        # settings.grab_set()
        settings.attributes("-topmost",True)
        settings.resizable(width=0, height=0)
        settings.title('Настройка ключей')

        width = 480
        heigh = 97
        screenwidth = settings.winfo_screenwidth()
        screenheight = settings.winfo_screenheight()
        settings.geometry('%dx%d+%d+%d'%(width, heigh, (screenwidth-width)/2, (screenheight-heigh)/2))

        setFrame=Frame(settings,bg="#304156")
        setFrame.grid(row=0,column=0,sticky = "nesw")

        Label(setFrame,font=('Microsoft Sans Serif',11),bg="#304156",fg="#bfcbd9",text='Token:').grid(row=1,column=0,sticky='w')
        Ent3=Entry(setFrame,textvariable=textTK,width=53,bg='#263445',fg="#bfcbd9",insertbackground="#bfcbd9",font=('Microsoft Sans Serif',11))
        Ent3.grid(row=1,column=1,sticky='e')
        Ent3.delete(0, END)
        Ent3.insert(END, f'{TK}')

        Label(setFrame,font=('Microsoft Sans Serif',11),width=32,bg="#304156",fg="#bfcbd9",text='Токен можно получить на этой странице:\nподробности в «Важные моменты»').grid(row=2,columnspan=2,column=0,sticky='w')
        lb=Label(setFrame, text="https://www.ACRcloud.com",bg="#304156", fg="#409eff", cursor="hand2",font=('Microsoft Sans Serif',11))
        lb.bind('<Button-1>',lambda e: webbrowser.open_new(r"https://console.acrcloud.com/account#/developer"))
        lb.grid(row=2,columnspan=2,column=1,sticky='ne')

        global Token_Warn
        Token_Warn=Label(setFrame,text='Авторизация не прошла',bg='#304156',fg='#ff0000',font=('Microsoft Sans Serif',9))

        global Token_Successful
        Token_Successful=Label(setFrame,text='Авторизация успешна',bg='#304156',fg='#008000',font=('Microsoft Sans Serif',9))

        enter=Button(setFrame,bg="#304156",activebackground='#263445',fg="#bfcbd9",activeforeground='#bfcbd9',font=Helvetica,borderwidth=0,text='Подтвердить',command=ent)
        enter.grid(row=4,column=0,columnspan=2,sticky='we')
        enter.bind("<Enter>", on_enter)
        enter.bind("<Leave>", on_leave)

#Сохранение введеных ключей и присвоение в переменные
def ent():
    global access_key,access_secret,requrl,Token
    global TK
    TK=textTK.get()

    header={"Authorization": f"Bearer {TK}"}
    r = requests.get('https://api-v2.acrcloud.com/api/base-projects',headers=header)
    Project_Lists = json.loads(r.text)

    try:
        AK=Project_Lists['data'][0]['access_key']
        SK=Project_Lists['data'][0]['access_secret']
        H=Project_Lists['data'][0]['region']
    except:
        try:
            if(Project_Lists['error']=='Authentication Exception'):
                Token_Successful.grid_forget()
                Warn.grid(row=1,column=0,sticky='s')
                Token_Warn.grid(row=2,column=1,sticky='se',ipadx=25)
                data_local={
                        "AccessKey":'',
                        "SecretKey":'',
                        "Host":'',
                        "Seconds":'',
                        "Token":str(TK)
                    }
                with open(f'{pathname}/Logs/data_file.json', "w") as write_file:
                        json.dump(data_local, write_file)
                access_key = ''
                access_secret = ''
                requrl = ''
                Token=str(TK)
                return
        except:
            pass
        New_Proj_Json={
        "name":"ACR_Of_Music",
        "region":"eu-west-1",
        "buckets":[23],
        "type":"AVR",
        "audio_type":"linein",
        "external_ids":["MusicBrainz","upc","isrc","youtube","deezer","spotify","LyricFind"]
        }
        New_Proj = {
        'Accept': 'application/json',
        'Authorization':  f"Bearer {TK}",
        'Content-Type': 'application/json'
        }
        r = requests.post('https://api-v2.acrcloud.com/api/base-projects',headers=New_Proj,json=New_Proj_Json)

        r = requests.get('https://api-v2.acrcloud.com/api/base-projects',headers=header)
        Project_Lists = json.loads(r.text)

        AK=Project_Lists['data'][0]['access_key']
        SK=Project_Lists['data'][0]['access_secret']
        H=Project_Lists['data'][0]['region']

    with open(f'{pathname}/Logs/data_file.json', "r") as write_file:
        f=json.load(write_file)
    f['AccessKey']=str(AK)
    f['SecretKey']=str(SK)
    f['Host']=str(H)
    f['Token']=str(TK)
    with open(f'{pathname}/Logs/data_file.json', "w") as write_file:
        json.dump(f,write_file)
    
    access_key = AK
    access_secret = SK
    requrl = f"http://identify-{H}.acrcloud.com/v1/identify"
    Token=TK
    if (Token_Warn.winfo_exists):
        Token_Successful.grid(row=2,column=1,sticky='se',ipadx=25)
        Token_Warn.grid_forget()
        Warn.grid_forget()
        root.update()
    if(len(TK)<1500):
        Warn.grid(row=1,column=0,sticky='s')
    elif (Warn.winfo_exists):
        Warn.grid_forget()
        root.update()

#функция записи с микшера и записывание в файл формата wav
def record():
    pythoncom.CoInitialize()
    import soundcard as sc #импортировать только отдельным потоком

    try:
        Rec.configure(state=DISABLED)
        Choice.configure(state=DISABLED)

        textline.configure(state=NORMAL)
        textline.insert(1.0, '🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑\n')
        textline.tag_add("Arrow", '1.0', '2.48')
        textline.tag_config('Arrow', font=('Microsoft Sans Serif',16))
        textline.configure(state=DISABLED)
        root.update()

        seconds = v.get()

        default_speaker = sc.default_speaker()
        mics = sc.all_microphones(include_loopback=True)
        for j in range(len(mics)):
            if((default_speaker.name in mics[j].name)and(mics[j].isloopback)):
                textline.configure(state=NORMAL)
                textline.insert(1.0, f'\n\nЗапись|{seconds}s\n')
                textline.configure(state=DISABLED)
                root.update()
                break
            
        default_mic = mics[j]

        with default_mic.recorder(samplerate=44100) as mic, \
            default_speaker.player(samplerate=44100) as sp:
                data = mic.record(numframes=44100*seconds)
                scaled = np.int16(data / np.max(np.abs(data)) * 10000)
                write(f'{pathname}/Logs/output.wav', 44100, scaled)
        global name
        name=f'{pathname}/Logs/output.wav'
        func(name)
    except:
        Rec.configure(state=NORMAL)
        Choice.configure(state=NORMAL)
        textline.configure(state=NORMAL)
        textline.insert(1.0, f'Устройство воспроизведения по умолчанию не обнаружено\n')
        textline.insert(1.0, '\n🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓\n')
        textline.tag_add("Arrow", '1.0', '2.48')
        textline.tag_config('Arrow', font=('Microsoft Sans Serif',16))
        textline.configure(state=DISABLED)
        root.update()

#выбор файла с пк
def callback():
    if os.path.exists(f'{pathname}/Logs/output.wav'):
        os.remove(f'{pathname}/Logs/output.wav')
    if os.path.exists(f'{pathname}/Logs/output_0.wav'):
        os.remove(f'{pathname}/Logs/output_0.wav')
    Rec.configure(state=DISABLED)
    Choice.configure(state=DISABLED)
    global name
    seconds = v.get()
    name = filedialog.askopenfilename(filetypes=[('Media','*.mp3 *.wav *.wma *.amr *.ogg *.ape *.acc *.spx *.m4a *.mp4 *.FLAC')])

    try:
        f = open(name, 'r')
        f.close()
    except:
        Rec.configure(state=NORMAL)
        Choice.configure(state=NORMAL)
        return

    textline.configure(state=NORMAL)
    textline.insert(1.0, '🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑🢑\n')
    textline.tag_add("Arrow", '1.0', '2.48')
    textline.tag_config('Arrow', font=('Microsoft Sans Serif',16))
    textline.insert(1.0, '—Обрезаем аудио\видео\n')
    textline.configure(state=DISABLED)
    root.update()

    audio.a_intercept(f'"{name}"',0,seconds,f'"{pathname}\Logs\output_0.wav"')
    if os.path.exists(f'{pathname}/Logs/output_0.wav'):
        pass
    else:
        try:
            Art.grid_forget()
            Photo_Image.grid_forget()
            root.update()
        except:
            pass
        textline.configure(state=NORMAL)
        textline.insert(1.0, f'У медиа файла отсутствует аудио дорожка или формат не поддерживается\n\n')
        textline.insert(1.0, '\n🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓\n')
        textline.tag_add("Arrow", '1.0', '2.48')
        textline.tag_config('Arrow', font=('Microsoft Sans Serif',16))
        root.update()
        Rec.configure(state=NORMAL)
        Choice.configure(state=NORMAL)
        textline.configure(state=DISABLED)
        return
    audio.a_volume(f'"{pathname}\Logs\output_0.wav"',2,f'"{pathname}\Logs\output.wav"')
        
    textline.configure(state=NORMAL)
    textline.insert(1.0, f'\n\n—{name}\n')
    textline.configure(state=DISABLED)
    root.update()

    func(f'{pathname}\Logs\output.wav')
    
# Подготовка ключей для сервиса
access_key = AK
access_secret = SK
requrl = f"http://identify-{H}.acrcloud.com/v1/identify"
http_method = "POST"
http_url = "/v1/identify"
data_type = "audio"
signature_version = "1"
timestamp = time.time()

requrl_meta = "https://eu-api-v2.acrcloud.com/api/external-metadata/tracks"
Token=TK

LinkId=0
#создание ссылок
class HyperLinks():
    def HyperLinkId(ServiceName,Number,LinkId):
        if(ServiceName=='YouTube'):
            Youtube_id=templates['metadata']['music'][Number]['external_metadata']['youtube']['vid']
        elif(ServiceName=='Spotify'):
            Spotify_id=templates['metadata']['music'][Number]['external_metadata']['spotify']['track']['id']
        else:
            Deezer_id=templates['metadata']['music'][Number]['external_metadata']['deezer']['track']['id']
        
        textline.insert(1.0, f' — {ServiceName}')
        if(ServiceName=='YouTube'):
            textline.tag_add(f'{ServiceName}_Link_{Number}{LinkId}', '1.3', '1.10') 
        elif(ServiceName=='Spotify'):
            textline.tag_add(f'{ServiceName}_Link_{Number}{LinkId}', '1.3', '1.10')
        else:
            textline.tag_add(f'{ServiceName}_Link_{Number}{LinkId}', '1.3', '1.9')
        
        textline.tag_config(f'{ServiceName}_Link_{Number}{LinkId}', foreground='#409eff', underline=True)
        textline.tag_bind(f'{ServiceName}_Link_{Number}{LinkId}', '<Enter>', show_hand_cursor)
        textline.tag_bind(f'{ServiceName}_Link_{Number}{LinkId}', '<Leave>', show_xterm_cursor)
        if(ServiceName=='YouTube'):
            textline.tag_bind(f'{ServiceName}_Link_{Number}{LinkId}', '<Button-1>',lambda e: webbrowser.open(f'https://www.youtube.com/watch?v={Youtube_id}') )
        elif(ServiceName=='Spotify'):
            textline.tag_bind(f'{ServiceName}_Link_{Number}{LinkId}', '<Button-1>',lambda e: webbrowser.open(f'https://open.spotify.com/track/{Spotify_id}'))
        else:
            textline.tag_bind(f'{ServiceName}_Link_{Number}{LinkId}', '<Button-1>',lambda e: webbrowser.open(f'https://www.deezer.com/us/track/{Deezer_id}'))

    def HyperLinkSearch(ServiceName,Number,LinkId,Artist,Title):
        textline.insert(1.0, f' — {ServiceName}')
        if(ServiceName=='SoundCloud'):
            textline.tag_add(f'{ServiceName}_Link_{Number}{LinkId}', '1.3', '1.13')
        elif(ServiceName=='VK Music'):
            textline.tag_add(f'{ServiceName}_Link_{Number}{LinkId}', '1.3', '1.11')
        else:
            textline.tag_add(f'{ServiceName}_Link_{Number}{LinkId}', '1.3', '1.10')
        
        textline.tag_config(f'{ServiceName}_Link_{Number}{LinkId}', foreground='#409eff', underline=True)
        textline.tag_bind(f'{ServiceName}_Link_{Number}{LinkId}', '<Enter>', show_hand_cursor)
        textline.tag_bind(f'{ServiceName}_Link_{Number}{LinkId}', '<Leave>', show_xterm_cursor)
        if(ServiceName=='SoundCloud'):
            textline.tag_bind(f'{ServiceName}_Link_{Number}{LinkId}', '<Button-1>',  lambda e: webbrowser.open(f'https://soundcloud.com/search?q={Artist} {Title}'))
        elif(ServiceName=='VK Music'):
            textline.tag_bind(f'{ServiceName}_Link_{Number}{LinkId}', '<Button-1>',  lambda e: webbrowser.open(f'https://vk.com/audio?q={Artist} {Title}'))
        else:
            textline.tag_bind(f'{ServiceName}_Link_{Number}{LinkId}', '<Button-1>',  lambda e: webbrowser.open(f'https://www.youtube.com/results?search_query={Artist} {Title}'))

#Главная функция реквестов и вывода
def func(name):
    string_to_sign = http_method + "\n" + http_url + "\n" + access_key + "\n" + data_type + "\n" + signature_version + "\n" + str(timestamp)
    sign = base64.b64encode(hmac.new(access_secret.encode('ascii'), string_to_sign.encode('ascii'),digestmod=hashlib.sha1).digest()).decode('ascii')
    global sample_bytes
    sample_bytes = os.path.getsize(name)

    files = [
        ('sample', (f'{name}', open(f'{name}', 'rb'), 'audio/mpeg'))
    ]

    #данные лога
    data = {'access_key': access_key,
            'sample_bytes': sample_bytes,
            'timestamp': str(timestamp),
            'signature': sign,
            'data_type': data_type,
            "signature_version": signature_version}

    #получение результата с сервиса и отправка файлов
    try:
        textline.configure(state=NORMAL)
        if('Запись' in textline.get('1.0','3.11')):
            textline.delete(1.0, 3.11)
        if('Обрезаем аудио\видео' in textline.get('1.0','4.25')):
            textline.delete(1.0, 4.25)
        textline.insert(1.0, f'\n\nПоиск...')
        textline.configure(state=DISABLED)
        r = requests.post(requrl, files=files, data=data)
        r.encoding = "utf-8"
        textline.configure(state=NORMAL)
        textline.delete(1.0, 3.8)
        textline.configure(state=DISABLED)

        global templates
        templates = json.loads(r.text)

        #вывод лога в текстовое окно приложения
        textline.configure(state=NORMAL)
        try:
            try:#Сколько найдено песен
                NumberOfMusics=0
                for i in range(100):
                    templates['metadata']['music'][i]['title']
                    NumberOfMusics+=1
            except:
                i=0

            if(NumberOfMusics==0):#перестраховка на ошибку
                raise

            try:
                for i in range(NumberOfMusics):
                    if(NumberOfMusics==1):
                        pass
                    else:
                        if(i==0):
                            pass
                        elif(i<=NumberOfMusics-2):
                            if(templates['metadata']['music'][i-1]['external_ids']['isrc']==templates['metadata']['music'][i]['external_ids']['isrc']):
                                textline.insert(1.0, '\n\n|\n\n')
                                continue
                            else:
                                textline.insert(1.0, '\n\n|\n\n')
                        elif(i==NumberOfMusics-1):
                            if(templates['metadata']['music'][NumberOfMusics-1]['external_ids']['isrc']==templates['metadata']['music'][i-1]['external_ids']['isrc']):
                                if(textline.get("1.0","5.0")=="\n\n|\n\n"):
                                    textline.delete("1.0","5.0")
                                raise
                            else:
                                if(textline.get("1.0","5.0")!="\n\n|\n\n"):
                                    textline.insert(1.0, '\n\n|\n\n')

                    Album=templates['metadata']['music'][i]['album']['name']
                    Artist=templates['metadata']['music'][i]['artists'][0]['name']
                    Title=templates['metadata']['music'][i]['title']
                    textline.insert(1.0,f'\nАльбом — {Album}\n{Artist} — {Title}')

                    global LinkId
                    #SoundCloud ссылка в любом случае
                    HyperLinks.HyperLinkSearch('SoundCloud',i,LinkId,Artist,Title)
                    #VK ссылка в любом случае
                    HyperLinks.HyperLinkSearch('VK Music',i,LinkId,Artist,Title)
                    
                    try:#YouTube ссылка при наличие
                        HyperLinks.HyperLinkId('YouTube',i,LinkId)
                    except:#YouTube ссылка если нет id
                        HyperLinks.HyperLinkSearch('YouTube',i,LinkId,Artist,Title)

                    try:#Spotify ссылка при наличие
                        HyperLinks.HyperLinkId('Spotify',i,LinkId)
                    except:
                        pass
                        
                    try:#Deezer ссылка при наличие
                        HyperLinks.HyperLinkId('Deezer',i,LinkId)
                    except:
                        pass 
    
                    if(textline.get(1.0,1.3)!="—"):
                        textline.delete(1.0,1.3)

                    LinkId+=1
            except:
                pass

            textline.configure(state=NORMAL)
            textline.insert(1.0, '\n🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓\n')
            textline.tag_add("Arrow", '1.0', '2.48')
            textline.tag_config('Arrow', font=('Microsoft Sans Serif',16))
            textline.configure(state=DISABLED)
            root.update()

            global Art,Photo_Image
            try:
                Art.grid_forget()
                Photo_Image.grid_forget()
            except:
                pass

            try:
                params = {'isrc': templates['metadata']['music'][0]['external_ids']['isrc']}
                header={"Authorization": f"Bearer {Token}"}
                r_meta = requests.get(requrl_meta,params=params,headers=header,json=True)
                templates_meta = json.loads(r_meta.text)
                try:
                    try:
                        image_url=templates_meta['data'][0]['album']['covers']['medium']
                    except:
                        image_url=templates_meta['data'][0]['album']['cover']
                except:
                    params = {'query': f'{Artist} — {Title}'}
                    header={"Authorization": f"Bearer {Token}"}
                    r_meta = requests.get(requrl_meta,params=params,headers=header,json=True)
                    templates_meta = json.loads(r_meta.text)
            except:
                try:
                    if(NumberOfMusics>=2):
                        params = {'isrc': templates['metadata']['music'][1]['external_ids']['isrc']}
                        header={"Authorization": f"Bearer {Token}"}
                        r_meta = requests.get(requrl_meta,params=params,headers=header,json=True)
                        templates_meta = json.loads(r_meta.text)
                        try:
                            try:
                                image_url=templates_meta['data'][0]['album']['covers']['medium']
                            except:
                                image_url=templates_meta['data'][0]['album']['cover']
                        except:
                            params = {'query': f'{Artist} — {Title}'}
                            header={"Authorization": f"Bearer {Token}"}
                            r_meta = requests.get(requrl_meta,params=params,headers=header,json=True)
                            templates_meta = json.loads(r_meta.text)
                        
                except:
                    Art.grid_forget()
                    Photo_Image.grid_forget()
                    root.update()
            try:
                try:
                    image_url=templates_meta['data'][0]['album']['covers']['medium']
                except:
                    image_url=templates_meta['data'][0]['album']['cover']
                response=requests.get(image_url)
                photo = ImageTk.PhotoImage(Image.open(BytesIO(response.content)).resize((100,100),Image.Resampling.LANCZOS))
                Photo_Image = Label(LeftMenu,image=photo,borderwidth=0)
                Photo_Image.image = photo
                Photo_Image.grid(row=3,column=0,pady=10)
            except:
                pass

            Art=Text(LeftMenu,state=NORMAL,width=22,height=5,wrap="word",font=('Microsoft Sans Serif',11),borderwidth=0,bg='#304156',fg="#bfcbd9")
            Art.tag_configure("center", justify='center')
            Art.insert(1.0,templates['metadata']['music'][0]['title'])
            Art.insert(1.0,templates['metadata']['music'][0]['artists'][0]['name']+'\n')
            Art.tag_add("center", "1.0", "end")
            Art.configure(state=DISABLED)
            Art.grid(row=4,column=0)

        except:
            if(templates['status']['msg']=="No result"):
                textline.insert(1.0,'Нет результа, попробуйте ещё раз')
            elif(templates['status']['msg']=="invalid signature"):
                textline.insert(1.0,'«Токен» введен неправильно или не введен вовсе')
            elif(('Invalid fingerprint' in templates['status']['msg'])or("Can't generate fingerprint" in templates['status']['msg'])):
                textline.insert(1.0,'Отсутствует звук, кромешная тишина')
            elif(templates['status']['msg']=="requests limit exceeded, please upgrade your account"):
                textline.insert(1.0,'Закончился днейвной лимит ключей')
            elif('Recognition service error' in templates['status']['msg']):
                textline.insert(1.0,'Сервис временно не доступен')
            else:
                textline.insert(1.0,templates['status']['msg'])
            try:
                Art.grid_forget()
                Photo_Image.grid_forget()
                root.update()
            except:
                pass
    except:
        try:
            Art.grid_forget()
            Photo_Image.grid_forget()
            root.update()
        except:
            pass
        textline.configure(state=NORMAL)
        textline.insert(1.0, f'«Токен» введен неправильно или не введен вовсе')
        root.update()

    if(textline.get('2.0','2.48')!='🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓'):
        textline.configure(state=NORMAL)
        textline.insert(1.0, '\n🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓🢓\n')
        textline.tag_add("Arrow", '1.0', '2.48')
        textline.tag_config('Arrow', font=('Microsoft Sans Serif',16))
        textline.configure(state=DISABLED)
        root.update()

    Rec.configure(state=NORMAL)
    Choice.configure(state=NORMAL)
    winsound.MessageBeep() #сигнал о завершение

#хоткеи на всех языках
def _onKeyRelease(event):
    ctrl  = (event.state & 0x4) != 0
    if event.keycode==67 and ctrl and event.keysym.lower() != "c":
        event.widget.event_generate("<<Copy>>")
    if event.keycode==86 and ctrl and event.keysym.lower() != "v":
        event.widget.event_generate("<<Paste>>")
    if event.keycode==65 and ctrl and event.keysym.lower() != "a":
        event.widget.event_generate("<<SelectAll>>")
    if event.keycode==88 and ctrl and event.keysym.lower() != "x": 
        event.widget.event_generate("<<Cut>>")
root.bind("<Key>", _onKeyRelease, "+")

#изменение ширины 0 колонки и 1 строки
root.grid_columnconfigure(0, weight = 1)
root.grid_rowconfigure(1, weight = 1)

#Подготовка иконок записи и файла
FileBase=b'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAABJmlDQ1BBZG9iZSBSR0IgKDE5OTgpAAAoz2NgYDJwdHFyZRJgYMjNKykKcndSiIiMUmA/z8DGwMwABonJxQWOAQE+IHZefl4qAwb4do2BEURf1gWZxUAa4EouKCoB0n+A2CgltTiZgYHRAMjOLi8pAIozzgGyRZKywewNIHZRSJAzkH0EyOZLh7CvgNhJEPYTELsI6Akg+wtIfTqYzcQBNgfClgGxS1IrQPYyOOcXVBZlpmeUKBhaWloqOKbkJ6UqBFcWl6TmFit45iXnFxXkFyWWpKYA1ULcBwaCEIWgENMAarTQZKAyAMUDhPU5EBy+jGJnEGIIkFxaVAZlMjIZE+YjzJgjwcDgv5SBgeUPQsykl4FhgQ4DA/9UhJiaIQODgD4Dw745AMDGT/0ZOjZcAAAACXBIWXMAAAsTAAALEwEAmpwYAAAE7mlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNi4wLWMwMDYgNzkuZGFiYWNiYiwgMjAyMS8wNC8xNC0wMDozOTo0NCAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iIHhtbG5zOnBob3Rvc2hvcD0iaHR0cDovL25zLmFkb2JlLmNvbS9waG90b3Nob3AvMS4wLyIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0RXZ0PSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VFdmVudCMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIDIyLjQgKFdpbmRvd3MpIiB4bXA6Q3JlYXRlRGF0ZT0iMjAyMi0xMC0xOVQxOTozMjo0NCswMzowMCIgeG1wOk1vZGlmeURhdGU9IjIwMjItMTAtMTlUMTk6Mzc6MDErMDM6MDAiIHhtcDpNZXRhZGF0YURhdGU9IjIwMjItMTAtMTlUMTk6Mzc6MDErMDM6MDAiIGRjOmZvcm1hdD0iaW1hZ2UvcG5nIiBwaG90b3Nob3A6Q29sb3JNb2RlPSIzIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOjY5ZmU0Mjc3LTM4YWMtMGI0Yi1hYjAzLWZkMTMyYTM3YjBkYSIgeG1wTU06RG9jdW1lbnRJRD0ieG1wLmRpZDo2OWZlNDI3Ny0zOGFjLTBiNGItYWIwMy1mZDEzMmEzN2IwZGEiIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDo2OWZlNDI3Ny0zOGFjLTBiNGItYWIwMy1mZDEzMmEzN2IwZGEiPiA8eG1wTU06SGlzdG9yeT4gPHJkZjpTZXE+IDxyZGY6bGkgc3RFdnQ6YWN0aW9uPSJjcmVhdGVkIiBzdEV2dDppbnN0YW5jZUlEPSJ4bXAuaWlkOjY5ZmU0Mjc3LTM4YWMtMGI0Yi1hYjAzLWZkMTMyYTM3YjBkYSIgc3RFdnQ6d2hlbj0iMjAyMi0xMC0xOVQxOTozMjo0NCswMzowMCIgc3RFdnQ6c29mdHdhcmVBZ2VudD0iQWRvYmUgUGhvdG9zaG9wIDIyLjQgKFdpbmRvd3MpIi8+IDwvcmRmOlNlcT4gPC94bXBNTTpIaXN0b3J5PiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/PqwwApkAAAJsSURBVGje7ZlBaNNQGMcrjqEwplWUOQrCpDLoseK1DLpBLxaE7TQ8lcHmYYhgETw4aJ0XBaGD9rSBPVS8eYqMjR52aGVjh13GYEVBHIpohWkHc8b/c1/gGV7TtI3Ji7zAD5r3XvK9X/O9l7wkEPiHW7VafQh0B4ka59Z1/Q9+6rx7AoLOPwFTHZJxVUDQ+ftdni9qKUANnCJr6nzRgXNOthLQfcT/LZBxOJ2cwnYKTQUk3OwMYiWgBJSAElACSkAJKAEl4IEAYg6CCdBv0eYiSIN5EJJN4DXF/gJy4HqpVDph51hZBNYFi5aP4CVbS4MkpdAlEITcSVkF3oGvNldl35mYbAIFcAokwBxYBt8sJPKyCSw2qb9AKRQH42DXEJZxDFTANAjbuWIyD2LGJ/AKPAYz9O+Pgh1ZBTbAWhuvV6QTKHA3rST986s0O/30jYBo0zStB/XnwBDY8p1AO4P4eRevwJtxxQjOHhGwfw3cAjfAeacFnGajXC73UuBw9Xjj6xtgX2aBBAUdAB9azSodC7iQ5wsU9AjMgrNgGKw0E6B0S9H0yq7UHn1reOuFwHsKumQqD4IfZgHqfNH2fcAFgQMKeldQZ9xZc1xZiuvoJrgHntJTqCcC2xRUM5VfBYdUd0eQ55uVSqWXK4+BX14IPDB9M4vTR4saNxuFuPYNKk8LzlXzQuA0eGORz7dN7T8bn2b5cnY1UFanuqxrAhS8j9a8fB6z/L8pEH7BrbxiXOfz3LEjrgqYrkYEXLZoE+FmJ50WMXVuX/trTSzpu6AxLpV4NDb9Si9AEmfoeeoZeMTSRvhaxfjhV3wv8BtR4EcJoAtCKQAAAABJRU5ErkJggg=='
photoimage = PhotoImage(data=FileBase)
PNG_File = photoimage.subsample(2, 2)
RecordBase=b'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAABMWlDQ1BBZG9iZSBSR0IgKDE5OTgpAAAoz62OsUrDUBRAz4ui4lArBHFweJMoKLbqYMakLUUQrNUhydakoUppEl5e1X6Eo1sHF3e/wMlRcFD8Av9AcergECGDgwie6dzD5XLBqNh1p2GUYRBr1W460vV8OfvEDFMA0Amz1G61DgDiJI74wecrAuB50647Df7GfJgqDUyA7W6UhSAqQP9CpxrEGDCDfqpB3AGmOmnXQDwApV7uL0ApyP0NKCnX80F8AGbP9Xww5gAzyH0FMHV0qQFqSTpSZ71TLauWZUm7mwSRPB5lOhpkcj8OE5UmqqOjLpD/B8BivthuOnKtall76/wzrufL3N6PEIBYeixaQThU598qjJ3f5+LGeBkOb2F6UrTdK7jZgIXroq1WobwF9+MvwMZP/U6/OGUAAAAJcEhZcwAACxMAAAsTAQCanBgAAATuaVRYdFhNTDpjb20uYWRvYmUueG1wAAAAAAA8P3hwYWNrZXQgYmVnaW49Iu+7vyIgaWQ9Ilc1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCI/PiA8eDp4bXBtZXRhIHhtbG5zOng9ImFkb2JlOm5zOm1ldGEvIiB4OnhtcHRrPSJBZG9iZSBYTVAgQ29yZSA2LjAtYzAwNiA3OS5kYWJhY2JiLCAyMDIxLzA0LzE0LTAwOjM5OjQ0ICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyIgeG1sbnM6cGhvdG9zaG9wPSJodHRwOi8vbnMuYWRvYmUuY29tL3Bob3Rvc2hvcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgMjIuNCAoV2luZG93cykiIHhtcDpDcmVhdGVEYXRlPSIyMDIyLTEwLTE5VDE5OjM3OjU2KzAzOjAwIiB4bXA6TW9kaWZ5RGF0ZT0iMjAyMi0xMC0xOVQxOTozODozMSswMzowMCIgeG1wOk1ldGFkYXRhRGF0ZT0iMjAyMi0xMC0xOVQxOTozODozMSswMzowMCIgZGM6Zm9ybWF0PSJpbWFnZS9wbmciIHBob3Rvc2hvcDpDb2xvck1vZGU9IjMiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6NDc4YTRiMTAtNDFhMS1kOTRjLWI1YjItZmQwMzZkODAyYzQwIiB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOjQ3OGE0YjEwLTQxYTEtZDk0Yy1iNWIyLWZkMDM2ZDgwMmM0MCIgeG1wTU06T3JpZ2luYWxEb2N1bWVudElEPSJ4bXAuZGlkOjQ3OGE0YjEwLTQxYTEtZDk0Yy1iNWIyLWZkMDM2ZDgwMmM0MCI+IDx4bXBNTTpIaXN0b3J5PiA8cmRmOlNlcT4gPHJkZjpsaSBzdEV2dDphY3Rpb249ImNyZWF0ZWQiIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6NDc4YTRiMTAtNDFhMS1kOTRjLWI1YjItZmQwMzZkODAyYzQwIiBzdEV2dDp3aGVuPSIyMDIyLTEwLTE5VDE5OjM3OjU2KzAzOjAwIiBzdEV2dDpzb2Z0d2FyZUFnZW50PSJBZG9iZSBQaG90b3Nob3AgMjIuNCAoV2luZG93cykiLz4gPC9yZGY6U2VxPiA8L3htcE1NOkhpc3Rvcnk+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwveDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+orpVOwAAAnxJREFUaN7t2UuITXEcB/DbDFM0Hhs0mTxSkoUy8lhMEbJRVpTF2IoVumyGhZSwwkoWQmpCUiwkKV0y93ykJEoiolhJHg3N9bgWjrrpPs4c59x7JvOr/+Iuzv9+P6fT/5krl8u50dxyY4AxQEqAJKpQKEzESvQk0V/qAHRhI476XSWUMTQwMNCeOQBmYBvO4UUYtmorFApTMgXATgzXC13ZisVid2YAWB01eEVbkCXA+RiAZVkC3Bth+J9YmCXA/QihP+Aa9mFppobRGoC3uIgdWNLT09OWS7jSADzAZnTlmlBJA95haq6JlTTgeq7JlTTgatIBBwcH27EI23EKp7EmswBMxjrsxw18rDEE92UCgHnYghN4iO8R55GXLQVgPR7HmL0r27iWALB2BG+6ZguCoKNVgNv/Gr7VgA8tBWAh9uICzqIv3LxEBQy3DBAGL9XoNNuA8E3X6zQtwFOcwVYsxeW4gGcN/uhKAoCvuIMj2IBpVZ7vjwv40gBwPAbgDS5hF1YEQdAR4fnYgDt1wg9F3eOGgALmxlxuxAYsxucq4T9h4wgCDOPgP6yX+mOPQsVisRvHwjdYwAHMHmGA1gGSqDgAzMT0UQXABBzCq4rP9TmeZB6ASXjUtLVQCoCTTV3M1QkyHr3YhFXh71IEwPsGgFI+n29LDZDP59vCw96PVWbacgTA6waAm6neD4RDbb0AjQCH6zz7CfNTA2B5uPGODQiCoCO8Y/i7n7uVZ6ppAfZEWGHujtjXrHBR14c5TbliCo8W64X/9ucTyOQdGTrDNXy18D+wI3Mnc1UQc8Kj9D+7txJuoTeTR4sN5oG56Gz52ejYTf0Y4D8B/AJeIGY6skaY/QAAAABJRU5ErkJggg=='
photoimage = PhotoImage(data=RecordBase)
PNG_Record = photoimage.subsample(2, 2)

#Переменная для одного только шрифта без изменений размера
Helvetica = Font(family='Microsoft Sans Serif')

#Разметка пространства
ProgName = Frame(root, bg ="#2b2f3a",width=22,height=22)
ProgName.grid(row = 0, column = 0, sticky = "nesw")
Label(ProgName,text='ACR of Music',width=14,height=2,bg="#2b2f3a",fg="#bfcbd9",font=('Microsoft Sans Serif',14,'bold')).grid(row=0,column=0)

#Кнопки записи, файла, настроек и инструкции
def record_thread():
    record_thread = threading.Thread(target=record)
    record_thread.start()
Rec=tk.Button(LeftMenu,bg="#304156",image=PNG_Record,compound=LEFT,activebackground='#263445',fg="#bfcbd9",activeforeground='#bfcbd9',font=Helvetica,borderwidth=0,text='Запись c ПК',command=record_thread,width=173,height=40)
Rec.grid(row=0,column=0,sticky="w")

def callback_thread():
    callback_thread = threading.Thread(target=callback)
    callback_thread.start()
Choice=Button(LeftMenu,bg="#304156",image=PNG_File,compound=LEFT,activebackground='#263445',fg="#bfcbd9",activeforeground='#bfcbd9',font=Helvetica,borderwidth=0,text='Выбор файла',command=callback_thread,width=173,height=40)
Choice.grid(row=1,column=0,sticky="w")
set=Button(root,bg="#304156",activebackground='#263445',fg="#bfcbd9",activeforeground='#bfcbd9',font=Helvetica,borderwidth=0,text='Настройки',command=windows.setting,width=22,height=2)
set.grid(row=3,column=0,sticky="s")
fq=Button(root,bg="#304156",activebackground='#263445',fg="#bfcbd9",activeforeground='#bfcbd9',font=Helvetica,borderwidth=0,text='Важные моменты',command=windows.FAQ,width=22,height=2)
fq.grid(row=4,column=0,sticky="s")

#поверх всех окон
TopVar = IntVar()
def TOPMOST():
    if(TopVar.get()==0):
        root.attributes("-topmost",False)
        root.update()
    else:
        root.attributes("-topmost",True)
        root.update()
topmost=Checkbutton(root,bg="#304156",selectcolor="#304156",activebackground='#263445',fg="#bfcbd9",activeforeground='#bfcbd9',font=Helvetica,text='Поверх всех окон',variable=TopVar,onvalue=1, offvalue=0,command=TOPMOST,width=22,height=2)
topmost.grid(row=2,column=0,sticky="s")

#Бинды на ховер
Rec.bind("<Enter>", on_enter)
Choice.bind("<Enter>", on_enter)
set.bind("<Enter>", on_enter)
fq.bind("<Enter>", on_enter)
topmost.bind("<Enter>", on_enter)
Rec.bind("<Leave>", on_leave)
Choice.bind("<Leave>", on_leave)
set.bind("<Leave>", on_leave)
fq.bind("<Leave>", on_leave)
topmost.bind("<Leave>", on_leave)

#Ползунок длительности
v=IntVar()
scale = Scale(variable = v, from_ = 5.0, to = 20.0,bg='#304156',highlightbackground='#304156',activebackground='#263445',fg='#bfcbd9',troughcolor='#2b2f3a', orient = HORIZONTAL)
scale.grid(row=0,column=1,columnspan=2,sticky="nsew")
try:
    scale.set(S)
except:
    S=10
    scale.set(S)

#Вывод данных файла
textline = Text(root,state=DISABLED,width=60,borderwidth=0,bg='#bfcbd9',wrap="word",font=('Microsoft Sans Serif',11))
textline.grid(row=1,rowspan=4,column=1,sticky='sen')

#удаление и сохранение данных при закрытие
def on_closing():
    if os.path.exists(f'{pathname}/Logs/output.wav'):
        os.remove(f'{pathname}/Logs/output.wav')
    if os.path.exists(f'{pathname}/Logs/output_0.wav'):
        os.remove(f'{pathname}/Logs/output_0.wav')
    if os.path.exists(f'{pathname}/Logs/data_file.json'):
        with open(f'{pathname}/Logs/data_file.json', "r") as write_file:
            f=json.load(write_file)
        f['Seconds']=v.get()
        with open(f'{pathname}/Logs/data_file.json', "w") as write_file:
            json.dump(f, write_file)
    raise SystemExit()
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
