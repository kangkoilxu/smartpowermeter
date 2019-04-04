#coding=utf-8
# flask_sqlalchemy.py
import datetime
import json
from flask import Flask,render_template,request
from flask_sqlalchemy import *
import threading
import time
import serial
import binascii
import sys #fosys.stdout.flush()  #
import paho.mqtt.publish as publish
from websocket_server import WebsocketServer

serialPort = "/dev/ttyUSB0"
serialBaudrate = 9600
serverPort = 8000

wsport = 9002
wskey = "Fetch One"

app = Flask(__name__)
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
    #return [ int(binascii.hexlify(i).decode('utf-8'),16) for i in hexa]

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
        try:
            ser  = serial.Serial(serialPort,serialBaudrate, timeout=1)
        # with serial.Serial(serialPort,serialBaudrate, timeout=1) as ser:
            x = ser.write(cmd_f_vol)
            vol_r_fmt = hex2dec(ser.read(7))          # read up to ten bytes (timeout)
            time.sleep(0.01)
            x = ser.write(cmd_f_cur)
            cur_r_fmt = hex2dec(ser.read(7))        # read up to ten bytes (timeout)

            time.sleep(0.01)
            x = ser.write(cmd_f_pow)
            pow_r_fmt = hex2dec(ser.read(7))        # read up to ten bytes (timeout)

            time.sleep(0.01)
            x = ser.write(cmd_f_eng)
            eng_r_fmt = hex2dec(ser.read(7))
        except :
            pass
        # pt("Fetched five data!")
        try:
            val  = float(vol_r_fmt[1] *256  + vol_r_fmt[2] + 0.1*vol_r_fmt[3] )
            val2 = float(cur_r_fmt[2] + 0.01*cur_r_fmt[3] )
            val3 = float(pow_r_fmt[1] *256  + pow_r_fmt[2])
            val4 = float(eng_r_fmt[1] *65536 + eng_r_fmt[2]*256 + eng_r_fmt[3])
            pt(str(val))#,str(val2),str(val3),str(val4))
            json_val = json.dumps( {"kwh": val4, "voltage": val, "current": val2, "power": val3 } )
            # send to mqtt server
            publish.single("sensor/sartpowermeter/1", str(json_val), hostname="broker.hivemq.com")
            #save to database
            db.create_all()
            now = datetime.datetime.now()
            #    def __init__(self,dt,kwh,voltage,freq,current,pfactor,power):
            pd = Power(now,val4,val,50.0,val2,1.0,val3)
            db.session.add(pd)
            db.session.commit()
        except:
            pass
        time.sleep(1)
# ajax
@app.route('/power')
def cpw():
    nowstr = ""
    pwdict = {}
    data = db.session.query(Power).order_by(Power.id.desc()).first()
    nowstr = datetime.datetime.strftime(data.dt,'%Y-%m-%d %H:%M:%S')
    pwdict.update( {"date":nowstr,"voltage":data.voltage,"current":data.current,"power":data.power,"energy":data.kwh } )
    return json.dumps(pwdict)

@app.route('/')
def index():
    return render_template('main.html')

# Called for every client connecting (after handshake)
def new_client(client, server):
	# print("New client connected and was given id %d" % client['id'])
	# server.send_message_to_all("Hey all, a new client has joined us")
    pass
# Called for every client disconnecting
def client_left(client, server):
	# print("Client(%d) disconnected" % client['id'])
    pass
# Called when a client sends a message
def message_received(client, server, message):
	if len(message) > 200:
		message = message[:200]+'..'
        if message == wskey :
            nowstr = ""
            pwdict = {}
            data = db.session.query(Power).order_by(Power.id.desc()).first()
            nowstr = datetime.datetime.strftime(data.dt,'%Y-%m-%d %H:%M:%S')
            server.send_message( client,  json.dumps( {"date":nowstr,"voltage":data.voltage,"current":data.current,"power":data.power,"energy":data.kwh } ))
        else :
            print ( "* Wrong Key!")
	# print("Client(%d) said: %s" % (client['id'], message))

def launch_ws():
    server = WebsocketServer(wsport)
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    server.run_forever()

# 运行
if __name__ == '__main__':
    addpm2dbt = threading.Thread(target = addpm2dbf) #
    addpm2dbt.setDaemon(True)
    addpm2dbt.start()
    wsthread = threading.Thread(target= launch_ws)
    wsthread.setDaemon = True
    wsthread.start()
    app.debug = True
    app.run('127.0.0.1', serverPort)
