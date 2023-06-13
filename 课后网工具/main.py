###################################################
##############--Author:Octpus_tank--###############
##############--------v3.50--------################
###################################################
import cv2
import win32api ,win32con ,win32ui ,win32gui
import aircv as ac
from PIL import Image ,ImageGrab
import time as tm
import numpy as np
import pyautogui as pag
import platform as pl
import os
import json as js
###############################################
def load():#加载-主函数
    global button , RES_WIDTH , RES_HEIGHT ,RECORDSCST, RECORDTXT ,ACTIONTM ,OS ,RECORD
    OS = pl.release()##[
    PATH = os.getcwd()
    RES = os.path.join(PATH,'res')
    BUTTON = os.path.join(RES,'button.png')
    ACTIONTM =os.path.join(RES,'move_time.res')
    RECORD = os.path.join(PATH,'record')
    RECORDSCST = os.path.join(RECORD,'screenshot')
    RECORDTXT = os.path.join(RECORD,'record.json')##]
    img = Image.open(BUTTON)##[
    button = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)##]
    MointorDev = win32api.EnumDisplayMonitors(None,None)##[
    RES_WIDTH = MointorDev[0][2][2]
    RES_HEIGHT = MointorDev[0][2][3]##]

def icon(download_icon=True) :
    icons = ['-','\\','|','/']
    count = 0
    while 1:
        text = icons[count]
        count = (count+1)%len(icons)
        yield text
###############################################
def writein(data, operation=None):#写入日志
    tmnw = tm.strftime('%Y/%m/%d %H:%M:%S',tm.localtime())
    record = [tmnw, str(data), operation]
    if not os.path.isfile(RECORDTXT):#不存在文件,则创建
        with open(RECORDTXT, 'w', encoding='utf-8') as f:
            js.dump([record], f)
    else:#存在
        with open(RECORDTXT, 'r', encoding='utf-8') as f:
            temp = js.load(f)
        temp.append(record)
        with open(RECORDTXT, 'w', encoding='utf-8') as f:
            js.dump(temp, f)
def tempin(s):
    tmnw=tm.time()
    with open('temp.temp','w') as f:
        f.write(str(tmnw+s))
###############################################
def imgin(img):#保存图片
    tmnw=tm.strftime("%Y%m%d%H%M%S", tm.localtime())
    imgname=tmnw+'.jpg'
    img.save(os.path.join(RECORDSCST,imgname))
###############################################
def grab1a():#剪切板方式子函数
    win32api.keybd_event(0x91,0,0,0)
    win32api.keybd_event(0x2C,0,0,0)
    win32api.keybd_event(0x91,0,win32con.KEYEVENTF_KEYUP,0)
    win32api.keybd_event(0x2C,0,win32con.KEYEVENTF_KEYUP,0)
    try:
        img=ImageGrab.grabclipboard()
    except:
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
    SaveBitMap.CreateCompatibleBitmap(MDC,RES_WIDTH,RES_HEIGHT)  # 为bitmap开辟空间
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
##############################
def shot():#截屏主函数
    if OS in ['7','XP']:
        img=grab1()
    else:
        img=grab2()
    return img
###############################################
def match(img):#匹配
    screen=cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
    match_result=ac.find_template(screen,button,0.5)
    return match_result
def find(screen):#寻找主函数
    match_result=match(screen)
    if match_result is not None:
        confi=match_result['confidence']
        if confi>=0.85:
            writein(str(confi),'action')
            imgin(screen)
            return match_result['rectangle'][1]
        elif confi>=0.7:
            imgin(screen)
            writein(str(confi),'imgshot')
##        else:
##            writein(str(confi))
    return False
###############################################
def getactiontm():#滑动耗时设定值读取
    flag=True
    try:
        f=open(ACTIONTM,'r')
        trd=f.read()
        f.close()
        t=float(trd)
        if not 0<=t<20:
            flag=False
    except Exception as er:
        flag=False
    if flag:
        return t
    else:
        print('设定的时间数据有误!默认2s')
        return 2
def action(x,y):#执行动作
    t=getactiontm()
    try:
        pag.moveTo(x,y)
        tempin(t+1)
        pag.dragTo(x+335,y,t,button='left')
    except:
        pass
###############################################
if __name__ == '__main__':
    load()
    I = icon()
    flag=False
    print('开始检测签到:')
    while True:
        screen=shot()
        result=find(screen)
        if result:
            print('发现签到!开始动作...')
            x,y=result
            action(x,y)
            print('动作结束!')
            flag=True
            tempin(1)
            tm.sleep(0.5)
        else:
            print('\r'+next(I),end='')
            tempin(3)
            tm.sleep(2)
            if flag:
                print('完成签到,休眠2min...')
                writein(None, '完成签到,休眠2min')
                tempin(123)
                tm.sleep(120)
                flag=False
