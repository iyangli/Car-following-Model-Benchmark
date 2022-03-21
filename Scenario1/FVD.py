import pandas as pd
import math
from pandas import DataFrame as Df
from pandas import Series
import numpy as np
import random

# ————————————————场景一通用的参数值————————————————————#
# 前车的速度，加速度，绝对距离
forehead_spe = 0
forehead_dis = 10000
forehead_acc = 0

#场景一实时输出的值：速度，加速度，车头间距，行驶的距离
acceleration_list,speed_list,head_space_list,absolute_distance_list,time_list=[],[],[],[],[]

# ————————————————模型的缺省参数————————————————————#

#期望速度
# Desire_Spe=np.random.normal(30,2,1)[0]
Desire_Spe=120.2915/3.6

# 常敏感性系数
Constant_Sensitivity_Coe=0.0626

# 相对速度差敏感性系数
Rel_Spe_Sen_Coe=0.7018

# beta，b系数
Para_Beta,Para_b=1.0776,19.39

#自由流与跟驰策略的间距阈值
Max_Fol_Dis=46.9134

# 有效的车长
Eff_veh_len=5

cur_Rel_Spe_Sen_Coe=0

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

    if cur_head_space <= Max_Fol_Dis:
        cur_Rel_Spe_Sen_Coe = Rel_Spe_Sen_Coe
    else:
        cur_Rel_Spe_Sen_Coe = 0

    cur_bef_des_spe = (0.5 * Desire_Spe) * (
            math.tanh(((cur_head_space - Eff_veh_len) / Para_b- Para_Beta))
            - math.tanh(-Para_Beta))

    cur_acc = Constant_Sensitivity_Coe * (cur_bef_des_spe - cur_spe) + cur_Rel_Spe_Sen_Coe * (forehead_spe-cur_spe)

    cur_spe=cur_spe+cur_acc*0.1
    absolute_distance+=cur_spe*0.1
    cur_head_space=forehead_dis-absolute_distance
    simulation_time+=0.1
    last_absolute_distance=absolute_distance
    print("加速度"+str(round(cur_acc,6)))
    print("速度"+str(cur_spe))
    print("绝对距离"+str(absolute_distance))
    print("仿真时间"+str(simulation_time))
    # ————————————————判断数值计算是否结束————————————————————#
    #倘若后车的绝对距离大于前车的绝对距离，数值仿真结束
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

    if round(simulation_time,2)==5000.00:
        break

    # 放入每一次计算过程中的参数值
    acceleration_list.append(cur_acc)
    speed_list.append(cur_spe)
    head_space_list.append(cur_head_space)       #两车间的车头间距
    absolute_distance_list.append(absolute_distance)   #后车的绝对距离
    time_list.append(simulation_time)

# 输出最终的excel至文件夹中

data=pd.DataFrame({"仿真时间":time_list,"FVD加速度":acceleration_list,"FVD速度":speed_list,
                   "FVD车头间距":head_space_list,"FVD绝对距离":absolute_distance_list})

data.to_excel("C:\\Users\\cc_01\\Desktop\\基准分析\\数值仿真\\数值仿真\\场景1，启动，加速，自由流，停车\\输出文件\\10公里\\FVD.xlsx")



