#coding=utf-8
import threading
import time
import serial
import random
import sys
import binascii

def hex2dec(hexa): #hex array
	tempa = []
	for i in hexa:
		tempa.append(int(binascii.hexlify(i).decode('utf-8'),16))
	return tempa

# with serial.Serial('COM4', 9600, timeout=1) as ser:
#     x = ser.write([0xB0,0xC0,0xA8,0x01,0x01,0x00,0x1A])

# ③ 读取当前电压
# 下发命令：B0 C0 A8 01 01 00 1A
# 回复数据：A0 00 E6 02 00 00 88
# 说明：回复电压数据为D1D2D3=00 E6 02，00 E6代表电压整数位，02代表电压小数位，电压小数位为1位，00 E6转化成十进制为230；02转化成十进制为2，所以当前电压值为230.2V。
# ④ 读取当前电流
# 下发命令：B1 C0 A8 01 01 00 1B
# 回复数据：A1 00 11 20 00 00 D2
# 说明：回复电流数据为D2D3=11 20，11代表电流整数位，20代表电流小数位，电流小数位为2位，11转化成十进制为17；20转化成十进制为32，所以当前电流值为17.32A。
# ⑤ 读取当前功率
# 下发命令：B2 C0 A8 01 01 00 1C
# 回复数据：A2 08 98 00 00 00 42
# 说明：回复功率数据为D1D2=08 98，08 98转化成十进制为2200，所以当前电压值为2200W。
# ⑥ 读取电量
# 下发命令：B3 C0 A8 01 01 00 1D
# 回复数据：A3 01 86 9F 00 00 C9
# 说明：回复电压数据为D1D2D3=01 86 9F，01 86 9F转化成十进制为99999,所以累计电量值为99999Wh。
ser = serial.Serial('COM5', 9600, timeout=1)
tempdat = [0xA0,0x00,0xE6,0x02,0x00,0x00,0x88]
while True:
	# with serial.Serial('COM2', 9600, timeout=1) as ser:
	s  = ser.read(7)
	read = hex2dec(s)
	if len(read) > 0:
		mark = read[0]
	else:
		continue
	# mark= 160
	# mark= 177
	# mark= 178
	# mark= 179
	# for mark in [0xA0,0xB1,0xB2,0xB3]:

		# print "mark=",mark#,type(mark),type(int(60)),str(mark == 160),str(mark == int(160))
	print "received data: ", mark
	sys.stdout.flush()

	if mark == 176 :
		tempdat[0] = 0xA0
		tempdat[2] = int(random.random() * 256)
		tempdat[3] = int(random.random() * 10)
	elif mark == 177 :
		tempdat[0] = 0xA1
		tempdat[2] = int(random.random() * 20)  #max current 20A
		tempdat[3] = int(random.random() * 10)
	elif mark == 178 :
		tempdat[0] = 0xA2
		tempdat[1] = int(random.random() * 20)  #max current 22KW
		tempdat[2] = int(random.random() * 256)
	elif mark == 179 :
		tempdat[0] = 0xA3
		tempdat[1] = 0
		tempdat[2] = int(random.random() * 256)  #max current 20A
		tempdat[3] = int(random.random() * 256)
	else:
		continue
	print tempdat
	sys.stdout.flush()
	ser.write(tempdat)

	# time.sleep(1)
