from ast import Str, arg
from crypt import methods
import json
from math import degrees
from sys import flags
from tabnanny import check
from flask import Flask, request, current_app, g, jsonify
from gevent import monkey
from gevent.pywsgi import WSGIServer
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager,create_access_token, current_user,jwt_required,get_jwt_identity
import config


monkey.patch_all()

app = Flask(__name__)

# 导入配置
app.config.from_object(config)

# 连接数据库
db = SQLAlchemy(app)

# 引入数据库用户类
from models import Users
from charge import *

# JWT管理器
jwtManager = JWTManager(app)

charge_sys = chargeSys()

@app.route("/")
@jwt_required(optional=False)
def index():
    users_list = []
    users = Users.get_users()

    current_userID = get_jwt_identity()
    if current_userID == app.config['ADMIN_ID']:
        for user in users:
            users_list.append({"userid": user.id, "username": user.username})
    else:
        users_list.append(current_user)

    return jsonify({
        "code": 200,
        "message": "success",
        "users": users_list
    })


# 登录接口
@app.route("/api/login",methods=['POST'])
def login():
    code = None
    message = None
    token = None
    userid = None

    args = request.get_data()
    args = json.loads(args)
    username = args["username"]
    password = args["password"]


    if Users.check_username(username) == False or Users.check_password(password) == False:
        code = 201 
        message = "username must be alpha or number, the username length is limited at 5 - 20 ." + \
                "password must be alpha or number, the password length is limited at 10 - 40 ."
    else:
        flag_user_exist, flag_password_correct, user = Users.authenticate(username=username, password=password)

        if not flag_user_exist:
            code = 202
            message = "user not exist"
        elif not flag_password_correct:
            code = 203
            message = "wrong password"
        else:
            code = 200
            message = "success"
            token = create_access_token(identity=user.id)
            userid = user.id

    return jsonify({
        "code": code,
        "message": message,
        "token": token,
        "userid": userid
    })

# 注册接口
@app.route("/api/registe",methods=['POST'])
def registe():
    username = None
    password = None
    code = None
    message = None
    userid = None

    args = request.get_data()
    args = json.loads(args)
    username = args["username"]
    password = args["password"]
    if Users.check_username(username) == False or Users.check_password(password) == False:
        code = 201 
        message = "username must be alpha or number, the username length is limited at 5 - 20 ." + \
                "password must be alpha or number, the password length is limited at 10 - 40. "

    else:
        if( Users.is_user_exist(username=username)):
            code = 202
            message = "user is exist"
        else:
            newUser = Users(username=username, password=password)
            newUser.insert_user(newUser)
            code = 200
            message = "registe success"
            userid = newUser.id

    return jsonify({
        "code": code,
        "message": message,
        "userid": userid
    })

# 获取系统时间
@app.route("/api/getSystemTime", methods=['GET'])
def getSystemTime():
    return jsonify({
        "code": 200,
        "time": charge_sys.get_systTime()
    })

# 发送预约信息进行排号(用户)
@app.route("/api/charge", methods=['POST'])
@jwt_required(optional=False)
def charge():
    code = None
    message = None

    current_userID = get_jwt_identity()
    if current_userID in orderList.keys():
        code = 202
        message = "cannot send a charge request before the last order end"
    else:
        args = request.get_data()
        args = json.loads(args)

        mode = args["mode"]
        degrees = args["degrees"]

        if mode == "fast" or mode == "slow":
            if charge_sys.line(mode,current_userID,degrees) == 0:
                code = 202
                message = "waiting queue len reached max"
            else:
                code = 200
                message = "success"

        else:
            code = 201
            message = "error mode"
    
    
    return jsonify({
        "code": code,
        "message": message
    })

# 关闭充电桩-模拟故障(管理员)
@app.route("/api/closeHub/<mode>/<hubID>", methods=['GET'])
@jwt_required(optional=False)
def closeHub(mode, hubID):

    code = None
    message = None
    current_userID = get_jwt_identity()

    if current_userID == app.config['ADMIN_ID']:
        if mode == "fast" or mode == "slow":
            ret = charge_sys.close_chargeHub(mode = mode, charge_hub_id = int(hubID))
            if ret == 1 :
                code = 200
                message = "close success"
            else:
                code = 201
                message = "close failed"
        else:
            code = 202
            message = "error charge hub info"
    else:
        code = 203
        message = "only admin can close"

    return jsonify({
        "code": code,
        "mode": mode,
        "hubid": str(hubID),
        "message":message
    })

# 打开充电桩-故障恢复(管理员)
@app.route("/api/openHub/<mode>/<hubID>", methods=['GET'])
@jwt_required(optional=False)
def openHub(mode, hubID):

    code = None
    message = None
    current_user = get_jwt_identity()

    if current_user == app.config['ADMIN_ID']:
        if mode == "fast" or mode == "slow":
            ret = charge_sys.open_chargeHub(mode = mode, charge_hub_id = int(hubID))
            if ret == 1 :
                code = 200
                message = "open success"
            else:
                code = 201
                message = "open failed"
        else:
            code = 202
            message = "error charge hub info"
    else:
        code = 203
        message = "only admin can open"

    return jsonify({
        "code": code,
        "mode": mode,
        "hubid": str(hubID),
        "message":message
    })

# 改变充电模式和电量(用户)
@app.route("/api/change", methods=['POST'])
@jwt_required(optional=False)
def changeMode():
    current_userID = get_jwt_identity()

    args = request.get_data()
    args = json.loads(args)

    modeFlag = args["modeFlag"]
    degrees = args["degrees"]
    
    if charge_sys.set_degrees_and_mode(current_userID, modeFlag, degrees):
        code = 200
        msg = "success"
    else:
        code = 201
        msg = "failed"

    return jsonify({
        "code": code,
        "message": msg
    })

# 取消本次充电(用户)
@app.route("/api/cancel",methods=['GET'])
@jwt_required(optional=False)
def cancelCharge():
    current_userID = get_jwt_identity()
    if charge_sys.cancel_charge(current_userID):
        code = 200
        msg = "success"
    else:
        code = 201
        msg = "failed"

    return jsonify({
        "code": code,
        "message": msg
    })

# 获取系统当前充电系统状态的信息(用户)
@app.route("/api/getInfo", methods=['GET'])
@jwt_required(optional=False)
def getInfo():

    code = 200
    msg = "success"
    ret = charge_sys.get_info()

    return jsonify({
        "code":code,
        "message":msg,
        "data":ret
    })

# 获取当前订单信息(用户)
@app.route("/api/getOrderInfo",methods=['GET'])
@jwt_required(optional=False)
def get_order_info():
    current_userID = get_jwt_identity()
    data = charge_sys.get_order_by_userID(current_userID)
    if data != None:
        code = 200
        msg = "success"
    else:
        code = 201
        msg = "user not in charging"
    return jsonify({
        "code":code,
        "message":msg,
        "data": data
    })

# 获取当前车辆排队号(用户)
@app.route("/api/getLineNum",methods=['GET'])
@jwt_required(optional=False)
def get_line_num():
    current_userID = get_jwt_identity()
    
    data = charge_sys.get_line_number(userID = current_userID)
    if data != '':
        code = 200
        msg = "success"
    else:
        code = 201
        msg = "user not in waiting"

    return jsonify({
        "code":code,
        "message":msg,
        "data": data
    })

# 获取该模式下前车数量(用户)
@app.route("/api/getBeforeNum",methods=['GET'])
@jwt_required(optional=False)
def get_before_num():
    current_userID = get_jwt_identity()
    
    data = charge_sys.get_num_before_user(userID = current_userID)
    if data != -1:
        code = 200
        msg = "success"
    else:
        code = 201
        msg = "user not in waiting"

    return jsonify({
        "code":code,
        "message":msg,
        "data": data
    })

# 获取报表(管理员)
@app.route("/api/getReportForm",methods=['GET'])
@jwt_required(optional=False)
def get_report_form():
    current_userID = get_jwt_identity()
    
   
    if current_userID == app.config['ADMIN_ID']:
        code = 200
        msg = "success"
        data = charge_sys.get_report_form()
    else:
        code = 201
        msg = "only admin can get"
        ret = ''

    return jsonify({
        "code":code,
        "message":msg,
        "data": data
    })

# 获取充电桩状态信息(管理员)
@app.route("/api/getHubState",methods=['GET'])
@jwt_required(optional=False)
def get_hub_state():
    current_userID = get_jwt_identity()
    
   
    if current_userID == app.config['ADMIN_ID']:
        code = 200
        msg = "success"
        data = charge_sys.get_chargeHub_state()
    else:
        code = 201
        msg = "only admin can get"
        ret = ''

    return jsonify({
        "code":code,
        "message":msg,
        "data": data
    })

# 获取充电桩中等待服务车辆信息(管理员)
@app.route("/api/getChargingInfo",methods=['GET'])
@jwt_required(optional=False)
def get_charging_info():
    current_userID = get_jwt_identity()
    
   
    if current_userID == app.config['ADMIN_ID']:
        code = 200
        msg = "success"
        data = charge_sys.get_user_info_in_charge()
    else:
        code = 201
        msg = "only admin can get"
        ret = ''

    return jsonify({
        "code":code,
        "message":msg,
        "data": data
    })



if __name__ == "__main__":

    http_server = WSGIServer(('0.0.0.0', 80), app)
    http_server.serve_forever()