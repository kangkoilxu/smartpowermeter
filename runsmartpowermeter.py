#coding=utf-8
# flask_sqlalchemy.py
import datetime
import json
from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
import threading
import time
import serial
import binascii
import sys #fosys.stdout.flush()  #

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///c:\One Driver-kkgg\OneDrive\kangx_sf\sqlite_db_pm\pmdb.db'
app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///pmdb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
# 定义ORM
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=False)
    def __init__(self, name, email):
        self.name = name
        self.email = email
    def __repr__(self):
        return '<User %r>' % self.name

class PM_data(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    dt = db.Column(db.DateTime,unique=True)
    val = db.Column(db.Float)
    dtp = db.Column(db.String(32))
    def __init__(self,dt,dtp,val):
        self.dt = dt
        self.dtp = dtp
        self.val = val

class Power(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    dt = db.Column(db.DateTime,unique=True)
    kwh = db.Column(db.Float)
    voltage = db.Column(db.Float)
    freq = db.Column(db.Float)
    current = db.Column(db.Float)
    pfactor = db.Column(db.Float)
    power = db.Column(db.Float)
    def __init__(self,dt,kwh,voltage,freq,current,pfactor,power):
        self.dt = dt
        self.kwh = kwh
        self.voltage = voltage
        self.freq = freq
        self.current = current
        self.pfactor = pfactor
        self.power = power

@app.route('/addpower/<float:val>')
def addpm(val,val2,val3,val4):
    now = datetime.datetime.now()
    db.create_all()
    pd = Power(now,val,val2,50.0,val3,1.0,val4)
    db.session.add(pd)
    db.session.commit()
    return "OK!"

def pt(txt,c = "92",i = 0):
    print " "*i*4 + "\033["+str(c)+"m"+str(txt)+"\033[0m"
    sys.stdout.flush()

def hex2dec(hexa): #hex array
	tempa = []
	for i in hexa:
		tempa.append(int(binascii.hexlify(i).decode('utf-8'),16))
	return tempa
    
# 更新数据库函数
def addpm2dbf(val=0,val2=0,val3=0,val4=0):
    # cmd_f_pal = [0xB5, 0xC0, 0xA8, 0x01, 0x01, 0x14, 0x33]
    cmd_f_vol = [0xB0,0xC0,0xA8,0x01,0x01,0x00,0x1A]
    cmd_f_cur = [0xB1,0xC0,0xA8,0x01,0x01,0x00,0x1B]
    cmd_f_pow = [0xB2,0xC0,0xA8,0x01,0x01,0x00,0x1C]
    cmd_f_eng = [0xB3,0xC0,0xA8,0x01,0x01,0x00,0x1D]
    # vol_r_fmt = [0xA0, 0x00, 0xE6, 0x02, 0x00, 0x00, 0x88]
    vol_r_fmt = []
    cur_r_fmt = []
    pow_r_fmt = []
    eng_r_fmt = []
    while True:
        with serial.Serial('COM4', 9600, timeout=2) as ser:
            x = ser.write(cmd_f_vol)
            vol_r_fmt = hex2dec(ser.read(7))          # read up to ten bytes (timeout)
            x = ser.write(cmd_f_cur)
            cur_r_fmt = hex2dec(ser.read(7))        # read up to ten bytes (timeout)
            x = ser.write(cmd_f_pow)
            pow_r_fmt = hex2dec(ser.read(7))        # read up to ten bytes (timeout)
            x = ser.write(cmd_f_eng)
            eng_r_fmt = hex2dec(ser.read(7))
        pt("Fetch one data!")
        try:
            val  = float(vol_r_fmt[1] *256  + vol_r_fmt[2] + 0.1*vol_r_fmt[3] )
            val2 = float(cur_r_fmt[2] + 0.1*cur_r_fmt[3] )
            val3 = float(pow_r_fmt[1] *256  + pow_r_fmt[2])
            val4 = float(eng_r_fmt[1] *65536 + eng_r_fmt[2]*256 + eng_r_fmt[3])
            pt(str(val))

            db.create_all()
            now = datetime.datetime.now()
            pd = Power(now,val4,val,50.0,val2,1.0,val3)
            db.session.add(pd)
            db.session.commit()
        except:
            pass
        time.sleep(1)
# 查询
@app.route('/power')
def cpw():
    nowstr = ""
    pwdict = {}
    data = db.session.query(Power).order_by(Power.id.desc()).first()
    nowstr = datetime.datetime.strftime(data.dt,'%Y-%m-%d %H:%M:%S')
    pwdict.update( {"date":nowstr,"voltage":data.voltage,"current":data.current,"power":data.power,"energy":data.kwh } )
    return json.dumps(pwdict)
# 查询
@app.route('/user')
def users():
    users = User.query.all()
    return "<br>".join(["{0}: {1}".format(user.name, user.email) for user in users])
# 查询
@app.route('/user/<int:id>')
def user(id):
    user = User.query.filter_by(id=id).one()
    return "{0}: {1}".format(user.name, user.email)

@app.route('/add/<string:name>')
def add(name):
    db.create_all()
    admin = User(name, name+'@example.com')
    db.session.add(admin)
    db.session.commit()
    return "success!"
@app.route('/')
def index():
    return render_template('main.html')
# 运行
if __name__ == '__main__':
    addpm2dbt = threading.Thread(target = addpm2dbf) #, args=(1.1,2.2,3.3,4.4)
    addpm2dbt.setDaemon(True)#设置为后台线程，这里默认是False，设置为True之后则主线程不用等待子线程
    addpm2dbt.start()#开启线程
    app.debug = True
    app.run('127.0.0.1', 5000)
