import pandas as pd
import math
from pandas import DataFrame as Df
from pandas import Series
import numpy as np
import random

#——————————————————————————————————————————————模型自带参数，函数    ————————————————————————————————————————————-
#最大速度
Max_Spe=25.7

# 最大加速度
Max_Acc=1.37

# 最大减速度
Max_Dec=0.73

model_parameter=0.4

# 有效的车长
Eff_veh_len=4

# 反应时间
Reaction_Time=1

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

path="C:\\Users\\cc_01\\Desktop\\基准分析\\数值仿真\\数值仿真\\场景2，跟驰，被抢道，跟驰，两辆车\\输出文件\\统计分析,version-8\\S-K-cut_in=10.xlsx"

# 计算实时的速度以及加速度
def get_forehead_spe_acc(time,ini_first_time,ini_second_time,acc_increase,
                     fir_car_speed,sec_car_speed,sec_car_de_speed):
    if time>=0 and time<ini_first_time:
        return fir_car_speed

    if time >=ini_first_time and time <ini_second_time:
        return sec_car_speed

    if time >=ini_second_time and \
            time <=(ini_second_time+(sec_car_de_speed-sec_car_speed)/acc_increase):
        return sec_car_speed+acc_increase*(time-ini_second_time)

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
    forehead_spe = get_forehead_spe_acc(round(time, 2), ini_first_time, ini_second_time,
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
    V_safe = forehead_spe + (cur_head_space - Eff_veh_len - cur_spe * Reaction_Time) / \
             ((forehead_spe + cur_spe) / (2 * Max_Dec) + Reaction_Time)
    V_desire = min(Max_Spe, cur_spe + Max_Acc, V_safe)
    V_zero = V_desire - 0.4 * (V_desire - (cur_spe - Max_Dec))

    cur_spe = random.uniform(V_zero, V_desire)

    cur_acc = (cur_spe - last_spe) / 0.01
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

data=pd.DataFrame({"仿真时间":time_list,"S-K加速度":acceleration_list,"S-K速度":speed_list,
                   "S-K车头间距":head_space_list,"S-K绝对距离":absolute_distance_list})

data.to_excel(path)


























