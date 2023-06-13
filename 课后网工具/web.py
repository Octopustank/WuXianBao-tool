###################################################
##############--Author:Octpus_tank--###############
##############--------v3.50--------################
###################################################
from flask import Flask, request, render_template, make_response,\
     redirect

import pyautogui as pag
from PIL import ImageGrab, Image
import os
import time as tm
import win32api ,win32con ,win32ui ,win32gui
import platform as pl
import json as js
################################################################
def load():#加载-主函数
    global OS, RES_WIDTH , RES_HEIGHT ,RECORDTXT ,ACTIONTM ,REMOTESHOT ,MAIN
    OS=pl.release()
    PATH=os.getcwd()##[
    MAIN=os.path.join(PATH,'main.py')
    RES=os.path.join(PATH,'res')
    ACTIONTM=os.path.join(RES,'move_time.res')
    REMOTESHOT=os.path.join(PATH,'remote_shot')
    RECORD=os.path.join(PATH,'record')
    RECORDTXT=os.path.join(RECORD,'record.json')##]
    MointorDev=win32api.EnumDisplayMonitors(None,None)##[
    RES_WIDTH=MointorDev[0][2][2]
    RES_HEIGHT=MointorDev[0][2][3]##]
#################################################
def grab1a():#剪切板方式子函数
    win32api.keybd_event(0x91,0,0,0)
    win32api.keybd_event(0x2C,0,0,0)
    win32api.keybd_event(0x91,0,win32con.KEYEVENTF_KEYUP,0)
    win32api.keybd_event(0x2C,0,win32con.KEYEVENTF_KEYUP,0)
    try:
        img=ImageGrab.grabclipboard()
    except Exception as r:
        img=False
    return img
def grab1():#剪切板方式主函数
    img=grab1a()
    while img is None or img==False:#如果没有获取图片,重试
        img=grab1a()
        tm.sleep(0.1)
    return img
########################
def grab2():#内存读出方式主函数
    WINDOW = 0              # 当前活跃窗口
    WDC = win32gui.GetWindowDC(WINDOW)      # 设备上下文dc
    MDC = win32ui.CreateDCFromHandle(WDC)   # mfcDC
    SaveDC = MDC.CreateCompatibleDC()       # 可兼容dc
    SaveBitMap = win32ui.CreateBitmap()     # 保存图片用bitmap
    SaveBitMap.CreateCompatibleBitmap(MDC,RES_WIDTH,RES_HEIGHT)
    # 为bitmap开辟空间
    SaveDC.SelectObject(SaveBitMap)         #  结果保存到savebitmap
    SaveDC.BitBlt((0,0),(RES_WIDTH,RES_HEIGHT),MDC,(0,0),win32con.SRCCOPY)
    # 获取位图信息
    bmpinfo = SaveBitMap.GetInfo()
    bmpstr = SaveBitMap.GetBitmapBits(True)
    # 生成图像
    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)
    win32gui.DeleteObject(SaveBitMap.GetHandle())
    SaveDC.DeleteDC()
    MDC.DeleteDC()
    win32gui.ReleaseDC(WINDOW,WDC)
    return im
########################
def shot():#截图主函数
    if OS in ['7','XP']:
        img=grab1()
        mode = 1
    else:
        img=grab2()
        mode = 2
    save(img, mode)

def save(im,mode):#保存图片
    tmnw = tm.strftime("%Y%m%d%H%M%S", tm.localtime())
    imgname = f'screenshot{mode}-'+tmnw+'.jpg'
    im.save(os.path.join(REMOTESHOT, imgname))
#################################################
def checkt(trd):#检查动作时间数据
    flag=True
    try:
        t=float(trd)
        if not 0<=t<20:
            flag=False
    except Exception as er:
        flag=False
    return flag
def check_main():
    flag = True
    tmnw = tm.time()
    try:
        with open('temp.temp','r') as f:
            t = float(f.read())
        print(t,tmnw)
        if t<tmnw:
            flag = False
    except:
        flag = False
    return flag
################################################################
app = Flask(__name__,static_url_path='')
################################################
@app.route('/')
def main():
    return redirect('/index')
@app.route('/index')
def index():
    return render_template("index.html")
################################################
@app.route('/records')
def show_records():
    record = RECORDTXT
    if not os.path.isfile(record):#没有记录文件
        return '无记录'
    else:
        with open(record, 'r', encoding='utf-8') as f:
            try:
                temp = js.load(f)
            except:#有文件，但没记录
                temp = None
        if temp is None:
            return '无记录'
        else:
            return render_template("show_records.html", lst=temp[::-1][:50], condition=check_main())
#################################################
@app.route('/shot')
def remote_shot():
    shot()
    return redirect('/rmsrecords')

@app.route('/rmsrecords')
def show_rms_records():
    path = REMOTESHOT
    files = os.listdir(path)
    file_paths = list(map(lambda x:os.path.join(path,x),files))
    lst = list(map(lambda x:[x[0],x[1]], zip(files, file_paths)))
##    return str(lst)
    return render_template("show_retote_shot.html",pics=lst[::-1])

@app.route('/img')
def img():
    path = request.args.get('path')
    with open(path,'rb') as f:
        i = f.read()
    res = make_response(i)
    res.headers['Content-Type'] = 'image/png'
    return res
#################################################
@app.route("/tm",methods=['GET'])
def tmch():
    trd=str(request.args.get('t'))
    flag=checkt(trd)
    if flag:
        f=open(ACTIONTM,'w')
        f.write(trd)
        f.close()
        return '现在设定的动作时长为:&emsp;'+trd+'&emsp;s'
    else:
        return '输入时间数据不合规!!'
#################################################
@app.route('/start')
def start():
    try:
        os.startfile(MAIN)
        return '尝试启动完成'
    except Exception as err:
        return f'<p>启动失败:</p><p>Error:{err}</p>'
################################################################
if __name__ == '__main__':
    load()
    app.run(host='0.0.0.0',port=1919,debug=True)

