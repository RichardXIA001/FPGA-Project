# SoundLocation - By: 16011 - 周日 7月 3 2022

from Maix import MIC_ARRAY as mic
import lcd,time
import math
#import utime
from board import board_info
from Maix import GPIO
from fpioa_manager import fm


mic.init(i2s_d0=12, i2s_d1=board_info.PIN5,\
i2s_d2=13, i2s_d3=board_info.PIN6,\
i2s_ws=14,i2s_sclk=board_info.PIN7,\
sk9822_dat=board_info.PIN4, sk9822_clk=board_info.PIN11)#可自定义配置 IO

# 留出PIN2和PIN输出控制信号
fm.register(board_info.PIN2,fm.fpioa.GPIO0,force=True)
fm.register(board_info.PIN3,fm.fpioa.GPIO1,force=True)

# 构建控制信号对象
c_out1 = GPIO(GPIO.GPIO0,GPIO.OUT)
c_out2 = GPIO(GPIO.GPIO1,GPIO.OUT)

'''
state表示控制状态
0是停下(00)
1是直行(01)
2是左转(10)
3是右转(11)
'''
# 当前状态
state = 0
# 真实准备输出的状态
real_state = 0
# 控制防抖
s_times = 0

def get_mic_dir():
    AngleX=0
    AngleY=0
    AngleR=0
    Angle=0
    AngleAddPi=0
    mic_list=[]
    imga = mic.get_map()    # 获取声音源分布图像
    b = mic.get_dir(imga)   # 计算、获取声源方向
    for i in range(len(b)):
        if b[i]>=2:
            AngleX+= b[i] * math.sin(i * math.pi/6)
            AngleY+= b[i] * math.cos(i * math.pi/6)
    AngleX=round(AngleX,6) #计算坐标转换值
    AngleY=round(AngleY,6)
    if AngleY<0:AngleAddPi=180
    if AngleX<0 and AngleY > 0:AngleAddPi=360
    if AngleX!=0 or AngleY!=0: #参数修正
        if AngleY==0:
            Angle=90 if AngleX>0 else 270 #填补X轴角度
        else:
            Angle=AngleAddPi+round(math.degrees(math.atan(AngleX/AngleY)),4) #计算角度
        AngleR=round(math.sqrt(AngleY*AngleY+AngleX*AngleX),4) #计算强度
        mic_list.append(AngleX)
        mic_list.append(AngleY)
        mic_list.append(AngleR)
        mic_list.append(Angle)
    a = mic.set_led(b,(0,0,255))# 配置 RGB LED 颜色值
    return mic_list #返回列表，X坐标，Y坐标，强度，角度

# 将state转换成对应的控制信号输出
def controller_output():
    global real_state
    out1 = real_state % 2
    out2 = 1 if real_state > 1 else 0
    c_out1.value(out1)
    c_out2.value(out2)

def change_state(angle):
    global state
    global s_times
    global real_state
    former_state = state

    theta1 = 20     # 直行的范围
    theta2 = 10     # 倒车的范围（默认右转倒车）
    if angle > theta1 and angle <= 180-theta2:  # 右转
        state = 3
    elif angle > 180+theta2 and angle <= 360-theta1:
        state = 2   #左转
    elif angle > 180-theta2 and angle <= 180+theta2:
        # 倒车统一用右转实现，不过如果之前已经在左转就继续左转
        if state < 2: state = 3
    # [-theta1, theta1的范围里，则直行]
    else: state = 1

    # 声源定位控制的防抖
    bar = 3
    if former_state == state:
        s_times = (s_times + 1) if s_times < bar else bar
        if s_times == bar: real_state = state
    else : s_times = 0

while True:
    mic_list = get_mic_dir()
    # 根据输入的角度
    #print(mic_list)
    if mic_list:
        change_state(mic_list[-1])
    print("state now:")
    print(state)
    print("s_times:")
    print(s_times)
    print("real state:")
    print(real_state)
    controller_output()

    time.sleep_ms(100)
#lcd.init()
#while True:
    #imga = mic.get_map()
    #b = mic.get_dir(imga)
    #print(b)
    #a = mic.set_led(b,(0,0,255))

    #imgb = imga.resize(160,160)
    #imgc = imgb.to_rainbow(1)
    #lcd.display(imgc)
    ##time.sleep_ms(100)

#mic.deinit()
