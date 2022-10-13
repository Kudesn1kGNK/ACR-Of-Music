#!/usr/bin/env python
#-*- coding:utf-8 -*-
import json,time,base64,hashlib,hmac,requests,pyaudio,os,wave,os.path
from PyQt6 import QtGui
import webbrowser
import winsound
from matplotlib.pyplot import text
from tkinter import filedialog as fd
from tkinter import *
from tkinter import Entry
import tkinter as tk
from ffmpeg import audio

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

#Объявление переменных под ключи
AK=''
SK=''
H=''

S=10#Секунды по умолчанию

if not os.path.exists('Logs'):
    os.makedirs('Logs')

#Загрузка ключей или создание файла конфигурации
if os.path.exists('Logs/data_file.json'):
    with open("Logs/data_file.json", "r") as write_file:
        f=json.load(write_file)
        data_local={
            "AccessKey":f['AccessKey'],
            "SecretKey":f['SecretKey'],
            "Host":f['Host'],
            "Seconds":f['Seconds']
        }
        with open("Logs/data_file.json", "w") as write_file:
            json.dump(data_local, write_file)
        AK=data_local['AccessKey']
        SK=data_local['SecretKey']
        H=data_local['Host']
        S=data_local['Seconds']
else:
    data_local={
            "AccessKey":'',
            "SecretKey":'',
            "Host":'',
            "Seconds":''
        }
    with open("Logs/data_file.json", "w") as write_file:
            json.dump(data_local, write_file)

#Предупреждение о несоответствие ключей минимальной характеристике
Warn=Label(text='Данные настроек не введены или введены не верно',fg='#ff0000')
if(len(AK)!=32 or len(SK)!=40 or len(H)<24):
    Warn.grid(row=5,columnspan=2)

#Переменные для сбора ключей с полей ввода
textH = StringVar()
textAK = StringVar()
textSK = StringVar()

#ввод ключей
def setting():
    def web(event):
        webbrowser.open_new(r"https://www.acrcloud.com")
    global settings
    settings=tk.Toplevel(root)
    settings.grab_set()
    settings.attributes("-topmost",True)
    settings.resizable(width=0, height=0)
    settings.title('Настройка ключей')

    width = 370
    heigh = 110
    screenwidth = settings.winfo_screenwidth()
    screenheight = settings.winfo_screenheight()
    settings.geometry('%dx%d+%d+%d'%(width, heigh, (screenwidth-width)/2, (screenheight-heigh)/2))

    Label(settings,text='Host:').grid(row=0,column=0,sticky='w')
    Ent1=Entry(settings,textvariable=textH,width=50)
    Ent1.grid(row=0,column=1,sticky='e')
    Ent1.delete(0, END)
    Ent1.insert(END, f'{H}')

    Label(settings,text='Access Key:').grid(row=1,column=0,sticky='w')
    Ent2=Entry(settings,textvariable=textAK,width=50)
    Ent2.grid(row=1,column=1,sticky='e')
    Ent2.delete(0, END)
    Ent2.insert(END, f'{AK}')

    Label(settings,text='Secret Key:').grid(row=2,column=0,sticky='w')
    Ent3=Entry(settings,textvariable=textSK,width=50)
    Ent3.grid(row=2,column=1,sticky='e')
    Ent3.delete(0, END)
    Ent3.insert(END, f'{SK}')

    Label(settings,text='Все данные находяться на этом сайте:').grid(row=3,columnspan=2,sticky='w')
    lb=Label(settings, text="https://www.ACRcloud.com", fg="blue", cursor="hand2")
    lb.bind('<Button-1>',web)
    lb.grid(row=3,columnspan=2,sticky='ne')
    Button(settings,text='Подтвердить',command=ent).grid(row=4,columnspan=2,sticky='we')

    

#Менюбар с входом в настройки конфигурации
menubar = Menu(root)
root.config(menu=menubar)
menubar.add_cascade(
    label="Settings",
    command=setting
)

#Сохранение введеных ключей и присвоение в переменные
def ent():
    global AK,SK,H
    AK=textAK.get()
    SK=textSK.get()
    H=textH.get()
    with open("Logs/data_file.json", "r") as write_file:
        f=json.load(write_file)
    f['AccessKey']=str(AK)
    f['SecretKey']=str(SK)
    f['Host']=str(H)
    with open("Logs/data_file.json", "w") as write_file:
        json.dump(f,write_file)
    
    print(AK,SK,H)
    global access_key,access_secret,requrl
    access_key = AK
    access_secret = SK
    requrl = f"http://{H}/v1/identify"
    if(len(AK)!=32 or len(SK)!=40 or len(H)<=24):
        Warn.grid(row=5,columnspan=2)
    elif (Warn.winfo_exists):
        Warn.grid_forget()
        root.update()

#функция записи с микшера и записывание в файл формата wav
def record():
    try:
        chunk = 1024
        sample_format = pyaudio.paInt16
        channels = 2
        rate = 44100
        seconds = v.get()
        filename = "Logs/output.wav"
        p = pyaudio.PyAudio()

        for i in range(p.get_device_count()):
            if (('Stereo Mix' in p.get_device_info_by_index(i)['name']) and (p.get_device_info_by_index(i)['hostApi']==0)):
                global index
                index=i
                textline.configure(state=NORMAL)
                textline.insert(1.0, f'\nЗапись|{seconds}s\n\n')
                root.update()
                textline.configure(state=DISABLED)
                break

        stream = p.open(format=sample_format,
        channels=channels,
        rate=rate,
        frames_per_buffer=chunk,
        input_device_index=index,
        input=True)

        frames = []

        for i in range(0, int(rate / chunk * seconds)):
            data = stream.read(chunk)
            frames.append(data)
        stream.stop_stream()
        stream.close()

        p.terminate()
        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        global name
        name='Logs/output.wav'
        func(name)
    except:
        textline.configure(state=NORMAL)
        textline.insert(1.0, f'Включите микшер и перезагрузите программу\n\n')
        root.update()
        textline.configure(state=DISABLED)

#выбор файла с пк
def callback():
    global name
    seconds = v.get()
    name = fd.askopenfilename()

    try:
        f = open(name, 'r')
        f.close()
    except:
        return

    textline.configure(state=NORMAL)
    textline.insert(1.0, '—Обрезаем аудио\видео\n\n')
    root.update()
    textline.configure(state=DISABLED)
    
    audio.a_intercept(f'"{name}"',0,seconds,'Logs/output.mp3')
    audio.a_volume('Logs/output.mp3',2,'output.mp3')
        
    textline.configure(state=NORMAL)
    textline.insert(1.0, f'\n—{name}\n')
    root.update()
    textline.configure(state=DISABLED)

    func('Logs/output.mp3')
    
#Подготовка ключей для сервиса
access_key = AK
access_secret = SK
requrl = f"http://{H}/v1/identify"

http_method = "POST"
http_uri = "/v1/identify"
data_type = "audio"
signature_version = "1"
timestamp = time.time()

def func(name):
    string_to_sign = http_method + "\n" + http_uri + "\n" + access_key + "\n" + data_type + "\n" + signature_version + "\n" + str(timestamp)
    sign = base64.b64encode(hmac.new(access_secret.encode('ascii'), string_to_sign.encode('ascii'),digestmod=hashlib.sha1).digest()).decode('ascii')
    global sample_bytes
    sample_bytes = os.path.getsize(name)

    files = [
        ('sample', ('1.mp4', open(f'{name}', 'rb'), 'audio/mpeg'))
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
        r = requests.post(requrl, files=files, data=data)
        r.encoding = "utf-8"

        #запись вывода в лог файл
        with open('Logs/log.json','w+',encoding='utf-8') as log:
            log.write(r.text)
        with open('Logs/log.json','r',encoding='utf-8') as log:
            global templates
            templates = json.load(log)

        #вывод лога в текстовое окно приложения
        textline.configure(state=NORMAL)
        # textline.insert(1.0, json.dumps(templates, sort_keys=True,indent=4,ensure_ascii=False))
        try:
            Album=templates['metadata']['music'][0]['album']['name']
            Artist=templates['metadata']['music'][0]['label']
            Title=templates['metadata']['music'][0]['title']
            textline.insert(1.0,f'Альбом — {Album}\n{Artist} — {Title}')
        except:
            if(templates['status']['msg']=="No result"):
                textline.insert(1.0,'Нет результа, попробуйте ещё раз')
            elif(templates['status']['msg']=="invalid signature"):
                textline.insert(1.0,'Ключи введены не правильно или не введены вовсе')
            else:
                textline.insert(1.0,'Закончился днейвной лимит ключей, попробуйте другие или дождитесь завтра')
        root.update()
        textline.configure(state=DISABLED)
        
    except:
        textline.configure(state=NORMAL)
        textline.insert(1.0, f'«Host» введен неправильно или не введен вовсе\n')
        root.update()
        textline.configure(state=DISABLED)
    
    winsound.MessageBeep() #сигнал о завершение

v=IntVar()

Label(root,text=f'1: Не трогать программу пока идет запись\n2: Обязательным условием записи с ПК — наличие включенного микшера').grid(row=0,columnspan=3)
# Button(root,text='Запись c ПК',command=rec.start,width=1).grid(row=1,column=0,sticky="nsew")
Button(root,text='Запись c ПК',command=record,width=1).grid(row=1,column=0,sticky="nsew")
Button(root,text='Выбор файла',command=callback,width=1).grid(row=1,column=1,sticky="nsew")
scale = Scale(variable = v, from_ = 5, to = 20, orient = HORIZONTAL)
scale.grid(row=3,columnspan=2,sticky="nsew")
scale.set(S)
Label(text='Сколько секунд будет запись/аудио\видео').grid(row=2,columnspan=2,sticky="n")
Label(text='↓Вывод↓').grid(row=4,columnspan=2)

def _onKeyRelease(event):#копирование на всех языках
    ctrl  = (event.state & 0x4) != 0
    if event.keycode==67 and  ctrl and event.keysym.lower() != "c":
        event.widget.event_generate("<<Copy>>")

#Вывод данных файла
textline = Text(state=DISABLED)
root.bind("<Key>", _onKeyRelease, "+")
textline.grid(row=6,columnspan=2,sticky='ew')
scroll = Scrollbar(command=textline.yview)
scroll.grid(row=6,column=3,sticky='ns')
textline.config(yscrollcommand=scroll.set)

#удаление и сохранение данных при закрытие
def on_closing():
    if os.path.exists('Logs/output.wav'):
        os.remove('Logs/output.wav')
    if os.path.exists('Logs/output.mp3'):
        os.remove('Logs/output.mp3')
    if os.path.exists('Logs/log.json'):
        os.remove('Logs/log.json')
    if os.path.exists('Logs/script.cmd'):
        os.remove('Logs/script.cmd')
    if os.path.exists('Logs/data_file.json'):
        with open("Logs/data_file.json", "r") as write_file:
            f=json.load(write_file)
        f['Seconds']=v.get()
        with open("Logs/data_file.json", "w") as write_file:
            json.dump(f, write_file)
    raise SystemExit()
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
