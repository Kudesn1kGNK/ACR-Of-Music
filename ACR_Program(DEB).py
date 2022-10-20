#!/usr/bin/env python
#-*- coding:utf-8 -*-
from playsound import playsound
import json,time,base64,hashlib,hmac,requests,pyaudio,os,wave,os.path,subprocess,sys
import webbrowser
from tkinter import filedialog as fd
from tkinter import *
from tkinter import Entry
from tkinter.font import Font
import tkinter as tk

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
    with open(f"{pathname}/Logs/data_file.json", "r") as write_file:
        f=json.load(write_file)
        data_local={
            "AccessKey":f['AccessKey'],
            "SecretKey":f['SecretKey'],
            "Host":f['Host'],
            "Seconds":f['Seconds']
        }
        with open(f"{pathname}/Logs/data_file.json", "w") as write_file:
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
    with open(f"{pathname}/Logs/data_file.json", "w") as write_file:
            json.dump(data_local, write_file)

LeftMenu = Frame(root, bg ="#304156",width=22)
LeftMenu.grid(row=1,rowspan = 10, column = 0, sticky = "nesw")

def on_enter(e):
    e.widget['background'] = '#263445'
def on_leave(e):
    e.widget['background'] = '#304156'

#Предупреждение о несоответствие ключей минимальной характеристике
Warn=Label(root,text='Данные настроек не введены\nили введены не верно',bg='#304156',fg='#ff0000',width=25,font=('Microsoft Sans Serif',8))
if(len(AK)!=32 or len(SK)!=40 or len(H)<24):
    Warn.grid(row=1,column=0,sticky='s')

#Переменные для сбора ключей с полей ввода
textH = StringVar()
textAK = StringVar()
textSK = StringVar()
SUD=IntVar()

#пароль для ffmpeg
def SUDO():
    global sudo
    sudo=tk.Toplevel(root)
    sudo.grab_set()
    sudo.attributes("-topmost",True)
    sudo.resizable(width=0, height=0)
    sudo.title('Установка ffpmeg')

    SudoFrame = Frame(sudo, bg ="#304156")
    SudoFrame.grid(row=1,rowspan = 10, column = 0, sticky = "nesw")

    width = 447
    heigh = 109
    screenwidth = sudo.winfo_screenwidth()
    screenheight = sudo.winfo_screenheight()
    sudo.geometry('%dx%d+%d+%d'%(width, heigh, (screenwidth-width)/2, (screenheight-heigh)/2))

    Label(SudoFrame,font=('Microsoft Sans Serif',12),state='normal',bg="#304156",fg="#bfcbd9",text='Необходимо установить ffmpeg\nПодтвердив данное требование начнется установка\nВы можете установить его самостоятельно\nsudo apt install ffmpeg').grid(row=2,column=0,sticky='n')
    f = Font(family='Microsoft Sans Serif',size=12,underline=True)
    Button(SudoFrame,font=f,bg="#304156",activebackground='#263445',fg="#bfcbd9",activeforeground='#bfcbd9',borderwidth=0,highlightthickness=0,text='Подтвердить',command=mpeg).grid(row=3,column=0,sticky='swe')

def mpeg():
    sudo.destroy()
    try:
        cmd = f"pkexec apt install ffmpeg"
        textline.configure(state=NORMAL)
        textline.insert(1.0, f'ffmpeg устанавливается...\n\n')
        root.update()
        textline.configure(state=DISABLED)
        res = subprocess.call(cmd, shell=True)
        if res != 0:
            textline.configure(state=NORMAL)
            textline.insert(1.0, f'Пароль не подходит\n')
            root.update()
            textline.configure(state=DISABLED)
            return False
        check()
        callback()
        return True
    except Exception:
        textline.configure(state=NORMAL)
        textline.insert(1.0, f'Пароль не подходит\n')
        root.update()
        textline.configure(state=DISABLED)
        return False

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

    width = 590
    heigh = 110
    screenwidth = faq.winfo_screenwidth()
    screenheight = faq.winfo_screenheight()
    faq.geometry('%dx%d+%d+%d'%(width, heigh, (screenwidth-width)/2, (screenheight-heigh)/2))

    Label(faqFrame,font=('Microsoft Sans Serif',11),bg="#304156",fg="#bfcbd9",text=f'1: Ползунком выбирается продолжительность в секундах как для записи\nтак и для файла\n2: Не трогать программу пока идет запись\n3: Обязательным условием записи с ПК — наличие включенного микшера').grid(row=0,column=0)

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

    width = 545
    heigh = 117
    screenwidth = settings.winfo_screenwidth()
    screenheight = settings.winfo_screenheight()
    settings.geometry('%dx%d+%d+%d'%(width, heigh, (screenwidth-width)/2, (screenheight-heigh)/2))

    setFrame=Frame(settings,bg="#304156")
    setFrame.grid(row=0,column=0,sticky = "nesw")

    Label(setFrame,font=('Microsoft Sans Serif',11),bg="#304156",fg="#bfcbd9",text='Host:').grid(row=0,column=0,sticky='w')
    Ent1=Entry(setFrame,textvariable=textH,highlightthickness=0,width=50,bg='#263445',fg="#bfcbd9",insertbackground="#bfcbd9",font=('Microsoft Sans Serif',11))
    Ent1.grid(row=0,column=1,sticky='e')
    Ent1.delete(0, END)
    Ent1.insert(END, f'{H}')

    Label(setFrame,font=('Microsoft Sans Serif',11),bg="#304156",fg="#bfcbd9",text='Access Key:').grid(row=1,column=0,sticky='w')
    Ent2=Entry(setFrame,textvariable=textAK,highlightthickness=0,width=50,bg='#263445',fg="#bfcbd9",insertbackground="#bfcbd9",font=('Microsoft Sans Serif',11))
    Ent2.grid(row=1,column=1,sticky='e')
    Ent2.delete(0, END)
    Ent2.insert(END, f'{AK}')

    Label(setFrame,font=('Microsoft Sans Serif',11),bg="#304156",fg="#bfcbd9",text='Secret Key:').grid(row=2,column=0,sticky='w')
    Ent3=Entry(setFrame,textvariable=textSK,highlightthickness=0,width=50,bg='#263445',fg="#bfcbd9",insertbackground="#bfcbd9",font=('Microsoft Sans Serif',11))
    Ent3.grid(row=2,column=1,sticky='e')
    Ent3.delete(0, END)
    Ent3.insert(END, f'{SK}')

    Label(setFrame,font=('Microsoft Sans Serif',11),bg="#304156",fg="#bfcbd9",text='Все данные находяться на этом сайте:').grid(row=3,columnspan=2,sticky='w')
    lb=Label(setFrame, text="https://www.ACRcloud.com",bg="#304156", fg="#409eff", cursor="hand2",font=('Microsoft Sans Serif',11))
    lb.bind('<Button-1>',web)
    lb.grid(row=3,columnspan=2,sticky='ne')
    enter=Button(setFrame,bg="#304156",activebackground='#263445',fg="#bfcbd9",activeforeground='#bfcbd9',font=Helvetica,borderwidth=0,highlightthickness=0,text='Подтвердить',command=ent)
    enter.grid(row=4,columnspan=2,sticky='we')
    enter.bind("<Enter>", on_enter)
    enter.bind("<Leave>", on_leave)

#Сохранение введеных ключей и присвоение в переменные
def ent():
    global AK,SK,H
    AK=textAK.get()
    SK=textSK.get()
    H=textH.get()
    with open(f"{pathname}/Logs/data_file.json", "r") as write_file:
        f=json.load(write_file)
    f['AccessKey']=str(AK)
    f['SecretKey']=str(SK)
    f['Host']=str(H)
    with open(f"{pathname}/Logs/data_file.json", "w") as write_file:
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
        filename = f"{pathname}/Logs/output.wav"
        p = pyaudio.PyAudio()

        for i in range(p.get_device_count()):
            if ((('default' in p.get_device_info_by_index(i)['name'])and('sysdefault' not in p.get_device_info_by_index(i)['name'])) and (p.get_device_info_by_index(i)['hostApi']==0)):
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

def intercept(input_file, str_second, duration, out_file):
    try:
        cmd = "ffmpeg -y -i %s -ss %s -t %s %s" % (input_file, str_second, duration, out_file)
        res = subprocess.call(cmd, shell=True)

        if res != 0:
            return False
        return True
    except Exception:
        return False

def volume(input_file, volume, out_file):
    try:
        cmd = "ffmpeg -y -i %s -af volume=%s %s" % (input_file, volume, out_file)
        res = subprocess.call(cmd, shell=True)

        if res != 0:
            return False
        return True
    except Exception:
        return False

ffmpeg_try=0
def check():
    global ffmpeg_try
    try:
        cmd = "ffmpeg -version"
        res = subprocess.call(cmd, shell=True)

        if res != 0:
            return False
        ffmpeg_try+=1
        return True
    except Exception:
        return False

#выбор файла с пк
def callback():
    global name,ffmpeg_try
    seconds = v.get()

    if(ffmpeg_try==0):
        SUDO()
        return

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
    
    intercept(f'"{name}"',0,seconds,f'"{pathname}/Logs/output_0.mp3"')
    volume(f'"{pathname}/Logs/output_0.mp3"',2,f'"{pathname}/Logs/output.mp3"')
        
    textline.configure(state=NORMAL)
    textline.insert(1.0, f'\n—{name}\n')
    root.update()
    textline.configure(state=DISABLED)
    func(f'{pathname}/Logs/output.mp3')
    
#Подготовка ключей для сервиса
access_key = AK
access_secret = SK
requrl = f"http://{H}/v1/identify"

http_method = "POST"
http_uri = "/v1/identify"
data_type = "audio"
signature_version = "1"
timestamp = time.time()

#отправка и запрос данных
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
                print(templates)
                textline.insert(1.0,'Закончился днейвной лимит ключей, попробуйте другие или дождитесь завтра')
        root.update()
        textline.configure(state=DISABLED)
        
    except:
        textline.configure(state=NORMAL)
        textline.insert(1.0, f'«Host» введен неправильно или не введен вовсе\n')
        root.update()
        textline.configure(state=DISABLED)
    
    playsound(f'{pathname}/windows-background.mp3')

v=IntVar()

def _onKeyRelease(event):#копирование на всех языках
    ctrl  = (event.state & 0x4) != 0
    if event.keycode==67 and  ctrl and event.keysym.lower() != "c":
        event.widget.event_generate("<<Copy>>")
root.bind("<Key>", _onKeyRelease, "+")

root.grid_columnconfigure(0, weight = 1)
root.grid_rowconfigure(1, weight = 1)

photoimage = PhotoImage(file = f'{pathname}/Logs/File.png')
PNG_File = photoimage.subsample(2, 2)
photoimage = PhotoImage(file = f'{pathname}/Logs/Record.png')
PNG_Record = photoimage.subsample(2, 2)

Helvetica = Font(family='Microsoft Sans Serif')

ProgName = Frame(root, bg ="#2b2f3a",width=22,height=22)
ProgName.grid(row = 0, column = 0, sticky = "nesw")
Label(ProgName,text='ACR of Music',width=14,height=2,bg="#2b2f3a",fg="#bfcbd9",font=('Microsoft Sans Serif',14,'bold')).grid(row=0,column=0)

Rec=Button(LeftMenu,bg="#304156",compound=LEFT,activebackground='#263445',fg="#bfcbd9",activeforeground='#bfcbd9',font=Helvetica,borderwidth=0,highlightthickness=0,text='Запись c ПК',command=record,width=153,height=40)
Rec.grid(row=0,column=0,sticky="w")
Rec.configure(image=PNG_Record)
Choice=Button(LeftMenu,bg="#304156",compound=LEFT,activebackground='#263445',fg="#bfcbd9",activeforeground='#bfcbd9',font=Helvetica,borderwidth=0,highlightthickness=0,text='Выбор файла',command=callback,width=153,height=40)
Choice.grid(row=1,column=0,sticky="w")
Choice.configure(image=PNG_File)
set=Button(root,bg="#304156",activebackground='#263445',fg="#bfcbd9",activeforeground='#bfcbd9',font=Helvetica,borderwidth=0,highlightthickness=0,text='Настройки',command=setting,width=22,height=2)
set.grid(row=2,column=0,sticky="s")
fq=Button(root,bg="#304156",activebackground='#263445',fg="#bfcbd9",activeforeground='#bfcbd9',font=Helvetica,borderwidth=0,highlightthickness=0,text='Важные моменты',command=FAQ,width=22,height=2)
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
textline = Text(root,state=DISABLED,width=53,borderwidth=0,bg='#bfcbd9',font=('Microsoft Sans Serif',11))
textline.grid(row=1,rowspan=3,column=1,sticky='sen')

#удаление и сохранение данных при закрытие
def on_closing():
    if os.path.exists(f'{pathname}/Logs/output.wav'):
        os.remove(f'{pathname}/Logs/output.wav')
    if os.path.exists(f'{pathname}/Logs/output_0.mp3'):
        os.remove(f'{pathname}/Logs/output_0.mp3')
    if os.path.exists(f'{pathname}/Logs/output.mp3'):
        os.remove(f'{pathname}/Logs/output.mp3')
    if os.path.exists(f'{pathname}/Logs/log.json'):
        os.remove(f'{pathname}/Logs/log.json')
    if os.path.exists(f'{pathname}/Logs/data_file.json'):
        with open(f'{pathname}/Logs/data_file.json', "r") as write_file:
            f=json.load(write_file)
        f['Seconds']=v.get()
        with open(f'{pathname}/Logs/data_file.json', "w") as write_file:
            json.dump(f, write_file)
    raise SystemExit()
root.protocol("WM_DELETE_WINDOW", on_closing)
check()
root.mainloop()
