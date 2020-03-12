from ModFuncsClass_dict import *
import json
import numpy as np
import threading
import random

with open('C:\Users\AKAYIKCI\.virtualenvs\modbus\devices.json') as f:
    DevData = json.load(f)

with open('C:\Users\AKAYIKCI\.virtualenvs\json\details.json') as f:
    reg_data = json.load(f)




#____________________________________Device Listte yer alan ancak Reg_listte yer almayan cihazlar uyari olarak verilmeli.
#iki konfigurasyon dosyasi karsilastirilarak olmayan , eslesmeyen log olarak cikacak. 


#___________________________________________________________
#device islemleri blogu

DevList = list(np.zeros(len(DevData['devices']))) #creating a list which will contain number of device instance in  it

#___________________________________________________________
#device instance atamalari blogu

for x in xrange(0,len(DevData['devices'])):
	DevList[x] = device()

IpList = []
for x in xrange(0,len(DevData['devices'])):
	DevList[x].device = DevData['devices'][x]['type']
	DevList[x].ip = DevData['devices'][x]['ip'] 
	DevList[x].port = int(DevData['devices'][x]['port'])
	DevList[x].address = int(DevData['devices'][x]['mb'])
	DevList[x].delay = DevData['devices'][x]['interval']
	IpList.append(DevData['devices'][x]['ip'])

for x in xrange(0,len(DevList)):
	try:
		DevList[x].DevDict = reg_data[DevList[x].device]
	except KeyError:
		pass

#Create a dict which contains IP unique addresses for the unique connections.
IpList = list({x for x in IpList if IpList.count(x) > 1})

#__________________________________________________________
#In this section we are grouping the devices which are connecting over a gateway
GatewayList = []
for x in xrange(0,len(DevData['devices'])):
	if IpList[0] == DevList[x].ip:
		GatewayList.append(x)


GateDict = {}
for x in GatewayList:
	GateDict[x] =  DevList[x].delay

GateDictP = {}
for key, value in sorted(GateDict.items()):
    GateDictP.setdefault(value, []).append(key)

print(GateDictP)

#__________________________________________________________
#In this part we are controling the connections
	
def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def MbReadGate():

	conn, con_stat = Connection(IpList[0],502, 1)
	for x in xrange(0,len(DevData['devices'])):
		if IpList[0] == DevList[x].ip:

			DevList[x].conn, DevList[x].con_stat  = conn, con_stat	
			DevList[x].ReadDict()
			print(DevList[x].data)
			#DevList[5].JustClose()
		else:
			pass
	conn.close()
#timer = set_interval(MbReadGate, 10)




'''
for x in xrange(0,len(DevData['devices'])):
	for y in xrange(0,len(reg_data[DevList[x].device])):
		DevList[x].code = reg_data[DevList[x].device][y] * len(reg_data[DevList[x].device]['count'])


#___________________________________________________________
#details islemleri blogu
#print(DevList[0].device)
#print(reg_data[DevList[1].device])

DevTypes = reg_data.keys()
print(DevTypes)
print(reg_data[DevTypes[1]].keys())


'''