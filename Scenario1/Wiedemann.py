import pandas as pd
import math
from pandas import DataFrame as Df
from pandas import Series
import numpy as np
import random

# ————————————————场景一通用的参数值————————————————————#
# 前车的速度，加速度，绝对距离
forehead_spe = 0
forehead_dis = 5000
forehead_acc = 0

#场景一实时输出的值：速度，加速度，车头间距，行驶的距离
acceleration_list,speed_list,head_space_list,absolute_distance_list,time_list=[],[],[],[],[]

# ————————————————模型的缺省参数————————————————————#

CC0=1.0192
CC1=1.4242
CC2=5.8715
CC3=-17.1579
CC4=-0.2312
CC5=1.7946
CC6=3.5519
CC7=0.5350
CC8=4.0101
CC9=2.6549
VDES=86.0492/3.6
Len_Of_Car=5
Eff_veh_len=5

# 实时阈值的定义
cur_d_x=0
cur_d_v=0
cur_SDXc=0  # 最短的跟驰距离
cur_slower=0
cur_RND=0
cur_SDV=0   # 速度差的感知阈值
cur_SDXo=0  #最大跟驰距离
cur_SDXv=0
cur_CLDV=0
cur_OPDV=0
last_acc=0


# 计算实时的阈值
def get_Wiedemann99_Threhold(forehead_dis,forehead_acc,forehead_spe,cur_dis,cur_spe,
                             CC0,CC1,CC2,CC3,CC4,CC5,CC6,CC7,CC8,CC9):

    # 当此时刻阈值的定义
    d_x = forehead_dis - cur_dis - Len_Of_Car
    d_v = forehead_spe - cur_spe
    RND=np.random.uniform(-0.5,0.5,1)[0]
    if d_x>0 or forehead_acc<-1:
        slower=cur_spe
    else:
        slower=forehead_spe-d_v*RND
    SDXc = CC0 + CC1 * slower
    SDV=CC6*math.pow(d_x-Len_Of_Car,2)
    SDXo=SDXc+CC2
    SDXv=SDXo+CC3*(d_v-CC4)
    if forehead_spe>0:
        CLDV=-SDV+CC4
    else:
        CLDV=0
    if cur_spe> CC5:
        OPDV=SDV+CC5
    else:
        OPDV=SDV

    return d_x,d_v,RND,slower,SDXc,SDV,SDXo,SDXv,CLDV,OPDV

# Wiedemann计算实时的加速度
def get_Wiedemann99_acc(last_acc,forehead_acc,forehead_cur_spe,
                          CC0,CC1,CC2,CC3,CC4,CC5,CC6,CC7,CC8,CC9,VDES,Len_Of_Car,
                          d_x,d_v,RND,slower,SDXc,SDV,SDXo,SDXv,CLDV,OPDV):
    acc = 0
    if d_v < OPDV and d_x <= SDXc:
        # 紧急刹车
        if cur_spe > 0 and d_v < 0:
            if d_x > CC0:
                acc = min(forehead_acc + math.pow(d_v, 2) / (CC0 - d_x), last_acc)
            else:
                acc = min(forehead_acc + 0.5 * (d_v - OPDV), last_acc)
                if acc > -CC7:
                    acc = -CC7
                else:
                    acc = max(acc, -10 + 0.5 * math.sqrt(cur_spe))
    else:
        # 逐渐接近的过程
        if d_v < CLDV and d_x <= SDXv:
            acc = max(math.pow(d_v, 2) / (2 * (SDXc - d_x - 0.1)), -10)
        else:
            if d_v < OPDV and d_x <= SDXo:
                # 跟驰的过程
                if last_acc <= 0:
                    acc = min(last_acc, -CC7)
                else:
                    acc = max(last_acc, CC7)
                    acc = min(acc, VDES - cur_spe)
            else:
                #         自由流的过程
                if d_x > SDXc:
                    if cur_spe > VDES:
                        acc = CC7
                    else:
                        amax = CC8 + 0.1 * CC9 * min(cur_spe, 22.2) + random.uniform(0, 1)
                        if d_x < SDXo:
                            acc = min(math.pow(d_v, 2) / (SDXo - d_x), amax)
                        else:
                            acc = amax
                    acc = min(acc, VDES - cur_spe)

    return acc


# ————————————————临时的参数值————————————————————#

# 后车这一时刻以及上一时刻的加速度，速度，车头间距，行驶的距离
cur_acc,cur_spe,cur_head_space,absolute_distance=0,0,forehead_dis,0
last_acc=0

# 加入初始时刻的参数值
acceleration_list.append(cur_acc)
speed_list.append(cur_spe)
head_space_list.append(cur_head_space)
absolute_distance_list.append(absolute_distance)
time_list.append(0)

# 仿真时长设置为一秒
simulation_time=0
last_absolute_distance=0

# ————————————————开始数值计算————————————————————#
'''
以下两种情形，模型停止自动计算：
（1）模型在逐渐接近前车时（未超越前车），两次计算中的绝对距离差小于 0.5m
（2）后车的绝对距离大于前车的绝对距离
'''

while True:
    # 更新每一次的速度，加速度，车头间距，行驶距离

    d_x, d_v, RND, slower, SDXc, SDV, SDXo, SDXv, CLDV, OPDV = \
        get_Wiedemann99_Threhold(forehead_dis, forehead_acc, forehead_spe, absolute_distance, cur_spe,
                                 CC0, CC1, CC2, CC3, CC4, CC5, CC6, CC7, CC8, CC9)
    # 获取实时的加速度
    cur_acc = get_Wiedemann99_acc(last_acc, forehead_acc, forehead_spe,
                                  CC0, CC1, CC2, CC3, CC4, CC5, CC6, CC7, CC8, CC9, VDES, Len_Of_Car,
                                  d_x, d_v, RND, slower, SDXc, SDV, SDXo, SDXv, CLDV, OPDV)

    cur_spe=cur_spe+cur_acc*1
    absolute_distance+=cur_spe*1
    if cur_spe <0:
        break

    cur_head_space=forehead_dis-absolute_distance
    simulation_time+=1
    last_absolute_distance=absolute_distance
    last_acc=cur_acc


    # ————————————————判断数值计算是否结束————————————————————#
    #倘若后车的绝对距离大于前车的绝对距离，数值仿真结束
    if  absolute_distance >=forehead_dis-Eff_veh_len:
        print("发生碰撞")
        print("后车在前车" + str(round(cur_head_space - Eff_veh_len,4)) + "m处停止，" + "数值仿真结束，共用时长为" + str(simulation_time))
        break

    # 两次绝对距离差小于0.5，同时两车不发生碰撞
    if ((absolute_distance - last_absolute_distance) <= 0.0005) and absolute_distance> 9993.9:
        print("后车停车")
        print("后车在前车+" + str(round(cur_head_space - Eff_veh_len,4)) + "m处停止，" + "数值仿真结束，共用时长为" + str(simulation_time))
        break
    # ————————————————判断数值计算是否结束————————————————————#

    # 放入每一次计算过程中的参数值
    acceleration_list.append(cur_acc)
    speed_list.append(cur_spe)
    head_space_list.append(cur_head_space)       #两车间的车头间距
    absolute_distance_list.append(absolute_distance)   #后车的绝对距离
    time_list.append(simulation_time)
    print("加速度"+str(round(cur_acc,6)))
    print("速度"+str(cur_spe))
    print("绝对距离"+str(absolute_distance))
    print("仿真时间"+str(simulation_time))
# 输出最终的excel至文件夹中

data=pd.DataFrame({"仿真时间":time_list,"Wiedemann加速度":acceleration_list,"Wiedemann速度":speed_list,
                   "Wiedemann车头间距":head_space_list,"Wiedemann绝对距离":absolute_distance_list})

data.to_excel("C:\\Users\\cc_01\\Desktop\\基准分析\\场景1，启动，加速，自由流，停车\\输出文件\\Wiedemann.xlsx")



