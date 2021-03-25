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
import threading

class MCUControl:

    # thread finish
    RotateAxisThreadingFinish = False
    ThreadingFinish = False
    GetTemperature = False

    content = []
    content1 = []
    content2 = []
    content3 = []


    delay = 0.3
    offset = 0.018
    strErrorMessage = "ok"
    myMCUSerialPort = None #MCU port
    myThermalSerialPort = None #Thermal Sensor port
    myAngleSerialPort = None #Angle sensor port
    myAngleSerialPort2 = None #Angle sensor port

    myMCUSerialPortName = ""
    myThermalSerialPortName = ""
    myAngleSerialPortName = ""
    myAngleSerialPortName2 = ""

    SwitchMCU = 0
    SwitchThermal = 1
    SwitchAngle1 = 2
    SwitchAngle2 = 3

    MCU = 0
    Thermal = 1
    AngleDevice = 2

    # For Axis
    ReadIOOneCommand = "readio_one:x00\r\n"
    ServoMotor = 0
    StepMotor = 1

    #for thermal
    GetChannelOne = "023031303030303130314330303030303030303030310340"
    GetChannelTwo = "023032303030303130314330303030303030303030310343"
    GetChannelThree = "023033303030303130314330303030303030303030310342"
    GetChannelFour = "023034303030303130314330303030303030303030310345"
    LCD1 = 0
    LCD2 = 1
    LCD3 = 2
    LCD4 = 3

    #read angle
    pullData = [0x68, 0x04, 0x00, 0x04, 0x08]

    #set home
    AbsoluteHome = 0
    RelativeHome = 1

    #get home model
    GetHomeModel = [0x86, 0x04, 0x00, 0x0D, 0x11]

    #set baud 设置波特
    SetBaud_9600 = [0x68, 0x05, 0x00, 0x0B, 0x02, 0x13] #defaul
    SetBaud_19200 = [0x68, 0x05, 0x00, 0x0B, 0x03, 0x13]
    SetBaud_38400 = [0x68, 0x05, 0x00, 0x0B, 0x04, 0x13]
    SetBaud_115200 = [0x68, 0x05, 0x00, 0x0b, 0x05, 0x13]

    #Filtering parameters 过滤参数
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

    Dutlock = 9
    DutUnlock = 10

    DoorClose = 11
    DoorOpen = 12

    PowerUp = 13
    PowerDown = 14

    USBOn = 15
    USBOff = 16

    #project name
    PIR_NQ = "GQ"

    max_retry = 1
    max_retry_x = 2

    def __init__(self,station):
        self.StationName = station
        self.Interpreter = int(platform.python_version()[0])
        self.current_angle = 0
    # **************************************************************************************#

    # **************************************************************************************#
    ################################ for Customer ###########################################
    def OpenSerial(self, switch, portname = ""):
        try:
            # port_list = list ( serial.tools.list_ports.comports () )
            # if len ( port_list ) < 1:
            #     self.strErrorMessage = "There is no serial port"
            #     return -1
            #温度
            if switch == self.SwitchThermal:
                self.myThermalSerialPort = serial.Serial(port=portname,
                                                    timeout=0.05,
                                                    baudrate=57600,
                                                    parity=PARITY_EVEN,
                                                    stopbits=2,
                                                    bytesize=7)

                if self.myThermalSerialPort.is_open:
                    ret = self.AutoChoose(switch)
                    if ret != 0:
                        self.myThermalSerialPort.close()
                        return -1
                    else:
                        # print("hans debug: Thermal port {}".format(self.myThermalSerialPortName))
                        return 0
            #MCU
            elif switch == self.SwitchMCU:
                self.myMCUSerialPort = serial.Serial(port=portname,
                                                 timeout=0.1,
                                                 baudrate=115200,
                                                 parity=PARITY_NONE,
                                                 stopbits=1,
                                                 bytesize=8)

                if self.myMCUSerialPort.is_open:
                    ret = self.AutoChoose(switch)
                    if ret != 0:
                        self.myMCUSerialPort.close()
                        return -1
                    else:
                        # print("hans debug: MCU port {}".format(self.myMCUSerialPortName))
                        return 0


            #角度1
            elif switch == self.SwitchAngle1:
                self.myAngleSerialPort = serial.Serial(port=portname,
                                                 timeout=0.05,
                                                 baudrate=115200,
                                                 parity=PARITY_NONE,
                                                 stopbits=1,
                                                 bytesize=8)

                if self.myAngleSerialPort.is_open:
                    ret = self.AutoChoose(switch)
                    if ret != 0:
                        self.myAngleSerialPort.close()
                        return -1
                    else:
                        # print("hans debug: Angle port {}".format(self.myAngleSerialPortName))
                        return 0

            # 角度2
            elif switch == self.SwitchAngle2:
                self.myAngleSerialPort2 = serial.Serial(port=portname,
                                                 timeout=0.05,
                                                 baudrate=9600,
                                                 parity=PARITY_NONE,
                                                 stopbits=1,
                                                 bytesize=8)

                if self.myAngleSerialPort2.is_open:
                    ret = self.AutoChoose(switch)
                    if ret != 0:
                        self.myAngleSerialPort2.close()
                        return -1
                    else:
                        # print("hans debug: Angle port {}".format(self.myAngleSerialPortName2))
                        return 0


            return -1
        except Exception as e:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1
    # **************************************************************************************#


    # **************************************************************************************#
    def Set_Power(self, direction, timeout=10):
        try:
            if direction == self.PowerDown:
                command = "writeoutput_off:y12\r\n"
                respond = "Ouput_OFF_OK.\r\n"
            elif direction == self.PowerUp:
                command = "writeoutput_on:y12\r\n"
                respond = "Ouput_ON_OK.\r\n"
            if self.Interpreter == 3:
                command = command.encode('utf-8')
            for i in range(self.max_retry):
                self.myMCUSerialPort.write(command)
                time.sleep(self.delay)
                ret = self.myMCUSerialPort.read_all()
                if self.Interpreter == 3:
                    ret = ret.decode()
                    if respond in ret:
                        return 0
                    else:
                        self.myMCUSerialPort.flushInput()
                        self.myMCUSerialPort.flushOutput()
                        return  -1
                        continue
            return 0
        except Exception as e:
            self.strErrorMessage = "Set_Power except fail"
            return -1
    # **************************************************************************************#

    # **************************************************************************************#
    def Set_USB(self, direction, timeout=10):
        try:
            if direction == self.USBOn:
                command = "writeoutput_on:y20\r\n"
                respond = "Ouput_ON_OK.\r\n"
            elif direction == self.USBOff:
                command = "writeoutput_off:y20\r\n"
                respond = "Ouput_OFF_OK.\r\n"
            if self.Interpreter == 3:
                command = command.encode('utf-8')
            for i in range(self.max_retry):
                self.myMCUSerialPort.write(command)
                time.sleep(self.delay)
                ret = self.myMCUSerialPort.read_all()
                if self.Interpreter == 3:
                    ret = ret.decode()
                    with open("linshi.txt", "a") as f:
                        f.writelines(ret)

                    if respond in ret:
                        return 0
                    else:
                        self.myMCUSerialPort.flushInput()
                        self.myMCUSerialPort.flushOutput()
                        return  -1
                        continue
            return 0
        except Exception as e:
            self.strErrorMessage = "Set_Power except fail"
            return -1
    # **************************************************************************************#


    # **************************************************************************************#
    # auto choose the serial port
    def AutoChoose(self,switch):
        try:
            if switch == self.SwitchThermal:
                self.myThermalSerialPort.write (binascii.unhexlify(self.GetChannelOne))
                time.sleep(0.05)
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
                    return -1096
            elif switch == self.SwitchAngle1:
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
            elif switch == self.SwitchAngle2:
                self.myAngleSerialPort2.write(self.pullData)
                time.sleep(self.delay)
                read_data = self.myAngleSerialPort2.read_all()
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
                    # print("serial is closed")
            elif switch == self.SwitchAngle1:
                if self.myAngleSerialPort.is_open:
                    self.myAngleSerialPort.close()
            elif switch == self.SwitchAngle2:
                if self.myAngleSerialPort2.is_open:
                    self.myAngleSerialPort2.close()
            elif switch == self.SwitchMCU:
                if self.myMCUSerialPort.is_open:
                    self.myMCUSerialPort.close()
            return 0
        except Exception as e:
            self.strErrorMessage = "CloseSerial except fail"
            return -1
    # ********************************************************************#

    # ********************************************************************#
    def SetSpeed(self,value,ofWahtAxis = ""):
        try:
            if str(type(value)) != "<type 'str'>":
                # value = int(round(value * 200, 2))
                command = "r_axis_speed:"+str(value)+"\r\n"
            else:
                self.strErrorMessage = "input parameters type fail"
                return -1
            if self.Interpreter == 3:
                command = command.encode('utf-8')

            for i in range(self.max_retry):
                self.myMCUSerialPort.write(command)
                time.sleep(self.delay)
                readstring = self.myMCUSerialPort.read(18)
                if self.Interpreter == 3:
                    readstring = readstring.decode()

                # print len(readstring)
                if "Receive Data OK." in readstring:
                    return 0
            self.strErrorMessage = "SetSpeed write command fail"
            return -1
        except Exception as e:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1
    # ********************************************************************#

    # ********************************************************************#
    def SetSpeed_X(self, value, ofWahtAxis=""):
        try:
            if str(type(value)) != "<type 'str'>":
                # value = int(round(value * 200, 2))
                command = "x_axis_speed:" + str(value) + "\r\n"
            else:
                self.strErrorMessage = "input parameters type fail"
                return -1
            if self.Interpreter == 3:
                command = command.encode('utf-8')

            for i in range(self.max_retry):
                self.myMCUSerialPort.write(command)
                time.sleep(self.delay)
                readstring3 = self.myMCUSerialPort.read(18)
                # readstring3 = self.myMCUSerialPort.read_all
                if self.Interpreter == 3:
                    readstring3 = readstring3.decode()

                # print len(readstring)
                if "Receive Data OK." in readstring3:
                    return 0
            self.strErrorMessage = "SetSpeed write command fail"
            return -1
        except Exception as e:
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

                for i in range(self.max_retry):
                    self.myMCUSerialPort.write(command)
                    time.sleep(self.delay)
                    ret = self.myMCUSerialPort.read_all()
                    if self.Interpreter == 3:
                        ret = ret.decode()

                    if 'R_Axis_Speed' in ret:
                        info = ret.split('\n')[0]
                        index = info.find(':')
                        return float(info[index + 1:])/200.0

                self.strErrorMessage = "GetSpeed fail"
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
                # command3 = "r_axis_go_home_cw\r\n"
                # if self.Interpreter == 3:
                #     command3 = command3.encode('utf-8')
                # self.myMCUSerialPort.write(command3)
                # time.sleep(self.delay)
                command = "test_reset\r\n"
                if self.Interpreter == 3:
                    command = command.encode('utf-8')
                self.myMCUSerialPort.write(command)
                time.sleep(1)
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
                            command3 = "r_axis_go_home_cw\r\n"
                            if self.Interpreter == 3:
                                command3 = command3.encode('utf-8')
                            self.myMCUSerialPort.write(command3)
                            time.sleep(self.delay)

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
                            command = "x_axis_go_home_cw\r\n"
                            if self.Interpreter == 3:
                                command = command.encode('utf-8')
                            self.myMCUSerialPort.write(command)
                            time.sleep(self.delay)

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



            # other position 其他位置
            panduan = []
            self.ReadXAngleAndYAngle(panduan)
            if (panduan[0] < 0 ):
                command1 = 'r_axis_go_min\r\n'
            else:
                command1 = 'r_axis_go_max\r\n'


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
                        self.strErrorMessage = 'SignalReSet：Motor go min timeout'
                        return -1
                    elif self.ReadOneIOState('x', 33) == 1:
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
                                # command3 = "x_axis_go_home_cw\r\n"
                                # if self.Interpreter == 3:
                                #     command3 = command3.encode('utf-8')
                                # self.myMCUSerialPort.write(command3)
                                # time.sleep(self.delay)

                                command2 = "test_reset\r\n"
                                if self.Interpreter == 3:
                                    command2 = command2.encode('utf-8')
                                self.myMCUSerialPort.write(command2)
                                time.sleep(self.delay)
                                break
                            else:
                                mytimeout = mytimeout + 0.05
                                time.sleep(0.05)
                                continue
                    # self.myMCUSerialPort.write('readio_one:x05')
                    # time.sleep(self.delay)
                    # signal = self.myMCUSerialPort.read_all()
                    # if 'X6=0' in signal:
                    time.sleep(1)
                    if self.ReadOneIOState('x', 5) == 0:
                        return 0
                    else:
                        return -1
#####################################add 20210305 判断复位时，走正极限##################################################################
            elif 'Motor_R_GO_Max' in ret:
                mytimeout = 0
                while True:
                    if mytimeout > timeout:
                        self.strErrorMessage = 'SignalReSet：Motor go min timeout'
                        return -1
                    elif self.ReadOneIOState('x', 33) == 1:
                        break
                    else:
                        mytimeout = mytimeout + 0.05
                        time.sleep(0.05)
                        continue
                # self.myMCUSerialPort.write('readio_one:x06')
                # time.sleep(self.delay)
                # signal = self.myMCUSerialPort.read_all()
                # if 'X6=0' in signal:
                if self.ReadOneIOState('x', 7) == 0:
                    time.sleep(1)
                    command2 = 'r_axis_go_home_cw\r\n'
                    if self.Interpreter == 3:
                        command2 = command2.encode('utf-8')
                    self.myMCUSerialPort.write(command2)
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
                            #？？？
                            elif self.ReadOneIOState('x', 5) == 0:
                                # command3 = "r_axis_go_home_cw\r\n"
                                # if self.Interpreter == 3:
                                #     command3 = command3.encode('utf-8')
                                # self.myMCUSerialPort.write(command3)
                                # time.sleep(self.delay)
                                command2 = "test_reset\r\n"
                                if self.Interpreter == 3:
                                    command2 = command2.encode('utf-8')
                                self.myMCUSerialPort.write(command2)
                                time.sleep(self.delay)
                                break
                            else:
                                mytimeout = mytimeout + 0.05
                                time.sleep(0.05)
                                continue
                    time.sleep(1)

                    if self.ReadOneIOState('x', 5) == 0:
                        return 0
                    else:
                        return -1
###########################################################################################################################
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
    def MoveToCoordinates(self, value, speed = 60, ofWhatAxis = "",timeout = 10):
        if value != 0:
            if self.ReadOneIOState('x', 4) == 0 or self.ReadOneIOState('x',17) == 1:
                self.strErrorMessage = "Dut no lock or Vacuum file!"
                print(self.strErrorMessage)
                return -1

        try:

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
            # if value > 120:
            #     value = 120
            # if value < -120:
            #     value = -120
            #
            # if value == -120:
            #     value = -119

            if str(type(value)) != "<type 'str'>":
                value = int(round(value * 200, 2))
                command = "r_axis_move_to:" + str(value) + "\r\n"
            else:
                self.strErrorMessage = "input parameters type fail" #输入参数类型失败
                return -1

            if self.Interpreter == 3:
                command = command.encode('utf-8')

            for i in range(self.max_retry):
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
                            #电机在正负极限位，需要复位
                            if self.ReadOneIOState('x',6) == 0 or self.ReadOneIOState('x',7) == 0:
                                self.strErrorMessage = 'MoveToCoordinates out of limit,need to reset'
                                return -1
                            else:
                                return 0
                        else:
                            mytimeout = mytimeout + 0.05
                            time.sleep(0.05)
                            continue
            
            self.strErrorMessage = "MoveToCoordinates write command fail"
            return -1
        except Exception as e:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1
    # ********************************************************************#

    # ********************************************************************#
    def MoveToCoordinates_X(self, value, speed=150, ofWhatAxis="", timeout=10):
        if self.ReadOneIOState('x', 4) == 0 or self.ReadOneIOState('x',17) == 1 :
            self.strErrorMessage = "Dut no lock or Vacuum file!"
            print(self.strErrorMessage)
            return -1
        try:
            if speed != 140 and speed != '':
                ret = self.SetSpeed_X(speed)
                if ret != 0:
                    self.strErrorMessage = "MoveToCoordinates set speed fail"
                    return -1

            elif speed == 39:
                ret = self.SetSpeed_X(39)
                if ret != 0:
                    self.strErrorMessage = "MoveToCoordinates set speed fail"
                    return -1
            # if value > 90:
            #     value = 90
            # if value > 0 and value <= 20:
            #     value = (float(value) + 0.0079) / 0.9874
            # if value > 20 and value <= 40:
            #     value = (float(value) - 0.0399) / 0.9835
            # # if value > 40 and value <= 50:
            # #     value = (float(value) + 0.4624) / 0.9859
            # # if value > 50 and value <= 60:
            # #     value = (float(value) + 0.371) / 0.9833
            # # if value > 60 and value <= 70:
            # #     value = (float(value) -0.1463) / 0.9746
            # # if value > 70 and value <= 80:
            # #     value = (float(value) -0.9255) / 0.9642
            # # if value > 80 and value <= 90:
            # #     value = (float(value) +1.864) / 0.9993
            # if value > 40 and value <= 60:
            #     value = (float(value)+ 0.2167) / 0.9884
            # if value > 60 and value <= 90:
            #     value = (float(value) +0.7283) / 0.9974

            # if value < 0.5 :
            #     value = 0
            if str(type(value)) != "<type 'str'>":
                value = int(round(value * 110, 2))
                command = "x_axis_move_to:" + str(value) + "\r\n"
            else:
                self.strErrorMessage = "input parameters type fail"  # 输入参数类型失败
                return -1

            if self.Interpreter == 3:
                command = command.encode('utf-8')

            for i in range(self.max_retry):
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
                        elif self.ReadOneIOState('x', 33) == 1:
                            # 电机在正负极限位，需要复位
                            if self.ReadOneIOState('x', 6) == 0 or self.ReadOneIOState('x', 7) == 0:
                                self.strErrorMessage = 'MoveToCoordinates out of limit,need to reset'
                                return -1
                            else:
                                return 0
                        else:
                            mytimeout = mytimeout + 0.05
                            time.sleep(0.05)
                            continue

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
            if self.ReadOneIOState('x', 4) == 0 or self.ReadOneIOState('x',17) == 1:
                self.strErrorMessage = "Dut no lock or Vacuum file!"
                print(self.strErrorMessage)
                return -1

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

                for i in range(self.max_retry):
                    self.myMCUSerialPort.write(command)
                    time.sleep(self.delay)
                    readstring = self.myMCUSerialPort.read_all()

                    if self.Interpreter == 3:
                        readstring = readstring.decode('ISO-8859-1')

                    if '_Axis_Motor_Moving' in readstring:
                        mytimeout = 0
                        while True:
                            if mytimeout > timeout:
                                self.strErrorMessage = 'MoveStep timeout'
                                return -1

                            if self.ReadOneIOState('x',33) == 0:
                                if self.ReadOneIOState('x',6) == 0 or self.ReadOneIOState('x',7) == 0:
                                    self.strErrorMessage = 'MoveToCoordinates out of limit,need to reset'
                                    return -1
                                else:
                                    return 0
                            else:
                                mytimeout = mytimeout + 0.05
                                time.sleep(0.05)
                                continue
                self.strErrorMessage = "MoveStep write command fail"
                return -1
        except Exception as e:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1
    # ********************************************************************#

    # ********************************************************************#
    def MoveStep_X(self, value, speed=60, ofWhatAxis="", timeout=10):
        if self.ReadOneIOState('x', 4) == 0 or self.ReadOneIOState('x',17) == 1:
            self.strErrorMessage = "Dut no lock or Vacuum file!"
            print(self.strErrorMessage)
            return -1

        try:
            if self.StationName == self.PIR_NQ:
                if speed != 60 and speed != '':
                    ret = self.SetSpeed_X(speed)
                    if ret != 0:
                        self.strErrorMessage = "MoveToCoordinates_X set speed fail"
                        return -1
                elif speed == 60:
                    ret = self.SetSpeed(60)
                    if ret != 0:
                        self.strErrorMessage = "MoveToCoordinates_X set speed fail"
                        return -1
                # value = (float(value)-0.2211) / 0.9757
                # value = float(value) + float(value) * 0.0204
                if str(type(value)) != "<class 'str'>":
                    value = int(round(value * 110, 2))
                    command = "x_axis_rel_move_to:" + str(value) + "\r\n"
                else:
                    self.strErrorMessage = "input parameters type fail"
                    return -1
                if self.Interpreter == 3:
                    command = command.encode('utf-8')

                for i in range(self.max_retry):
                    self.myMCUSerialPort.write(command)
                    time.sleep(self.delay)
                    readstring = self.myMCUSerialPort.read_all()

                    if self.Interpreter == 3:
                        readstring = readstring.decode('ISO-8859-1')

                    if "X_Axis_Motor_Moving" in readstring:
                        mytimeout = 0
                        while True:
                            if mytimeout > timeout:
                                self.strErrorMessage = 'MoveStep timeout'
                                return -1
                            elif self.ReadOneIOState('x', 33) == 1:
                                if self.ReadOneIOState('x', 6) == 0 or self.ReadOneIOState('x', 7) == 0:
                                    self.strErrorMessage = 'MoveToCoordinates out of limit,need to reset'
                                    return -1
                                else:
                                    return 0
                            else:
                                mytimeout = mytimeout + 0.05
                                time.sleep(0.05)
                                continue
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
            myDelay = 0.005
            # print('write command to get temp = {}'.format(command))
            for i in range(1,4,1):
                self.myThermalSerialPort.write(binascii.unhexlify(command))
                # print("finish write command")
                time.sleep(myDelay*i)
                ret = self.myThermalSerialPort.read(25)
                # print('read port finish {}'.format(ret))
                hex_data = binascii.hexlify(ret)
                # print("data = {}".format(hex_data))
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
                strRead = self.myAngleSerialPort.read(6)########
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
    # set home for angle device
    def SetAngleHome_X(self, model=1):
        try:
            if self.StationName == self.PIR_NQ:
                if model == "68050005000A":
                    command = self.SetAbsoluteHome

                elif model == self.RelativeHome:
                    command = "68050005010B"
                if self.Interpreter == 3:
                    command = command.encode('utf-8')
                self.myAngleSerialPort2.write(binascii.unhexlify(command))
                time.sleep(self.delay)
                strRead = self.myAngleSerialPort2.read(6)  ########
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
            myDely = 0.001
            # range() 函数可创建一个整数列表
            # range(start, stop[, step]) start开始  stop停止，不包括stop（即不包括4） step步长
            for times in range(1,4,1):
                self.myAngleSerialPort.write(self.pullData)
                time.sleep(myDely*times)
                strRead = self.myAngleSerialPort.read(14)
                #binascii.hexlify  转换成二进制数据然后在用十六进制表示
                hex_data = binascii.hexlify(strRead)
                if self.Interpreter == 3:
                    hex_data = hex_data.decode()
                # print(hex_data)
                # print("\n")
                if hex_data[0:2] == "68" and strRead.__len__() == 14:
                    anglex = hex_data[8:14]
                    flag_x = 1 if anglex[0:1] == '0' else -1
                    angley = hex_data[14:20]
                    flag_y = 1 if angley[0:1] == '0' else -1
                    myAnglex = round(float(anglex[1:6])/100.00 * flag_x, 2)
                    myAngley = round(float(angley[1:6])/100.00 * flag_y, 2)
                    myAngleList.append(myAnglex)
                    myAngleList.append(myAngley)
                    # print("get angle_R value")
                    return 0
                else:
                    continue
            self.strErrorMessage = "ReadXAngleAndYAngle timeout"
            return -1
        except Exception as e:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1
    # ********************************************************************#

    # ********************************************************************#
    # get angle
    def ReadXAngleAndYAngle_X(self, myAngleList):
        try:
            if not self.myAngleSerialPort2.is_open:
                self.strErrorMessage = "myAngleSerialPort is no opened"
                return -1
            myDely = 0.01
            # range() 函数可创建一个整数列表
            # range(start, stop[, step]) start开始  stop停止，不包括stop（即不包括4） step步长
            for times in range(1, 4, 1):
                self.myAngleSerialPort2.write(self.pullData)
                time.sleep(myDely * times)
                strRead = self.myAngleSerialPort2.read(14)
                # binascii.hexlify  转换成二进制数据然后在用十六进制表示
                hex_data = binascii.hexlify(strRead)
                if self.Interpreter == 3:
                    hex_data = hex_data.decode()
                print(hex_data)
                print("\n")
                if hex_data[0:2] == "68" and strRead.__len__() == 14:
                    anglex = hex_data[8:14]
                    flag_x = 1 if anglex[0:1] == '0' else -1
                    angley = hex_data[14:20]
                    flag_y = 1 if angley[0:1] == '0' else -1
                    myAnglex = round(float(anglex[1:6]) / 100.00 * flag_x, 2)
                    myAngley = round(float(angley[1:6]) / 100.00 * flag_y, 2)
                    myAngleList.append(myAnglex)
                    myAngleList.append(myAngley)
                    print("get angle_X value")
                    return 0
                else:
                    continue
            self.strErrorMessage = "ReadXAngleAndYAngle about X timeout"
            return -1
        except Exception as e:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1

    # ********************************************************************#


    # ********************************************************************#
    def Set_DoorState(self, direction, timeout=10):
        try:
            # if (self.ReadOneIOState('x', 2) == 0):
                if direction == self.DoorOpen:
                    command = "writeoutput_off:Y11\r\n"
                    respond = "Ouput_OFF_OK"
                    ID = 13
                elif direction == self.DoorClose:
                    command = "writeoutput_on:Y11\r\n"
                    respond = "Ouput_ON_OK"
                    ID = 14


                if self.Interpreter == 3:
                    command = command.encode('utf-8')

                for i in range(self.max_retry):
                    #print("MCU执行命令1")
                    self.myMCUSerialPort.write(command)
                    #print("MCU执行命令2")
                    time.sleep(self.delay)
                    ret = self.myMCUSerialPort.read_all()
                    if self.Interpreter == 3:
                        ret = ret.decode()
                    mytimeout = 0
                    if respond in ret:
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
                self.strErrorMessage = 'dut not in place or dut is loosen'
                return -1
        except Exception as e:
            self.strErrorMessage = "Set_DoorState except fail"
            return -1

# ********************************************************************#


# ********************************************************************#
    def Set_CylinderFunction_1(self, direction,timeout=10):
        if (self.ReadOneIOState('x', 5)  == 1):
            if -1 == self.MoveToCoordinates(0):
                self.strErrorMessage = "MoveToCoordinates to zero fail "
                return -1
        try:
            if self.StationName == 'GQ':
                if self.ReadOneIOState('x', 13) == 1:
                    self.strErrorMessage = 'must door open'
                    print(self.strErrorMessage)
                    return -1


            if True:
                if self.ReadOneIOState('x',17) == 1 and self.ReadOneIOState('x',15) == 0:
                    if direction == self.Out:
                        command_off = "writeoutput_off:Y05\r\n"
                        command = "writeoutput_on:Y06\r\n"
                        ID = 4
                    elif direction == self.In:
                        command_off = "writeoutput_off:Y06\r\n"
                        command = "writeoutput_on:Y05\r\n"
                        ID = 3

                # if self.ReadOneIOState('x', 17) == 1 and self.ReadOneIOState('x',15) == 0:
                #     if direction == self.In:
                #         command_off = "writeoutput_off:Y06\r\n"
                #         command = "writeoutput_on:Y05\r\n"
                #         ID = 3

                if self.Interpreter == 3:
                    command_off = command_off.encode('utf-8')
                    command = command.encode('utf-8')
                
                for i in range(self.max_retry):
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
                                    self.strErrorMessage = "Set_CylindeFunction_1 timeout"
                                    return -1
                                if self.ReadOneIOState('x',ID) == 0:
                                    return 0
                                else:
                                    mytimeout = mytimeout + 0.05
                                    time.sleep(0.05)
                                    continue
                        else:
                            return -1
                
                self.strErrorMessage = "Set_CylindeFunction_1 Off error"
                return -1
            else:
                self.strErrorMessage = "Set_CylindeFunction_1 Off error"
                return -1

        except:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1

        # ********************************************************************#
    # # ********************************************************************#
    # def Set_CylinderFunction_2(self, direction, timeout=10):
    #     if self.ReadOneIOState('x', 5) == 1:
    #         if -1 == self.MoveToCoordinates(0):
    #             self.strErrorMessage = "MoveToCoordinates to zero fail"
    #             return -1
    #
    #     try:
    #         if self.StationName == 'GQ':
    #             if self.ReadOneIOState('x', 20) == 1:
    #                 self.strErrorMessage = 'must door open'
    #                 print(self.strErrorMessage)
    #                 return -1
    #
    #         if True:  # self.ReadOneIOState('x',14) == 0 and self.ReadOneIOState('x',15) == 0:
    #             if direction == self.Out:
    #                 command_off = "writeoutput_off:Y15\r\n"
    #                 command = "writeoutput_on:Y16\r\n"
    #                 ID = 23
    #             elif direction == self.In:
    #                 command_off = "writeoutput_off:Y16\r\n"
    #                 command = "writeoutput_on:Y15\r\n"
    #                 ID = 22
    #
    #             if self.Interpreter == 3:
    #                 command_off = command_off.encode('utf-8')
    #                 command = command.encode('utf-8')
    #
    #             for i in range(self.max_retry):
    #                 self.myMCUSerialPort.write(command_off)
    #                 time.sleep(self.delay)
    #                 ret = self.myMCUSerialPort.read_all()
    #
    #                 if self.Interpreter == 3:
    #                     ret = ret.decode()
    #
    #                 if 'Ouput_OFF_OK' in ret:
    #                     self.myMCUSerialPort.write(command)
    #                     time.sleep(self.delay)
    #                     ret = self.myMCUSerialPort.read_all()
    #                     if self.Interpreter == 3:
    #                         ret = ret.decode()
    #
    #                     if 'Ouput_ON_OK' in ret:
    #                         mytimeout = 0
    #                         while True:
    #                             if mytimeout > timeout:
    #                                 self.strErrorMessage = "Set_CylindeFunction_2 timeout"
    #                                 return -1
    #                             if self.ReadOneIOState('x', ID) == 0:
    #                                 return 0
    #                             else:
    #                                 mytimeout = mytimeout + 0.05
    #                                 time.sleep(0.05)
    #                                 continue
    #                     else:
    #                         return -1
    #             self.strErrorMessage = "Set_CylindeFunction_2 Off error"
    #             return -1
    #         else:
    #             self.strErrorMessage = "Set_CylindeFunction_2 Off error"
    #             return -1
    #
    #     except:
    #         self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
    #         print(self.strErrorMessage)
    #         return -1
    #
    #     # ********************************************************************#



        # ********************************************************************#
    def Set_USB1State(self, direction, timeout=10):
        try:
            if (self.ReadOneIOState('x',16) == 0 and self.ReadOneIOState('x',12 ) == 0):
                if direction == self.USBLock:
                    command = "writeoutput_on:Y10\r\n"
                    confirm = 'Ouput_ON_OK'
                    state = 0
                elif direction == self.USBUnlock:
                    command = "writeoutput_off:Y10\r\n"
                    confirm = 'Ouput_OFF_OK'
                    state = 1
                if self.Interpreter == 3:
                    command = command.encode('utf-8')

                for i in range(self.max_retry):
                    self.myMCUSerialPort.write(command)
                    time.sleep(self.delay)
                    ret = self.myMCUSerialPort.read_all()
                    if self.Interpreter == 3:
                        ret = ret.decode()
                    mytimeout = 0
                    if confirm in ret:
                        while True:
                            if mytimeout > timeout:
                                self.strErrorMessage = "Set_USB1State timeout"
                                return -1
                            if self.ReadOneIOState('x', 14) == state:
                                return 0
                            else:
                                mytimeout = mytimeout + 0.05
                                time.sleep(0.05)
                                continue
                        else:
                            return -1
                    else:
                        self.strErrorMessage = "Set_USBS1tate except error"
                        return -1
            self.strErrorMessage = 'dut not in place or dut is loosen'
            return -1
        except:
            self.strErrorMessage = "Set_USB1State except fail"
            return -1


    # ********************************************************************#

       # ********************************************************************#
    def Set_USB2State(self, direction, timeout=10):
        try:
            if (self.ReadOneIOState('x',17 ) == 0  and self.ReadOneIOState('x',13 ) == 0):
                if direction == self.USBLock:
                    command = "writeoutput_off:Y11\r\n"
                    confirm = 'Ouput_OFF_OK'
                    state = 0
                elif direction == self.USBUnlock:
                    command = "writeoutput_on:Y11\r\n"
                    confirm = 'Ouput_ON_OK'
                    state = 1
                if self.Interpreter == 3:
                    command = command.encode('utf-8')

                for i in range(self.max_retry):
                    self.myMCUSerialPort.write(command)
                    time.sleep(self.delay)
                    ret = self.myMCUSerialPort.read_all()
                    if self.Interpreter == 3:
                        ret = ret.decode()
                    mytimeout = 0
                    if confirm in ret:
                        while True:
                            if mytimeout > timeout:
                                self.strErrorMessage = "Set_USB2State timeout"
                                return -1
                            if self.ReadOneIOState('x', 15) == state:
                                return 0
                            else:
                                mytimeout = mytimeout + 0.05
                                time.sleep(0.05)
                                continue
                        else:
                            return -1
                    else:
                        self.strErrorMessage = "Set_USBS2tate except error"
                        return -1
            self.strErrorMessage = 'dut not in place or dut is loosen'
            return -1
        except:
            self.strErrorMessage = "Set_USB2State except fail"
            return -1


    # ********************************************************************#

    # ********************************************************************#
    # for dut 1
    def Set_DutState1(self, direction, timeout=10):
        try:
            if (self.ReadOneIOState('x', 4) == 0  or self.ReadOneIOState('x', 3) == 1):
                self.strErrorMessage = "lock no ok"
                # print(self.strErrorMessage)
                return -1

            if (self.ReadOneIOState('x', 17) == 0 or self.ReadOneIOState('x',17) == 1)  :
                if direction == self.Dutlock:
                    command = "writeoutput_on:Y07\r\n"
                    confirm = 'Ouput_ON_OK'
                    ID = 17
                    flag = 0
                elif direction == self.DutUnlock:
                    command = "writeoutput_off:Y07\r\n"
                    confirm = 'Ouput_OFF_OK'
                    ID = 17
                    flag = 1
                if self.Interpreter == 3:
                    command = command.encode('utf-8')

                for i in range(self.max_retry):
                    self.myMCUSerialPort.write(command)
                    time.sleep(self.delay)
                    ret = self.myMCUSerialPort.read_all()
                    if self.Interpreter == 3:
                        ret = ret.decode()
                    # mytimeout = 0
                    if confirm in ret:
                        return 0
                        # while True:
                        #     if mytimeout > timeout:
                        #         self.strErrorMessage = "Set_USBState timeout"
                        #         return -1
                        #     if self.ReadOneIOState('x', ID) == flag:
                        #         return 0
                        #     else:
                        #         mytimeout = mytimeout + 0.05
                        #         time.sleep(0.05)
                        #         continue
                        # else:
                        #     return -1
                    else:
                        self.strErrorMessage = "Set_USBState except error"
                        return -1
                self.strErrorMessage = 'dut not in place or usb is lock'
                return -1
        except Exception as e:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1

    # ********************************************************************#

    # ********************************************************************#
    def Set_DutState2(self, direction, timeout=10):
        try:
            # if self.ReadOneIOState('x', 17) == 0 :
            if direction == self.Dutlock:
                command = "writeoutput_on:Y05\r\n"
                command2 = "writeoutput_off:Y06\r\n"
                confirm = 'Ouput_ON_OK'
                confirm2 = 'Ouput_OFF_OK'
                ID = 13
                flag = 0
            elif direction == self.DutUnlock:
                command = "writeoutput_off:Y05\r\n"
                command2 = "writeoutput_on:Y06\r\n"
                confirm = 'Ouput_OFF_OK'
                confirm2 = 'Ouput_ON_OK'
                ID = 13
                flag = 0
            if self.Interpreter == 3:
                command = command.encode('utf-8')
                command2 = command2.encode('utf-8')

            for i in range(self.max_retry):
                self.myMCUSerialPort.write(command)
                time.sleep(self.delay)
                ret = self.myMCUSerialPort.read_all()
                if self.Interpreter == 3:
                    ret = ret.decode()
                mytimeout = 0
                if confirm in ret:
                    # while True:
                    #     if mytimeout > timeout:
                    #         self.strErrorMessage = "Set_Dut State timeout"
                    #         return -1
                    #     if self.ReadOneIOState('x', ID) == flag:
                    #         return 0
                    #     else:
                    #         mytimeout = mytimeout + 0.05
                    #         time.sleep(0.05)
                    #         continue
                    # else:
                    #     return -1
                    return 0
                else:
                    self.strErrorMessage = "Set_USBState except error"
                    return -1
            # self.strErrorMessage = 'dut not in place or usb is lock'
            # return -1

            # for i in range(self.max_retry):
            #     self.myMCUSerialPort.write(command2)
            #     time.sleep(self.delay)
            #     ret = self.myMCUSerialPort.read_all()
            #     if self.Interpreter == 3:
            #         ret = ret.decode()
            #     mytimeout = 0
            #     if confirm2 in ret:
            #         return 0
            #     else:
            #         self.strErrorMessage = "Set_USBState except error"
            #         return -1
            # self.strErrorMessage = 'dut not in place or usb is lock'
            # return -1
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

            for i in range(self.max_retry):
                self.myMCUSerialPort.write(command)
                time.sleep(self.delay)
                ret = self.myMCUSerialPort.read_all()

                if self.Interpreter == 3:
                    ret = ret.decode()

                if result in ret:
                    return 0
            self.strErrorMessage = "SetLight curtain time out"
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

            for i in range(self.max_retry):
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
            self.strErrorMessage = "write command fail"
            return -1
        except Exception as e:
            self.strErrorMessage = "{} except fail {}".format(inspect.stack()[0][3], e)
            print(self.strErrorMessage)
            return -1
    # ********************************************************************#

    # ********************************************************************#
    def ReadValveState(self,valve):
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

            for i in range(self.max_retry):
                self.myMCUSerialPort.write(command)
                time.sleep(self.delay)
                readstring = self.myMCUSerialPort.read_all()
                if len(readstring)>0:
                    if readstring[0] == "Y" and readstring[2] == "=" and int(readstring[1]) == ID:
                        return int(readstring[3])
                    elif readstring[0] == "Y" and 0<= int(readstring[2]) <= 9 and int(readstring[1:3]) == ID:
                        return int(readstring[4])
                    else:
                        self.strErrorMessage = "write command fail"
                        return -1
            self.strErrorMessage = "ReadValveState time out"
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

            for i in range(self.max_retry):
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

            self.strErrorMessage = "readIO_One time out"    
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
    def SetValveState(self,valve,state):
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
            time.sleep(self.delay)
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

            for i in range(self.max_retry):
                self.myMCUSerialPort.write(command)
                readstring = self.myMCUSerialPort.read_all()

                if self.Interpreter == 3:
                    readstring = readstring.decode()

                if readstring.strip() == "R_Axis_Motor_Stop":
                    return 0
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

                    for i in range(self.max_retry):
                        self.myMCUSerialPort.write(command)
                        time.sleep(self.delay)
                        readstring = self.myMCUSerialPort.read_all()

                        if self.Interpreter == 3:
                            readstring = readstring.decode()

                        if readstring.strip() == "R_Axis_Motor_GO_Home_CW":
                            return 0
                    self.strErrorMessage = "write command fail"
                    return -1
                elif direction == 0:
                    command = "r_axis_go_home_ccw\r\n"
                    if self.Interpreter == 3:
                        command = command.encode('utf-8')

                    for i in range(self.max_retry):
                        self.myMCUSerialPort.write(command)
                        time.sleep(self.delay)
                        readstring = self.myMCUSerialPort.read_all()
                        if self.Interpreter == 3:
                            readstring = readstring.decode()
                        if readstring.strip() == "R_Axis_Motor_GO_Home_CCW":
                            return 0
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

    # ********************************************************************#
    def GOEInterface(self, argv):
        try:
            # if (argv.__len__() != 1):
            #     return

            if (argv.__len__() > 2 and argv.__len__() < 5):
                print("The input parameter is wrong")
                self.ThreadingFinish = True

            #单步动作
            if (argv.__len__() == 2):
                Event = str(argv[1])

                #开门
                if Event == "open":
                    ret = self.Set_DoorState(self.DoorOpen)
                    if ret != 0:
                        print("FAIL")
                        print("Set Set_DoorState DoorOpen fail")
                    else:
                        print("PASS")
                #关门
                if Event == "close":
                   ret = self.Set_DoorState(self.DoorClose)
                   if ret != 0:
                       print("FAIL")
                       print("Set Set_DoorState DoorClose fail")
                   else:
                       print("PASS")
                #托盘出
                if Event == "out":
                    # ret = self.Set_DoorState(self.DoorOpen)
                    # if ret != 0:
                    #     print("FAIL")
                    #     print("Set Set_DoorState DoorOpen fail")
                    ret = self.Set_CylinderFunction_1(self.Out)
                    if ret != 0:
                        print("FAIL")
                        print("Set Set_CylinderFunction_1 Out fail")
                    else:
                        print("PASS")
                #托盘进
                if Event == "in":
                    # ret = self.Set_DutState1(self.DutUnlock)
                    # if ret != 0:
                    #     print("FAIL")
                    #     print("Set Set_DutState1 DutUnlock fail")
                    ret = self.Set_CylinderFunction_1(self.In)
                    if ret != 0:
                        print("FAIL")
                        print("Set Set_CylinderFunction_1 In fail")
                    else:
                        print("PASS")

                #dut 真空吸
                if Event == "holdon":
                    if self.ReadOneIOState('x',6)==0:
                        ret = self.SignalReSet()
                    ret = self.Set_DutState1(self.Dutlock)
                    if ret != 0:
                        print("FAIL")
                        print("Set Set_DutState1 Dutlock fail")
                    else:
                        print("PASS")

                #dut 真空松
                if Event == "holdoff":
                    ret = self.Set_DutState1(self.DutUnlock)
                    if ret != 0:
                        print("FAIL")
                        print("Set Set_DutState1 DutUNlock fail")
                    else:
                        print("PASS")
                #dut 锁
                if Event == "lock":
                    ret = self.Set_DutState2(self.Dutlock)
                    if ret != 0:
                        print("FAIL")
                        print("Dut lock fail")
                    else:
                        print("PASS")

                #dut 松
                if Event == "unlock":
                    ret = self.Set_DutState2(self.DutUnlock)
                    if ret != 0:
                        print("FAIL")
                        print("Dut unlock fail")
                    else:
                        print("PASS")

                #复位
                if Event == "reset":
                    ret = self.SignalReSet()
                    if ret != 0:
                        print("FAIL")
                        print("Set SignalReSet  fail")
                    else:
                        print("PASS")
                #上电
                if Event == "up":
                    ret = self.Set_Power(self.PowerUp)
                    if ret != 0:
                        print("FAIL")
                        print("Set Set_Power PowerUp fail")
                    else:
                        print("PASS")
                #断电
                if Event == "down":
                    ret = self.Set_Power(self.PowerDown)
                    if ret != 0:
                        print("FAIL")
                        print("Set Set_Power PowerDown fail")
                    else:
                        print("PASS")
                #USB打开
                if Event == "on":
                    ret = self.Set_USB(self.USBOn)
                    if ret != 0:
                        print("FAIL")
                        print("Set Set_USB USBOn fail")
                    else:
                        print("PASS")
                #USB关闭
                if Event == "off":
                    ret = self.Set_USB(self.USBOff)
                    if ret != 0:
                        print("FAIL")
                        print("Set Set_USB USBOff fail")
                    else:
                        print("PASS")

                parameter_list = ["open","close","in","out","lock","unlock","up","down","reset","on","off"]
                if (Event not in parameter_list):
                    print("The input parameter is wrong")

                self.ThreadingFinish = True

            #单步移动
            elif (argv.__len__() == 5):
                Axid = str(argv[1])
                Move = int(argv[2])
                Speed = int(argv[3])
                Delay = float(argv[4])
                Delay = Delay /1000

                if Axid == "R":
                    # ret = self.SetSpeed(Speed)
                    time.sleep(Delay)
                    ret = self.MoveToCoordinates(value=Move, speed=Speed)
                    print("PASS")
                    self.ThreadingFinish = True
                if Axid == "X":
                    # ret = self.SetSpeed_X(Speed)
                    time.sleep(Delay)
                    ret = self.MoveToCoordinates_X(value=Move, speed=Speed)
                    print("PASS")
                    self.ThreadingFinish = True

                # self.ThreadingFinish == True

            # 边跑边抓数据
            elif (argv.__len__() > 6):
                # if(argv.__len__() == 7):

                TotalTime = float(argv[1])  #持续时间
                TotalTime = TotalTime/1000.00
                frequency = float(argv[2])  #间隔时间
                frequency = frequency/1000.00

                fileName = str(argv[3])     #文件名
                filePath = str(argv[4])     #文件保存路径
                Move1 = int(argv[5])        #移动距离
                Delay1 = float(argv[6])     #延迟 是指延迟几秒后执行线程  时间单位都是毫秒
                Delay1 = Delay1 / 1000.00
                    # Stride = 5
                # elif (argv.__len__() == 7):
                #     TotalTime = int(argv[1])
                #     frequency = int(argv[2])
                #     fileName = str(argv[3])
                #     filePath = str(argv[4])
                #     Move = int(argv[5])
                #     Delay = float(argv[6])
                #     Delay = Delay / 1000.00
                #     Stride = int(argv[7])

                # add 2021-1-18
                # 这里转动标靶轴
                # 获取当前位置,判断标靶轴应该是往正方向走还是负方向走
                datalist = []
                self.ReadXAngleAndYAngle(datalist)
                # print("获取当前位置：" + str(datalist[0]))
                if (datalist[0] > 0 or datalist[0] == 0):
                    Move1 = Move1 * -1
                    Move = 90
                else:
                    Move1 = Move1
                    Move = 0
                # print("检查值是否有改变：" + str(Move1))

                try:
                    time.sleep(Delay1)
                    Speed = 98
                    Speed_x = 39
                    # ret = self.MoveToCoordinates(value=0, speed=90)
                    # ret = self.SignalReSet()
                    # print("复位成功")

                    # acionThread = threading.Thread(target=self.TestMove,args=(Move1,))
                    # acionThread.start()

                    #双线程
                    recordThread = threading.Thread(target=self.GetAngleAndTemperature, args=(TotalTime,frequency,fileName,filePath))
                    recordThread.start()
                    recordThread = threading.Thread(target=self.GetAngleAndTemperature1, args=(TotalTime, frequency, fileName, filePath))
                    recordThread.start()

                    ret = self.MoveToCoordinates(value=Move1, speed=Speed)
                    # self.RotateAxisThreadingFinish = True
                    self.GetTemperature = True

                    # ret = self.MoveToCoordinates_X(value=Move, speed=Speed_x)

                    # ret = self.MoveToCoordinates(value=0,speed=90)
                    # acionThread.join()
                    # recordThread.join()
                except Exception as e:
                    print ("Error: unable to start thread {}".format(e))

        except Exception as e:
            print("GOE Interface except fail {}".format(e))
            return e

    # ********************************************************************#
    def GetAngleAndTemperature(self,TotalTime,frequency,fileName,filePath):
        # print('hello, this is get sensor value thread')
        count = 0
        timeout = 0
        i = 0
        Transfer = 0
        angle_device = []
        angle_target = []
        # content = []
        try:
            while (True):
                # print('hello, this is while true')
                if (self.RotateAxisThreadingFinish == True):
                    self.ThreadingFinish = True
                    #print("移动结束，不在记录")
                    break
                else:
                    if (TotalTime > timeout):
                        # 时戳获取
                        Time_stamp = round(time.time(), 3)
                        Time_stamp = int((Time_stamp * 1000))
                        time_start = time.time()
                        self.ReadXAngleAndYAngle(angle_device)  # 标靶轴
                        # self.ReadXAngleAndYAngle_X(angle_target)  # Dut轴
                        # target_temperature = self.GetCurrentTemperature(self.LCD1)
                        # room_temperature = self.GetCurrentTemperature(self.LCD4)

                        data_path_file = os.path.join(filePath, fileName + '.txt')
                        # with open(data_path_file, 'a') as f:
                        list = (str(Time_stamp)+",")
                        # list1 = (str(angle_device[i])+",")
                        list1 = (str(angle_device[i]) + ",")
                        # list2 = (str(target_temperature) + ",")
                        # list3 = (str(room_temperature) + "\n")

                        # list = (str(Time_stamp)+ "," + str(angle_device[i])+ "," + str(target_temperature) + "\n")
                        self.content.append(list)
                        self.content2.append(list1)
                        timeout = timeout + frequency
                        i = i+2
                        if (self.GetTemperature == False):
                            Transfer = i
                        else:
                            i = Transfer
                        # count = count+1
                        #print("第"+ str(count) +"次")
                        #print("已经记录了：" + str(timeout) +"秒")
                        time_end = time.time()
                        consuming_time = time_end - time_start
                        consuming_time = round(consuming_time, 3)
                        # print("线程1消耗了：" + str(consuming_time))
                        real_time = frequency - consuming_time
                        if real_time<0:
                            real_time = 0
                            # print("***************1 real time < 0 ************")
                        # print("这是线程1休眠时间：" + str(real_time))
                        # real_time = real_time - 0.001
                        time.sleep(real_time)
                # else:
                    # self.RotateAxisThreadingFinish = True
                    # file = open(data_path_file, 'w')
                    # for i in range(len(self.content)):
                    #     s = str(self.content[i]).replace('[', '').replace(']', '')  # 去除[],这两行按数据不同，可以选择
                    #     file.write(s)
                    # file.close()
                    # #print("时间结束")
        except Exception as e:
            print("GOE Interface except fail {}".format(e))
            return e
    # ********************************************************************#
    def GetAngleAndTemperature1(self,TotalTime,frequency,fileName,filePath):
        # print('hello, this is get sensor value thread')
        count = 0
        i = 0
        timeout = 0
        Transfer = 0
        angle_device = []
        angle_target = []


        # content = []
        try:
            while (True):
                # print('hello, this is while true')
                if (self.RotateAxisThreadingFinish == True):
                    self.ThreadingFinish = True
                    # print("移动结束，不在记录")
                    break
                else:
                    if (TotalTime > timeout):
                        time_start = time.time()
                        # self.ReadXAngleAndYAngle(angle_device)  # 标靶轴
                        # self.ReadXAngleAndYAngle_X(angle_target)  # Dut轴
                        target_temperature = self.GetCurrentTemperature(self.LCD1)
                        room_temperature = self.GetCurrentTemperature(self.LCD4)
                        # list1 = (str(angle_device[i]) + ",")
                        list2 = (str(target_temperature)+",")
                        list3 = (str(room_temperature)+ "\n")

                        self.content1.append(list2)
                        self.content3.append(list3)

                        timeout = timeout + frequency
                        i = i + 2
                        if (self.GetTemperature == False):
                            Transfer = i
                        else:
                            i = Transfer

                        count = count+1
                        # print("第"+ str(count) +"次")
                        # print("已经记录了：" + str(timeout) +"秒")

                        time_end = time.time()
                        consuming_time = time_end - time_start
                        consuming_time = round(consuming_time, 3)
                        real_time = frequency - consuming_time
                        # print("线程2消耗了："+ str(consuming_time))
                        if real_time < 0:
                            real_time = 0
                            # print("**************2 real_time<0 *****************")
                        # print("这是线程2休眠时间：" + str(real_time))
                        # print("###############################################################")
                        time.sleep(real_time)
                    else:
                        self.RotateAxisThreadingFinish = True
                        data_path_file = os.path.join(filePath, fileName + '.txt')
                        file = open(data_path_file, 'w')
                        for i in range(len(self.content1)):
                            s = str(self.content[i]).replace('[', '').replace(']', '')                                                                          # 去除[],这两行按数据不同，可以选择
                            s1 = str(self.content1[i]).replace('[', '').replace(']', '')
                            s2 = str(self.content2[i]).replace('[', '').replace(']', '')
                            s3 = str(self.content3[i]).replace('[', '').replace(']', '')
                            file.write(s)
                            file.write(s2)
                            file.write(s1)
                            file.write(s3)
                        file.close()
                        # print("记录结束")
        except Exception as e:
            print("GOE Interface except fail {}".format(e))
            return e
    # # ********************************************************************#

    # ********************************************************************#
    # def GetAngleAndTemperature2(self,TotalTime,frequency,fileName,filePath):
    #     # print('hello, this is get sensor value thread')
    #     count = 0
    #     timeout = 0
    #     Transfer = 0
    #     angle_device = []
    #     angle_target = []
    #     # content = []
    #
    #     while (True):
    #         # print('hello, this is while true')
    #         if (self.RotateAxisThreadingFinish == True):
    #             self.ThreadingFinish = True
    #             #print("移动结束，不在记录")
    #             break
    #         else:
    #             if (TotalTime > timeout):
    #                 time_start = time.time()
    #                 room_temperature = self.GetCurrentTemperature(self.LCD4)
    #                 data_path_file = os.path.join(filePath, fileName + '.txt')
    #                 list3 = (str(room_temperature)+ "\n")
    #                 self.content.append(list3)
    #                 timeout = timeout + frequency
    #
    #                 count = count+1
    #                 print("第"+ str(count) +"次")
    #                 print("已经记录了：" + str(timeout) +"秒")
    #
    #                 time_end = time.time()
    #                 consuming_time = time_end - time_start
    #                 consuming_time = round(consuming_time, 3)
    #                 real_time = frequency - consuming_time
    #
    #                 print("消耗了："+ str(consuming_time))
    #                 if real_time < 0:
    #                     real_time = 0
    #                 time.sleep(real_time)
    #             # else:
    #                 self.RotateAxisThreadingFinish = True
    #                 file = open(data_path_file, 'w')
    #                 for i in range(len(self.content)):
    #                     s = str(self.content[i]).replace('[', '').replace(']', '')  # 去除[],这两行按数据不同，可以选择
    #                     file.write(s)
    #                 file.close()
    #                 print("时间结束")
    # # # ********************************************************************#

    # ********************************************************************#
    def TestMove(self,Move1):
        if (self.RotateAxisThreadingFinish == False):
            Speed = 92
            ret = self.MoveToCoordinates(value = Move1,speed = Speed)
            self.RotateAxisThreadingFinish = True
    # ********************************************************************#

if __name__ == '__main__':
    # 0.instance class
    GOE = MCUControl("GQ")

    # 1.open device port txt
    # SerialportName = "BojayDevice.txt"
    #with open(SerialportName, "r") as f:
        #MCUPortName = str((f.readline().split("="))[1].replace("\n", "").replace(" ", ""))
        #AnglePortName = str((f.readline().split("="))[1].replace("\n", "").replace(" ", ""))
        #AnglePortName2 = str((f.readline().split("="))[1].replace("\n", "").replace(" ", ""))
        #TempPortName = str((f.readline().split("="))[1].replace("\n", "").replace(" ", ""))
        #f.close()
 
    ret = GOE.OpenSerial(GOE.SwitchMCU, "COM8")
    ret = GOE.OpenSerial(GOE.SwitchAngle1, "COM11")
    ret = GOE.OpenSerial(GOE.SwitchAngle2, "COM9")
    ret = GOE.OpenSerial(GOE.SwitchThermal, "COM10")



    # ret = GOE.OpenSerial(GOE.SwitchMCU, "COM7")
    # ret = GOE.OpenSerial(GOE.SwitchAngle1, "COM9")
    # ret = GOE.OpenSerial(GOE.SwitchAngle2, "COM8")
    # ret = GOE.OpenSerial(GOE.SwitchThermal, "COM10")


    # 2.convert parametres vector
    GOE.GOEInterface(sys.argv)
    while (True):
         if (GOE.ThreadingFinish == False):
            time.sleep(1)
            # print('running...........')
         else:
             # print("子线程结束，执行完成")
             break


    GOE.CloseSerial(GOE.SwitchMCU)
    GOE.CloseSerial(GOE.SwitchThermal)
    GOE.CloseSerial(GOE.SwitchAngle1)
    GOE.CloseSerial(GOE.SwitchAngle2)
    # print("finish main thread")

