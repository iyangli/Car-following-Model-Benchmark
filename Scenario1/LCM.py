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

#期望速度
# Desire_Spe=np.random.normal(30,2,1)[0]
Desire_Spe=30

# 最大加速度
# Max_Acc=random.triangular(3,5,4)
Max_Acc=5

# 驾驶员i对于驾驶员j在紧急情况下，刹车时减速度的估计值
# Eme_Dec_Bi=random.triangular(5,7,6)
Eme_Dec_Bi=4

#驾驶员i在紧急情况下，自信能够采取的最大减速度。
# Dec_bi=random.triangular(8,10,9)
Dec_bi=4

# 有效的车长
Eff_veh_len=5

# 反应时间
Reaction_Time=1

# ————————————————临时的参数值————————————————————#

# 后车这一时刻以及上一时刻的加速度，速度，车头间距，行驶的距离
cur_acc,cur_spe,cur_head_space,absolute_distance=0,0,forehead_dis,0

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
    cur_des_spa = (cur_spe**2) / (Dec_bi * 2) - (forehead_spe**2) / (
                Eme_Dec_Bi * 2) + cur_spe * Reaction_Time + Eff_veh_len
    cur_des_spa=round(cur_des_spa,2)
    cur_acc = Max_Acc * (1 - cur_spe / Desire_Spe - np.e**(1 - (cur_head_space/ cur_des_spa)))
    cur_acc=round(cur_acc,2)
    cur_spe=cur_spe+cur_acc*1
    absolute_distance+=cur_spe*1
    absolute_distance=round(absolute_distance,2)
    cur_head_space=forehead_dis-absolute_distance
    simulation_time+=1


    last_absolute_distance=absolute_distance

    # ————————————————判断数值计算是否结束————————————————————#
    # 倘若后车的绝对距离大于前车的绝对距离，数值仿真结束
    if  absolute_distance >=forehead_dis-Eff_veh_len:
        print("发生碰撞")
        print("后车在前车" + str(round(cur_head_space - Eff_veh_len,4)) + "m处停止，" + "数值仿真结束，共用时长为" + str(simulation_time))
        break

    # 两次绝对距离差小于0.5，同时两车不发生碰撞
    if ((absolute_distance - last_absolute_distance) <= 0.5) and absolute_distance> 95000:
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

data=pd.DataFrame({"仿真时间":time_list,"LCM加速度":acceleration_list,"LCM速度":speed_list,
                   "LCM车头间距":head_space_list,"LCM绝对距离":absolute_distance_list})

data.to_excel("C:\\Users\\cc_01\\Desktop\\基准分析\\场景1，启动，加速，自由流，停车\\输出文件\\LCM.xlsx")



