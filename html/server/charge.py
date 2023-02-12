from ssl import SSL_ERROR_SSL
import time
import threading

from flask import jsonify
from models import Orders
from config import MAX_TIME , CHARGE_MAX_NUM,SLOW_CHARGE_NUM, FAST_CHARGE_NUM, MAX_LEN
import json
orderList={}
nowTimeStr="2022-06-25 05:55:00"
timeArray = time.strptime(nowTimeStr, "%Y-%m-%d %H:%M:%S")
nowTime=int((time.mktime(timeArray)))
def sysTime():
    global nowTime
    while 1:
        time.sleep(0.1)
        nowTime=nowTime+1



class chargeSys():
    def __init__(self):
        self.slowChargeState=[]
        self.fastChargeState=[]
        self.fastcharge=[]
        self.slowcharge=[]
        self.fastWait=[]
        self.slowWait=[]
        self.threadTimeSlow=[]
        self.threadTimeFast=[]
        self.threadSlowFlag=[]
        self.threadFastFlag=[]
        self.slowfault=[]
        self.fastfault=[] #故障队列
        self.slowChargeLock=threading.RLock()
        self.fastChargeLock=threading.RLock()
        self.slowSumTime=[]
        self.fastSumTime=[]
        self.slowSumcount=[]
        self.fastSumcount=[]
        self.slowSumdegrees=[]
        self.fastSumdegrees=[]
        self.slowSumChargeCost=[]
        self.fastSumChargeCost=[]
        self.slowSumServeCost=[]
        self.fastSumServeCost=[]
        self.slowSumCost=[]
        self.fastSumCost=[]
        #self.slowfaultLock=threading.RLock()
        #self.fastfaultLock=threading.RLock()
        for i in range(SLOW_CHARGE_NUM):
            self.slowChargeState.append('on')
            self.slowcharge.append([])
            self.threadTimeSlow.append(0)
            self.threadSlowFlag.append(True)
            self.slowSumTime.append(0)
            self.slowSumcount.append(0)
            self.slowSumdegrees.append(0)
            self.slowSumChargeCost.append(0)
            self.slowSumServeCost.append(0)
            self.slowSumCost.append(0)
        for i in range(FAST_CHARGE_NUM):
            self.fastChargeState.append('on')
            self.fastcharge.append([])
            self.threadTimeFast.append(0)
            self.threadFastFlag.append(True)
            self.fastSumTime.append(0)
            self.fastSumcount.append(0)
            self.fastSumdegrees.append(0)
            self.fastSumChargeCost.append(0)
            self.fastSumServeCost.append(0)
            self.fastSumCost.append(0)
        self.thread=threading.Thread(target=sysTime)
        self.thread.start()

    def get_systTime(self):
        time_local = time.localtime(nowTime)
        timeStr = time.strftime("%Y-%m-%d %H:%M:%S",time_local)
        return timeStr

    def line(self,mode,userID,degrees):
        if mode=='slow':
            self.slowChargeLock.acquire()
            if len(self.slowWait)+len(self.fastWait)<MAX_LEN:
                self.slowWait.append([userID,degrees])
                self.slowChargeLock.release()
            else:
                self.slowChargeLock.release()
                return 0

            time_local = time.localtime(nowTime)
            create_time = time.strftime("%Y-%m-%d %H:%M:%S",time_local)
            order=Orders(userID,mode,degrees,create_time)
            
            Orders.insert_order(order)
            
            orderList[userID]=order

        elif mode=='fast':
            self.fastChargeLock.acquire()
            if len(self.slowWait)+len(self.fastWait)<MAX_LEN:
                self.fastWait.append([userID,degrees])
                self.fastChargeLock.release()
            else:
                self.fastChargeLock.release()
                return 0
            time_local = time.localtime(nowTime)
            create_time = time.strftime("%Y-%m-%d %H:%M:%S",time_local)
            order=Orders(userID,mode,degrees,create_time)
            Orders.insert_order(order)
            orderList[userID]=order
        #else:
        #    return #error()############
        self.dispatch(mode)
        return 1
    def is_enough(self,mode):
        haveSpace=[]
        if mode=='slow':
            for i in range(SLOW_CHARGE_NUM):
                if len(self.slowcharge[i])<CHARGE_MAX_NUM and self.slowChargeState[i]=='on':
                    haveSpace.append(i)
            return haveSpace
        elif mode=='fast':
            for i in range(FAST_CHARGE_NUM):
                if len(self.fastcharge[i])<CHARGE_MAX_NUM and self.fastChargeState[i]=='on':
                    haveSpace.append(i)
            return haveSpace
    
    def find_min_time(self,mode,spaceList):
        (spaceList)
        (self.fastcharge)
        minTimeno=0
        minTime=MAX_TIME
        minTimeTem=0
        if mode=='slow':
            for i in spaceList:
                minTimeTem=self.threadTimeSlow[i]
                #for j in range(1,len(self.slowcharge[i])):
                j=1
                while j<len(self.slowcharge[i]):
                    minTimeTem=minTimeTem+self.slowcharge[i][j][1]/10*3600
                    j=j+1
                if minTimeTem<minTime:
                    minTime=minTimeTem
                    minTimeno=i
        else:
            for i in spaceList:
                minTimeTem=self.threadTimeFast[i]
                #for j in range(1,len(self.fastcharge[i])):
                j=1
                while j<len(self.fastcharge[i]):
                    minTimeTem=minTimeTem+self.fastcharge[i][j][1]/30*3600
                    j=j+1
                if minTimeTem<minTime:
                    minTime=minTimeTem
                    minTimeno=i
        return minTimeno


    def charging(self,mode,minTimeNo):
        if mode=='slow':
            while len(self.slowcharge[minTimeNo])>0:
                #orderList[userID].output()
                userID=self.slowcharge[minTimeNo][0][0]
                orderList[userID].change_flag(1)
                time_local = time.localtime(nowTime)
                start_time=time.strftime("%Y-%m-%d %H:%M:%S",time_local)
                orderList[userID].set_start_time(start_time)
                self.threadSlowFlag[minTimeNo]=True
                degrees=self.slowcharge[minTimeNo][0][1]
                self.threadTimeSlow[minTimeNo]=degrees/10 *3600
                #expectedend_time=nowTime+self.threadTimeSlow[minTimeNo]
                #orderList[userID].set_end_time(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(expectedend_time)))

                while self.threadSlowFlag[minTimeNo] and self.threadTimeSlow[minTimeNo]>0:
                    time.sleep(0.1)
                    self.threadTimeSlow[minTimeNo]=self.threadTimeSlow[minTimeNo]-1
                    time_local = time.localtime(nowTime)
                    nowtime=time.strftime("%Y-%m-%d %H:%M:%S",time_local)
                    current_degrees=degrees*(((degrees/10)*3600-self.threadTimeSlow[minTimeNo])/(degrees/10 *3600))
                    orderList[userID].set_current_degrees(current_degrees)
                    orderList[userID].set_cost(orderList[userID].start_time,nowtime)
                    orderList[userID].set_charge_time()
                
                '''
                if self.threadTimeSlow[minTimeNo]<=0:
                    time_local = time.localtime(nowTime)
                    end_time=time.strftime("%Y-%m-%d %H:%M:%S",time_local)
                    orderList[userID].set_end_time(end_time)
                    orderList[userID].set_cost()
                else:
                    time_local = time.localtime(nowTime)
                    end_time=time.strftime("%Y-%m-%d %H:%M:%S",time_local)
                    orderList[userID].set_end_time(end_time)
                    orderList[userID].set_degrees(degrees*(((degrees/10)*3600-self.threadTimeSlow[minTimeNo])/(degrees/10 *3600)))
                    orderList[userID].set_cost()
                '''

                end_time=time.strftime("%Y-%m-%d %H:%M:%S",time_local)
                orderList[userID].set_end_time(end_time)
                
                
                orderList[userID].change_flag(2)
                self.slowSumTime[minTimeNo]=self.slowSumTime[minTimeNo]+orderList[userID].charge_time
                self.slowSumcount[minTimeNo]=self.slowSumcount[minTimeNo]+1
                self.slowSumdegrees[minTimeNo]=self.slowSumdegrees[minTimeNo]+orderList[userID].current_degrees
                self.slowSumChargeCost[minTimeNo]=self.slowSumChargeCost[minTimeNo]+orderList[userID].charge_cost
                self.slowSumServeCost[minTimeNo]=self.slowSumServeCost[minTimeNo]+orderList[userID].server_cost
                self.slowSumCost[minTimeNo]=self.slowSumCost[minTimeNo]+orderList[userID].sum_cost

                Orders.update_order(orderList[userID])

                self.slowChargeLock.acquire()
                self.slowcharge[minTimeNo].pop(0)
                orderList.pop(userID)
                self.threadTimeSlow[minTimeNo]=0
                self.threadSlowFlag[minTimeNo]=True
                
                if(self.slowChargeState[minTimeNo]=='on'):
                    if len(self.slowfault)>0:
                        temp=self.slowfault.pop(0)
                        self.slowcharge[minTimeNo].append(temp[1])
                        orderList[self.slowcharge[minTimeNo][-1][0]].change_charge_hub_id(minTimeNo)
                    elif len(self.slowWait)>0:
                        self.slowcharge[minTimeNo].append(self.slowWait.pop(0))
                        orderList[self.slowcharge[minTimeNo][-1][0]].change_charge_hub_id(minTimeNo)
                self.slowChargeLock.release()
                        
            
        elif mode=='fast':
            while len(self.fastcharge[minTimeNo])>0:
                userID=self.fastcharge[minTimeNo][0][0]
                orderList[userID].change_flag(1)
                #orderList[userID].output()
                time_local = time.localtime(nowTime)
                start_time=time.strftime("%Y-%m-%d %H:%M:%S",time_local)
                orderList[userID].set_start_time(start_time)
                self.threadFastFlag[minTimeNo]=True
                degrees=self.fastcharge[minTimeNo][0][1]
                self.threadTimeFast[minTimeNo]=degrees/30 *3600
                #expectedend_time=nowTime+self.threadTimeFast[minTimeNo]
                #orderList[userID].set_end_time(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(expectedend_time)))
                #orderList[userID].set_end_time(expectedend_time)
                while self.threadFastFlag[minTimeNo] and self.threadTimeFast[minTimeNo]>0:
                    time.sleep(0.1)
                    self.threadTimeFast[minTimeNo]=self.threadTimeFast[minTimeNo]-1
                    time_local = time.localtime(nowTime)
                    nowtime=time.strftime("%Y-%m-%d %H:%M:%S",time_local)
                    current_degrees=degrees*(((degrees/30)*3600-self.threadTimeFast[minTimeNo])/(degrees/30 *3600))
                    orderList[userID].set_current_degrees(current_degrees)
                    orderList[userID].set_cost(orderList[userID].start_time,nowtime)
                    orderList[userID].set_charge_time()
                '''
                if self.threadTimeFast[minTimeNo]<=0:
                    time_local = time.localtime(nowTime)
                    end_time=time.strftime("%Y-%m-%d %H:%M:%S",time_local)
                    orderList[userID].set_end_time(end_time)
                    orderList[userID].set_cost()
                else:
                    time_local = time.localtime(nowTime)
                    end_time=time.strftime("%Y-%m-%d %H:%M:%S",time_local)
                    orderList[userID].set_end_time(end_time)
                    orderList[userID].set_degrees(degrees*(((degrees/30 *3600)-self.threadTimeFast[minTimeNo])/(degrees/30 *3600)))
                    orderList[userID].set_cost()
                '''
                time_local = time.localtime(nowTime)
                end_time=time.strftime("%Y-%m-%d %H:%M:%S",time_local)
                orderList[userID].set_end_time(end_time)


                
                orderList[userID].change_flag(2)
                self.fastSumTime[minTimeNo]=self.fastSumTime[minTimeNo]+orderList[userID].charge_time
                self.fastSumcount[minTimeNo]=self.fastSumcount[minTimeNo]+1
                self.fastSumdegrees[minTimeNo]=self.fastSumdegrees[minTimeNo]+orderList[userID].current_degrees
                self.fastSumChargeCost[minTimeNo]=self.fastSumChargeCost[minTimeNo]+orderList[userID].charge_cost
                self.fastSumServeCost[minTimeNo]=self.fastSumServeCost[minTimeNo]+orderList[userID].server_cost
                self.fastSumCost[minTimeNo]=self.fastSumCost[minTimeNo]+orderList[userID].sum_cost
                Orders.update_order(orderList[userID])

                self.fastChargeLock.acquire()
                self.fastcharge[minTimeNo].pop(0)
                orderList.pop(userID)
                self.threadTimeFast[minTimeNo]=0
                self.threadFastFlag[minTimeNo]='True'
                if(self.fastChargeState[minTimeNo]=='on'):
                    if len(self.fastfault)>0:
                        temp=self.fastfault.pop(0)
                        self.fastcharge[minTimeNo].append(temp[1])
                        orderList[self.fastcharge[minTimeNo][-1][0]].change_charge_hub_id(minTimeNo)
                    elif len(self.fastWait)>0:
                        self.fastcharge[minTimeNo].append(self.fastWait.pop(0))
                        orderList[self.fastcharge[minTimeNo][-1][0]].change_charge_hub_id(minTimeNo)
                self.fastChargeLock.release()




    def dispatch(self,mode):
        if mode=='slow':
            self.slowChargeLock.acquire()
            space=self.is_enough(mode)
            if len(space)==0:
                self.slowChargeLock.release()
                return 0
            else:
                minTimeNo=self.find_min_time(mode,space)
                if len(self.slowfault)>0:
                    temp=self.slowfault.pop(0)
                    userID=temp[1][0]   
                    self.slowcharge[minTimeNo].append(temp[1])
                else:
                    userID=self.slowWait[0][0]
                    self.slowcharge[minTimeNo].append(self.slowWait.pop(0))
                self.slowChargeLock.release()
                orderList[userID].change_charge_hub_id(minTimeNo)
                #orderList[userID].flag=1
                if(self.slowcharge[minTimeNo][0][0]==userID):
                    thread1=threading.Thread(target=self.charging,args=('slow',minTimeNo))
                    thread1.start()
        else:
            self.fastChargeLock.acquire()
            space=self.is_enough(mode)
            if len(space)==0:
                self.fastChargeLock.release()
                return 0
            else:
                minTimeNo=self.find_min_time(mode,space)
                if len(self.fastfault)>0:
                    temp=self.fastfault.pop(0)
                    userID=temp[1][0]
                    self.fastcharge[minTimeNo].append(temp[1])
                else:
                    userID=self.fastWait[0][0]
                    self.fastcharge[minTimeNo].append(self.fastWait.pop(0))
                self.fastChargeLock.release()
                orderList[userID].change_charge_hub_id(minTimeNo)
                #orderList[userID].flag=1
                if(self.fastcharge[minTimeNo][0][0]==userID):
                    thread2=threading.Thread(target=self.charging,args=('fast',minTimeNo))
                    thread2.start()
        return 1

    def set_degrees_and_mode(self, userID, modeFlag, degrees):
        self.slowChargeLock.acquire()
        for i in range(len(self.slowWait)):
            if self.slowWait[i][0]==userID:
                if degrees != 0:
                    self.slowWait[i][1]=degrees
                    orderList[userID].set_degrees(degrees)
                if modeFlag !=0:    
                    self.fastChargeLock.acquire()
                    orderList[userID].set_mode('fast')
                    self.fastWait.append(self.slowWait.pop(i))
                    self.fastChargeLock.release()
                    self.dispatch('fast')
                self.slowChargeLock.release()
                return 1
        self.slowChargeLock.release()
        
        self.fastChargeLock.acquire()
        for i in range(len(self.fastWait)):
            if self.fastWait[i][0]==userID:
                if degrees!=0:
                    self.fastWait[i][1]=degrees
                    orderList[userID].set_degrees(degrees)
                if modeFlag!=0:
                    self.slowChargeLock.acquire()
                    orderList[userID].set_mode('slow')
                    self.slowWait.append(self.fastWait.pop(i))
                    self.slowChargeLock.release()
                    self.dispatch('slow')
                self.fastChargeLock.release() 
                return 1
        self.fastChargeLock.release()
        return 0

    def cancel_charge(self,userID):
        self.slowChargeLock.acquire()#slow等待队列中查找
        for i in range(len(self.slowWait)):
            if self.slowWait[i][0]==userID:
                self.slowWait.pop(i)
                orderList.pop(userID)
                Orders.update_order(orderList[userID])
                
                self.slowChargeLock.release()
                return 1

        for i in range(SLOW_CHARGE_NUM):#slow充电队列中查找
            for j in range(len(self.slowcharge[i])):
                if self.slowcharge[i][j][0]==userID:
                    if j==0:
                        self.threadSlowFlag[i]=False
                    else:
                        self.slowcharge[i].pop(j)
                        Orders.update_order(orderList[userID])
                        orderList.pop(userID)
                        if len(self.slowfault)>0:
                            temp=self.slowfault.pop(0)
                            self.slowcharge[i].append(temp[1])
                            orderList[self.slowcharge[i][-1][0]].change_charge_hub_id(i)
                        elif len(self.slowWait)>0:
                            self.slowcharge[i].append(self.slowWait.pop(0))
                            orderList[self.slowcharge[i][-1][0]].change_charge_hub_id(i)
                    self.slowChargeLock.release()
                    return 1
        

        #slow维修队列中查找
        for i in range(len(self.slowfault)):
            if self.slowfault[i][1][0]==userID:
                self.slowfault.pop(i)
                Orders.update_order(orderList[userID])
                orderList.pop(userID)
                
                self.slowChargeLock.release()
                return 1
        self.slowChargeLock.release()


        self.fastChargeLock.acquire()#fast等待队列中查找
        for i in range(len(self.fastWait)):
            if self.fastWait[i][0]==userID:
                self.fastWait.pop(i)
                Orders.update_order(orderList[userID])
                orderList.pop(userID)
                
                self.fastChargeLock.release()
                return 1
        for i in range(FAST_CHARGE_NUM):#fast充电队列中查找
            for j in range(len(self.fastcharge[i])):
                if self.fastcharge[i][j][0]==userID:
                    if j==0:
                        self.threadFastFlag[i]=False
                    else:
                        self.fastcharge[i].pop(j)
                        orderList.pop(userID)
                        Orders.update_order(orderList[userID])
                        if len(self.fastfault)>0:
                            temp=self.fastfault.pop(0)
                            self.fastcharge[i].append(temp[1])
                            orderList[self.fastcharge[i][-1][0]].change_charge_hub_id(i)
                        elif len(self.fastWait)>0:
                            self.fastcharge[i].append(self.fastWait.pop(0))
                            orderList[self.fastcharge[i][-1][0]].change_charge_hub_id(i)
                    self.fastChargeLock.release()
                    return 1
        #fast维修队列中查找
        for i in range(len(self.fastfault)):
            if self.fastfault[i][1][0]==userID:
                self.fastfault.pop(i)
                Orders.update_order(orderList[userID])
                orderList.pop(userID)
                
                self.fastChargeLock.release()
                return 1
        self.fastChargeLock.release()
        return 0

    def open_chargeHub(self,mode,charge_hub_id):
        if mode=='slow':
            if self.slowChargeState[charge_hub_id]=='on' or charge_hub_id<0 or charge_hub_id>SLOW_CHARGE_NUM-1:
                return 0
            else:
                self.slowChargeLock.acquire()
                self.slowChargeState[charge_hub_id]='on'
                #将维修队列和等待队列中的车加到新开的充电桩
                while len(self.slowcharge[charge_hub_id])<CHARGE_MAX_NUM and len(self.slowfault)>0:
                    temp=self.slowfault.pop(0)
                    self.slowcharge[charge_hub_id].append(temp[1])
                while len(self.slowcharge[charge_hub_id])<CHARGE_MAX_NUM and len(self.slowWait)>0:
                    self.slowcharge[charge_hub_id].append(self.slowWait.pop(0))
                for i in range(len(self.slowcharge[charge_hub_id])):
                    orderList[self.slowcharge[charge_hub_id][i][0]].change_charge_hub_id(charge_hub_id)
                self.slowChargeLock.release()
                if len(self.slowcharge[charge_hub_id])>0:
                    thread3=threading.Thread(target=self.charging,args=('slow',charge_hub_id))
                    thread3.start()
                return 1
        elif mode=='fast':
            if self.fastChargeState[charge_hub_id]=='on' or charge_hub_id<0 or charge_hub_id>FAST_CHARGE_NUM-1:
                return 0
            else:
                self.fastChargeLock.acquire()
                self.fastChargeState[charge_hub_id]='on'
                #将维修队列和等待队列中的车加到新开的充电桩
                while len(self.fastcharge[charge_hub_id])<CHARGE_MAX_NUM and len(self.fastfault)>0:
                    temp=self.fastfault.pop(0)
                    self.fastcharge[charge_hub_id].append(temp[1])
                while len(self.fastcharge[charge_hub_id])<CHARGE_MAX_NUM and len(self.fastWait)>0:
                    self.fastcharge[charge_hub_id].append(self.fastWait.pop(0))
                for i in range(len(self.fastcharge[charge_hub_id])):
                    orderList[self.fastcharge[charge_hub_id][i][0]].change_charge_hub_id(charge_hub_id)
                self.fastChargeLock.release()
                if len(self.fastcharge[charge_hub_id])>0:
                    thread3=threading.Thread(target=self.charging,args=('fast',charge_hub_id))
                    thread3.start()
                return 1
    

    def close_chargeHub(self,mode,charge_hub_id):
        if mode=='slow':
            if self.slowChargeState[charge_hub_id]=='off' or charge_hub_id<0 or charge_hub_id>SLOW_CHARGE_NUM-1:
                return 0
            else:
                self.slowChargeLock.acquire()
                if(len(self.slowcharge[charge_hub_id])==0):
                    self.slowChargeState[charge_hub_id]='off'
                    self.slowChargeLock.release()
                elif len(self.slowcharge[charge_hub_id])==1:
                    self.slowChargeState[charge_hub_id]='off'
                    self.threadSlowFlag[charge_hub_id]=False
                    self.slowChargeLock.release()
                #将充电队列中未充电的车放到维修队列优先调度
                elif len(self.slowcharge[charge_hub_id])>1:
                    self.slowChargeState[charge_hub_id]='off'
                    self.threadSlowFlag[charge_hub_id]=False
                    j=0
                    for i in range(len(self.slowcharge[charge_hub_id])-1):
                        temp=self.slowcharge[charge_hub_id].pop(1)
                        self.slowfault.append([charge_hub_id,temp])
                        j=j+1
                    self.slowChargeLock.release()
                    for i in range(j):
                        self.dispatch('slow')
            return 1
        elif mode=='fast':
            if self.fastChargeState[charge_hub_id]=='off' or charge_hub_id<0 or charge_hub_id>FAST_CHARGE_NUM-1:
                return 0
            else:
                self.fastChargeLock.acquire()
                if(len(self.fastcharge[charge_hub_id])==0):
                    self.fastChargeState[charge_hub_id]='off'
                    self.fastChargeLock.release()
                elif len(self.fastcharge[charge_hub_id])==1:
                    self.fastChargeState[charge_hub_id]='off'
                    self.threadFastFlag[charge_hub_id]=False
                    self.fastChargeLock.release()
                #将充电队列中未充电的车放到维修队列优先调度
                elif len(self.fastcharge[charge_hub_id])>1:
                    self.fastChargeState[charge_hub_id]='off'
                    self.threadFastFlag[charge_hub_id]=False
                    j=0
                    for i in range(len(self.fastcharge[charge_hub_id])-1):
                        temp=self.fastcharge[charge_hub_id].pop(1)
                        self.fastfault.append([charge_hub_id,temp])
                        j=j+1
                    self.fastChargeLock.release()
                    for i in range(j):
                        self.dispatch('fast')
                return 1

    def get_info(self):
        slowInfo={}
        slowWaitInfo={}
        self.slowChargeLock.acquire()
        for i in range(SLOW_CHARGE_NUM):
            tempList={}
            for j in range(len(self.slowcharge[i])):
                if j==0:
                    now_useid=self.slowcharge[i][j][0]
                    templist1={}
                    templist1['user_id']=now_useid
                    templist1['current_degrees']=orderList[now_useid].current_degrees
                    templist1['sum_cost']=orderList[now_useid].sum_cost
                    #tempList.append([now_useid,orderList[now_useid].current_degrees,orderList[now_useid].sum_cost])
                    tempList[j]=templist1
                else:
                    tempList[j]=self.slowcharge[i][j][0]
            slowInfo[i]=tempList
        m=0
        flag=-1
        for i in range(len(self.slowfault)):
            if self.slowfault[i][0]!=flag:
                flag=self.slowfault[i][0]
                m=0
            slowInfo[self.slowfault[i][0]][m]=self.slowfault[i][1][0]
            m=m+1
            #slowfaultInfo.append([self.slowfault[i][0],self.slowfault[i][1][0]])
        for i in range(len(self.slowWait)):
            tempdict2={}
            tempdict2['user_id']=self.slowWait[i][0]
            tempdict2['degrees']=self.slowWait[i][1]
            slowWaitInfo[i]=tempdict2
        self.slowChargeLock.release()


        fastInfo={}
        fastWaitInfo={}
        self.fastChargeLock.acquire()
        for i in range(FAST_CHARGE_NUM):
            tempdict={}
            for j in range(len(self.fastcharge[i])):
                if j==0:
                    tempdict1={}
                    now_useid=self.fastcharge[i][j][0]
                    tempdict1['user_id']=now_useid
                    tempdict1['current_degrees']=orderList[now_useid].current_degrees
                    tempdict1['current_sum_cost']=orderList[now_useid].sum_cost
                    #tempList.append([now_useid,orderList[now_useid].current_degrees,orderList[now_useid].sum_cost])
                    tempdict[0]=tempdict1
                else:
                    tempdict[j]=self.fastcharge[i][j][0]
                    #tempList.append(self.fastcharge[i][j][0])
            fastInfo[i]=tempdict
        m=0
        flag=-1
        for i in range(len(self.fastfault)):
            if self.fastfault[i][0]!=flag:
                flag=self.fastfault[i][0]
                m=0
            fastInfo[self.fastfault[i][0]][m]=self.fastfault[i][1][0]
            m=m+1
            #fastfaultInfo.append([self.fastfault[i][0],self.fastfault[i][1][0]])
        for i in range(len(self.fastWait)):
            tempdict2={}
            tempdict2['user_id']=self.fastWait[i][0]
            tempdict2['degrees']=self.fastWait[i][1]
            fastWaitInfo[i]=tempdict2
            #fastWaitInfo.append([self.fastWait[i][0],self.fastWait[i][1]])
        self.fastChargeLock.release()
        dict={}
        dict['slow_charge']=slowInfo
        dict['slow_wait']=slowWaitInfo
        dict['fast_charge']=fastInfo
        dict['fast_wait']=fastWaitInfo
        return json.dumps(dict)

    
    def get_order_by_userID(self, userID):
        if userID not in orderList.keys():
            return None
        else:
            order = orderList[userID]
            return order.get_order_info()


    def get_line_number(self,userID):#返回（F/T）排队号，不在排队队列返回‘’
        self.slowChargeLock.acquire()
        for i in range(len(self.slowWait)):
            if self.slowWait[i][0]==userID:
                self.slowChargeLock.release()
                return 'T'+str(i+1)
        self.slowChargeLock.release()
        
        self.fastChargeLock.acquire()
        for i in range(len(self.fastWait)):
            if self.fastWait[i][0]==userID:
                self.fastChargeLock.release()
                return 'F'+str(i+1)
        self.fastChargeLock.release()
        return ''
    
    def get_num_before_user(self,userID):
        self.slowChargeLock.acquire()
        for i in range(len(self.slowWait)):
            if self.slowWait[i][0]==userID:
                self.slowChargeLock.release()
                return i
        self.slowChargeLock.release()
        
        self.fastChargeLock.acquire()
        for i in range(len(self.fastWait)):
            if self.fastWait[i][0]==userID:
                self.fastChargeLock.release()
                return i
        self.fastChargeLock.release()
        return -1

    def get_report_form(self):
        report_form_dict={}
        time_local = time.localtime(nowTime)
        now_time=time.strftime("%Y-%m-%d",time_local)
        self.slowChargeLock.acquire()
        for i in range(SLOW_CHARGE_NUM):
            tempdict={}
            tempdict['time']=now_time
            tempdict['chargeHub_id']=i
            tempdict['sum_count']=self.slowSumcount[i]
            tempdict['sum_time']=self.slowSumTime[i]
            tempdict['sum_degrees']=self.slowSumdegrees[i]
            tempdict['sum_charge_cost']=self.slowSumChargeCost[i]
            tempdict['sum_serve_cost']=self.slowSumServeCost[i]
            tempdict['sum_cost']=self.slowSumCost[i]
            report_form_dict[('s'+str(i))]=tempdict
        self.slowChargeLock.release()
        self.fastChargeLock.acquire()
        for i in range(FAST_CHARGE_NUM):
            tempdict={}
            tempdict['time']=now_time
            tempdict['chargeHub_id']=i
            tempdict['sum_count']=self.fastSumcount[i]
            tempdict['sum_time']=self.fastSumTime[i]
            tempdict['sum_degrees']=self.fastSumdegrees[i]
            tempdict['sum_charge_cost']=self.fastSumChargeCost[i]
            tempdict['sum_serve_cost']=self.fastSumServeCost[i]
            tempdict['sum_cost']=self.fastSumCost[i]
            report_form_dict[('f'+str(i))]=tempdict
        self.fastChargeLock.release()
        return json.dumps(report_form_dict)
    
    def get_chargeHub_state(self):
        chargeHub_state_dict={}
        self.slowChargeLock.acquire()
        for i in range(SLOW_CHARGE_NUM):
            tempdict={}
            tempdict['state']=self.slowChargeState[i]
            tempdict['sum_count']=self.slowSumcount[i]
            tempdict['sum_time']=self.slowSumTime[i]
            tempdict['sum_degrees']=self.slowSumdegrees[i]
            chargeHub_state_dict[('s'+str(i))]=tempdict
        self.slowChargeLock.release()

        self.fastChargeLock.acquire()
        for i in range(FAST_CHARGE_NUM):
            tempdict={}
            tempdict['state']=self.fastChargeState[i]
            tempdict['sum_count']=self.fastSumcount[i]
            tempdict['sum_time']=self.fastSumTime[i]
            tempdict['sum_degrees']=self.fastSumdegrees[i]
            chargeHub_state_dict[('f'+str(i))]=tempdict
        self.fastChargeLock.release()
        return json.dumps(chargeHub_state_dict)



    def get_user_info_in_charge(self):
        user_info_dict={}
        time_local = time.localtime(nowTime)
        nowtime=time.strftime("%Y-%m-%d %H:%M:%S",time_local)
        timeArray=time.strptime(nowtime,"%Y-%m-%d %H:%M:%S")
        nowtimeStamp=int(time.mktime(timeArray))
        self.slowChargeLock.acquire()
        for i in range(SLOW_CHARGE_NUM):
            tempdict1={}
            for j in range(len(self.slowcharge[i])):
                tempdict={}
                user_ID=self.slowcharge[i][j][0]
                timeArray=time.strptime(orderList[user_ID].create_time,"%Y-%m-%d %H:%M:%S")
                creatTimeStamp=int(time.mktime(timeArray))
                tempdict['user_ID']=user_ID
                tempdict['request_degrees']=orderList[user_ID].degrees
                if j==0:
                    start_time=orderList[user_ID].start_time
                    timeArray=time.strptime(start_time,"%Y-%m-%d %H:%M:%S")
                    startTimeStamp=int(time.mktime(timeArray))
                    tempdict['wait_time']=startTimeStamp-creatTimeStamp
                else:
                    tempdict['wait_time']=nowtimeStamp-creatTimeStamp
                tempdict1[('charge'+str(j))]=tempdict
            user_info_dict[('s'+str(i))]=tempdict1
        self.slowChargeLock.release()

        self.fastChargeLock.acquire()
        for i in range(FAST_CHARGE_NUM):
            tempdict1={}
            for j in range(len(self.fastcharge[i])):
                tempdict={}
                user_ID=self.fastcharge[i][j][0]
                timeArray=time.strptime(orderList[user_ID].create_time,"%Y-%m-%d %H:%M:%S")
                creatTimeStamp=int(time.mktime(timeArray))
                tempdict['user_ID']=user_ID
                tempdict['request_degrees']=orderList[user_ID].degrees
                if j==0:
                    start_time=orderList[user_ID].start_time
                    timeArray=time.strptime(start_time,"%Y-%m-%d %H:%M:%S")
                    startTimeStamp=int(time.mktime(timeArray))
                    tempdict['wait_time']=startTimeStamp-creatTimeStamp
                else:
                    tempdict['wait_time']=nowtimeStamp-creatTimeStamp
                tempdict1[('charge'+str(j))]=tempdict
            user_info_dict[('f'+str(i))]=tempdict1
        self.fastChargeLock.release()
        return json.dumps(user_info_dict)


