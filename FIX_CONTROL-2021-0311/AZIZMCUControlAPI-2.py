#-*-coding:utf-8-*-
'''
Author: bojay
Ver 1.0
2019/07/18
'''

import serial
from serial import *
import serial.tools.list_ports
import time
import binascii
import struct
import inspect
import platform

class MCUControl:

    delay = 0.2
    strErrorMessage = "ok"
    myMCUSerialPort = None #MCU port
    myThermalSerialPort = None #Thermal Sensor port
    myAngleSerialPort = None #Angle sensor port
    myMCUSerialPortName = ""
    myThermalSerialPortName = ""
    myAngleSerialPortName = ""
    myTemperatur_serial_isOpen = False
    myAngle_serial_isOpen = False
    myMCU_serial_isOpen = False

    SwitchMCU = 0
    SwitchThermal = 1
    SwitchAngle = 2

    MCU = 0
    Thermal = 1
    AngleDevice = 2

    # Limit Stop Signal
    # Limit_Stop_Flag = False
    # Exceed_limit_flag = False


    # For Axis
    ReadIOOneCommand = "readio_one:x00\r\n"
    ServoMotor = 0
    StepMotor = 1

    #for thermal
    GetChannelOne = "023031303030303130314330303030303030303030310340"
    GetChannelTwo = "023032303030303130314330303030303030303030310343"
    GetChannelThree= "023033303030303130314330303030303030303030310342"
    GetChannelFour = "023034303030303130314330303030303030303030310345"
    GetChannelFive = "023035303030303130314330303030303030303030310344"
    GetChannelSix = "023036303030303130314330303030303030303030310347"
    GetChannelSeven = "023037303030303130314330303030303030303030310346"
    LCD1 = 0
    LCD2 = 1
    LCD3 = 2
    LCD4 = 3
    LCD5 = 4
    LCD6 = 5
    LCD7 = 6

    #read angle
    pullData = [0x68, 0x04, 0x00, 0x04, 0x08]

    #set home
    AbsoluteHome = 0
    RelativeHome = 1

    #get home model
    GetHomeModel = [0x86, 0x04, 0x00, 0x0D, 0x11]

    #set baud
    SetBaud_9600 = [0x68, 0x05, 0x00, 0x0B, 0x02, 0x13] #defaul
    SetBaud_19200 = [0x68, 0x05, 0x00, 0x0B, 0x03, 0x13]
    SetBaud_38400 = [0x68, 0x05, 0x00, 0x0B, 0x04, 0x13]
    SetBaud_115200 = [0x68, 0x05, 0x00, 0x0b, 0x05, 0x13]

    #Filtering parameters
    SampleRate_100 = [0x68, 0x05, 0x00, 0x17, 0x01, 0x1D]
    SampleRate_30 = [0x68, 0x05, 0x00, 0x17, 0x02, 0x1D] #default
    SampleRate_5 = [0x68, 0x05, 0x00, 0x17, 0x03, 0x1D]

    Axis_X = 0
    Axis_Y = 1
    Axis_Z = 2

    Out = 3
    In = 4

    LightCurtainOn = 5
    LightCurtainOff = 6

    USBLock = 7
    USBUnlock = 8

    DutLock = 9
    DutUnlock = 10

    DoorClose = 11
    DoorOpen = 12
    #project name
    PIR_NQ = "NQ"

    def __init__(self,station):
        self.StationName = station
        self.Interpreter = int(platform.python_version()[0])
        self.current_angle = 0
    # **************************************************************************************#

    # **************************************************************************************#
    ################################ for Customer ###########################################
    def OpenSerial(self, switch=''):
        try:
            port_list = list ( serial.tools.list_ports.comports () )
            if len ( port_list ) < 1:
                self.strErrorMessage = "There is no serial port"
                return -1
            if switch == self.SwitchThermal:
                for i in range(0, len(port_list), 1):
                    if port_list[i].device != self.myAngleSerialPortName and port_list[i].device != self.myMCUSerialPortName:
                        print ('SwitchThermal list port: i = {},port = {}'.format(i,port_list[i].device))
                        self.myThermalSerialPort = serial.Serial(port=port_list[i].device,
                                                            timeout=0.05,
                                                            baudrate=57600,
                                                            parity=PARITY_EVEN,
                                                            stopbits=2,
                                                            bytesize=7)
                        # self.myThermalSerialPort = serial.Serial("/dev/ttyUSB0",
                        #                                          timeout=0.05,
                        #                                          baudrate=57600,
                        #                                          parity=PARITY_EVEN,
                        #                                          stopbits=2,
                        #                                          bytesize=7)

                        if self.myThermalSerialPort.is_open:
                            # ret = self.AutoChoose(switch)
                            # if ret != 0:
                            #     self.myThermalSerialPort.close()
                            # else:
                            #     self.myThermalSerialPortName = port_list[i].device
                            self.myTemperatur_serial_isOpen = True
                            return 0
                self.strErrorMessage = "Did not find suitable SwitchAngle serial port"
                return -1
            elif switch == self.SwitchMCU:
                for i in range(0, len(port_list), 1):
                    if port_list[i].device != self.myThermalSerialPortName and port_list[i].device != self.myAngleSerialPortName:
                        print ('SwitchMCU list port: i = {},port = {}'.format(i,port_list[i].device))
                        self.myMCUSerialPort = serial.Serial(port=port_list[i].device,
                                                         timeout=0.1,
                                                         baudrate=115200,
                                                         parity=PARITY_NONE,
                                                         stopbits=1,
                                                         bytesize=8)
                        if self.myMCUSerialPort.is_open:
                            ret = self.AutoChoose(switch)
                            if ret != 0:
                                self.myMCUSerialPort.close()
                            else:
                                self.myMCUSerialPortName = port_list[i].device
                                self.myMCU_serial_isOpen = True
                                return 0
                self.strErrorMessage = "Did not find suitable SwitchMCU serial port"
                return -1
            elif switch == self.SwitchAngle:
                for i in range(0, len(port_list), 1):
                    if port_list[i].device != self.myMCUSerialPortName and port_list[i].device != self.myThermalSerialPortName:
                        print ('SwitchAngle list port: i = {},port = {}'.format(i,port_list[i].device))
                        self.myAngleSerialPort = serial.Serial(port=port_list[i].device,
                                                         timeout=0.1,
                                                         baudrate=115200,
                                                         parity=PARITY_NONE,
                                                         stopbits=1,
                                                         bytesize=8)
                        if self.myAngleSerialPort.is_open:
                            ret = self.AutoChoose(switch)
                            if ret != 0:
                                self.myAngleSerialPort.close()
                            else:
                                self.myAngleSerialPortName = port_list[i].device
                                self.myAngle_serial_isOpen = True
                                return 0
                self.strErrorMessage = "Did not find suitable SwitchAngle serial port"
                return -1
            return -1
        except Exception as e:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1
    # **************************************************************************************#



    # **************************************************************************************#
    # auto choose the serial port
    def AutoChoose(self,switch):
        try:
            if switch == self.SwitchThermal:
                self.myThermalSerialPort.write (binascii.unhexlify(self.GetChannelOne))
                time.sleep(self.delay)
                read_data = self.myThermalSerialPort.read_all()
                hex_data = binascii.hexlify(read_data)
                if self.Interpreter == 3:
                    hex_data = hex_data.decode()
                # print struct.unpack('!f',(hex_data[10:14] + hex_data[6:10]).decode('hex'))[0]
                if hex_data[0:6] == "023031" and len(read_data) == 25:
                    return 0
                else:
                    return -1
            elif switch == self.SwitchMCU:
                ReadIOOneComman = "readio_one:x0\r\n"
                if self.Interpreter == 3:
                    ReadIOOneComman = ReadIOOneComman.encode('utf-8')
                self.myMCUSerialPort.write(ReadIOOneComman)
                time.sleep(self.delay)
                read_data = self.myMCUSerialPort.read_all()
                if self.Interpreter == 3:
                    read_data = read_data.decode()
                if "X0=" in read_data:
                    return 0
                else:
                    return -1
            elif switch == self.SwitchAngle:
                self.myAngleSerialPort.write(self.pullData)
                time.sleep(self.delay)
                read_data = self.myAngleSerialPort.read_all()
                hex_data = binascii.hexlify(read_data)
                if self.Interpreter == 3:
                    hex_data = hex_data.decode()
                if hex_data[0:2] == "68" and len(read_data) == 14:
                    return 0
                else:
                    return -1
        except Exception as e:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3],e)
            print(self.strErrorMessage)
            return -1
    # ********************************************************************#

    # ********************************************************************#
    #close serial port
    def CloseSerial(self,switch):
        try:
            if switch == self.SwitchThermal:
                if  self.myThermalSerialPort.is_open:
                    self.myThermalSerialPort.close()
                    self.myTemperatur_serial_isOpen = False
            elif switch == self.SwitchAngle:
                if self.myAngleSerialPort.is_open:
                    self.myAngleSerialPort.close()
                    self.myAngle_serial_isOpen = False
            elif switch == self.SwitchMCU:
                if self.myMCUSerialPort.is_open:
                    self.myMCUSerialPort.close()
                    self.myMCU_serial_isOpen = False
            return 0
        except Exception as e:
            self.strErrorMessage = "CloseSerial except fail"
            return -1
    # ********************************************************************#

    # ********************************************************************#
    def SetSpeed(self,value):
        try:
            if self.StationName == self.PIR_NQ:
                if str(type(value)) != "<type 'str'>":
                    # value = int(round(value * 200, 2))
                    command = "r_axis_speed:"+str(value)+"\r\n"
                else:
                    self.strErrorMessage = "input parameters type fail"
                    return -1
                if self.Interpreter == 3:
                    command = command.encode('utf-8')

                self.myMCUSerialPort.write(command)
                time.sleep(self.delay)
                readstring = self.myMCUSerialPort.read(18)
                if self.Interpreter == 3:
                    readstring = readstring.decode()

                # print len(readstring)
                if "Receive Data OK." in readstring:
                    return 0
                else:
                    self.strErrorMessage = "SetSpeed write command fail"
                    return -1
        except:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1
    # ********************************************************************#

    # ********************************************************************#
    #get speed
    def GetSpeed(self,ofWhatAxis = ''):
        try:
            if self.StationName == self.PIR_NQ:
                command = 'readsaveinfo:\r\n'
                if self.Interpreter == 3:
                    command = command.encode('utf-8')

                self.myMCUSerialPort.write(command)
                time.sleep(self.delay)
                ret = self.myMCUSerialPort.read_all()
                if self.Interpreter == 3:
                    ret = ret.decode()

                if 'R_Axis_Speed' in ret:
                    info = ret.split('\n')[0]
                    index = info.find(':')
                    return float(info[index + 1:])/200.0
                else:
                    return -1
        except Exception as e:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1
    # ********************************************************************#

    # ********************************************************************#
    def SignalReSet(self,timeout = 30):
        try:
            #home position
            if self.ReadOneIOState('x',5) == 0:
                command = "test_reset\r\n"
                if self.Interpreter == 3:
                    command = command.encode('utf-8')
                self.myMCUSerialPort.write(command)
                # ret = self.SetAngleHome()
                # if ret != 0:
                #     self.ShowErroeMessage('set zero for angle fail')
                #     return -1
                time.sleep(self.delay)
                return 0
            #min
            if self.ReadOneIOState('x',6) == 0:
                command = 'r_axis_go_home_ccw\r\n'

                if self.Interpreter == 3:
                    command = command.encode('utf-8')

                self.myMCUSerialPort.write(command)
                time.sleep(self.delay)
                ret = self.myMCUSerialPort.read_all()
                if self.Interpreter == 3:
                    ret = ret.decode()

                if 'R_Axis_Motor_GO_Home_CCW' in ret:
                    mytimeout = 0
                    while True:
                        if mytimeout > timeout:
                            self.strErrorMessage = 'SignalReSet timeout'
                            return -1
                        elif self.ReadOneIOState('x',33) == 1:
                            command = "test_reset\r\n"
                            if self.Interpreter == 3:
                                command = command.encode('utf-8')
                            self.myMCUSerialPort.write(command)
                            # ret = self.SetAngleHome()
                            # if ret != 0:
                            #     self.ShowErroeMessage('set zero for angle fail')
                            #     return -1
                            time.sleep(self.delay)
                            return 0
                        else:
                            mytimeout = mytimeout + 0.05
                            time.sleep(0.05)
                            continue
                else:
                    self.strErrorMessage = 'SignalReSet from min go home fail'
                    return -1
            #max
            if self.ReadOneIOState('x',7) == 0:
                command = 'r_axis_go_home_cw\r\n'
                if self.Interpreter == 3:
                    command = command.encode('utf-8')
                self.myMCUSerialPort.write(command)
                time.sleep(self.delay)
                ret = self.myMCUSerialPort.read_all()
                if self.Interpreter == 3:
                    ret = ret.decode()
                if 'R_Axis_Motor_GO_Home_CW' in ret:
                    mytimeout = 0
                    while True:
                        if mytimeout > timeout:
                            self.strErrorMessage = 'SignalReSet timeout'
                            return -1
                        elif self.ReadOneIOState('x', 33) == 1:
                            command = "test_reset\r\n"
                            if self.Interpreter == 3:
                                command = command.encode('utf-8')
                            self.myMCUSerialPort.write(command)
                            time.sleep(self.delay)
                            # ret = self.SetAngleHome()
                            # if ret != 0:
                            #     self.ShowErroeMessage('set zero for angle fail')
                            #     return -1
                            return 0
                        else:
                            mytimeout = mytimeout + 0.05
                            time.sleep(0.05)
                            continue
                else:
                    self.strErrorMessage = 'SignalReSet from max go home fail'
                    return -1

            # other position
            command1 = 'r_axis_go_min\r\n'
            if self.Interpreter == 3:                 
                command1 = command1.encode('utf-8')

            self.myMCUSerialPort.write(command1)
            time.sleep(self.delay)
            ret = self.myMCUSerialPort.read_all()
            if self.Interpreter == 3:
                ret = ret.decode()
            if 'Motor_R_GO_Min' in ret:
                mytimeout = 0
                while True:
                    if mytimeout > timeout:
                        self.strErrorMessage = 'SignalReSet timeout'
                        return -1
                    elif self.ReadOneIOState('x', 33) == 1:
                        mytimeout = 0
                        while self.ReadOneIOState('x', 6) != 0:
                            command1 = 'r_axis_go_min\r\n'
                            if self.Interpreter == 3:
                                command1 = command1.encode('utf-8')
                            self.myMCUSerialPort.write(command1)
                            time.sleep(self.delay)
                            ret = self.myMCUSerialPort.read_all()
                            if 'Motor_R_GO_Min' in ret:
                                mytimeout = 0
                                while True:
                                    if mytimeout > timeout:
                                        self.strErrorMessage = 'SignalReSet timeout'
                                        return -1
                                    elif self.ReadOneIOState('x', 33) == 1:
                                        break
                                    else:
                                        mytimeout = mytimeout + 0.05
                                        time.sleep(0.05)
                                        continue
                        break
                    else:
                        mytimeout = mytimeout + 0.05
                        time.sleep(0.05)
                        continue
                # self.myMCUSerialPort.write('readio_one:x06')
                # time.sleep(self.delay)
                # signal = self.myMCUSerialPort.read_all()
                # if 'X6=0' in signal:
                if self.ReadOneIOState('x', 6) == 0:
                    time.sleep(1)
                    command2 = 'r_axis_go_home_ccw\r\n'
                    if self.Interpreter == 3:
                        command2 = command2.encode('utf-8')
                    self.myMCUSerialPort.write(command2)
                    time.sleep(self.delay)
                    ret = self.myMCUSerialPort.read_all()
                    if self.Interpreter == 3:
                        ret = ret.decode()
                    if 'R_Axis_Motor_GO_Home_CCW' in ret:
                        mytimeout = 0
                        while True:
                            if mytimeout > timeout:
                                self.strErrorMessage = 'SignalReSet timeout'
                                return -1
                            elif self.ReadOneIOState('x', 33) == 1:
                                command2 = "test_reset\r\n"
                                if self.Interpreter == 3:
                                    command2 = command2.encode('utf-8')
                                self.myMCUSerialPort.write(command2)
                                time.sleep(self.delay)
                                # ret = self.SetAngleHome()
                                # if ret != 0:
                                #     self.ShowErroeMessage('set zero for angle fail')
                                #     return -1
                                break
                            else:
                                mytimeout = mytimeout + 0.05
                                time.sleep(0.05)
                                continue
                    # self.myMCUSerialPort.write('readio_one:x05')
                    # time.sleep(self.delay)
                    # signal = self.myMCUSerialPort.read_all()
                    # if 'X6=0' in signal:
                    if self.ReadOneIOState('x', 5) == 0:
                        return 0
                    else:
                        return -1
                else:
                    self.strErrorMessage = 'SignalReSet timeout'
                    return -1
            else:
                self.strErrorMessage = "SignalReset go min fail"
                return -1
        except Exception as e:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1
    # ********************************************************************#

    # ********************************************************************#
    def MoveToCoordinates(self, value, speed = 60,timeout = 10):
        try:
            if self.StationName == self.PIR_NQ:
                if speed != 60 and speed != '':
                    ret = self.SetSpeed(speed)
                    if ret != 0:
                        self.strErrorMessage = "MoveToCoordinates set speed fail"
                        return -1
                elif speed == 60:
                    ret = self.SetSpeed(60)
                    if ret != 0:
                        self.strErrorMessage = "MoveToCoordinates set speed fail"
                        return -1
                if value > 90:
                    value = 90
                if value < -90:
                    value = -90
                if str(type(value)) != "<type 'str'>":
                    value = int(round(value * 200, 2))
                    command = "r_axis_move_to:" + str(value) + "\r\n"
                else:
                    self.strErrorMessage = "input parameters type fail"
                    return -1

                if self.Interpreter == 3:
                    command = command.encode('utf-8')

                self.myMCUSerialPort.write(command)
                time.sleep(self.delay)
                readstring = self.myMCUSerialPort.read_all()
                if self.Interpreter == 3:
                    readstring = readstring.decode('gbk')

                if "_Axis_Motor_Moving" in readstring:
                    mytimeout = 0
                    while True:
                        if mytimeout > timeout:
                            self.strErrorMessage = 'MoveToCoordinates timeout'
                            return -1
                        elif self.ReadOneIOState('x',33) == 1:
                            if self.ReadOneIOState('x',6) == 0 or self.ReadOneIOState('x',7) == 0:
                                self.strErrorMessage = 'MoveToCoordinates out of limit,need to reset'
                                return -1
                            else:
                                return 0
                        else:
                            mytimeout = mytimeout + 0.05
                            time.sleep(0.05)
                            continue
                else:
                    self.strErrorMessage = "MoveToCoordinates write command fail"
                    return -1
        except Exception as e:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1
    # ********************************************************************#

    # ********************************************************************#
    def MoveStep(self,value, speed = 60, ofWhatAxis = "",timeout = 10):
        try:
            if self.StationName == self.PIR_NQ:
                if speed != 60 and speed != '':
                    ret = self.SetSpeed(speed)
                    if ret != 0:
                        self.strErrorMessage = "MoveToCoordinates set speed fail"
                        return -1
                elif speed == 60:
                    ret = self.SetSpeed(60)
                    if ret != 0:
                        self.strErrorMessage = "MoveToCoordinates set speed fail"
                        return -1
                if str(type(value)) != "<class 'str'>":
                    value = int(round(value * 200, 2))
                    command = "r_axis_rel_move_to:"+str(value)+"\r\n"
                else:
                    self.strErrorMessage = "input parameters type fail"
                    return -1
                if self.Interpreter == 3:
                    command = command.encode('utf-8')

                self.myMCUSerialPort.write(command)
                time.sleep(self.delay)
                readstring = self.myMCUSerialPort.read_all()

                if self.Interpreter == 3:
                    readstring = readstring.decode('gbk')

                if "R_Axis_Motor_Moving" in readstring:
                    mytimeout = 0
                    while True:
                        if mytimeout > timeout:
                            self.strErrorMessage = 'MoveStep timeout'
                            return -1
                        elif self.ReadOneIOState('x',33) == 1:
                            if self.ReadOneIOState('x',6) == 0 or self.ReadOneIOState('x',7) == 0:
                                self.strErrorMessage = 'MoveToCoordinates out of limit,need to reset'
                                return -1
                            else:
                                return 0
                        else:
                            mytimeout = mytimeout + 0.05
                            time.sleep(0.05)
                            continue
                else:
                    self.strErrorMessage = "MoveStep write command fail"
                    return -1
        except Exception as e:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1
    # ********************************************************************#

    # ********************************************************************#
    #get thermal temperature
    def GetCurrentTemperature(self,whichLCD):
        try:
            if whichLCD == self.LCD1:
                command = self.GetChannelOne
            elif whichLCD == self.LCD2:
                command = self.GetChannelTwo
            elif whichLCD == self.LCD3:
                command = self.GetChannelThree
            elif whichLCD == self.LCD4:
                command = self.GetChannelFour
            elif whichLCD == self.LCD5:
                command = self.GetChannelFive
            elif whichLCD == self.LCD6:
                command = self.GetChannelSix
            elif whichLCD == self.LCD7:
                command = self.GetChannelSeven
            myDelay = 0.05
            for i in range(1,4,1):
                self.myThermalSerialPort.write (binascii.unhexlify(command))
                time.sleep(myDelay*i)
                ret = self.myThermalSerialPort.read(25)
                hex_data = binascii.hexlify(ret)
                if self.Interpreter == 3:
                    hex_data = hex_data.decode()
                if hex_data[0:5] == "02303" and len(ret) == 25:
                    return round(float(int(ret[-6:-2],16))/10.0,1)
                else:
                    continue
            self.strErrorMessage = "GetCurrentTemperature timeout"
            return -1
        except Exception as e:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1
    # ********************************************************************#

    # ********************************************************************#
    def SetTargetTemperature(self,value):
        try:
            # hex_data = '010000102810003000001030'
            head = '010000102C10003000001'
            value = hex(int(value*10))
            value = value[2:]
            for i in range(8-len(value)):
                value = '0' + value
            bcc = self.__bccValue(head.strip() + value.upper() + '03')
            command = head.strip() + value.upper()
            if self.Interpreter == 3:
                command = binascii.hexlify(command.encode('utf-8'))
                command = '02' + str(command.upper())[2:-1] + '03' + str(bcc.upper())[2:-1]
            else:
                command = binascii.hexlify(command)
                command = '02' + command.upper() + '03' +bcc.upper()
            #strcommand = binascii.hex
            self.myThermalSerialPort.write(binascii.unhexlify(command))
            time.sleep(self.delay)
            ret = self.myThermalSerialPort.read_all()
            if self.Interpreter == 3:
                ret = ret.decode()
            if ret[-6:-2] == '0000' and len(ret) == 17:
                return 0
            return -1
        except Exception as e:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1
    # ********************************************************************#

    # ********************************************************************#
    # Get BCC Value
    def __bccValue(self, code):
        # code = "020000101C0000000000103"
        code1 = ord(code[0])
        code2 = ord(code[1])
        bcc = code1 ^ code2
        for i in range(code.__len__() - 2):
            codetem = ord(code[i + 2])
            bcc = bcc ^ codetem
        bcc = binascii.hexlify(struct.pack('>i', bcc))
        bcc = bcc[6:8]
        return bcc
    # ********************************************************************#

    # ********************************************************************#
    # set baud for angle
    def SetBaudrate(self,SampleRate):
        # print self.__bccValue()
        try:
            self.myAngleSerialPort.write(SampleRate)
            time.sleep(self.delay)
            ret = self.myAngleSerialPort.read_all()
            hex_data = binascii.hexlify(ret)
            if "68" == hex_data[0:2] and len(ret) == 5:
                return 0
            else:
                return -1
        except Exception as e:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1
    # ********************************************************************#

    # ********************************************************************#
    # set home for angle device
    def SetAngleHome(self,model=1):
        try:
            if self.StationName == self.PIR_NQ:
                if model == "68050005000A":
                    command = self.SetAbsoluteHome
                elif model == self.RelativeHome:
                    command = "68050005010B"
                if self.Interpreter == 3:
                    command = command.encode('utf-8')
                self.myAngleSerialPort.write(binascii.unhexlify(command))
                time.sleep(self.delay)
                strRead = self.myAngleSerialPort.read(6)
                hex_data = binascii.hexlify(strRead)
                if self.Interpreter == 3:
                    hex_data = hex_data.decode()
                if hex_data[0:2] == "68" and hex_data[8:10] == "00" and len(strRead) == 6:
                    return 0
                else:
                    return -1
        except Exception as e:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1
    # ********************************************************************#

    # ********************************************************************#
    #get angle
    def ReadXAngleAndYAngle(self,myAngleList):
        try:
            if not self.myAngleSerialPort.is_open:
                self.strErrorMessage = "myAngleSerialPort is no opened"
                return -1
            myDely = 0.02
            sum = 0.0
            for loop in range(3):
                for times in range(1,4,1):
                    self.myAngleSerialPort.write(self.pullData)
                    time.sleep(myDely*times)
                    strRead = self.myAngleSerialPort.read(14)
                    hex_data = binascii.hexlify(strRead)
                    if self.Interpreter == 3:
                        hex_data = hex_data.decode()
                    if hex_data[0:2] == "68" and strRead.__len__() == 14:
                        anglex = hex_data[8:14]
                        flag_x = 1 if anglex[0:1] == '0' else -1
                        angley = hex_data[14:20]
                        flag_y = 1 if angley[0:1] == '0' else -1

                        myAnglex = round(float(anglex[1:6])/100.00 * flag_x,2)
                        break
                        # if -90 < myAnglex < -89:
                        #    myAnglex = myAnglex-0.6
                        # else:
                        #     pass
                    else:
                        self.strErrorMessage = "ReadXAngleAndYAngle fail"
                        return -1

                myAnglex =round(0.00005 * myAnglex * myAnglex + 0.9937 * myAnglex,2)
                if 60 < myAnglex < 89.8:
                    myAnglex = myAnglex-0.4
                elif 89.8 < myAnglex < 90:
                    myAnglex = myAnglex + 0.2
                elif -89 > myAnglex > -90:
                    myAnglex = myAnglex - 0.8
                sum = sum + myAnglex

            myAnglex = round(sum / 3.0, 2)


                        # self.current_angle = myAnglex
                        # if 89.5 < myAnglex < 91:
                        #     myAnglex = myAnglex+0.6
                        # elif 50 < myAnglex < -90:

                        # myAnglex = round(-myAnglex * myAnglex * 0.00003 + myAnglex*1.0026-0.0888,2)
                        # if myAnglex > 90:
                        #     myAnglex = 90
                        # elif myAnglex < -90:
                        #     myAnglex = -90

                        # if abs(round(float(anglex[1:6])/100.00,2) * flag_x) < 10:
                        #     myAngleList.append(round(float(anglex[1:6]) / 100.00, 2) * flag_x)
                        # else:
                        #     myAngleList.append(round(float(anglex[1:6])/100.00,2) * flag_x + offset)
            myAngleList.append(myAnglex)
            myAngleList.append(round(float(angley[1:6])/100.00,2) * flag_y)
            return 0


        except Exception as e:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1
    # ********************************************************************#

    # ********************************************************************#
    def Set_CylinderFunction(self, direction,timeout=10):
        try:
            if self.StationName == 'GQ':
                if self.ReadOneIOState('x', 13) != 0 or self.ReadOneIOState('x',15) != 0:
                    self.strErrorMessage = 'must usb onlock or dut unlock'
                    print(self.strErrorMessage)
                    return -1

            if True: #self.ReadOneIOState('x',13) == 0 and self.ReadOneIOState('x',15) == 0:
                if direction == self.Out:
                    command_off = "writeoutput_off:Y05\r\n"
                    command = "writeoutput_on:Y06\r\n"
                    ID = 4
                elif direction == self.In:
                    command_off = "writeoutput_off:Y06\r\n"
                    command = "writeoutput_on:Y05\r\n"
                    ID = 3

                if self.Interpreter == 3:
                    command_off = command_off.encode('utf-8')
                    command = command.encode('utf-8')

                self.myMCUSerialPort.write(command_off)
                time.sleep(self.delay)
                ret = self.myMCUSerialPort.read_all()

                if self.Interpreter == 3:
                    ret = ret.decode()

                if 'Ouput_OFF_OK' in ret:
                    self.myMCUSerialPort.write(command)
                    time.sleep(self.delay)
                    ret = self.myMCUSerialPort.read_all()
                    if self.Interpreter == 3:
                        ret = ret.decode()

                    if 'Ouput_ON_OK' in ret:
                        mytimeout = 0
                        while True:
                            if mytimeout > timeout:
                                self.strErrorMessage = "Set_CylindeFunction timeout"
                                return -1
                            if self.ReadOneIOState('x',ID) == 0:
                                return 0
                            else:
                                mytimeout = mytimeout + 0.05
                                time.sleep(0.05)
                                continue
                    else:
                        return -1
                else:
                    self.strErrorMessage = "Set_CylindeFunction Off error"
                    return -1
            else:
                self.strErrorMessage = "Set_CylindeFunction Off error"
                return -1

        except:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1

# ********************************************************************#

# ********************************************************************#
    def Set_DoorState(self, direction, timeout=10):
        try:
            if (self.ReadOneIOState('x', 16) == 0 or self.ReadOneIOState('x', 17) == 0):
                if direction == self.DoorClose:
                    command = "writeoutput_on:Y14\r\n"
                    confirm = 'Ouput_ON_OK'
                    ID = 14
                elif direction == self.DoorOpen:
                    command = "writeoutput_off:Y13\r\n"
                    confirm = 'Ouput_OFF_OK'
                    ID = 15
                if self.Interpreter == 3:
                    command = command.encode('utf-8')
                self.myMCUSerialPort.write(command)
                time.sleep(self.delay)
                ret = self.myMCUSerialPort.read_all()
                if self.Interpreter == 3:
                    ret = ret.decode()
                mytimeout = 0
                if confirm in ret:
                    while True:
                        if mytimeout > timeout:
                            self.strErrorMessage = "Set_DoorState timeout"
                            return -1
                        if self.ReadOneIOState('x', ID) == 0:
                            return 0
                        else:
                            mytimeout = mytimeout + 0.05
                            time.sleep(0.05)
                            continue
                    else:
                        return -1
                else:
                    self.strErrorMessage = "Set_DoorState except error"
                    return -1
            else:
                self.strErrorMessage = 'dut not in place or dut is loosen'
                return -1
        except:
            self.strErrorMessage = "Set_DoorState except fail"
            return -1

# ********************************************************************#

# ********************************************************************#
    def Set_USBState(self, direction, timeout=10):
        try:
            if (self.ReadOneIOState('x',16) == 0 or self.ReadOneIOState('x',17) == 0):
                if direction == self.USBLock:
                    command = "writeoutput_on:Y10\r\n"
                    confirm = 'Ouput_ON_OK'
                    ID = 14
                elif direction == self.USBUnlock:
                    command = "writeoutput_off:Y10\r\n"
                    confirm = 'Ouput_OFF_OK'
                    ID = 15
                if self.Interpreter == 3:
                    command = command.encode('utf-8')
                self.myMCUSerialPort.write(command)
                time.sleep(self.delay)
                ret = self.myMCUSerialPort.read_all()
                if self.Interpreter == 3:
                    ret = ret.decode()
                mytimeout = 0
                if confirm in ret:
                    while True:
                        if mytimeout > timeout:
                            self.strErrorMessage = "Set_USBState timeout"
                            return -1
                        if self.ReadOneIOState('x', ID) == 0:
                            return 0
                        else:
                            mytimeout = mytimeout + 0.05
                            time.sleep(0.05)
                            continue
                    else:
                        return -1
                else:
                    self.strErrorMessage = "Set_USBState except error"
                    return -1
            else:
                self.strErrorMessage = 'dut not in place or dut is loosen'
                return -1
        except:
            self.strErrorMessage = "Set_USBState except fail"
            return -1


    # ********************************************************************#

    # ********************************************************************#
    def Set_DutState(self, direction, timeout=10):
        try:
            if (self.ReadOneIOState('x', 16) == 0 or self.ReadOneIOState('x', 17) == 0) :
                if direction == self.DutLock:
                    command = "writeoutput_on:Y07\r\n"
                    confirm = 'Ouput_ON_OK'
                    ID = 12
                elif direction == self.DutUnlock:
                    command = "writeoutput_off:Y07\r\n"
                    confirm = 'Ouput_OFF_OK'
                    ID = 13
                if self.Interpreter == 3:
                    command = command.encode('utf-8')
                self.myMCUSerialPort.write(command)
                time.sleep(self.delay)
                ret = self.myMCUSerialPort.read_all()
                if self.Interpreter == 3:
                    ret = ret.decode()
                mytimeout = 0
                if confirm in ret:
                    while True:
                        if mytimeout > timeout:
                            self.strErrorMessage = "Set_USBState timeout"
                            return -1
                        if self.ReadOneIOState('x', ID) == 0:
                            return 0
                        else:
                            mytimeout = mytimeout + 0.05
                            time.sleep(0.05)
                            continue
                    else:
                        return -1
                else:
                    self.strErrorMessage = "Set_USBState except error"
                    return -1
            else:
                self.strErrorMessage = 'dut not in place or usb is lock'
                return -1
        except Exception as e:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1

    # ********************************************************************#

    # ********************************************************************#


    def SetLightCurtain(self, state):
        try:
            if (state == self.LightCurtainOn):
                command = "writeoutput_on:Y05\r\n"
                result = 'Ouput_ON_OK'
            elif (state == self.LightCurtainOff):
                command = "writeoutput_off:Y05\r\n"
                result = 'Ouput_ON_OK'
            else:
                self.strErrorMessage = "SetLight curtain Input parameter error"
                return -1

            if self.Interpreter == 3:
                command = command.encode('utf-8')

            self.myMCUSerialPort.write(command)
            time.sleep(self.delay)
            ret = self.myMCUSerialPort.read_all()

            if self.Interpreter == 3:
                ret = ret.decode()

            if result in ret:
                return 0
            else:
                return -1
        except:
            self.strErrorMessage = "SetLight curtain error"
            return -1
    ####################### for Customer ##################################

    # ********************************************************************#

    # ********************************************************************#
    def ReadSensorState(self,sensor,delaytime = 0.2):
        try:
            if self.myMCUSerialPort.is_open != 1:
                self.strErrorMessage = "there is not open MCUPort"
                return -1
            if 1 <= sensor <= 8:
                ID = sensor-1
            elif 9 <= sensor <= 16:
                ID = sensor+1
            elif 17 <= sensor <= 24:
                ID = sensor +3
            elif 25 <= sensor <= 28:
                ID = sensor +5
            else:
                self.strErrorMessage = "Sensor ID fail"
                return -1


            if 0 <= ID <= 7:
                ReadIOOneCommand = "readio_one:x0"
                command = ReadIOOneCommand+str(ID)+"\r\n"
            elif  10 <= ID <= 17 or 20 <= ID <= 27 or 30<= ID <= 33:
                ReadIOOneCommand = "readio_one:x"
                command = ReadIOOneCommand + str(ID) + "\r\n"
            else:
                self.strErrorMessage = "input IO ID fail"
                return -1


            if self.Interpreter == 3:
                command = command.encode('utf-8')

            self.myMCUSerialPort.write(command)
            time.sleep(delaytime)
            readstring = self.myMCUSerialPort.read_all()

            if self.Interpreter == 3:
                readstring = readstring.decode()

            if len(readstring)>0:
                if readstring[0] == "X" and readstring[2] == "=" and int(readstring[1]) == ID:
                    return int(readstring[3])
                elif readstring[0] == "X" and 0<= int(readstring[2]) <= 9 and int(readstring[1:3]) == ID:
                    return int(readstring[4])
                else:
                    self.strErrorMessage = "write command fail"
                    return -1
            else:
                self.strErrorMessage = "write command fail"
                return -1
        except Exception as e:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1
    # ********************************************************************#

    # ********************************************************************#
    def ReadValveState(self,valve,delaytime = 0.2):
        try:
            if 1 <= valve <= 8:
                ID = valve-1
            elif 9 <= valve <= 16:
                ID = valve+1
            elif 17 <= valve <= 23:
                ID = valve +3
            else:
                self.strErrorMessage = "Sensor ID fail"
                return -1

            if 0 <= ID <= 7:
                ReadIOOneCommand = "readio_one:y0"
                command = ReadIOOneCommand+str(ID)+"\r\n"
            elif  10 <= ID <= 17 or 20 <= ID <= 26 :
                ReadIOOneCommand = "readio_one:y"
                command = ReadIOOneCommand + str(ID) + "\r\n"
            else:
                self.strErrorMessage = "input IO ID fail"
                return -1

            self.myMCUSerialPort.write(command)
            time.sleep(delaytime)
            readstring = self.myMCUSerialPort.read_all()
            if len(readstring)>0:
                if readstring[0] == "Y" and readstring[2] == "=" and int(readstring[1]) == ID:
                    return int(readstring[3])
                elif readstring[0] == "Y" and 0<= int(readstring[2]) <= 9 and int(readstring[1:3]) == ID:
                    return int(readstring[4])
                else:
                    self.strErrorMessage = "write command fail"
                    return -1
            else:
                self.strErrorMessage = "write command fail"
                return -1
            return -1
        except:
            self.strErrorMessage = "readIO_One except fail"
    # ********************************************************************#

    # ********************************************************************#
    #read one IO state
    def ReadOneIOState(self,type_IO,ID):
        try:
            # if str(type(ID)) == "<class 'int'>" and str(type(type_IO)) == "<class 'str'>":
            if str(type_IO) == "x" and 0 <= ID <8:
                ReadIOOneCommand = "readio_one:x0"
                command = ReadIOOneCommand+str(ID)+"\r\n"
            elif str(type_IO) == "x" and (10 <= ID <= 17 or 20 <= ID <= 27 or 30<= ID <= 33):
                ReadIOOneCommand = "readio_one:x"
                command = ReadIOOneCommand + str(ID) + "\r\n"
            elif str(type_IO)== "y" and 0 <= ID < 8:
                ReadIOOneCommand = "readio_one:y0"
                command = ReadIOOneCommand+str(ID)+"\r\n"
            elif str(type_IO)== "y" and (10 <= ID <= 17 or 20 <= ID <= 27 or 30<= ID <= 37 or 40 <= ID <=43):
                ReadIOOneCommand = "readio_one:y"
                command = ReadIOOneCommand + str(ID) + "\r\n"
            else:
                self.strErrorMessage = "input IO ID,type fial"
                return -1
            # else:
            #     self.strErrorMessage = "input parameters type fail"
            #     return -1

            if self.Interpreter == 3:
                command = command.encode('utf-8')

            self.myMCUSerialPort.write(command)
            time.sleep(self.delay)
            readstring = self.myMCUSerialPort.read_all()
            if self.Interpreter == 3:
                readstring = readstring.decode()

            if len(readstring)>0:
                if readstring[0] == type_IO.upper() and readstring[2] == "=" and int(readstring[1]) == ID:
                    return int(readstring[3])
                elif readstring[0] == type_IO.upper() and 0<= int(readstring[2]) <= 9 and int(readstring[1:3]) == ID:
                    return int(readstring[4])
                else:
                    self.strErrorMessage = "write command fail"
                    return -1
            else:
                self.strErrorMessage = "write command fail"
                return -1
        except:
            self.strErrorMessage = "readIO_One except fail"
            return -1
    # ********************************************************************#

    # ********************************************************************#
    def readInIOAll(self):
        try:
            readInIOCommand = "readinput_all:\r\n"
            if self.Interpreter == 3:
                readInIOCommand = readInIOCommand.encode('utf-8')

            self.myMCUSerialPort.write(readInIOCommand)
            time.sleep(self.delay)
            readstring = self.myMCUSerialPort.read_all()
            if self.Interpreter == 3:
                readstring = readstring.decode()

            if "X33-X00:" in readstring.strip():
                return readstring[27:58].replace(' ','')
            else:
                self.strErrorMessage = "write command fail"
                return -1
        except:
            self.strErrorMessage = "readOutIOALl except fail"
            return -1
    # ********************************************************************#

    # ********************************************************************#
    def readOutIOAll(self):
        try:
            readOutIOCommand = "readoutput_all:\r\n"
            if self.Interpreter == 3:
                readOutIOCommand = readOutIOCommand.encode('utf-8')

            self.myMCUSerialPort.write(readOutIOCommand)
            time.sleep(self.delay)
            readstring = self.myMCUSerialPort.read_all()
            if self.Interpreter == 3:
                readstring = readstring.decode()

            if "Y43-Y00:" in readstring.strip():
                return readstring[19:59].replace(' ','')
            else:
                self.strErrorMessage = "write command fail"
                return -1
        except:
            self.strErrorMessage = "readOutIOALl except fail"
            return -1
    # ********************************************************************#

    # ********************************************************************#
    def readIOAll(self):
        try:
            readIOAllCommand = "readio_all:\r\n"
            if self.Interpreter == 3:
                readIOAllCommand = readIOAllCommand.encode('utf-8')
            self.myMCUSerialPort.write(readIOAllCommand)
            time.sleep(self.delay)
            readstring = self.myMCUSerialPort.read_all()
            if self.Interpreter == 3:
                readstring = readstring.decode()

            if "X33-X00:" in readstring.strip() and "Y43-Y00" in readstring.strip():
                return readstring
            else:
                return -1
        except:
            self.strErrorMessage = "readIOALl except fail"
            return -1
    # ********************************************************************#

    # ********************************************************************#
    def SetValveState(self,valve,state,delaytime = 0.2):
        try:
            if 1 <= valve <= 8:
                ID = valve-1
            elif 9 <= valve <= 16:
                ID = valve+1
            elif 17 <= valve <= 23:
                ID = valve +3
            else:
                self.strErrorMessage = "Sensor ID fail"
                return -1

            if str(type(state)) == "<class 'int'>" and str(type(valve)) == "<class 'int'>":
                if state == 1 and 0 <= ID <= 9 :
                    setIOCommand = "writeoutput_on:y0"+str(ID)+"\r\n"
                elif state == 1 and 10<= ID <= 26:
                    setIOCommand = "writeoutput_on:y"+str(ID)+"\r\n"
                elif state == 0 and 0 <= ID <= 9 :
                    setIOCommand = "writeoutput_off:y0"+str(ID)+"\r\n"
                elif state == 0 and 10<= ID <= 26:
                    setIOCommand = "writeoutput_off:y"+str(ID)+"\r\n"
                else:
                    self.strErrorMessage = "input IO type,ID,state fail"
                    return -1
            else:
                self.strErrorMessage = "input parameters type fail"
                return -1
            self.myMCUSerialPort.write(setIOCommand)
            if self.Interpreter == 3:
                setIOCommand = setIOCommand.encode('utf-8')
            time.sleep(delaytime)
            readstring = self.myMCUSerialPort.read_all()
            if self.Interpreter == 3:
                readstring = readstring.decode()
            string = readstring[10:12]
            if state == 0 and readstring[10:12] == "OK":
                return 0
            elif state ==1 and readstring[9:11] == "OK":
                return 0
            else:
                return -1
        except Exception as e:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1
    # ********************************************************************#

    # ********************************************************************#
    def SetMotorStop(self):
        try:
            command = "r_axis_disable\r\n"
            if self.Interpreter == 3:
                command = command.encode('utf-8')

            self.myMCUSerialPort.write(command)
            readstring = self.myMCUSerialPort.read_all()

            if self.Interpreter == 3:
                readstring = readstring.decode()

            if readstring.strip() == "R_Axis_Motor_Stop":
                return 0
            else:
                self.strErrorMessage = "write command fail"
                return -1
        except:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1
    # ********************************************************************#

    # ********************************************************************#
    def SetMotorGohome(self,direction):
        try:
            if str(type(direction)) == "<class 'int'>" :
                if direction == 1:
                    command = "r_axis_go_home_cw\r\n"
                    if self.Interpreter == 3:
                        command = command.encode('utf-8')

                    self.myMCUSerialPort.write(command)
                    time.sleep(self.delay)
                    readstring = self.myMCUSerialPort.read_all()

                    if self.Interpreter == 3:
                        readstring = readstring.decode()

                    if readstring.strip() == "R_Axis_Motor_GO_Home_CW":
                        return 0
                    else:
                        self.strErrorMessage = "write command fail"
                        return -1
                elif direction == 0:
                    command = "r_axis_go_home_ccw\r\n"
                    if self.Interpreter == 3:
                        command = command.encode('utf-8')

                    self.myMCUSerialPort.write(command)
                    time.sleep(self.delay)
                    readstring = self.myMCUSerialPort.read_all()
                    if self.Interpreter == 3:
                        readstring = readstring.decode()
                    if readstring.strip() == "R_Axis_Motor_GO_Home_CCW":
                        return 0
                    else:
                        self.strErrorMessage = "write command fail"
                        return -1
            else:
                self.strErrorMessage = "input parameters type fail"
                return -1

        except:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1
    # ********************************************************************#


    # ********************************************************************#
    def emergency_stop(self):
        try:
            if abs(self.current_angle) > 100:
                command = 'r_axis_disable\r\n'
                if self.Interpreter == 3:
                    command = command.encode('utf-8')
                self.myMCUSerialPort.write(command)

                self.strErrorMessage = "current angle is {}".format(self.current_angle)
                return -1
            return 0
        except Exception as e:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1
    # ********************************************************************#
    def SendMsg(self,Msg):
        try:
            if self.Interpreter == 3:
                Msg = Msg.encode('utf-8')
            self.myMCUSerialPort.write(command)
            return 0
        except:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1


if __name__ == '__main__':
    pass
