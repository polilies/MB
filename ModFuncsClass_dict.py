from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ConnectionException as CError
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
from pymodbus.compat import iteritems
from collections import OrderedDict
import struct
import ctypes
import csv
import time


def Connection(ip,port,timeout):
    conn = ModbusTcpClient(host=ip, port=port, timeout=timeout)
    try:
        con_stat = conn.connect()
    except CError:
        #print(hata)
        con_stat = False
    return conn, con_stat

#cihazlar icin class
class device():
    
    
    def __init__(self, device='ION7650', code=[], reg=[], cnt=[], indexes=[], ip='127.0.0.1', port=502, timeout=1, hata='hata', address=255):
        self.device = device    #device'in tipi icin kullanilmakta. ION7650 vs.
        #self.whole = {}         #?
        self.ip = ip            #device ip bilgisi tasir
        self.port = port        #okuma yapilacak port 502 default
        self.timeout = timeout  #timeout suresi
        self.hata = hata        #hata tipi ya da cumlesi
        self.code = code        #details config file'dan INPUT ya da HOLDING gibi okuma ayrimlari icin
        self.reg = reg          # register verisini tutar
        self.cnt = cnt          # register okuma adedi
        self.indexes = indexes  # one shot read index addresses
        self.address = address  # modbus address
        self.con_stat = False   #connection status
        self.DevDict = {}
        #self.regs = []
        self.reg_type = "UINT16"
        self.delay = 3600
        self.old_data = []    
        self.data = []
        self.TempData = []  #okunan ancak indexlenmemis ilk veriyi tutmak icin. Ozellikle float verilerde.
        self.conn = 5
    
    def Connect(self):
        self.conn = ModbusTcpClient(host=self.ip, port=self.port, timeout=self.timeout)
        try:
            self.con_stat = self.conn.connect()
        except CError:
            print(self.hata)
            self.con_stat = False

    


    def read_input_U16(self, x):  #for the single reads
        if self.conn.is_socket_open(self):
            try:
                self.rr = self.conn.read_input_registers(self.reg[x], self.cnt[x], unit=self.address)
            except CError:
                print "no connection try again" #CSVWrite("connection_logs.csv", Error=CError.message)
            else:
                if hasattr(self.rr, 'registers'):
                    self.data.append(self.rr.registers[0])
                    
                else:
                    print "possible close_wait situation"             
        else:
            print "No active connection"

    def read_input_S16(self, x): # for the single reads
        if self.conn.is_socket_open():            
            try:
                self.rr = self.conn.read_input_registers(self.reg[x], self.cnt[x], unit=self.address)
            except CError:
                print "no connection try again"#CSVWrite("connection_logs.csv", Error=CError.message)
            else:
                if hasattr(self.rr, 'registers'):
                    if self.rr.registers[0] > 32768:
                        self.data.append(ctypes.c_int((self.rr.registers[0] ^ 0XFFFF) * -1).value)
                    else:
                        self.data.append(self.rr.registers[0])                        
                else:
                    print "possible close_wait situation"             
        else:
            print "No active connection"    

    def read_holding_floats(self, reg,cnt,index): # for the multi reads x degeri read() fonksiyonundaki 
        if self.conn.is_socket_open():
            try:
                self.TempData = []
                self.rr = self.conn.read_holding_registers(reg, cnt * 2, unit=self.address)
                if hasattr(self.rr, 'registers'):
                    self.decoder = BinaryPayloadDecoder.fromRegisters(self.rr.registers, Endian.Big, wordorder=Endian.Big)
                    for a in range(0, cnt):            
                        self.TempData.append(round(self.decoder.decode_32bit_float(), 2))
                    self.data.append([self.TempData[i] for i in index])
                else:
                    self.TempData = []
                    self.rr = self.conn.read_holding_registers(reg, cnt * 2, unit=self.address)
                    if hasattr(self.rr, 'registers'):
                        self.decoder = BinaryPayloadDecoder.fromRegisters(self.rr.registers, Endian.Big, wordorder=Endian.Big)
                        for a in range(0, cnt):            
                            self.TempData.append(round(self.decoder.decode_32bit_float(), 2))
                        self.data.append([self.TempData[i] for i in index]) #a list comprehantion.we may use even an if clause.
            except CError:
                print "no connection try again"#CSVWrite("connection_logs.csv", Er


                #error=CError.message)
            else:      
                pass
        else:
            print "No active connection"                


    #def JustConnect(self):
    #    self.conn, self.con_stat = Connection(self.ip, self.port, self.timeout, self.hata)
    
    def read(self):
        self.data.clear()  #cihazdan okunan toplam veri her okumada sifirlanir.
        for x in range(0,len(self.code)):
            time.sleep(self.delay)
            if self.code[x] == "INPUT":
                # Read input unsigned registers    
                if self.reg_type[x] == "UINT16":
                    #self.read_input_U16(x)
                    pass                    
                # Read input registers signed values
                elif self.reg_type[x] == "INT16":                        
                    pass
                # multi float reading aproach from payload        Text
                    pass
            elif self.code[x] == "HOLDING":

                if self.reg_type[x] == "UINT16":
                    #self.read_input_U16(x)                    
                    pass
                # Read input registers signed values
                elif self.reg_type[x] == "INT16":                        
                    pass
                # multi float reading aproach from payload        
                elif self.reg_type[x] == "FLOATS":                
                    self.read_holding_floats(x)
    
#_________________________________Dictionary Version
    def ReadDict(self):
        if self.conn.is_socket_open():
            self.data = []  #cihazdan okunan toplam veri her okumada sifirlanir.
            for x in self.DevDict.keys():
                if x == 'HOLDING':
                    for y in self.DevDict[x].keys():
                        if y == 'UINT16':
                            pass
                        elif y == "INT16":                        
                            pass
                        elif y == "FLOAT":
                            for z in xrange(0,len(self.DevDict[x][y]['count'])):
                                self.read_holding_floats(self.DevDict[x][y]['start_reg'][z], self.DevDict[x][y]['count'][z], self.DevDict[x][y]['indexes'][z])
                else:
                    pass
        else:
            print "No active connection"

    def JustClose(self):
        self.conn.close()

    def socket(self):
        return self.conn.is_socket_open()        


'''        
    def read(self):
        for a in self.whole:
            if a == "INPUT"
                for x in self.whole[a]: 
                    # Read input unsigned registers    
                    if self.reg_type == "UINT16":
                        
                    # Read input registers signed values
                    elif self.reg_type == "INT16":    
                        

                    # multi float reading aproach from payload        
                    elif self.reg_type == "FLOATS":    
                    
            elif a == "HOLDING"
                for y in self.whole[a]:

'''


#########################################################################################
# 1)Seperator cihaz adina gore gidip ilgili register listesini edinir
# 2)Liste icindeki verileri oncelikle register tipine gore siralar.Dicitionary sorting ornegin Float olanlar ard arda gelecek sekilde
# 3)Her register grubu kendi icinde buyukten kucuge siralanir.
# 4)Her grup cihazdan talep edilebilecek en fazla register adedine gore parcalara ayrilir.
# separator buraya kadar isi halledip bir json file olusturur. Alttaki verileri icerir veri bloklari seklinde.
    #index
    #count
    #start_reg
    #reg_type
# 5)Her alt grup icin ilk ve son reg arasindaki tum registerlarida istenmese dahi kapsayacak mahiyette bir sanal grup olusturulur.
# 6)Gercek grup registerlari sanal grup registerlarina gore indexlenir. Cunki sanal grup elemani adedince veri talep edilecektir. Donen veri icinden gercekte istenen veriler bu indexe gore sagaltilmalidir.
# 7)Veriler bir onceki asamada olusturulmus olan indexe gore kullanilmak uzere bir listede tutulur.  
''' 
    def seperator(register_link):
        dev_list = []
        with open(register_link) as f:
            dev_info = json.load(f)

    # print(data['colors']['color'])
        for item in dev_info['device']:
            dev_list.append(tm(item['enable']))
'''

#############################################################################################



