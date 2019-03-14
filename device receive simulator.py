import binascii
import serial
import threading
import time


def func():
	with serial.Serial('COM1', 9600) as seru:
		global t
		s = seru.read(7)
		hex_string =""
		for i in s:
			hex_string = binascii.hexlify(i).decode('utf-8')
			print(hex_string)
		with open("debug1.log", "a+") as f:
			f.write(hex_string)
		t = threading.Timer(2, func)
		t.start()

def hex2dec(hexa): #hex array
	tempa = []
	for i in hexa:
		tempa.append(int(binascii.hexlify(i).decode('utf-8'),16))
	return tempa

if __name__ == "__main__":
	# t = threading.Timer(2, func)
	# t.start()
	seru = serial.Serial('COM1', 9600)
	debuginfo = open("debuginfo.txt","w")
	while True:
			# with serial.Serial('COM1', 9600) as seru:
			s = seru.read(7)
			# dbgstr = ""
			# hex_string =""
			# hex_string = binascii.hexlify(s).decode('utf-8')
			# for i in s:
			# 	hexstr = binascii.hexlify(i).decode('utf-8')
			# 	dbgstr +=  "dbg: {}, dat10: {}, len: {}, type: {}\n ".format(hexstr,int(hexstr,16),len(i),type(i))
			tempa = hex2dec(s)
			# print hex_string
			debuginfo.write(str(tempa))
			time.sleep(1)
