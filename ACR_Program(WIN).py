#!/usr/bin/env python
#-*- coding:utf-8 -*-
#python 3.9
import json,time,base64,hashlib,hmac,requests,pyaudio,os,wave,os.path,sys
import webbrowser
import winsound
from tkinter import filedialog as fd
from tkinter import *
from tkinter import Entry
from tkinter.font import Font
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

pathname = os.path.dirname(sys.argv[0])

if not os.path.exists(f'{pathname}/Logs'):
    os.makedirs(f'{pathname}/Logs')

#Загрузка ключей или создание файла конфигурации
if os.path.exists(f'{pathname}/Logs/data_file.json'):
    with open(f'{pathname}/Logs/data_file.json', "r") as write_file:
        f=json.load(write_file)
        data_local={
            "AccessKey":f['AccessKey'],
            "SecretKey":f['SecretKey'],
            "Host":f['Host'],
            "Seconds":f['Seconds']
        }
        with open(f'{pathname}/Logs/data_file.json', "w") as write_file:
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
    with open(f'{pathname}/Logs/data_file.json', "w") as write_file:
            json.dump(data_local, write_file)

LeftMenu = Frame(root, bg ="#304156",width=22)
LeftMenu.grid(row=1,rowspan = 10, column = 0, sticky = "nesw")

def on_enter(e):
    e.widget['background'] = e.widget['activebackground']
def on_leave(e):
    e.widget['background'] = '#304156'

#Предупреждение о несоответствие ключей минимальной характеристике
Warn=Label(root,text='Данные настроек не введены\nили введены не верно',bg='#304156',fg='#ff0000',width=25,font=('Microsoft Sans Serif',9))
if(len(AK)!=32 or len(SK)!=40 or len(H)<24):
    Warn.grid(row=1,column=0,sticky='s')

#Переменные для сбора ключей с полей ввода
textH = StringVar()
textAK = StringVar()
textSK = StringVar()

def FAQ():
    global faq
    faq=tk.Toplevel(root)
    faq.grab_set()
    # faq.attributes("-topmost",True)
    faq.resizable(width=0, height=0)
    faq.title('Важные моменты пользования')

    faq.grid_columnconfigure(0, weight = 1)
    faq.grid_rowconfigure(0, weight = 1)
    faqFrame=Frame(faq,bg="#304156")
    faqFrame.grid(row=0,column=0,sticky = "nesw")

    width = 580
    heigh = 110
    screenwidth = faq.winfo_screenwidth()
    screenheight = faq.winfo_screenheight()
    faq.geometry('%dx%d+%d+%d'%(width, heigh, (screenwidth-width)/2, (screenheight-heigh)/2))

    Label(faqFrame,font=('Microsoft Sans Serif',12),bg="#304156",fg="#bfcbd9",text=f'1: Ползунком выбирается продолжительность в секундах как для записи\nтак и для файла\n2: Не трогать программу пока идет запись\n3: Обязательным условием записи с ПК — наличие включенного микшера').grid(row=0,column=0)


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

    width = 492
    heigh = 127
    screenwidth = settings.winfo_screenwidth()
    screenheight = settings.winfo_screenheight()
    settings.geometry('%dx%d+%d+%d'%(width, heigh, (screenwidth-width)/2, (screenheight-heigh)/2))

    setFrame=Frame(settings,bg="#304156")
    setFrame.grid(row=0,column=0,sticky = "nesw")

    Label(setFrame,font=('Microsoft Sans Serif',11),bg="#304156",fg="#bfcbd9",text='Host:').grid(row=0,column=0,sticky='w')
    Ent1=Entry(setFrame,textvariable=textH,width=50,bg='#263445',fg="#bfcbd9",insertbackground="#bfcbd9",font=('Microsoft Sans Serif',11))
    Ent1.grid(row=0,column=1,sticky='e')
    Ent1.delete(0, END)
    Ent1.insert(END, f'{H}')

    Label(setFrame,font=('Microsoft Sans Serif',11),bg="#304156",fg="#bfcbd9",text='Access Key:').grid(row=1,column=0,sticky='w')
    Ent2=Entry(setFrame,textvariable=textAK,width=50,bg='#263445',fg="#bfcbd9",insertbackground="#bfcbd9",font=('Microsoft Sans Serif',11))
    Ent2.grid(row=1,column=1,sticky='e')
    Ent2.delete(0, END)
    Ent2.insert(END, f'{AK}')

    Label(setFrame,font=('Microsoft Sans Serif',11),bg="#304156",fg="#bfcbd9",text='Secret Key:').grid(row=2,column=0,sticky='w')
    Ent3=Entry(setFrame,textvariable=textSK,width=50,bg='#263445',fg="#bfcbd9",insertbackground="#bfcbd9",font=('Microsoft Sans Serif',11))
    Ent3.grid(row=2,column=1,sticky='e')
    Ent3.delete(0, END)
    Ent3.insert(END, f'{SK}')

    Label(setFrame,font=('Microsoft Sans Serif',11),bg="#304156",fg="#bfcbd9",text='Все данные находяться на этом сайте:').grid(row=3,columnspan=2,sticky='w')
    lb=Label(setFrame, text="https://www.ACRcloud.com",bg="#304156", fg="#409eff", cursor="hand2",font=('Microsoft Sans Serif',11))
    lb.bind('<Button-1>',web)
    lb.grid(row=3,columnspan=2,sticky='ne')
    enter=Button(setFrame,bg="#304156",activebackground='#263445',fg="#bfcbd9",activeforeground='#bfcbd9',font=Helvetica,borderwidth=0,text='Подтвердить',command=ent)
    enter.grid(row=4,columnspan=2,sticky='we')
    enter.bind("<Enter>", on_enter)
    enter.bind("<Leave>", on_leave)

#Сохранение введеных ключей и присвоение в переменные
def ent():
    global AK,SK,H
    AK=textAK.get()
    SK=textSK.get()
    H=textH.get()
    with open(f'{pathname}/Logs/data_file.json', "r") as write_file:
        f=json.load(write_file)
    f['AccessKey']=str(AK)
    f['SecretKey']=str(SK)
    f['Host']=str(H)
    with open(f'{pathname}/Logs/data_file.json', "w") as write_file:
        json.dump(f,write_file)
    
    print(AK,SK,H)
    global access_key,access_secret,requrl
    access_key = AK
    access_secret = SK
    requrl = f"http://{H}/v1/identify"
    if(len(AK)!=32 or len(SK)!=40 or len(H)<=24):
        Warn.grid(row=1,column=0,sticky='s')
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
        filename = f'{pathname}/Logs/output.wav'
        p = pyaudio.PyAudio()

        for i in range(p.get_device_count()):
            if ((('Stereo Mix' in p.get_device_info_by_index(i)['name'])or('Стерео микшер' in p.get_device_info_by_index(i)['name'])) and (p.get_device_info_by_index(i)['hostApi']==0)):
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
        name=f'{pathname}/Logs/output.wav'
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
    
    audio.a_intercept(f'"{name}"',0,seconds,f'"{pathname}\Logs\output_0.mp3"')
    audio.a_volume(f'"{pathname}\Logs\output_0.mp3"',2,f'"{pathname}\Logs\output.mp3"')
        
    textline.configure(state=NORMAL)
    textline.insert(1.0, f'\n—{name}\n')
    root.update()
    textline.configure(state=DISABLED)

    func(f'{pathname}\Logs\output.mp3')
    
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
        with open(f'{pathname}/Logs/log.json','w+',encoding='utf-8') as log:
            log.write(r.text)
        with open(f'{pathname}/Logs/log.json','r',encoding='utf-8') as log:
            global templates
            templates = json.load(log)

        #вывод лога в текстовое окно приложения
        textline.configure(state=NORMAL)
        try:
            Album=templates['metadata']['music'][0]['album']['name']
            try:
                Artist=templates ['metadata']['music'][0]['artists'][0]['name']
            except:
                try:
                    Artist=templates ['metadata']['music'][0]['artists'][0]['name'][0]
                except:
                    Artist=templates['metadata']['music'][0]['label']
            Title=templates['metadata']['music'][0]['title']
            textline.insert(1.0,f'Альбом — {Album}\n{Artist} — {Title}')
        except:
            if(templates['status']['msg']=="No result"):
                textline.insert(1.0,'Нет результа, попробуйте ещё раз')
            elif(templates['status']['msg']=="invalid signature"):
                textline.insert(1.0,'Ключи введены не правильно или не введены вовсе')
            elif(templates['status']['msg']=="Can't generate fingerprint"):
                textline.insert(1.0,'Отсутствует звук, кромешная тишина')
            else:
                textline.insert(1.0,'Закончился днейвной лимит ключей или брандмауэр блокирует соединение')
        root.update()
        textline.configure(state=DISABLED)
        
    except:
        textline.configure(state=NORMAL)
        textline.insert(1.0, f'«Host» введен неправильно или не введен вовсе\n')
        root.update()
        textline.configure(state=DISABLED)
    
    winsound.MessageBeep() #сигнал о завершение

v=IntVar()

def _onKeyRelease(event):#копирование на всех языках
    ctrl  = (event.state & 0x4) != 0
    if event.keycode==67 and  ctrl and event.keysym.lower() != "c":
        event.widget.event_generate("<<Copy>>")
root.bind("<Key>", _onKeyRelease, "+")

root.grid_columnconfigure(0, weight = 1)
root.grid_rowconfigure(1, weight = 1)

FileBase=b'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAABJmlDQ1BBZG9iZSBSR0IgKDE5OTgpAAAoz2NgYDJwdHFyZRJgYMjNKykKcndSiIiMUmA/z8DGwMwABonJxQWOAQE+IHZefl4qAwb4do2BEURf1gWZxUAa4EouKCoB0n+A2CgltTiZgYHRAMjOLi8pAIozzgGyRZKywewNIHZRSJAzkH0EyOZLh7CvgNhJEPYTELsI6Akg+wtIfTqYzcQBNgfClgGxS1IrQPYyOOcXVBZlpmeUKBhaWloqOKbkJ6UqBFcWl6TmFit45iXnFxXkFyWWpKYA1ULcBwaCEIWgENMAarTQZKAyAMUDhPU5EBy+jGJnEGIIkFxaVAZlMjIZE+YjzJgjwcDgv5SBgeUPQsykl4FhgQ4DA/9UhJiaIQODgD4Dw745AMDGT/0ZOjZcAAAACXBIWXMAAAsTAAALEwEAmpwYAAAE7mlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNi4wLWMwMDYgNzkuZGFiYWNiYiwgMjAyMS8wNC8xNC0wMDozOTo0NCAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iIHhtbG5zOnBob3Rvc2hvcD0iaHR0cDovL25zLmFkb2JlLmNvbS9waG90b3Nob3AvMS4wLyIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0RXZ0PSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VFdmVudCMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIDIyLjQgKFdpbmRvd3MpIiB4bXA6Q3JlYXRlRGF0ZT0iMjAyMi0xMC0xOVQxOTozMjo0NCswMzowMCIgeG1wOk1vZGlmeURhdGU9IjIwMjItMTAtMTlUMTk6Mzc6MDErMDM6MDAiIHhtcDpNZXRhZGF0YURhdGU9IjIwMjItMTAtMTlUMTk6Mzc6MDErMDM6MDAiIGRjOmZvcm1hdD0iaW1hZ2UvcG5nIiBwaG90b3Nob3A6Q29sb3JNb2RlPSIzIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOjY5ZmU0Mjc3LTM4YWMtMGI0Yi1hYjAzLWZkMTMyYTM3YjBkYSIgeG1wTU06RG9jdW1lbnRJRD0ieG1wLmRpZDo2OWZlNDI3Ny0zOGFjLTBiNGItYWIwMy1mZDEzMmEzN2IwZGEiIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDo2OWZlNDI3Ny0zOGFjLTBiNGItYWIwMy1mZDEzMmEzN2IwZGEiPiA8eG1wTU06SGlzdG9yeT4gPHJkZjpTZXE+IDxyZGY6bGkgc3RFdnQ6YWN0aW9uPSJjcmVhdGVkIiBzdEV2dDppbnN0YW5jZUlEPSJ4bXAuaWlkOjY5ZmU0Mjc3LTM4YWMtMGI0Yi1hYjAzLWZkMTMyYTM3YjBkYSIgc3RFdnQ6d2hlbj0iMjAyMi0xMC0xOVQxOTozMjo0NCswMzowMCIgc3RFdnQ6c29mdHdhcmVBZ2VudD0iQWRvYmUgUGhvdG9zaG9wIDIyLjQgKFdpbmRvd3MpIi8+IDwvcmRmOlNlcT4gPC94bXBNTTpIaXN0b3J5PiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/PqwwApkAAAJsSURBVGje7ZlBaNNQGMcrjqEwplWUOQrCpDLoseK1DLpBLxaE7TQ8lcHmYYhgETw4aJ0XBaGD9rSBPVS8eYqMjR52aGVjh13GYEVBHIpohWkHc8b/c1/gGV7TtI3Ji7zAD5r3XvK9X/O9l7wkEPiHW7VafQh0B4ka59Z1/Q9+6rx7AoLOPwFTHZJxVUDQ+ftdni9qKUANnCJr6nzRgXNOthLQfcT/LZBxOJ2cwnYKTQUk3OwMYiWgBJSAElACSkAJKAEl4IEAYg6CCdBv0eYiSIN5EJJN4DXF/gJy4HqpVDph51hZBNYFi5aP4CVbS4MkpdAlEITcSVkF3oGvNldl35mYbAIFcAokwBxYBt8sJPKyCSw2qb9AKRQH42DXEJZxDFTANAjbuWIyD2LGJ/AKPAYz9O+Pgh1ZBTbAWhuvV6QTKHA3rST986s0O/30jYBo0zStB/XnwBDY8p1AO4P4eRevwJtxxQjOHhGwfw3cAjfAeacFnGajXC73UuBw9Xjj6xtgX2aBBAUdAB9azSodC7iQ5wsU9AjMgrNgGKw0E6B0S9H0yq7UHn1reOuFwHsKumQqD4IfZgHqfNH2fcAFgQMKeldQZ9xZc1xZiuvoJrgHntJTqCcC2xRUM5VfBYdUd0eQ55uVSqWXK4+BX14IPDB9M4vTR4saNxuFuPYNKk8LzlXzQuA0eGORz7dN7T8bn2b5cnY1UFanuqxrAhS8j9a8fB6z/L8pEH7BrbxiXOfz3LEjrgqYrkYEXLZoE+FmJ50WMXVuX/trTSzpu6AxLpV4NDb9Si9AEmfoeeoZeMTSRvhaxfjhV3wv8BtR4EcJoAtCKQAAAABJRU5ErkJggg=='
photoimage = PhotoImage(data=FileBase)
PNG_File = photoimage.subsample(2, 2)
RecordBase=b'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAABMWlDQ1BBZG9iZSBSR0IgKDE5OTgpAAAoz62OsUrDUBRAz4ui4lArBHFweJMoKLbqYMakLUUQrNUhydakoUppEl5e1X6Eo1sHF3e/wMlRcFD8Av9AcergECGDgwie6dzD5XLBqNh1p2GUYRBr1W460vV8OfvEDFMA0Amz1G61DgDiJI74wecrAuB50647Df7GfJgqDUyA7W6UhSAqQP9CpxrEGDCDfqpB3AGmOmnXQDwApV7uL0ApyP0NKCnX80F8AGbP9Xww5gAzyH0FMHV0qQFqSTpSZ71TLauWZUm7mwSRPB5lOhpkcj8OE5UmqqOjLpD/B8BivthuOnKtall76/wzrufL3N6PEIBYeixaQThU598qjJ3f5+LGeBkOb2F6UrTdK7jZgIXroq1WobwF9+MvwMZP/U6/OGUAAAAJcEhZcwAACxMAAAsTAQCanBgAAATuaVRYdFhNTDpjb20uYWRvYmUueG1wAAAAAAA8P3hwYWNrZXQgYmVnaW49Iu+7vyIgaWQ9Ilc1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCI/PiA8eDp4bXBtZXRhIHhtbG5zOng9ImFkb2JlOm5zOm1ldGEvIiB4OnhtcHRrPSJBZG9iZSBYTVAgQ29yZSA2LjAtYzAwNiA3OS5kYWJhY2JiLCAyMDIxLzA0LzE0LTAwOjM5OjQ0ICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyIgeG1sbnM6cGhvdG9zaG9wPSJodHRwOi8vbnMuYWRvYmUuY29tL3Bob3Rvc2hvcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgMjIuNCAoV2luZG93cykiIHhtcDpDcmVhdGVEYXRlPSIyMDIyLTEwLTE5VDE5OjM3OjU2KzAzOjAwIiB4bXA6TW9kaWZ5RGF0ZT0iMjAyMi0xMC0xOVQxOTozODozMSswMzowMCIgeG1wOk1ldGFkYXRhRGF0ZT0iMjAyMi0xMC0xOVQxOTozODozMSswMzowMCIgZGM6Zm9ybWF0PSJpbWFnZS9wbmciIHBob3Rvc2hvcDpDb2xvck1vZGU9IjMiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6NDc4YTRiMTAtNDFhMS1kOTRjLWI1YjItZmQwMzZkODAyYzQwIiB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOjQ3OGE0YjEwLTQxYTEtZDk0Yy1iNWIyLWZkMDM2ZDgwMmM0MCIgeG1wTU06T3JpZ2luYWxEb2N1bWVudElEPSJ4bXAuZGlkOjQ3OGE0YjEwLTQxYTEtZDk0Yy1iNWIyLWZkMDM2ZDgwMmM0MCI+IDx4bXBNTTpIaXN0b3J5PiA8cmRmOlNlcT4gPHJkZjpsaSBzdEV2dDphY3Rpb249ImNyZWF0ZWQiIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6NDc4YTRiMTAtNDFhMS1kOTRjLWI1YjItZmQwMzZkODAyYzQwIiBzdEV2dDp3aGVuPSIyMDIyLTEwLTE5VDE5OjM3OjU2KzAzOjAwIiBzdEV2dDpzb2Z0d2FyZUFnZW50PSJBZG9iZSBQaG90b3Nob3AgMjIuNCAoV2luZG93cykiLz4gPC9yZGY6U2VxPiA8L3htcE1NOkhpc3Rvcnk+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwveDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+orpVOwAAAnxJREFUaN7t2UuITXEcB/DbDFM0Hhs0mTxSkoUy8lhMEbJRVpTF2IoVumyGhZSwwkoWQmpCUiwkKV0y93ykJEoiolhJHg3N9bgWjrrpPs4c59x7JvOr/+Iuzv9+P6fT/5krl8u50dxyY4AxQEqAJKpQKEzESvQk0V/qAHRhI476XSWUMTQwMNCeOQBmYBvO4UUYtmorFApTMgXATgzXC13ZisVid2YAWB01eEVbkCXA+RiAZVkC3Bth+J9YmCXA/QihP+Aa9mFppobRGoC3uIgdWNLT09OWS7jSADzAZnTlmlBJA95haq6JlTTgeq7JlTTgatIBBwcH27EI23EKp7EmswBMxjrsxw18rDEE92UCgHnYghN4iO8R55GXLQVgPR7HmL0r27iWALB2BG+6ZguCoKNVgNv/Gr7VgA8tBWAh9uICzqIv3LxEBQy3DBAGL9XoNNuA8E3X6zQtwFOcwVYsxeW4gGcN/uhKAoCvuIMj2IBpVZ7vjwv40gBwPAbgDS5hF1YEQdAR4fnYgDt1wg9F3eOGgALmxlxuxAYsxucq4T9h4wgCDOPgP6yX+mOPQsVisRvHwjdYwAHMHmGA1gGSqDgAzMT0UQXABBzCq4rP9TmeZB6ASXjUtLVQCoCTTV3M1QkyHr3YhFXh71IEwPsGgFI+n29LDZDP59vCw96PVWbacgTA6waAm6neD4RDbb0AjQCH6zz7CfNTA2B5uPGODQiCoCO8Y/i7n7uVZ6ppAfZEWGHujtjXrHBR14c5TbliCo8W64X/9ucTyOQdGTrDNXy18D+wI3Mnc1UQc8Kj9D+7txJuoTeTR4sN5oG56Gz52ejYTf0Y4D8B/AJeIGY6skaY/QAAAABJRU5ErkJggg=='
photoimage = PhotoImage(data=RecordBase)
PNG_Record = photoimage.subsample(2, 2)

Helvetica = Font(family='Microsoft Sans Serif')

ProgName = Frame(root, bg ="#2b2f3a",width=22,height=22)
ProgName.grid(row = 0, column = 0, sticky = "nesw")
Label(ProgName,text='ACR of Music',width=14,height=2,bg="#2b2f3a",fg="#bfcbd9",font=('Microsoft Sans Serif',14,'bold')).grid(row=0,column=0)

Rec=Button(LeftMenu,bg="#304156",image=PNG_Record,compound=LEFT,activebackground='#263445',fg="#bfcbd9",activeforeground='#bfcbd9',font=Helvetica,borderwidth=0,text='Запись c ПК',command=record,width=171,height=40)
Rec.grid(row=0,column=0,sticky="w")
Choice=Button(LeftMenu,bg="#304156",image=PNG_File,compound=LEFT,activebackground='#263445',fg="#bfcbd9",activeforeground='#bfcbd9',font=Helvetica,borderwidth=0,text='Выбор файла',command=callback,width=171,height=40)
Choice.grid(row=1,column=0,sticky="w")
set=Button(root,bg="#304156",activebackground='#263445',fg="#bfcbd9",activeforeground='#bfcbd9',font=Helvetica,borderwidth=0,text='Настройки',command=setting,width=22,height=2)
set.grid(row=2,column=0,sticky="s")
fq=Button(root,bg="#304156",activebackground='#263445',fg="#bfcbd9",activeforeground='#bfcbd9',font=Helvetica,borderwidth=0,text='Важные моменты',command=FAQ,width=22,height=2)
fq.grid(row=3,column=0,sticky="s")

Rec.bind("<Enter>", on_enter)
Choice.bind("<Enter>", on_enter)
set.bind("<Enter>", on_enter)
fq.bind("<Enter>", on_enter)
Rec.bind("<Leave>", on_leave)
Choice.bind("<Leave>", on_leave)
set.bind("<Leave>", on_leave)
fq.bind("<Leave>", on_leave)

scale = Scale(variable = v, from_ = 5.0, to = 20.0,bg='#304156',highlightbackground='#304156',activebackground='#263445',fg='#bfcbd9',troughcolor='#2b2f3a', orient = HORIZONTAL)
scale.grid(row=0,column=1,columnspan=2,sticky="nsew")
scale.set(S)

#Вывод данных файла
textline = Text(root,state=DISABLED,width=60,borderwidth=0,bg='#bfcbd9',font=('Microsoft Sans Serif',11))
textline.grid(row=1,rowspan=3,column=1,sticky='sen')

#удаление и сохранение данных при закрытие
def on_closing():
    if os.path.exists(f'{pathname}/Logs/output.wav'):
        os.remove(f'{pathname}/Logs/output.wav')
    if os.path.exists(f'{pathname}/Logs/output.mp3'):
        os.remove(f'{pathname}/Logs/output.mp3')
    if os.path.exists(f'{pathname}/Logs/output_0.mp3'):
        os.remove(f'{pathname}/Logs/output_0.mp3')
    if os.path.exists(f'{pathname}/Logs/log.json'):
        os.remove(f'{pathname}/Logs/log.json')
    if os.path.exists(f'{pathname}/Logs/script.cmd'):
        os.remove(f'{pathname}/Logs/script.cmd')
    if os.path.exists(f'{pathname}/Logs/data_file.json'):
        with open(f'{pathname}/Logs/data_file.json', "r") as write_file:
            f=json.load(write_file)
        f['Seconds']=v.get()
        with open(f'{pathname}/Logs/data_file.json', "w") as write_file:
            json.dump(f, write_file)
    raise SystemExit()
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
