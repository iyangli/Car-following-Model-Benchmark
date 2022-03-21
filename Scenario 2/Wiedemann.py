import pandas as pd
import math
from pandas import DataFrame as Df
from pandas import Series
import numpy as np
import random
#——————————————————————————————————————————————模型自带参数，函数    ————————————————————————————————————————————-
# 模型默认的参数值

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



#——————————————————————————————————————————————模型自带参数，函数    ————————————————————————————————————————————-



#——————————————————————————————————————————————中间变量，函数（通用） ————————————————————————————————————————————-

#场景二实时输出的值：速度，加速度，车头间距，行驶的距离
acceleration_list,speed_list,head_space_list,absolute_distance_list,time_list=[],[],[],[],[]

time=0.0
time_interval=0.01

# 场景启动时间
ini_first_time=100
ini_second_time=150

#第一辆车参数的设置
forehead_acc_increase=1
forehead_fir_car_speed=15
forehead_sec_car_speed=5
forehead_sec_car_de_speed=25
forehead_total_time=ini_second_time+(forehead_sec_car_de_speed-forehead_sec_car_speed)/forehead_acc_increase

# 前车插入的间距
forehead_cut_in=20

# 刚开始两车的间距
ori_head_space=100

# 刚开始后车的速度
ori_spe=10

path="C:\\Users\\cc_01\\Desktop\\基准分析\\数值仿真\\数值仿真\\场景2，跟驰，被抢道，跟驰，两辆车\\输出文件\\统计分析,version-8\\Wiedemann-cut_in=10.xlsx"

# 计算实时的速度以及加速度
def get_forehead_spe_acc(time,ini_first_time,ini_second_time,acc_increase,
                     fir_car_speed,sec_car_speed,sec_car_de_speed):
    if time>=0 and time<ini_first_time:
        return fir_car_speed,0

    if time >=ini_first_time and time <ini_second_time:
        return sec_car_speed,0

    if time >=ini_second_time and \
            time <=(ini_second_time+(sec_car_de_speed-sec_car_speed)/acc_increase):
        return sec_car_speed+acc_increase*(time-ini_second_time),acc_increase

#——————————————————————————————————————————————中间变量，函数（通用） ————————————————————————————————————————————-



# ————————————————临时参数值————————————————————#

# 后车这一时刻以及上一时刻的加速度，速度，车头间距，行驶的距离
cur_acc,cur_spe,cur_head_space,absolute_distance=0,ori_spe,ori_head_space,0

# 前车行驶的路程
forehead_dis=0
forehead_dis_stage1=ori_head_space
forehead_dis_stage2=0

#模型自带参数
cur_des_spa=0
last_spe=cur_spe

# 加入初始时刻的参数值
acceleration_list.append(cur_acc)
speed_list.append(cur_spe)
head_space_list.append(cur_head_space)
absolute_distance_list.append(absolute_distance)
time_list.append(time)

# ————————————————临时的参数值————————————————————#

while time <=forehead_total_time:

    # 前车的加速度，速度
    forehead_spe,forehead_acc = get_forehead_spe_acc(round(time, 2), ini_first_time, ini_second_time,
                                                      forehead_acc_increase,
                                                      forehead_fir_car_speed, forehead_sec_car_speed,
                                                      forehead_sec_car_de_speed)
    time+=0.01

    print(forehead_spe)
    # 前车的绝对距离
    if round(time, 2) <ini_first_time :
        forehead_dis_stage1+=forehead_spe*time_interval
        forehead_dis=forehead_dis_stage1

    if round(time, 2)==ini_first_time :
        forehead_dis_stage2=absolute_distance+forehead_cut_in
        forehead_dis=forehead_dis_stage2

    if round(time, 2) > ini_first_time:
        forehead_dis_stage2+=forehead_spe*time_interval
        forehead_dis=forehead_dis_stage2

    if round(time, 2)> forehead_total_time:
        break


    # 后车参数的更新
    d_x, d_v, RND, slower, SDXc, SDV, SDXo, SDXv, CLDV, OPDV = \
        get_Wiedemann99_Threhold(forehead_dis, forehead_acc, forehead_spe, absolute_distance, cur_spe,
                                 CC0, CC1, CC2, CC3, CC4, CC5, CC6, CC7, CC8, CC9)
    # 获取实时的加速度
    cur_acc = get_Wiedemann99_acc(last_acc, forehead_acc, forehead_spe,
                                  CC0, CC1, CC2, CC3, CC4, CC5, CC6, CC7, CC8, CC9, VDES, Len_Of_Car,
                                  d_x, d_v, RND, slower, SDXc, SDV, SDXo, SDXv, CLDV, OPDV)

    cur_spe = cur_spe + cur_acc * time_interval
    absolute_distance += cur_spe * time_interval
    last_spe = cur_spe
    # 车头间距的更新
    cur_head_space=forehead_dis-absolute_distance
    acceleration_list.append(cur_acc)
    speed_list.append(cur_spe)
    head_space_list.append(cur_head_space)  # 两车间的车头间距
    absolute_distance_list.append(absolute_distance)  # 后车的绝对距离
    time_list.append(time)
    print("----------------------------------------------------")
    print("加速度" + str(cur_acc))
    print("速度" + str(cur_spe))
    print("相对距离" + str(cur_head_space))
    print("仿真时间" + str(round(time,2)))

data=pd.DataFrame({"仿真时间":time_list,"Wiedemann加速度":acceleration_list,"Wiedemann速度":speed_list,
                   "Wiedemann车头间距":head_space_list,"Wiedemann绝对距离":absolute_distance_list})

data.to_excel(path)


























