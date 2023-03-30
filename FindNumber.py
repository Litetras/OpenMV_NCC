'''视频教程https://www.bilibili.com/video/BV1UL411V7XK?p=2&share_source=copy_web'''

import time, image,sensor,math,pyb,ustruct
from image import SEARCH_EX, SEARCH_DS

from pyb import Pin, Timer,LED
#从imgae模块引入SEARCH_EX和SEARCH_DS。使用from import仅仅引入SEARCH_EX,
#SEARCH_DS两个需要的部分，而不把image模块全部引入。


sensor.reset()

# Set sensor settings
sensor.set_contrast(1)
sensor.set_gainceiling(16)
# Max resolution for template matching with SEARCH_EX is QQVGA
sensor.set_framesize(sensor.QQVGA)
# You can set windowing to reduce the search image.

sensor.set_pixformat(sensor.GRAYSCALE)

sensor.set_windowing(0, 40, 160, 40)  #这个是观察窗口  后面ROI设置也会以这个为新的基准


# Load template.
# Template should be a small (eg. 32x32 pixels) grayscale image.
#加载模板图片（需要自己重新截图并放入openmv的u盘中）
template01 = image.Image("/1.pgm")
'''template02 = image.Image("/2.pgm")
template03 = image.Image("/3.pgm")
template04 = image.Image("/4.pgm")
template05 = image.Image("/5.pgm")
template06 = image.Image("/6.pgm")
template07 = image.Image("/7.pgm")
template08 = image.Image("/8.pgm")


template3L = image.Image("/3L.pgm")
template3LL = image.Image("/3LL.pgm")
template3R = image.Image("/3R.pgm")
template3RR = image.Image("/3RR.pgm")

template4L = image.Image("/4L.pgm")
template4LL = image.Image("/4LL.pgm")
template4R = image.Image("/4R.pgm")
template4RR = image.Image("/4RR.pgm")

template5L = image.Image("/5L.pgm")
template5LL = image.Image("/5LL.pgm")
template5R = image.Image("/5R.pgm")
template5RR = image.Image("/5RR.pgm")

template6L = image.Image("/6L.pgm")
template6LL = image.Image("/6LL.pgm")
template6R = image.Image("/6R.pgm")
template6RR = image.Image("/6RR.pgm")

template7L = image.Image("/7L.pgm")
template7LL = image.Image("/7LL.pgm")
template7R = image.Image("/7R.pgm")
template7RR = image.Image("/7RR.pgm")

template8L = image.Image("/8L.pgm")
template8LL = image.Image("/8LL.pgm")
template8R = image.Image("/8R.pgm")
template8RR = image.Image("/8RR.pgm")'''



uart = pyb.UART(3, 115200, timeout_char = 1000)     
#串口通信波特率115200
#定义串口3变量
blue_led = LED(3)


#通过接收stm32F103传过来数据，来决定使用以下哪种模式
# FindTask：    1.轮询1~8，直至识别到。  2.根据f103给的值，单纯识别那个数
Find_Task = 1
Target_Num = 0

find_flag = 0
x = 0
blue_led  = LED(3)
data = [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]




########串口接收数据函数处理##############


def UartReceiveDate():  #这个函数不能运行太快，否则会导致串口读取太快导致出错
    global Find_Task
    global Target_Num
    global x
    global data
    data[0] = uart.readchar()
    data[1] = uart.readchar()
    data[2] = uart.readchar()
    data[3] = uart.readchar()
    data[4] = uart.readchar()
    data[5] = uart.readchar()
    data[6] = uart.readchar()
    data[7] = uart.readchar()


    if data[x] == 42 and data[x+3] == 38 and x < 5:
        Find_Task =  data[x+1]
        Target_Num = data[x+2]
        Find_Task =  Find_Task - 48
        Target_Num = Target_Num - 48
        print(Find_Task, Target_Num)
        x = 0
    elif x >= 5: x = 0
    x+=1
    #blue_led.toggle



########串口接收数据函数处理完毕#############


# 当被调用时，我们将返回timer对象
# 注意:在回调中不允许分配内存的函数  #openmv会自动把接收到的数据放在缓冲区里
'''def tick(timer):
    blue_led.toggle()


tim = Timer(2, freq=5)      # 使用定时器2创建定时器对象-以1Hz触发
tim.callback(tick) '''         # 将回调设置为tick函数


#####  FindTask == 0 时使用
#最初加载匹配
def FirstFindTemplate(template):
    R = img.find_template(template, 0.8, step=1, roi=(55, 0, 50, 40), search=SEARCH_EX)   #只检测中间的
    return R

def FirstFindedNum(R, Finded_Num):     #第一个参数是模板匹配的对象，第二个是它所代表的数字
   global Find_Task
   global find_flag
   img.draw_rectangle(R, color=(225, 0, 0))

   #本来中值是80的，但返回值是框边缘，所以减去15就好  小于65是在左边，大于65是在右边
   LoR = 0
   find_flag = 1
   Num = Finded_Num
   FH = bytearray([0x2C,0x12,Num, LoR, find_flag, Find_Task,0x5B])
   uart.write(FH)
   print("目标病房号：", Num)


######  FindTask == 1 时使用
#模板匹配
def FindTemplate(template):
    R = img.find_template(template, 0.8, step=1, roi=(0, 0, 160, 40), search=SEARCH_EX)
    return R

def FindedNum(R, Finded_Num):     #第一个参数是模板匹配的对象，第二个是它所代表的数字
   global Find_Task
   global find_flag
   img.draw_rectangle(R, color=(225, 0, 0))

   #本来中值是80的，但返回值是框边缘，所以减去15就好  小于65是在左边，大于65是在右边
   if R[0] >= 65:
       LoR = 2    #2是右
   elif 0< R[0] <65:
       LoR = 1     #1是左
   find_flag = 1
   Num = Finded_Num
   FH = bytearray([0x2C,0x12,Num, LoR, find_flag, Find_Task,0x5B])
   uart.write(FH)
   print("识别到的数字是：", Num, "此数字所在方位：", LoR) #打印模板名字


clock = time.clock()
# Run template matching
while (True):
    clock.tick()
    img = sensor.snapshot()

    UartReceiveDate()


    # find_template(template, threshold, [roi, step, search])
    # ROI: The region of interest tuple (x, y, w, h).
    # Step: The loop step used (y+=step, x+=step) use a bigger step to make it faster.
    # Search is either image.SEARCH_EX for exhaustive search or image.SEARCH_DS for diamond search
    #
    # Note1: ROI has to be smaller than the image and bigger than the template.
    # Note2: In diamond search, step and ROI are both ignored.

    if Find_Task == 1:

       #进行模板匹配
        r01 = FirstFindTemplate(template01)
        '''r02 = FirstFindTemplate(template02)
        r03 = FirstFindTemplate(template03)
        r04 = FirstFindTemplate(template04)
        r05 = FirstFindTemplate(template05)
        r06 = FirstFindTemplate(template06)
        r07 = FirstFindTemplate(template07)
        r08 = FirstFindTemplate(template08)'''


        #判断哪个模板匹配成功，并将成功匹配的相应数据发送给主控
        if r01:
             FirstFindedNum(r01, 1)
        '''elif r02:
             FirstFindedNum(r02,2)
        elif r03:
             FirstFindedNum(r03,3)
        elif r04:
             FirstFindedNum(r04,4)
        elif r05:
             FirstFindedNum(r05,5)
        elif r06:
             FirstFindedNum(r06,6)
        elif r07:
             FirstFindedNum(r07,7)
        elif r08:
             FirstFindedNum(r08,8)
        else:
             FH = bytearray([0x2C,0x12,0x00, 0x00, 0x00, 0x00,0x5B])
             uart.write(FH)'''


    '''
    elif Find_Task == 2:

        #判断需要数字3~8中断哪一个

        if Target_Num == 3:
            #进行模板匹配  //这里每个数字至少给3个模板， 但给五六个其实也行
            r3L = FindTemplate(template3L)
            r3LL = FindTemplate(template3LL)
            r3R = FindTemplate(template3R)
            r3RR = FindTemplate(template3RR)

            #判断哪个模板匹配成功，并将成功匹配的相应数据发送给主控

            if r3L:
                FindedNum(r3L, 3)
            elif r3LL:
                FindedNum(r3LL, 3)
            elif r3R:
                FindedNum(r3R, 3)
            elif r3RR:
                FindedNum(r3RR, 3)
            else:
                FH = bytearray([0x2C,0x12, 0x00, 0x00, find_flag, Find_Task,0x5B])
                uart.write(FH)

        elif Target_Num == 4:
            #进行模板匹配  //这里每个数字至少给3个模板， 但给五六个其实也行
            r4L = FindTemplate(template4L)
            r4LL = FindTemplate(template4LL)
            r4R = FindTemplate(template4R)
            r4RR = FindTemplate(template4RR)

            #判断哪个模板匹配成功，并将成功匹配的相应数据发送给主控

            if r4L:
                FindedNum(r4L, 4)
            elif r4LL:
                FindedNum(r4LL, 4)
            elif r4R:
                FindedNum(r4R, 4)
            elif r4RR:
                FindedNum(r4RR, 4)
            else:
                FH = bytearray([0x2C,0x12, 0x00, 0x00, find_flag, Find_Task,0x5B])
                uart.write(FH)

        elif Target_Num == 5:
            #进行模板匹配  //这里每个数字至少给3个模板， 但给五六个其实也行

            r5L = FindTemplate(template5L)
            r5LL = FindTemplate(template5LL)
            r5R = FindTemplate(template5R)
            r5RR = FindTemplate(template5RR)

            #判断哪个模板匹配成功，并将成功匹配的相应数据发送给主控

            if r5L:
                FindedNum(r5L, 5)
            elif r5LL:
                FindedNum(r5LL, 5)
            elif r5R:
                FindedNum(r5R, 5)
            elif r5RR:
                FindedNum(r5RR, 5)
            else:
                FH = bytearray([0x2C,0x12, 0x00, 0x00, find_flag, Find_Task,0x5B])
                uart.write(FH)

        elif Target_Num == 6:
            #进行模板匹配  //这里每个数字至少给3个模板， 但给五六个其实也行

            r6L = FindTemplate(template6L)
            r6LL = FindTemplate(template6LL)
            r6R = FindTemplate(template6R)
            r6RR = FindTemplate(template6RR)

            #判断哪个模板匹配成功，并将成功匹配的相应数据发送给主控

            if r6L:
                FindedNum(r6L, 6)
            elif r6LL:
                FindedNum(r6LL, 6)
            elif r6R:
                FindedNum(r6R, 6)
            elif r6RR:
                FindedNum(r6RR, 6)
            else:
                FH = bytearray([0x2C,0x12, 0x00, 0x00, find_flag, Find_Task,0x5B])
                uart.write(FH)


        elif Target_Num == 7:
            #进行模板匹配  //这里每个数字至少给3个模板， 但给五六个其实也行

            r7L = FindTemplate(template7L)
            r7LL = FindTemplate(template7LL)
            r7R = FindTemplate(template7R)
            r7RR = FindTemplate(template7RR)

            #判断哪个模板匹配成功，并将成功匹配的相应数据发送给主控
            if r7L:
                FindedNum(r7L, 7)
            elif r7LL:
                FindedNum(r7LL, 7)
            elif r7R:
                FindedNum(r7R, 7)
            elif r7RR:
                FindedNum(r7RR, 7)
            else:
                FH = bytearray([0x2C,0x12, 0x00, 0x00, find_flag, Find_Task,0x5B])
                uart.write(FH)

        elif Target_Num == 8:
            #进行模板匹配  //这里每个数字至少给3个模板， 但给五六个其实也行

            r8L = FindTemplate(template8L)
            r8LL = FindTemplate(template8LL)
            r8R = FindTemplate(template8R)
            r8RR = FindTemplate(template8RR)

            #判断哪个模板匹配成功，并将成功匹配的相应数据发送给主控

            if r8L:
                FindedNum(r8L, 8)
            elif r8LL:
                FindedNum(r8LL, 8)
            elif r8R:
                FindedNum(r8R, 8)
            elif r8RR:
                FindedNum(r8RR, 8)
            else:
                FH = bytearray([0x2C,0x12, 0x00, 0x00, find_flag, Find_Task,0x5B])
                uart.write(FH)

        #else: time.sleep_ms(100)
    else: time.sleep_ms(100)'''

    print(clock.fps(),Find_Task, Target_Num)
