from dataclasses import dataclass
from http import server
import json
from mimetypes import encodings_map
from tabnanny import check
from server import db
from curses.ascii import isalpha, isdigit

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(40), nullable=False)
    

    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

    @staticmethod
    def check_username( username):
        checkPass = False

        if len(username) < 20 and len(username) >= 5:
            for each in username:
                if isdigit(each) or isalpha(each):
                    checkPass = True
                else:
                    checkPass = False
                    break
        
        return checkPass

    @staticmethod
    def check_password(password):
        checkPass = False

        if len(password) < 40 and len(password) >= 10:
            for each in password:
                if isdigit(each) or isalpha(each):
                    checkPass = True
                else:
                    checkPass = False
                    break
        
        return checkPass


    @staticmethod
    def is_user_exist(username):
        return Users.query.filter(Users.username == username).first()

    @staticmethod
    def authenticate(username, password):
        flag_user_exist = True
        flag_password_correct = True

        user = Users.query.filter(Users.username == username).first()
        if user:
            if not user.password == password:
                flag_password_correct = False
        else:
            flag_user_exist = False

        return flag_user_exist, flag_password_correct, user

    @staticmethod
    def get_users():
        return Users.query.filter().all()

    @staticmethod
    def insert_user(user):
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def update_user():
        db.session.commit()

    @staticmethod
    def deactivate_user():
        db.session.commit()

class Orders(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False, unique=True)
    flag = db.Column(db.Integer, nullable = False)
    charge_hub_id = db.Column(db.Integer, nullable = False)
    create_time = db.Column(db.String(20), nullable=False)
    mode = db.Column(db.String(5), nullable=False)
    start_time = db.Column(db.String(20), nullable=False)
    end_time = db.Column(db.String(20), nullable=False)
    degrees = db.Column(db.Float(precision="10,2"), nullable=False)
    current_degrees = db.Column(db.Float(precision="10,2"), nullable=False)
    charge_time = db.Column(db.String(20), nullable=False)
    charge_cost = db.Column(db.Float(precision="10,2"), nullable=False)
    server_cost = db.Column(db.Float(precision="10,2"), nullable=False)
    sum_cost = db.Column(db.Float(precision="10,2"), nullable=False)

    def __init__(self, user_id, mode, degrees, create_time):
        self.flag = 0
        self.charge_hub_id=-1
        self.create_time = create_time
        self.user_id=user_id
        self.mode=mode #''
        self.degrees=degrees
        self.start_time='0'
        self.end_time='0'
        self.charge_time=0
        self.current_degrees=0
        self.charge_cost=0
        self.server_cost=0
        self.sum_cost=0
        
    def set_mode(self,mode):
        self.mode=mode

    def change_flag(self,arg_flag):
        self.flag = arg_flag

    def change_charge_hub_id(self,charge_hub_id):
        self.charge_hub_id = charge_hub_id

    def set_start_time(self,start_time):
        self.start_time = start_time

    def set_end_time(self,end_time):
        self.end_time = end_time

    def set_degrees(self,degrees):
        self.degrees = degrees

    def set_current_degrees(self, current_degrees):
        self.current_degrees = current_degrees

    def set_charge_time(self):
        if self.mode=='slow':
            self.charge_time=int((self.current_degrees/10)*3600)
        elif self.mode=='fast':
            self.charge_time=int((self.current_degrees/30)*3600)
    
    def get_order_info(self):
        data = {}
        for name,value in vars(self).items():
            data[name] = value
        data.pop('_sa_instance_state')
        return json.dumps(data)

    def cal_dur(self, start_time,end_time):
        start_t = start_time.split(' ')[-1]
        end_t = end_time.split(' ')[-1]
        # 提取时分秒
        start_h = int(start_t.split(':')[0]) + 1
        start_m = int(start_t.split(':')[1])
        start_s = int(start_t.split(':')[-1])
        end_h = int(end_t.split(':')[0]) + 1
        end_m = int(end_t.split(':')[1])
        end_s = int(end_t.split(':')[-1])
        start_t = start_h * 3600 + start_m * 60 + start_s
        end_t = end_h * 3600 + end_m * 60 + end_s
        # 单位 秒
        if end_t > start_t:
            duration = end_t - start_t
        else:
            duration = 3600 * (24 - end_h + start_h) + 60 * (start_m - end_m) + start_s - end_s

        return start_t, end_t, start_h, end_h,duration

    # 充电费=单位电价*充电度数，服务费=服务费单价*充电度数。
    # 快充功率为30度/小时，慢充功率为10度/小时
    # 服务费单价：0.8元/度
    # 1      10~15,18~21
    # 0.7    7~10,15~18,21~23
    # 0.4    23~7

    def set_cost(self,start_time,end_time):
        charge_cost = 0
        s_t, e_t,start_h,end_h,duration = self.cal_dur(start_time,end_time)

        if 0 <= start_h <= 8 and 0 <= end_h <= 8:  # 1
            charge_cost = 0.4 * duration
        elif 0 <= start_h <= 8 and 8 <= end_h <= 11:  # 2
            charge_cost = 0.7 * (e_t - 8 * 3600) + 0.4 * (8 * 3600 - s_t)
        elif 0 <= start_h <= 8 and 11 <= end_h <= 16:  # 3
            charge_cost = 1.0 * (e_t - 11 * 3600) + 0.7 * 3 * 3600 + 0.4 * (8 * 3600 - s_t)
        elif 8 <= start_h <= 11 and 8 <= end_h <= 11:  # 4
            charge_cost = 0.7 * duration
        elif 8 <= start_h <= 11 and 11 <= end_h <= 16:  # 5
            charge_cost = 1.0 * (e_t - 11 * 3600) + 0.7 * (11 * 3600 - s_t)
        elif 8 <= start_h <= 11 and 16 <= end_h <= 19:  # 6
            charge_cost = 0.7 * (duration - 5 * 3600) + 1.0 * 5 * 3600
        elif 11 <= start_h <= 16 and 11 <= end_h <= 16:  # 7
            charge_cost = 1.0 * duration
        elif 11 <= start_h <= 16 and 16 <= end_h <= 19:  # 8
            charge_cost = 0.7 * (e_t - 16 * 3600) + 1.0 * (16 * 3600 - s_t)
        elif 11 <= start_h <= 16 and 19 <= end_h <= 22:  # 9
            charge_cost = 1.0 * (duration - 3 * 3600) + 0.7 * 3 * 3600
        elif 11 <= start_h <= 16 and 22 <= end_h <= 24:  # 10
            charge_cost = 1.7 * 3 * 3600 + 0.7 * (e_t - 22 * 3600) + 1.0 * (16 * 3600 - s_t)
        elif 16 <= start_h <= 19 and 16 <= end_h <= 19:  # 11
            charge_cost = 0.7 * duration
        elif 16 <= start_h <= 19 and 19 <= end_h <= 22:  # 12
            charge_cost = 1.0 * (e_t - 19 * 3600) + 0.7 * (19 * 3600 - s_t)
        elif 16 <= start_h <= 19 and 22 <= end_h <= 24:  # 13
            charge_cost=0.7*(duration-3*3600)+1.0*3*3600
        elif 16 <= start_h <= 19 and 0 <= end_h <= 8:  # 14
            charge_cost=1.0*3*3600+0.7*2+3600+e_t*0.4+0.7*(19*3600-s_t)
        elif 19 <= start_h <= 22 and 19 <= end_h <= 22:  # 15
            charge_cost=1.0*duration
        elif 19 <= start_h <= 22 and 22 <= end_h <= 24:  # 16
            charge_cost=0.7*(e_t-22*3600)+1.0*(22*3600-s_t)
        elif 19 <= start_h <= 22 and 0 <= end_h <= 8:  # 17
            charge_cost=0.4*e_t+0.7*3600*2+1.0*(22*3600-s_t)
        elif 22 <= start_h <= 24 and 22 <= end_h <= 24:  # 18
            charge_cost=0.7*duration
        elif 22 <= start_h <= 24 and 0 <= end_h <= 8:  # 19
            charge_cost=e_t*0.4+0.7*(24*3600-s_t)

        if self.mode == 'fast':
            #0.8*30*(duration/3600)
            service_cost = 0.8 * duration / 120
            #(charge_cost/3600)*30,单位转化为h
            charge_cost = charge_cost / 120
        else:
            #0.8*10*(duration/3600)
            service_cost = 0.8 * duration / 360
            # (charge_cost/3600)*10,单位转化为h
            charge_cost = charge_cost / 360

        sum_cost = service_cost + charge_cost
   
        self.sum_cost=sum_cost
        self.charge_cost=charge_cost
        self.server_cost=service_cost

    @staticmethod
    def get_all_order():
        return Orders.query.filter().all()

    @staticmethod
    def insert_order(order):
        db.session.add(order)
        db.session.commit()

        db.session.refresh(order)
        db.session.expunge(order)

    @staticmethod
    def update_order(order):

        db.session.query(Orders).filter_by(id = order.id).update({
            "flag":order.flag,
            "mode": order.mode,
            "degrees": order.degrees,
            "charge_hub_id":order.charge_hub_id,
            "start_time":order.start_time,
            "end_time": order.end_time,
            "charge_cost": order.charge_cost,
            "server_cost": order.server_cost,
            "charge_time": order.charge_time,
            "sum_cost": order.sum_cost,
            "current_degrees": order.current_degrees}
            , synchronize_session=False)
        db.session.commit()

    @staticmethod
    def deactivate_order():
        db.session.commit()

    
