﻿# CarChargeStationSystem


BUPT 软件工程课设

课题基本要求：
   作为新型交通工具，电动汽车是未来汽车行业的发展趋势。在环境保护日益受到重视的今天，电动汽车越来越多，充电需求日益增大。充电桩作为重要基础设施，其运营管理水平直接影响着波普特大学电动汽车拥有者的使用体验以及车辆停放的管理，为此学校需要在校区设计一套智能充电桩调度计费系统，以便使得电动车完成充电服务的时间（充电时间+排队时间）达到最短的效果。
   
充电站分为“等候区”和“充电区”两个部分。
假定车辆到达充电站后首先进入等候区，此时可以通过客户端软件发起充电请求（暂时不考虑等候区外的请求），等候区的容量待定（暂时考虑能容纳任意数量车辆）。用户在等候区发起充电请求后，将按照充电模式（快/慢）进入不同的等待队列，此后等待系统叫号进入充电区。
充电区安装有2个快充充电桩+3个慢充充电桩（验收时该数值可变更）。充电区面积有限，每个充电桩后仅设置4个停车位（验收时该数值可变更）供车辆等候充电。当充电区有空余车位时，系统将按照进入等候区的先后顺序从对应充电模式的等待队列中调入车辆，并根据调度策略分配充电桩，并加入对应充电桩的排队队列。 

前后端分离 
html文件夹内为后端文件
  - Nginx
  - Uwsgi
  - Flask
  - Jwt
  - Mysql
ChargeWX文件夹内为前端文件
  - 微信小程序
  - JavaScript
