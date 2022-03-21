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
Desire_Spe=90.6106/3.6

# 后车最大加速度
Max_Acc=3.31

# 后车最大减速度
Max_dec=3.801

# 前车最大减速度
Max_Bi=4.783

# 有效的车长
Eff_veh_len=5

# 反应时间
Reaction_Time=0.567

# ————————————————临时的参数值————————————————————#

# 后车这一时刻以及上一时刻的加速度，速度，车头间距，行驶的距离
cur_acc,cur_spe,cur_head_space,absolute_distance=0,0,forehead_dis,0
last_spe=0


# 仿真时长设置为一秒
simulation_time=0
last_absolute_distance=0

# ————————————————开始数值计算————————————————————#
'''
以下两种情形，模型停止自动计算：
（1）模型在逐渐接近前车时（未超越前车），两次计算中的绝对距离差小于 0.5m
（2）后车的绝对距离大于前车的绝对距离
'''
pre_spe_list=[cur_spe]*57
pre_rel_dis=[cur_head_space-Eff_veh_len]*57

while True:
    # 更新每一次的速度，加速度，车头间距，行驶距离

    cur_spe_1 = math.sqrt(math.pow(Max_dec, 2) * math.pow(Reaction_Time, 2)
                          + Max_dec * (2 * (pre_rel_dis[0] - Eff_veh_len) -pre_spe_list[0] * Reaction_Time + (
                math.pow(forehead_spe, 2) / Max_Bi))) - Max_dec * Reaction_Time

    cur_spe_2=pre_spe_list[0]+2.5*Max_Acc*Reaction_Time*(1-pre_spe_list[0]/Desire_Spe)*math.sqrt(0.025+pre_spe_list[0]/Desire_Spe)

    if cur_spe_1>=0 and cur_spe_2>=0:


        cur_spe=min(cur_spe_1,cur_spe_2)
    else:
        cur_spe=0

    print(cur_spe)

    cur_acc=(cur_spe-last_spe)/0.01
    absolute_distance+=cur_spe*0.01
    cur_head_space=forehead_dis-absolute_distance
    simulation_time+=0.01
    if simulation_time>500:
        break
    last_absolute_distance=absolute_distance

    last_spe=cur_spe
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

    pre_spe_list.append(cur_spe)
    pre_spe_list.remove(pre_spe_list[0])
    pre_rel_dis.append(cur_head_space - Eff_veh_len)
    pre_rel_dis.remove(pre_rel_dis[0])


# 输出最终的excel至文件夹中

data=pd.DataFrame({"仿真时间":time_list,"GIPPS加速度":acceleration_list,"GIPPS速度":speed_list,
                   "GIPPS车头间距":head_space_list,"GIPPS绝对距离":absolute_distance_list})

data.to_excel("C:\\Users\\cc_01\\Desktop\\基准分析\\场景1，启动，加速，自由流，停车\\输出文件\\Gipps.xlsx")



