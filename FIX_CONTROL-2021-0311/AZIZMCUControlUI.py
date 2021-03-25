#-*-coding:utf-8-*-
from PySide2 import QtCore,QtGui,QtWidgets
from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QDialog,QMessageBox
from PySide2.QtGui import QPalette,QColor
import inspect
import  sys
from UI import *
from AZIZMCUControlAPI import *
import threading
import datetime
import os
import time
# import pandas as pd
# import openpyxl
myMCUControl = MCUControl('GQ')


# MCUPortName="COM6"
# AnglePortName="COM5"
# AnglePortName2 = "COM4"
# TempPortName="COM8"

MCUPortName = "COM8"
AnglePortName = "COM11"
AnglePortName2 = "COM9"
TempPortName = "COM10"



class MuduFrame(QDialog):

    def __init__(self, parent=None):
        try:
            super(MuduFrame,self).__init__(parent)
            self.ui = Ui_Form()
            self.ui.setupUi(self)
            self.ErrorMessage = ""

            #PassWord
            self.ui.BtnPassword.clicked.connect(lambda: self.SetPassword())

            # MCU
            self.ui.BtOpenportContorl.clicked.connect(lambda :self.OpenSerial("MCU"))
            self.ui.BtCloseportContorl.clicked.connect(lambda :self.CloseSerial("MCU"))

            # R Motor Move
            self.ui.ButtonSetServoSpeed.clicked.connect(self.SetServoSpeed)
            self.ui.ButtonAbsoluteMove.clicked.connect(self.SetAbsoluteMove)
            self.ui.ButtonRelativeMove.clicked.connect(self.SetRelativeMove)

            # X Motor Move
            self.ui.ButtonSetServoSpeed_X.clicked.connect(self.SetServoSpeed_X)
            self.ui.ButtonAbsoluteMove_X.clicked.connect(self.SetAbsoluteMove_X)
            self.ui.ButtonRelativeMove_X.clicked.connect(self.SetRelativeMove_X)

            self.ui.ButtonCloseDoor.clicked.connect(lambda :self.Set_DoorState('Close'))
            self.ui.ButtonOpenDoor.clicked.connect(lambda :self.Set_DoorState('Open'))

            self.ui.ButtonCylinderIN_1.clicked.connect(lambda: self.Set_Cylinder_1('IN'))
            self.ui.ButtonCylinderOUT_1.clicked.connect(lambda: self.Set_Cylinder_1('OUT'))

            self.ui.ButtonCylinderIN_2.clicked.connect(lambda: self.Set_Cylinder_2('IN'))
            self.ui.ButtonCylinderOUT_2.clicked.connect(lambda: self.Set_Cylinder_2('OUT'))

            self.ui.BtUSBLock.clicked.connect(lambda: self.Set_USB1State('lock'))
            self.ui.BtUSBUnlock.clicked.connect(lambda: self.Set_USB1State('unlock'))

            self.ui.BtUSBLock_2.clicked.connect(lambda: self.Set_USB2State('lock'))
            self.ui.BtUSBUnlock_2.clicked.connect(lambda: self.Set_USB2State('unlock'))

            self.ui.BtDutLock.clicked.connect(lambda: self.Set_DutState1('lock'))
            self.ui.BtDutUnlock.clicked.connect(lambda: self.Set_DutState1('unlock'))

            self.ui.BtDutLock_2.clicked.connect(lambda: self.Set_DutState2('lock'))
            self.ui.BtDutUnlock_2.clicked.connect(lambda: self.Set_DutState2('unlock'))

            self.ui.ButtonSignalReset.clicked.connect(lambda: self.actionReset())
            self.ui.BtSetMotorStop.clicked.connect(lambda: self.SetMotorStop())


            # self.ui.ButtonBurningStart.clicked.connect(lambda: self.Burning())
            self.ui.ButtonBurningStart.clicked.connect(lambda: self.Burning1())

            self.ui.ButtonGetSensorState.clicked.connect(self.GetSensorState)

            # Motor Validation
            self.ui.ButtonMotorValidation_2.clicked.connect(lambda :self.MotorValidation())

            # temperature
            self.ui.BtOpenportShow.clicked.connect(lambda: self.OpenSerial("TempAndAngle"))
            self.ui.BtCloseportShow.clicked.connect(lambda: self.CloseSerial("TempAndAngle"))

            # Automic Read Temperature
            self.ui.BtAutomaticGet.clicked.connect(self.GetTemperatureAndAngle)
            self.ui.BtAutomaticStop.clicked.connect(self.StopTemperatureAndAngle)

            # 上电
            self.ui.BtPower_Up.clicked.connect(lambda: self.Power('Up'))
            self.ui.BtPower_Down.clicked.connect(lambda: self.Power('Down'))

            # USB控制
            self.ui.BtUSB_On.clicked.connect(lambda: self.USB('On'))
            self.ui.BtUSB_Off.clicked.connect(lambda: self.USB('Off'))


            self.target = 0
            self.CH2_Temp = 0
            self.CH3_Temp = 0
            self.indoor = 0
            self.different = 0

            self.xValue = 0
            self.yValue = 0
            self.xValue_X = 0
            self.yValue_X = 0
            self.angle_ret = 0

            self.start_get_temperature = False
            self.timer_temp = QTimer()
            self.timer_temp.timeout.connect(self.ShowTimer)

            # set target temperature
            self.ui.BtSetTargetTemperature.clicked.connect(self.SetTargetTemperature)

            # Temperature Validation
            self.ui.BtTemperatureValidation.clicked.connect(self.TemperatureValidation)
            self.temperature_validation_end = False
            self.timer_temp_validation = QTimer()
            self.timer_temp_validation.timeout.connect(self.ShowTemperatureTimer)

            self.ui.BtSetToZero.clicked.connect(self.SetToZero)
            self.ui.BtSetToZero_X.clicked.connect(self.SetToZero_X)

            # Step validation
            self.ui.BtStepValidation.clicked.connect(lambda :self.StepValidation())
            self.step_validation_end = False
            self.timer_step = QTimer()
            self.timer_step.timeout.connect(self.ShowStepTimer)

            # Angle validation
            self.ui.BtAngleValidation.clicked.connect(lambda :self.AngleValidation())
            self.move_axis_stop = False
            self.angle_validation_end = False
            self.count = 0
            self.DataTimeStart = ""
            self.writer = None

            # get  current Sensor state
            filepath = os.getcwd()
            filepath += "/SensorIoConfig.txt"
            with open(filepath, 'rb') as output:
                readstring = output.readlines()
                string = readstring[0].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor1.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor1.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[1].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor2.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor2.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[2].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor3.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor3.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[3].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor4.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor4.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[4].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor5.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor5.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[5].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor6.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor6.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[6].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor7.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor7.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[7].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor8.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor8.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[8].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor9.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor9.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[9].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor10.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor10.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[10].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor11.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor11.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[11].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor12.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor12.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[12].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor13.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor13.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[13].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor14.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor14.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[14].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor15.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor15.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[15].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor16.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor16.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[16].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor17.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor17.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[17].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor18.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor18.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[18].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor19.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor19.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[19].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor20.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor20.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[20].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor21.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor21.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[21].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor22.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor22.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[22].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor23.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor23.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[23].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor24.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor24.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[24].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor25.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor25.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[25].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor26.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor26.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[26].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor27.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor27.setStyleSheet("background-color: rgb(0, 255, 0);")
                string = readstring[27].strip()
                if int(string[len(string)-1]) == 1:
                    self.ui.labelSensor28.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    self.ui.labelSensor28.setStyleSheet("background-color: rgb(0, 255, 0);")
                output.close()

            self.ui.BtCloseportContorl.setEnabled(0)
            self.ui.ButtonSetServoSpeed.setEnabled(0)
            self.ui.BtnPassword.setEnabled(0)
            self.ui.ButtonSetServoSpeed_X.setEnabled(0)

            self.ui.ButtonRelativeMove.setEnabled(0)
            self.ui.ButtonAbsoluteMove.setEnabled(0)
            self.ui.ButtonRelativeMove_X.setEnabled(0)
            self.ui.ButtonAbsoluteMove_X.setEnabled(0)

            self.ui.ButtonCylinderIN_1.setEnabled(0)
            self.ui.ButtonCylinderOUT_1.setEnabled(0)
            self.ui.ButtonCylinderIN_2.setEnabled(0)
            self.ui.ButtonCylinderOUT_2.setEnabled(0)
            self.ui.BtUSBLock.setEnabled(0)
            self.ui.BtUSBUnlock.setEnabled(0)
            self.ui.BtUSBLock_2.setEnabled(0)
            self.ui.BtUSBUnlock_2.setEnabled(0)
            self.ui.BtAutomaticGet.setEnabled(0)
            # self.ui.BtAutomaticGet.setEnabled(0)
            self.ui.BtCloseportShow.setEnabled(0)
            self.ui.BtCloseportContorl.setEnabled(0)
            self.ui.BtSetTargetTemperature.setEnabled(0)
            self.ui.BtTemperatureValidation.setEnabled(0)

            self.ui.BtDutLock.setEnabled(0)
            self.ui.BtDutUnlock.setEnabled(0)
            self.ui.BtDutLock_2.setEnabled(0)
            self.ui.BtDutUnlock_2.setEnabled(0)
            self.ui.BtPower_Up.setEnabled(0)
            self.ui.BtPower_Down.setEnabled(0)
            self.ui.BtUSB_On.setEnabled(0)
            self.ui.BtUSB_Off.setEnabled(0)


            self.ui.ButtonSignalReset.setEnabled(0)
            self.ui.BtSetMotorStop.setEnabled(0)
            self.ui.ButtonBurningStart.setEnabled(1)
            self.ui.ButtonGetSensorState.setEnabled(0)
            self.ui.BtSetToZero.setEnabled(0)
            self.ui.BtSetToZero_X.setEnabled(0)
            self.ui.BtAutomaticStop.setEnabled(0)
            self.ui.BtAngleValidation.setEnabled(0)
            self.ui.BtStepValidation.setEnabled(0)
            self.ui.ButtonMotorValidation.setEnabled(0)
            self.ui.ButtonCloseDoor.setEnabled(0)
            self.ui.ButtonOpenDoor.setEnabled(0)
            self.ui.radioGQ.setChecked(1)
            self.ui.BtUSBLock_2.setEnabled(0)
            self.ui.BtUSBUnlock_2.setEnabled(0)
        except Exception as e:
            self.ShowErrorMessage("__init__  except Fail {}".format(e))

#*********************************************************************************
    def Power(self, state):
        try:
            if state == 'Up':
                ret = myMCUControl.Set_Power(myMCUControl.PowerUp)
                if ret != 0:
                    self.ui.labelError.setText("Set Power On State fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.ui.labelError.setText("Set Power On pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                return 0

            elif state == 'Down':
                ret = myMCUControl.Set_Power(myMCUControl.PowerDown)
                if ret != 0:
                    self.ui.labelError.setText("Set Power Off State fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.ui.labelError.setText("Set Power Off pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                return 0
        except Exception as e:
            self.ui.labelError.setText("Set_DoorState  except fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
#*********************************************************************************

#*********************************************************************************
    def USB(self, state):
        try:
            if state == 'On':
                ret = myMCUControl.Set_USB(myMCUControl.USBOn)
                if ret != 0:
                    self.ui.labelError.setText("Set USB On State fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.ui.labelError.setText("Set USB On pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                return 0

            elif state == 'Off':
                ret = myMCUControl.Set_USB(myMCUControl.USBOff)
                if ret != 0:
                    self.ui.labelError.setText("Set USB Off State fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.ui.labelError.setText("Set USB Off pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                return 0
        except Exception as e:
            self.ui.labelError.setText("Set_DoorState  except fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")

# *********************************************************************************

# ********************************Password****************************************
    def SetPassword(self):
        try:
            if self.ui.textEditPassword.toPlainText() == "Bojay":
                self.ui.BtSetToZero.setEnabled(1)
                self.ui.BtSetToZero_X.setEnabled(1)
                return 0
            else:
                self.ShowErroeMessage("Please input correct Password")
                return -1
        except:
            self.ShowErroeMessage("Set Password except error")
            return -1
# ********************************Password****************************************
# **************************open serial port**************************************
    def OpenSerial(self, flags):
        try:
            if flags == "TempAndAngle":
                ret = myMCUControl.OpenSerial(myMCUControl.SwitchThermal,TempPortName)
                if ret != 0:
                    # self.ShowErrorMessage("open temperature show port fail")
                    self.ui.labelError.setText("open temperature show port fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.ui.labelError.setText("open temperature show port pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                self.ui.BtOpenportShow.setEnabled(0)
                self.ui.BtAutomaticGet.setEnabled(1)
                self.ui.BtCloseportShow.setEnabled(1)
                self.ui.BtTemperatureValidation.setEnabled(1)
                self.ui.BtStepValidation.setEnabled(1)
                self.ui.BtAngleValidation.setEnabled(1)
                self.ui.BtSetTargetTemperature.setEnabled(1)

                ret = myMCUControl.OpenSerial(myMCUControl.SwitchAngle1,AnglePortName)
                if ret == -1:
                    # self.ShowErrorMessage("open Angle control port fail ")
                    self.ui.labelError.setText("open Angle control port fail ")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.ui.labelError.setText("open Angle control port pass ")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                # self.ui.BtSetToZero.setEnabled(1)

                ret = myMCUControl.OpenSerial(myMCUControl.SwitchAngle2, AnglePortName2)
                if ret == -1:
                    # self.ShowErrorMessage("open Angle control port fail ")
                    self.ui.labelError.setText("open Angle control port fail ")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.ui.labelError.setText("open Angle_X control port pass ")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                # self.ui.BtSetToZero.setEnabled(1)



            elif flags == "MCU":
                # ret = myMCUControl.OpenSerial(myMCUControl.SwitchAngle2, AnglePortName2)
                # if ret == -1:
                #     # self.ShowErrorMessage("open Angle control port fail ")
                #     self.ui.labelError.setText("open Angle_X control port fail ")
                #     self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                #     return -1
                # self.ui.labelError.setText("open Angle_X control port pass ")
                # self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")

                ret = myMCUControl.OpenSerial(myMCUControl.SwitchMCU,MCUPortName)
                if ret == -1:
                    # self.ShowErrorMessage("open MCU control port fail ")
                    self.ui.labelError.setText("open MCU control port fail ")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.ui.labelError.setText("open MCU control port pass ")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                self.ui.BtOpenportContorl.setEnabled(0)
                self.ui.BtCloseportContorl.setEnabled(1)
                self.ui.ButtonSetServoSpeed.setEnabled(1)
                self.ui.ButtonSetServoSpeed_X.setEnabled(1)
                self.ui.BtnPassword.setEnabled(1)

                self.ui.ButtonRelativeMove.setEnabled(1)
                self.ui.ButtonAbsoluteMove.setEnabled(1)
                self.ui.ButtonRelativeMove_X.setEnabled(1)
                self.ui.ButtonAbsoluteMove_X.setEnabled(1)
                self.ui.BtPower_Up.setEnabled(1)
                self.ui.BtPower_Down.setEnabled(1)
                self.ui.BtUSB_On.setEnabled(1)
                self.ui.BtUSB_Off.setEnabled(1)

                self.ui.ButtonGetSensorState.setEnabled(1)
                self.ui.ButtonCylinderOUT_1.setEnabled(1)
                self.ui.ButtonCylinderIN_1.setEnabled(1)
                self.ui.ButtonSignalReset.setEnabled(1)
                self.ui.BtSetMotorStop.setEnabled(1)
                self.ui.ButtonBurningStart.setEnabled(1)
                self.ui.ButtonMotorValidation.setEnabled(1)

                if self.ui.radioGQ.isChecked():
                    self.ui.BtUSBUnlock.setEnabled(1)
                    self.ui.BtUSBLock.setEnabled(1)
                    self.ui.BtDutUnlock.setEnabled(1)
                    self.ui.BtDutLock.setEnabled(1)

                    self.ui.BtDutUnlock_2.setEnabled(1)
                    self.ui.BtDutLock_2.setEnabled(1)

                    self.ui.ButtonOpenDoor.setEnabled(1)
                    self.ui.ButtonCloseDoor.setEnabled(1)
                    self.ui.BtUSBUnlock_2.setEnabled(1)
                    self.ui.BtUSBLock_2.setEnabled(1)
                    self.ui.ButtonCylinderOUT_2.setEnabled(1)
                    self.ui.ButtonCylinderIN_2.setEnabled(1)


        except Exception as e:
            self.ui.labelError.setText("open serial except fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
            # self.ShowErrorMessage("open serial except fail")
            return -1
# **************************open serial port***************************************

# **************************close serial port***************************************
    def CloseSerial(self,flag):
        try:
            if flag == "MCU":
                ret = myMCUControl.CloseSerial(myMCUControl.SwitchMCU)
                if ret != 0:
                    # self.ShowErrorMessage("close MCU control port fail ")
                    self.ui.labelError.setText("close MCU control port fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.ui.labelError.setText("close MCU control port pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                self.ui.BtOpenportContorl.setEnabled(1)
                self.ui.BtCloseportContorl.setEnabled(0)
                self.ui.ButtonSetServoSpeed.setEnabled(0)

                self.ui.ButtonRelativeMove.setEnabled(0)
                self.ui.ButtonAbsoluteMove.setEnabled(0)
                self.ui.ButtonRelativeMove_X.setEnabled(0)
                self.ui.ButtonAbsoluteMove_X.setEnabled(0)

                self.ui.ButtonGetSensorState.setEnabled(0)
                self.ui.BtDutUnlock.setEnabled(0)
                self.ui.BtDutLock.setEnabled(0)
                self.ui.ButtonCylinderOUT_1.setEnabled(0)
                self.ui.ButtonCylinderIN_1.setEnabled(0)
                self.ui.ButtonCylinderOUT_2.setEnabled(0)
                self.ui.ButtonCylinderIN_2.setEnabled(0)
                self.ui.BtUSBUnlock.setEnabled(0)
                self.ui.BtUSBLock.setEnabled(0)
                self.ui.ButtonSignalReset.setEnabled(0)
                self.ui.BtSetMotorStop.setEnabled(0)
                self.ui.ButtonBurningStart.setEnabled(0)
                self.ui.ButtonMotorValidation.setEnabled(0)
                self.ui.ButtonOpenDoor.setEnabled(0)
                self.ui.ButtonCloseDoor.setEnabled(0)
                self.ui.BtUSBUnlock_2.setEnabled(0)
                self.ui.BtUSBLock_2.setEnabled(0)
                self.ui.BtPower_Up.setEnabled(0)
                self.ui.BtPower_Down.setEnabled(0)
                self.ui.BtUSB_On.setEnabled(0)
                self.ui.BtUSB_Off.setEnabled(0)
            elif flag == "TempAndAngle":
                ret = myMCUControl.CloseSerial(myMCUControl.SwitchThermal)
                if ret != 0:
                    # self.ShowErrorMessage("close thermal control port fail ")
                    self.ui.labelError.setText("close thermal control port fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.ui.labelError.setText("close thermal control port pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                self.ui.BtAutomaticGet.setEnabled(0)
                self.ui.BtOpenportShow.setEnabled(1)
                self.ui.BtCloseportShow.setEnabled(0)
                self.ui.BtTemperatureValidation.setEnabled(0)
                self.ui.BtSetTargetTemperature.setEnabled(0)
                ret = myMCUControl.CloseSerial(myMCUControl.SwitchAngle1)
                if ret != 0:
                    # self.ShowErrorMessage("close Angle control port fail ")
                    self.ui.labelError.setText( "close Angle control port fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.ui.labelError.setText("close Angle control port pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                # self.ui.BtSetToZero.setEnabled(0)
                self.ui.BtAngleValidation.setEnabled(0)
                self.ui.BtStepValidation.setEnabled(0)
        except Exception as e:
            # self.ShowErrorMessage("open serial except fail")
            self.ui.labelError.setText("CloseSerial except fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
            return -1

# **************************close serial port***************************************

# **************************Set Servo Speed***************************************
    def SetServoSpeed(self):
        try:
            value= self.ui.EditServoSpeed.text()
            ret =  myMCUControl.SetSpeed(float(value))
            if ret == -1:
                # self.ShowErrorMessage(myMCUControl.strErrorMessage)
                self.ui.labelError = "Set speed for axis fail"
                self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                return -1
            self.ui.labelError.setText("Set speed for axis pass")
            self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
            # self.ShowErrorMessage('Set speed ok')
        except:
            # self.ShowErrorMessage("SetServoSpeed  except fail")
            self.ui.labelError.setText("SetServoSpeed  except fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
# **************************Set Servo Speed***************************************

# **************************Set Servo Speed***************************************
    def SetServoSpeed_X(self):
        try:
            value = self.ui.EditServoSpeed_X.text()
            ret = myMCUControl.SetSpeed_X(float(value))
            if ret == -1:
                # self.ShowErrorMessage(myMCUControl.strErrorMessage)
                self.ui.labelError = "Set speed for axis_x fail"
                self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                return -1
            self.ui.labelError.setText("Set speed for axis_x pass")
            self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
            # self.ShowErrorMessage('Set speed ok')
        except:
            # self.ShowErrorMessage("SetServoSpeed  except fail")
            self.ui.labelError.setText("SetServoSpeed  for axis_x fail 1")
            self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")

# **************************Set Servo Speed***************************************

# **************************Set Absolute Move***************************************
    def SetAbsoluteMove(self):
        try:
            if self.ui.EditServoSpeed.text() != '':
                speed = float(self.ui.EditServoSpeed.text())
                value = self.ui.EditAbsolute.text()
                ret = myMCUControl.MoveToCoordinates(float(value),speed)
                if ret == -1:
                    # self.ShowErrorMessage(myMCUControl.strErrorMessage)
                    self.ui.labelError.setText("dut no lock or vacuum file")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                else:
                    self.ui.labelError.setText("Set absolute_R movement fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                    return 0
            value = self.ui.EditAbsolute.text()
            ret = myMCUControl.MoveToCoordinates(float(value),98)
            if ret == -1:
                # self.ShowErrorMessage(myMCUControl.strErrorMessage)
                self.ui.labelError.setText("Set absolute movement fail")
                self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                return -1
            self.ui.labelError.setText("Set absolute_R movement pass")
            self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
        except:
            # self.ShowErrorMessage("SetAbsoluteMove except fail")
            self.ui.labelError.setText("SetAbsoluteMove except fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
# **************************Set Absolute Move***************************************



# **************************Set Absolute_X Move***************************************
    def SetAbsoluteMove_X(self):
        try:
            if self.ui.EditServoSpeed_X.text() != '':
                speed = float(self.ui.EditServoSpeed_X.text())
                value = self.ui.EditAbsolute_X.text()
                ret = myMCUControl.MoveToCoordinates_X(float(value), speed)
                if ret == -1:
                    # self.ShowErrorMessage(myMCUControl.strErrorMessage)
                    self.ui.labelError.setText("Set absolute_X movement fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                else:
                    self.ui.labelError.setText("Set absolute_X movement fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                    return 0
            #当没有设置速度的时候，默认为1
            value = float(self.ui.EditAbsolute_X.text())
            ret = myMCUControl.MoveToCoordinates_X(float(value), 39)
            if ret == -1:
                # self.ShowErrorMessage(myMCUControl.strErrorMessage)
                self.ui.labelError.setText("Set absolute_X movement fail")
                self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                return -1
            self.ui.labelError.setText("Set absolute_X movement pass")
            self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
        except:
            # self.ShowErrorMessage("SetAbsoluteMove except fail")
            self.ui.labelError.setText("SetAbsoluteMove except fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
# **************************Set Absolute_X Move***************************************

# **************************Set Relative Move***************************************
    def SetRelativeMove(self):
        try:
            if self.ui.EditServoSpeed.text() != '':
                speed = float(self.ui.EditServoSpeed.text())
                value = self.ui.EditRelative.text()
                ret = myMCUControl.MoveStep(float(value),speed=speed)
                if ret == -1:
                    # self.ShowErrorMessage(myMCUControl.strErrorMessage)
                    self.ui.labelError.setText("Set relative movement fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                else:
                    self.ui.labelError.setText("Set relative movement pass")
                    self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                    return 0
            value = self.ui.EditRelative.text()
            ret = myMCUControl.MoveStep(float(value),98)
            if ret == -1:
                # self.ShowErrorMessage(myMCUControl.strErrorMessage)
                self.ui.labelError.setText("Set relative movement fail")
                self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                return -1
            self.ui.labelError.setText("Set relative movement pass")
            self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
            # if myMCUControl.Exceed_limit_flag == True:
            #     self.ShowErrorMessage("Exceed Limit,please click reset button")
            #     myMCUControl.Exceed_limit_flag = False
        except:
            self.ShowErrorMessage("SetRelativeMove except fail")
# **************************Set Relative Move***************************************

# **************************Set Relative_X Move*************************************
    def SetRelativeMove_X(self):
        try:
            if self.ui.EditServoSpeed_X.text() != '':
                speed = float(self.ui.EditServoSpeed_X.text())
                value = self.ui.EditRelative_X.text()
                ret = myMCUControl.MoveStep_X(float(value), speed=speed)
                if ret == -1:
                    # self.ShowErrorMessage(myMCUControl.strErrorMessage)
                    self.ui.labelError.setText("Set relative_X movement fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                else:
                    self.ui.labelError.setText("Set relative_X movement pass")
                    self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                    return 0
            value = self.ui.EditRelative_X.text()
            ret = myMCUControl.MoveStep_X(float(value), 39)
            if ret == -1:
                # self.ShowErrorMessage(myMCUControl.strErrorMessage)
                self.ui.labelError.setText("Set relative_X movement fail")
                self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                return -1
            self.ui.labelError.setText("Set relative_X movement pass")
            self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
            # if myMCUControl.Exceed_limit_flag == True:
            #     self.ShowErrorMessage("Exceed Limit,please click reset button")
            #     myMCUControl.Exceed_limit_flag = False
        except:
            self.ShowErrorMessage("SetRelativeMove_X except fail")
# **************************Set Relative_X Move*************************************


# **************************Set Door State******************************************

    def Set_DoorState(self,state):
        try:
            if state == 'Close':
                ret = myMCUControl.Set_DoorState(myMCUControl.DoorClose)
                if ret != 0:
                    self.ui.labelError.setText("Set Door State fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.ui.labelError.setText("Set Door State pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                return 0

            elif state == 'Open':
                ret = myMCUControl.Set_DoorState(myMCUControl.DoorOpen)
                if ret != 0:
                    self.ui.labelError.setText("Set Door State fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.ui.labelError.setText("Set Door State pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                return 0
        except Exception as e:
            self.ui.labelError.setText("Set_DoorState  except fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")


# **************************Set Cylinder1*******************************************
    def Set_Cylinder_1(self,state):
        try:
            if state == 'IN':
                ret = myMCUControl.Set_CylinderFunction_1(myMCUControl.In)
                if ret != 0:
                    # self.ShowErrorMessage("Set_Cylinder in fail")
                    self.ui.labelError.setText("Set Cylinder_1 State fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.ui.labelError.setText("Set Cylinder_1 State pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                return 0

            elif state == 'OUT':
                ret = myMCUControl.Set_CylinderFunction_1(myMCUControl.Out)
                if ret != 0:
                    # self.ShowErrorMessage("Set_Cylinder out fail")
                    self.ui.labelError.setText("Set Cylinder_1 State fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.ui.labelError.setText("Set Cylinder_1 State pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                return 0
        except Exception as e:
            # self.ShowErrorMessage("Set_Cylinder except Fail {}".format(e))
            self.ui.labelError.setText("Set_Cylinder_1  except fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
# **************************Set Cylinder1*******************************************

# **************************Set Cylinder1*******************************************
    def Set_Cylinder_2(self, state):
        try:
            if state == 'IN':
                ret = myMCUControl.Set_CylinderFunction_2(myMCUControl.In)
                if ret != 0:
                    # self.ShowErrorMessage("Set_Cylinder in fail")
                    self.ui.labelError.setText("Set Cylinder_2 State fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.ui.labelError.setText("Set Cylinder_2 State pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                return 0
            elif state == 'OUT':
                ret = myMCUControl.Set_CylinderFunction_2(myMCUControl.Out)
                if ret != 0:
                    # self.ShowErrorMessage("Set_Cylinder out fail")
                    self.ui.labelError.setText("Set Cylinder_2 State fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.ui.labelError.setText("Set Cylinder_2 State pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                return 0
        except Exception as e:
            # self.ShowErrorMessage("Set_Cylinder except Fail {}".format(e))
            self.ui.labelError.setText("Set_Cylinder_2  except fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")

# **************************Set Cylinder1*******************************************

# ****************************Set USB1 State*************************************
    def Set_USB1State(self, state):
        try:
            if state == 'lock':
                ret = myMCUControl.Set_USB1State(myMCUControl.USBLock)
                if ret != 0:
                    self.ui.labelError.setText("Set USB1 State fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                # ret = myMCUControl.Set_USB2State(myMCUControl.USBLock)
                # if ret != 0:
                #     self.ui.labelError.setText("Set USB2 State fail")
                #     self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                #     return -1
                self.ui.labelError.setText("Set USB1 State pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                return 0
            elif state == 'unlock':
                ret = myMCUControl.Set_USB1State(myMCUControl.USBUnlock)
                if ret != 0:
                    self.ui.labelError.setText("Set USB1 State fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                # ret = myMCUControl.Set_USB2State(myMCUControl.USBUnlock)
                # if ret != 0:
                #     self.ui.labelError.setText("Set USB2 State fail")
                #     self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                #     return -1
                self.ui.labelError.setText("Set USB1 State pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                # return 0
        except Exception as e:
            # self.ShowErrorMessage("Set_Cylinder except Fail {}".format(e))
            self.ui.labelError.setText("Set_USB1State  except fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")

# ****************************Set USB1 State*************************************

# ****************************Set USB2 State*************************************
    def Set_USB2State(self, state):
        try:
            if state == 'lock':
                ret = myMCUControl.Set_USB2State(myMCUControl.USBLock)
                if ret != 0:
                    self.ui.labelError.setText("Set USB2 State fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                # ret = myMCUControl.Set_USB2State(myMCUControl.USBLock)
                # if ret != 0:
                #     self.ui.labelError.setText("Set USB2 State fail")
                #     self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                #     return -1
                self.ui.labelError.setText("Set USB2 State pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                return 0
            elif state == 'unlock':
                ret = myMCUControl.Set_USB2State(myMCUControl.USBUnlock)
                if ret != 0:
                    self.ui.labelError.setText("Set USB2 State fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                # ret = myMCUControl.Set_USB2State(myMCUControl.USBUnlock)
                # if ret != 0:
                #     self.ui.labelError.setText("Set USB2 State fail")
                #     self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                #     return -1
                self.ui.labelError.setText("Set USB2 State pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                # return 0
        except Exception as e:
            # self.ShowErrorMessage("Set_Cylinder except Fail {}".format(e))
            self.ui.labelError.setText("Set_USB2State  except fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")

# ****************************Set USB2 State*************************************

# ***************************Set Dut State**************************************

    def Set_DutState1(self, state):
        try:
            if state == 'lock':
                ret = myMCUControl.Set_DutState1(myMCUControl.Dutlock)
                if ret != 0:
                    # self.ShowErrorMessage(myMCUControl.strErrorMessage)
                    self.ui.labelError.setText("Set Dut State fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.ui.labelError.setText("Set Dut State pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
            elif state == 'unlock':
                ret = myMCUControl.Set_DutState1(myMCUControl.DutUnlock)
                if ret != 0:
                    # self.ShowErrorMessage(myMCUControl.strErrorMessage)
                    self.ui.labelError.setText("Set Dut State fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.ui.labelError.setText("Set Dut State pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                return 0
        except Exception as e:
            # self.ShowErrorMessage("Set_Cylinder except Fail {}".format(e))
            self.ui.labelError.setText("Set_DutState1 except fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")

# ***************************Set Dut State**************************************

# ***************************Set Dut2 State**************************************

    def Set_DutState2(self, state):
        try:
            if state == 'lock':
                ret = myMCUControl.Set_DutState2(myMCUControl.Dutlock)
                if ret != 0:
                    # self.ShowErrorMessage(myMCUControl.strErrorMessage)
                    self.ui.labelError.setText("Set Dut State lock fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.ui.labelError.setText("Set Dut State lock pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
            elif state == 'unlock':
                ret = myMCUControl.Set_DutState2(myMCUControl.DutUnlock)
                if ret != 0:
                    # self.ShowErrorMessage(myMCUControl.strErrorMessage)
                    self.ui.labelError.setText("Set Dut State unlock fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.ui.labelError.setText("Set Dut State unlock pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                return 0
        except Exception as e:
            # self.ShowErrorMessage("Set_Cylinder except Fail {}".format(e))
            self.ui.labelError.setText("Set_DutState2 except fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")

# ***************************Set Dut2 State**************************************

# ***************************action Reset**************************************
    def actionReset(self):
        try:
            # myMCUControl.Limit_Stop_Flag = True
            ret = myMCUControl.SignalReSet(30)
            if ret != 0:
                # self.ShowErrorMessage("actionReset fail")
                self.ui.labelError.setText("fixture reset fail")
                self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                return -1
            self.ui.labelError.setText("fixture reset pass")
            self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
            # self.ui.BtSetMotorStop.setEnabled(1)
        except Exception as e:
            # self.ShowErrorMessage("actionReset except Fail {}".format(e))
            self.ui.labelError.setText("actionReset except fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")

# ***************************action Reset**************************************

# ***************************Set Motor Stop**************************************
    def SetMotorStop(self):
        try:
            ret = myMCUControl.SetMotorStop(self)
            if ret == -1:
                # self.ShowErrorMessage(myMCUControl.strErrorMessage)
                self.ui.labelError = "Set motor stop fail"
                self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                return -1
            else:
                self.ui.labelError = "Set motor stop pass"
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                return 0
        except Exception as e:
            # self.ShowErrorMessage("SetMotorStop except fail {}".format(e))
            self.ui.labelError = "SetMotorStop except fail"
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
# ***************************Set Motor Stop**************************************

# ***************************Motor Validation*******************************************
    def MotorValidation(self):
        try:
            DataTimeStart = datetime.datetime.now().strftime('%Y%m%d-%H-%M-%S')
            path1 = os.getcwd() + "/BojayLogs/PIR-AZIZ/MotorValidation/"
            if not os.path.exists(path1):
                os.makedirs(path1)


            if self.ui.EditServoSpeed.text() == '':
                self.ShowErrorMessage("Please input servo speed")
                return -1
            speed = float(self.ui.EditServoSpeed.text())

            ret = myMCUControl.SignalReSet(30)
            if ret != 0:
                self.ShowErrorMessage("fixture reset fail")
                return -1

            with open(path1 + DataTimeStart + ".csv", 'wb') as anglefile:
                string = "sweep_count,speed,sweep_time\n"
                if myMCUControl.Interpreter == 3:
                    string = string.encode('utf-8')
                anglefile.write(string)

                ret = myMCUControl.MoveToCoordinates(-120, speed)
                if ret != 0:
                    self.ShowErrorMessage('set absolute movement fail'   )
                    return -1
                StartTime = time.time()
                # move to -90
                ret = myMCUControl.MoveToCoordinates(120, speed)
                if ret != 0:
                    self.ShowErrorMessage('set absolute movement fail'   )
                    return -1
                EndTime = time.time()
                string = str(1) + ',' + str(speed) + ','+ str(round(EndTime-StartTime,2)) + '\n'
                if myMCUControl.Interpreter == 3:
                    string = string.encode('utf-8')
                anglefile.write(string)

            self.ui.EditSweepTimes.setText(str(round(EndTime-StartTime,2)))

            return 0

        except:
            self.ui.labelError.setText("AngleTestThread except fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
# ***************************Motor Validation Thread*******************************************

# ***************************Burning*********************************************
    def Burning(self):
        try:
            ThreadTemp = threading.Thread(target=self.TemperatureValidationThread)
            ThreadTemp.start()
            # self.timer_temp_validation.start()


            DataTimeStart = datetime.datetime.now().strftime('%Y%m%d-%H-%M-%S')
            path1 = os.getcwd() + "/BojayLogs/PIR-AZIZ/AngleValidation/StepValidation/"
            if not os.path.exists(path1):
                os.makedirs(path1)

            path2 = os.getcwd() + "/BojayLogs/PIR-AZIZ/AngleValidation/StepValidation2/"
            if not os.path.exists(path2):
                os.makedirs(path2)


            # list_Step = [120,110,90, 70, 50, 30, 10, 0, -10, -30, -50, -70, -89,-90,-110,-120]
            list_Step = [-10,10]
            anglefile = open(path1 + DataTimeStart + ".csv", 'wb')
            string = " count,120,110,90, 70, 50, 30, 10, 0, -10, -30, -50, -70, -89,-90,-110,-120\n"
            if myMCUControl.Interpreter == 3:
                string = string.encode('utf-8')
            anglefile.write(string)

            # list_Step = [120 ,-119]
            # anglefile = open(path1 + DataTimeStart + ".csv", 'wb')
            # string = " count,120,-119\n"
            # if myMCUControl.Interpreter == 3:
            #     string = string.encode('utf-8')
            # anglefile.write(string)
            #
            list_Step_x = [0, 40]
            anglefile_x = open(path2 + DataTimeStart + ".csv", 'wb')
            string = " count,0,90\n"
            if myMCUControl.Interpreter == 3:
                string = string.encode('utf-8')
            anglefile_x.write(string)

            # list_Step_x = []
            # for i in range(0,91,1):
            #     list_Step_x.append(i)
            #     anglefile_x = open(path2 + DataTimeStart + ".csv", 'wb')
            #     string = " count,0\n"
            #     if myMCUControl.Interpreter == 3:
            #         string = string.encode('utf-8')
            #     anglefile_x.write(string)

            if self.ui.EditBurnTimes.text() == '':
                self.ShowErrorMessage('please input the digital')
                return -1



            # reset
            ret = myMCUControl.SignalReSet(20)
            if ret != 0:
                self.ShowErrorMessage('MoveToCoordinates error')
                return -1
            #file
            count = int(self.ui.EditBurnTimes.text())

            wait_time = 2

            for i in range(count):
                print (i+1)
                #cylinder out
                if self.ui.radioGQ.isChecked():
                    ret = myMCUControl.Set_DutState2(myMCUControl.Dutlock)
                    if ret != 0:
                        self.ShowErrorMessage('Set_DutState2 out error')
                        return -1
                    time.sleep(0.5)

                    ret = myMCUControl.Set_DutState1(myMCUControl.Dutlock)
                    if ret != 0:
                        self.ShowErrorMessage('Set_DutState1 out error')
                        return -1
                    time.sleep(0.5)
                    # ret = myMCUControl.Set_DutState2(myMCUControl.Dutlock)
                    # if ret != 0:
                    #     self.ShowErrorMessage('Set_DutState2 out error')
                    #     return -1
                    # time.sleep(0.5)
                    # ret = myMCUControl.Set_USB1State(myMCUControl.USBLock)
                    # if ret != 0:
                    #     self.ShowErrorMessage('Set_USBState1 out error')
                    #     return -1
                    # time.sleep(0.5)
                    # ret = myMCUControl.Set_USB2State(myMCUControl.USBLock)
                    # if ret != 0:
                    #     self.ShowErrorMessage('Set_USBState2 out error')
                    #     return -1

                # 托盘出
                # ret = myMCUControl.Set_CylinderFunction_1(myMCUControl.In)
                # if ret != 0:
                #     self.ShowErrorMessage('Set_CylinderFunction1 out error')
                #     return -1
                # time.sleep(0.5)

                # ret = myMCUControl.Set_CylinderFunction_2(myMCUControl.In)
                # if ret != 0:
                #     self.ShowErrorMessage('Set_CylinderFunction2 out error')
                #     return -1
                # time.sleep(0.5)

                #关门
                # if self.ui.radioGQ.isChecked():
                #     ret = myMCUControl.Set_DoorState(myMCUControl.DoorClose)
                #     if ret != 0:
                #         self.ShowErrorMessage('Set_DoorState close error')
                #         return -1

                # anglefile = open(path1 + DataTimeStart + ".csv", 'wb')
                string = str(i+1) + ','
                if myMCUControl.Interpreter == 3:
                    string = string.encode('utf-8')
                anglefile.write(string)


                for angle in list_Step:
                    datalist = []
                    ret = myMCUControl.MoveToCoordinates(angle, 65)
                    if ret != 0:
                        self.ErrorMessage = 'Set absolute movement fail'
                        return -1
                    starttime = time.time()
                    while (time.time() - starttime) < wait_time:
                        ret = myMCUControl.ReadXAngleAndYAngle(datalist)
                        if ret != 0:
                            self.ErrorMessage = "Read XYAngle error"
                            return -1
                        print("datalist[0] = {0},angle = {1},diff = {2}".format(datalist[0], angle,abs(datalist[0] - angle)))
                        if abs(datalist[0]-angle) < 0.2:
                            break
                    string = str(datalist[0]) + ','
                    if myMCUControl.Interpreter == 3:
                        string = string.encode('utf-8')
                    anglefile.write(string)
                string = str('\n')
                if myMCUControl.Interpreter == 3:
                    string = string.encode('utf-8')
                anglefile.write(string)

                ret = myMCUControl.MoveToCoordinates(0, 65)
                if ret != 0:
                    self.ErrorMessage = 'Set absolute movement fail'
                    return -1


            #****************************
                string = str(i + 1) + ','
                if myMCUControl.Interpreter == 3:
                    string = string.encode('utf-8')
                anglefile_x.write(string)
                for angle in list_Step_x:
                    datalist1 = []
                    ret = myMCUControl.MoveToCoordinates_X(angle, 170)
                    if ret != 0:
                        self.ErrorMessage = 'Set absolute_X movement fail'
                        return -1
                    time.sleep(0.5)
                    starttime = time.time()
                    while (time.time() - starttime) < wait_time:
                        ret = myMCUControl.ReadXAngleAndYAngle_X(datalist1)
                        if ret != 0:
                            self.ErrorMessage = "Read XYAngle error"
                            return -1
                        print("datalist1[0] = {0},angle = {1},diff = {2}".format(datalist1[0], angle,
                                                                                abs(datalist1[0] - angle)))
                        if abs(datalist1[0] - angle) < 0.2:
                            break
                    string = str(datalist1[0]) + ','
                    if myMCUControl.Interpreter == 3:
                        string = string.encode('utf-8')
                    anglefile_x.write(string)
                string = str('\n')
                if myMCUControl.Interpreter == 3:
                    string = string.encode('utf-8')
                anglefile_x.write(string)
                ret = myMCUControl.MoveToCoordinates_X(0,170)
                if ret != 0:
                    self.ErrorMessage = 'Set absolute_x movement fail'
                    return -1

                time.sleep(1)




            #*************************************
                #开门
                # ret = myMCUControl.Set_DoorState(myMCUControl.DoorOpen)
                # if ret != 0:
                #     self.ShowErrorMessage('Set_DoorState open error')
                #     return -1
                # time.sleep(0.5)

                # ret = myMCUControl.Set_CylinderFunction_2(myMCUControl.Out)
                # if ret != 0:
                #     self.ShowErrorMessage('Set_CylinderFunction2 in error')
                #     return -1
                # time.sleep(0.5)

                # 托盘出
                # ret = myMCUControl.Set_CylinderFunction_1(myMCUControl.Out)
                # if ret != 0:
                #     self.ShowErrorMessage('Set_CylinderFunction1 in error')
                #     return -1
                # time.sleep(0.5)



                if self.ui.radioGQ.isChecked():
                    # ret = myMCUControl.Set_USB1State(myMCUControl.USBUnlock)
                    # if ret != 0:
                    #     self.ShowErrorMessage('Set_USBState1 out error')
                    #     return -1
                    # time.sleep(0.5)
                    #
                    # ret = myMCUControl.Set_USB2State(myMCUControl.USBUnlock)
                    # if ret != 0:
                    #     self.ShowErrorMessage('Set_USBState2 out error')
                    #     return -1
                    # time.sleep(0.5)

                    ret = myMCUControl.Set_DutState1(myMCUControl.DutUnlock)
                    if ret != 0:
                        self.ShowErrorMessage('Set_DutState1 out error')
                        return -1
                    time.sleep(0.5)

                    ret = myMCUControl.Set_DutState2(myMCUControl.DutUnlock)
                    if ret != 0:
                        self.ShowErrorMessage('Set_DutState1 out error')
                        return -1
                    time.sleep(0.5)

                    ret = myMCUControl.Set_DutState2(myMCUControl.Dutlock)
                    if ret != 0:
                        self.ShowErrorMessage('Set_DutState1 out error')
                        return -1
                    time.sleep(0.5)

                    ret = myMCUControl.Set_DutState1(myMCUControl.Dutlock)
                    if ret != 0:
                        self.ShowErrorMessage('Set_DutState1 out error')
                        return -1
                    time.sleep(0.5)

                    # ret = myMCUControl.Set_DutState2(myMCUControl.DutUnlock)
                    # if ret != 0:
                    #     self.ShowErrorMessage('Set_DutState2 out error')
                    #     return -1
                    # time.sleep(0.5)

            ret = myMCUControl.SignalReSet(30)
            if ret != 0:
                self.ErrorMessage = "fixture reset fail"
                return -1

        except Exception as e:
            self.ui.labelError.setText("Burning except fail {}".format(e))
            self.ui.labelError.setStyleSheet("background-color: rgb(255,0 , 0);")
# ***************************Burning*******************************************

# ***************************Get Sensor State**********************************
    def GetSensorState(self):
        try:
            list_state = []
            for i in range(0, 28, 1):
                ret = myMCUControl.ReadSensorState(i + 1, 0.05)
                if ret == -1:
                    # self.ShowErrorMessage(myMCUControl.strErrorMessage)
                    self.ui.labelError.setText("Read Sensor State get fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                list_state.append(ret)
                self.ui.labelError.setText("Read Sensor State get pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
            if int(list_state[0]) == 1:
                self.ui.labelSensor1.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor1.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[1]) == 1:
                self.ui.labelSensor2.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor2.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[2]) == 1:
                self.ui.labelSensor3.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor3.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[3]) == 1:
                self.ui.labelSensor4.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor4.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[4]) == 1:
                self.ui.labelSensor5.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor5.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[5]) == 1:
                self.ui.labelSensor6.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor6.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[6]) == 1:
                self.ui.labelSensor7.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor7.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[7]) == 1:
                self.ui.labelSensor8.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor8.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[8]) == 1:
                self.ui.labelSensor9.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor9.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[9]) == 1:
                self.ui.labelSensor10.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor10.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[10]) == 1:
                self.ui.labelSensor11.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor11.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[11]) == 1:
                self.ui.labelSensor12.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor12.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[12]) == 1:
                self.ui.labelSensor13.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor13.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[13]) == 1:
                self.ui.labelSensor14.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor14.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[14]) == 1:
                self.ui.labelSensor15.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor15.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[15]) == 1:
                self.ui.labelSensor16.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor16.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[16]) == 1:
                self.ui.labelSensor17.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor17.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[17]) == 1:
                self.ui.labelSensor18.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor18.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[18]) == 1:
                self.ui.labelSensor19.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor19.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[19]) == 1:
                self.ui.labelSensor20.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor20.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[20]) == 1:
                self.ui.labelSensor21.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor21.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[21]) == 1:
                self.ui.labelSensor22.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor22.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[22]) == 1:
                self.ui.labelSensor23.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor23.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[23]) == 1:
                self.ui.labelSensor24.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor24.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[24]) == 1:
                self.ui.labelSensor25.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor25.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[25]) == 1:
                self.ui.labelSensor26.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor26.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[26]) == 1:
                self.ui.labelSensor27.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor27.setStyleSheet("background-color: rgb(0, 255, 0);")

            if int(list_state[27]) == 1:
                self.ui.labelSensor28.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.labelSensor28.setStyleSheet("background-color: rgb(0, 255, 0);")

            filepath = os.getcwd()
            filepath += "/SensorIoConfig.txt"
            with open(filepath, 'w') as output:
                for i in range(0, 28, 1):
                    output.write("Sensor" + str(i + 1) + "=" + str(list_state[i]) + "\n")
                output.close()
        except Exception as e:
            # self.ShowErrorMessage("get sensor state fail")
            self.ui.labelError.setText("GetSensorState except fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
            return -1

# ***************************Get Sensor State**********************************

# ***************************Get Temperature*******************************************
    def GetTemperatureAndAngle(self):
        try:
            self.start_get_temperature = True
            self.ThreadTempAndAngle = threading.Thread(target=self.GetTempAndAngleThread)
            self.ThreadTempAndAngle.start()
            self.timer_temp.start(100)
            self.ui.BtAutomaticStop.setEnabled(1)
            self.ui.BtAutomaticGet.setEnabled(0)
            self.ui.BtTemperatureValidation.setEnabled(0)
            self.ui.BtSetTargetTemperature.setEnabled(0)
            self.ui.BtStepValidation.setEnabled(0)
            self.ui.BtAngleValidation.setEnabled(0)
            self.ui.BtSetToZero.setEnabled(0)
            self.ui.BtSetToZero_X.setEnabled(0)
            return 0
        except Exception as e:
            self.ui.labelError.setText("GetTemperature except Fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")

    #显示计时器
    def ShowTimer(self):
        try:
            if self.ErrorMessage != "":
                self.start_get_temperature == False
                self.ui.EditCH1Temperature.setText(str(""))
                self.ui.EditCH2Temperature.setText(str(""))
                self.ui.EditCH3Temperature.setText(str(""))
                self.ui.EditCH4Temperature.setText(str(""))
                self.ui.EditDiffTemperature.setText(str(""))
                self.ui.BtAutomaticGet.setEnabled(1)
                self.ui.BtAutomaticStop.setEnabled(0)
                self.ui.BtStepValidation.setEnabled(1)
                self.ui.BtAngleValidation.setEnabled(1)
                self.ui.BtSetToZero.setEnabled(1)
                self.timer_temp.stop()
                self.ui.labelError.setText(self.ErrorMessage)
                self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                self.ui.EditCH1Temperature.setText(str(self.target))
                self.ui.EditCH2Temperature.setText(str(self.CH2_Temp))
                self.ui.EditCH3Temperature.setText(str(self.CH3_Temp))
                self.ui.EditCH4Temperature.setText(str(self.indoor))
                self.ui.EditDiffTemperature.setText(str(float('%.2f' % (self.target-self.indoor))))
                self.ui.EditXAngle.setText(str(self.xValue))
                self.ui.EditYAngle.setText(str(self.yValue))
                self.ui.EditXAngle_X.setText(str(self.xValue_X))
                self.ui.EditYAngle_X.setText(str(self.yValue_X))


        except Exception as e:
            self.ui.labelError.setText("Show_Temp_Timer except Fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
            self.timer_temp.stop()
            return -1

    def GetTempAndAngleThread(self):
        try:
            while True:
                if self.start_get_temperature == True:
                    print("************************************************8")
                    time.sleep(0.2)
                    self.target = myMCUControl.GetCurrentTemperature(myMCUControl.LCD1)
                    if self.target == -1:
                        self.ErrorMessage = myMCUControl.strErrorMessage
                        return -1
                    time.sleep(0.2)
                    self.CH2_Temp = myMCUControl.GetCurrentTemperature(myMCUControl.LCD2)
                    if self.CH2_Temp == -1:
                        self.ErrorMessage = myMCUControl.strErrorMessage
                        return -1
                    time.sleep(0.2)
                    self.CH3_Temp = myMCUControl.GetCurrentTemperature(myMCUControl.LCD3)
                    if self.CH3_Temp == -1:
                        self.ErrorMessage = myMCUControl.strErrorMessage
                        return -1
                    time.sleep(0.2)
                    self.indoor = myMCUControl.GetCurrentTemperature(myMCUControl.LCD4)
                    if self.indoor == -1:
                        self.ErrorMessage = myMCUControl.strErrorMessage
                        return -1
                    time.sleep(0.2)

                    #获取角度1
                    datalist = []
                    self.angle_ret = myMCUControl.ReadXAngleAndYAngle(datalist)
                    if self.angle_ret == -1:
                        self.ErrorMessage = myMCUControl.strErrorMessage
                        return -1
                    self.xValue = datalist[0]
                    self.yValue = datalist[1]

                    #获取角度2
                    datalist2 = []
                    self.angle_ret = myMCUControl.ReadXAngleAndYAngle_X(datalist2)
                    if self.angle_ret == -1:
                        self.ErrorMessage = myMCUControl.strErrorMessage
                        return -1
                    self.xValue_X = datalist2[0]
                    self.yValue_X = datalist2[1]
                else:
                    return -1
        except Exception as e:
            self.ErrorMessage = "GetTempThread except fail"

    def StopTemperatureAndAngle(self):
        try:

            self.start_get_temperature = False
            self.timer_temp.stop()
            self.ui.BtAutomaticGet.setEnabled(1)
            self.ui.BtAutomaticStop.setEnabled(0)
            self.ui.BtTemperatureValidation.setEnabled(1)
            self.ui.BtStepValidation.setEnabled(1)
            self.ui.BtAngleValidation.setEnabled(1)
            self.ui.BtSetToZero.setEnabled(1)
            self.ui.BtSetToZero_X.setEnabled(1)
            self.ui.BtSetTargetTemperature.setEnabled(1)
            self.ui.labelError.setText("Stop to get temperature pass")
            self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
            return 0
        except Exception as e:
            self.ui.labelError.setText("StopTemperature except Fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")


# ***************************Get Temperature*******************************************

# ***************************Set Target Temperature*******************************************
    def SetTargetTemperature(self):
        try:
            if self.ui.EditSetTargetTemperature.text() != '':
                temp = self.ui.EditSetTargetTemperature.text()
                ret = myMCUControl.SetTargetTemperature(float(temp))
                if ret != 0:
                    # self.ShowErrorMessage('SetTargetTemperature timeout')
                    self.ui.labelError.setText("Set Target Temperature fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.ui.labelError.setText("Set Target Temperature pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
            else:
                # self.ShowErrorMessage('input paramreter wrong')
                self.ui.labelError.setText("input paramreter wrong")
                self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                return -1
        except Exception as e:
            self.ui.labelError.setText("SetTargetTemperature get except Fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
            # self.ShowErrorMessage("SetTargetTemperature get except Fail {}".format(e))

# ***************************Set Target Temperature*******************************************

# ***************************Temperature Validation*******************************************
    def TemperatureValidation(self):
        try:
            self.ThreadTempValidation = threading.Thread(target=self.TemperatureValidationThread)
            self.ui.BtAutomaticGet.setEnabled(0)
            self.ui.BtAutomaticStop.setEnabled(0)
            self.ui.BtTemperatureValidation.setEnabled(0)
            self.ui.BtSetTargetTemperature.setEnabled(0)
            self.ui.labelError.setText("TemperatureValidation start ...")
            self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
            self.timer_temp.stop()
            self.ThreadTempValidation.start()
            self.timer_temp_validation.start()

        except Exception as e:
            self.ui.labelError.setText("TemperatureValidation except Fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
            return -1

    def TemperatureValidationThread(self):
        try:
            DataTimeStart = datetime.datetime.now().strftime('%Y%m%d-%H-%M-%S')
            path1 = os.getcwd() + "//BojayLogs//PIR-AZIZ//TemperatureValidation//"
            if not os.path.exists(path1):
                os.makedirs(path1)
            with open(path1 + DataTimeStart + ".csv", 'ab+') as Tempfile:
                string = ",target_Temp,CH2_Temp,CH3_Temp,indoor_Temp,\n"
                if myMCUControl.Interpreter == 3:
                    string = string.encode('utf-8')
                Tempfile.write(string)
                k = 0
                hours = 12
                #120 * hours
                for i in range(0, 120 * hours, 1):
                    while True:
                        temp_CH1 = myMCUControl.GetCurrentTemperature(myMCUControl.LCD1)
                        if temp_CH1 == -1:
                            print("CH1_Fail:".format(myMCUControl.strErrorMessage))
                            self.ErrorMessage = "Temperature Burning Fail"
                            continue
                        else:
                            break
                    while True:
                        temp_CH2 = myMCUControl.GetCurrentTemperature(myMCUControl.LCD2)
                        if temp_CH2 == -1:
                            print("CH2_Fail:".format(myMCUControl.strErrorMessage))
                            self.ErrorMessage = "Temperature Burning Fail"
                            continue
                        else:
                            break
                    while True:
                        temp_CH3 = myMCUControl.GetCurrentTemperature(myMCUControl.LCD3)
                        if temp_CH3 == -1:
                            print("CH3_Fail:".format(myMCUControl.strErrorMessage))
                            self.ErrorMessage = "Temperature Burning Fail"
                            continue
                        else:
                            break

                    while True:
                        temp_CH4 = myMCUControl.GetCurrentTemperature(myMCUControl.LCD4)
                        if temp_CH4 == -1:
                            print("CH4_Fail:".format(myMCUControl.strErrorMessage))
                            self.ErrorMessage = "Temperature Burning Fail"
                            continue
                        else:
                            break
                    print("temperature data:\nCH1 = {0},CH2 = {1}, CH3 = {2},CH4 = {3}".format(temp_CH1,temp_CH2,temp_CH3,temp_CH4))
                    if i == 4*k:
                        k = k+1
                        while True:
                            ret = myMCUControl.SetTargetTemperature(temp_CH4+25)
                            if ret == -1:
                                print("SetTarget_Fail:".format(myMCUControl.strErrorMessage))
                                self.ErrorMessage = "Temperature Burning Fail"
                                continue
                            else:
                                break
                        print("Set Target Pass:{0}".format(temp_CH4+25))
                    string = str(i + 1) + ',' + str(temp_CH1) + ',' + str(temp_CH2) + ',' + str(temp_CH3) + ',' + str(
                        temp_CH4) +  '\n'
                    if myMCUControl.Interpreter == 3:
                        string = string.encode('utf-8')
                    Tempfile.write(string)
                    time.sleep(30)
                    print(i + 1)
                DataTimeStop = datetime.datetime.now().strftime('%Y%m%d-%H-%M-%S')
                string = "Start-Time:" + ',' + DataTimeStart + '\n'
                if myMCUControl.Interpreter == 3:
                    string = string.encode('utf-8')
                Tempfile.write(string)
                string = "Stop-Time:" + ',' + DataTimeStop + '\n'
                if myMCUControl.Interpreter == 3:
                    string = string.encode('utf-8')
                Tempfile.write(string)
                self.temperature_validation_end = True
                # self.timer_temp_validation.stop()
        except Exception as e:
            self.ErrorMessage = "TemperatureValidationThread except fail"
            return -1

    def ShowTemperatureTimer(self):
        try:
            if self.ErrorMessage != "":
                self.ui.labelError.setText(self.ErrorMessage)
                self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                self.ui.BtAutomaticGet.setEnabled(1)
                self.ui.BtAutomaticStop.setEnabled(1)
                self.ui.BtTemperatureValidation.setEnabled(1)
                self.timer_temp_validation.stop()
                return -1
            if self.temperature_validation_end == True:
                self.temperature_validation_end = False
                self.ui.labelError.setText("Temperature validation pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                self.ui.BtAutomaticGet.setEnabled(1)
                self.ui.BtAutomaticStop.setEnabled(1)
                self.ui.BtSetTargetTemperature.setEnabled(1)
                self.ui.BtTemperatureValidation.setEnabled(1)
                self.timer_temp_validation.stop()
                return -1
        except:
            self.ui.labelError.setText("ShowTemperatureTimer except fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
# ***************************Temperature Validation*******************************************

# ********************************Set To Zero ************************************************
    def SetToZero(self):
        try:
            ret = myMCUControl.SetAngleHome()
            if ret != 0:
                # self.ShowErrorMessage('set zero for angle fail')
                self.ui.labelError.setText("ret!=0 set zero for angle_R fail")
                self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                return -1
            self.ui.labelError.setText("set zero for angle_R pass")
            self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
            return 0
        except Exception as e:
            # self.ShowErrorMessage("open serial fail")
            self.ui.labelError.setText("SetToZero except fail R")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
            return -1
# ********************************Set To Zero ************************************************

# ********************************Set To Zero_X **********************************************
    def SetToZero_X(self):
        try:
            ret = myMCUControl.SetAngleHome_X()
            if ret != 0:
                # self.ShowErrorMessage('set zero for angle fail')
                self.ui.labelError.setText("ret!=0 set zero for angle_X fail")
                self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                return -1
            self.ui.labelError.setText("set zero for angle_X pass")
            self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
            return 0
        except Exception as e:
            # self.ShowErrorMessage("open serial fail")
            self.ui.labelError.setText("SetToZero except fail X")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
            return -1

# ********************************Set To Zero_X **********************************************

# ********************************Step Validation*********************************************

    def StepValidation(self):
        try:
            self.ThreadStep = threading.Thread(target=self.StepValidationThread)
            self.ui.BtSetToZero.setEnabled(0)
            self.ui.BtAngleValidation.setEnabled(0)
            self.ui.BtStepValidation.setEnabled(0)
            self.ui.BtAutomaticGet.setEnabled(0)
            self.ThreadStep.start()
            self.timer_step.start(100)
        except:
            self.ui.labelError.setText("StepValidation except fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")

    def StepValidationThread(self):
        try:
            if True:
                DataTimeStart = datetime.datetime.now().strftime('%Y%m%d-%H-%M-%S')
                path1 = os.getcwd() + "/BojayLogs/PIR-AZIZ/AngleValidation/StepValidation/"
                if not os.path.exists(path1):
                    os.makedirs(path1)

                if self.ui.EditStepTimes.text() == '':
                    self.ErrorMessage = 'please input the digital'
                    return -1
                count = int(self.ui.EditStepTimes.text())

                ret = myMCUControl.SignalReSet(30)
                if ret != 0:
                    self.ErrorMessage = "fixture reset fail"
                    return -1
                wait_time = 2
                list_Step = [-90,-70,-50,-30,-10,0,10,30,50,70,90]
                with open(path1 + DataTimeStart + ".csv", 'wb') as anglefile:
                    string = " count,-90,-70,-50,-30,-10,0,10,30,50,70,90,\n"
                    if myMCUControl.Interpreter == 3:
                        string = string.encode('utf-8')
                    anglefile.write(string)
                    for i in range(count):
                        string = str(count) + ','
                        if myMCUControl.Interpreter == 3:
                            string = string.encode('utf-8')
                        anglefile.write(string)
                        for angle in list_Step:
                            datalist = []
                            ret = myMCUControl.MoveToCoordinates(angle, 65)
                            if ret != 0:
                                self.ErrorMessage = 'Set absolute movement fail'
                                return -1
                            starttime = time.time()
                            while (time.time() - starttime) < wait_time:
                                ret = myMCUControl.ReadXAngleAndYAngle(datalist)
                                if ret != 0:
                                    self.ErrorMessage = "Read XYAngle error"
                                    return -1
                                print("datalist[0] = {0},angle = {1},diff = {2}".format(datalist[0],angle,abs(datalist[0]-angle)))
                                if abs(datalist[0] - angle) < 0.2:
                                    break
                            string = str(datalist[0]) + ','
                            if myMCUControl.Interpreter == 3:
                                string = string.encode('utf-8')
                            anglefile.write(string)
                        string = str( '\n')
                        if myMCUControl.Interpreter == 3:
                            string = string.encode('utf-8')
                        anglefile.write(string)

                ret = myMCUControl.SignalReSet(30)
                if ret != 0:
                    self.ErrorMessage = "fixture reset fail"
                    return -1

                self.step_validation_end = True
            else:


                if self.ui.EditStepTimes.text() == '':
                    self.ErrorMessage = 'please input the digital'
                    return -1
                count = int(self.ui.EditStepTimes.text())

                ret = myMCUControl.SignalReSet(30)
                if ret != 0:
                    self.ErrorMessage = "fixture reset fail"
                    return -1

                # ret = myMCUControl.SetAngleHome()
                # if ret != 0:
                #     self.ErrorMessage = "Set angle home fail"
                #     return -1
                list_Step = []
                for i in range(-90,91,1):
                    list_Step.append(i)

                for i in range(count):
                    DataTimeStart = datetime.datetime.now().strftime('%Y%m%d-%H-%M-%S')
                    path1 = os.getcwd() + "/BojayLogs/PIR-AZIZ/AngleTest/SensorValidation/"
                    if not os.path.exists(path1):
                        os.makedirs(path1)

                    with open(path1 + DataTimeStart + ".csv", 'wb') as anglefile:
                        string = " angle,X_angle,Y_angle,\n"
                        if myMCUControl.Interpreter == 3:
                            string = string.encode('utf-8')
                        anglefile.write(string)
                        for angle in list_Step:
                            datalist = []
                            ret = myMCUControl.MoveToCoordinates(angle, 71)
                            if ret != 0:
                                self.ErrorMessage = 'Set absolute movement fail'
                                return -1

                            while True:
                                ret = myMCUControl.ReadXAngleAndYAngle(datalist)
                                print("datalist[0] = {0},angle = {1},ret = {2}".format(datalist[0],angle,ret))
                                if abs(datalist[0] - angle) < 0.1:
                                    break
                            # ret = myMCUControl.ReadXAngleAndYAngle(datalist)
                            # if ret != 0:
                            #     self.ErrorMessage = "Read XYAngle error"
                            #     return -1

                            # if abs(datalist[0] - angle) > 0.1:
                            #     ret = myMCUControl.ReadXAngleAndYAngle(datalist)

                            string = str(angle)+','+str(datalist[0]) + ','+str(datalist[1]) + str('\n')
                            if myMCUControl.Interpreter == 3:
                                string = string.encode('utf-8')
                            anglefile.write(string)


                ret = myMCUControl.SignalReSet(30)
                if ret != 0:
                    self.ErrorMessage = "fixture reset fail"
                    return -1

                self.step_validation_end = True

        except:
            self.ErrorMessage = "StepValidationThread except fail"

    def  ShowStepTimer(self):
        try:
            if self.ErrorMessage != '':
                self.ui.labelError.setText(self.ErrorMessage)
                self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                self.ui.BtSetToZero.setEnabled(1)
                self.ui.BtAngleValidation.setEnabled(1)
                self.ui.BtStepValidation.setEnabled(1)
                self.ui.BtAutomaticGet.setEnabled(1)
                self.timer_step.stop()
            if self.step_validation_end == True:
                self.step_validation_end = False
                self.ui.BtSetToZero.setEnabled(1)
                self.ui.BtAngleValidation.setEnabled(1)
                self.ui.BtStepValidation.setEnabled(1)
                self.ui.BtAutomaticGet.setEnabled(1)
                self.ui.labelError.setText("step validation pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                self.timer_step.stop()
        except:
            self.ui.labelError.setText("ShowStepTimer except fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
            return -1
# ********************************Step Validation*********************************************

# ********************************Angle Validation*********************************************

    def AngleValidation(self):
        try:
            path1 = os.getcwd() + "/BojayLogs/PIR-AZIZ/AngleValidation/SensorValidation/"
            if not os.path.exists(path1):
                os.makedirs(path1)
            self.DataTimeStart = datetime.datetime.now().strftime('%Y%m%d-%H-%M-%S')
            self.writer = pd.ExcelWriter(path1 + self.DataTimeStart + ".xls")
            ret = myMCUControl.SignalReSet()
            if ret != 0:
                self.ui.labelError.setText("fixture reset fail")
                self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                return -1

            ret = myMCUControl.SetAngleHome()
            if ret != 0:
                self.ui.labelError.setText("Set angle home fail")
                self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                return -1

            for i in range(10):
                self.count = i+1
                self.ThreadAngle = threading.Thread(target=self.AngleValidationThread)
                ret = myMCUControl.MoveToCoordinates(-90,71)
                if ret != 0:
                    self.ui.labelError.setText("fixture reset fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.ThreadAngle.start()
                ret = myMCUControl.MoveToCoordinates(90,71)
                if ret != 0:
                    self.ui.labelError.setText("set absolute movement fail")
                    self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
                    return -1
                self.move_axis_stop = True
                while True:
                    if self.angle_validation_end == True:
                        self.angle_validation_end = False
                        break
            self.writer.save()

        except:
            self.ui.labelError.setText("AngleValidation except fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")

    def AngleValidationThread(self):
        try:



            dict_data = {"Angle1":[],"Angle2":[],"diff":[]}

            datalist1 = []
            ret = myMCUControl.ReadXAngleAndYAngle(datalist1)
            if ret != 0:
                self.ErrorMessage = "Read XYAngle error"
                return -1
            while True:
                if self.move_axis_stop == True:
                    self.move_axis_stop = False
                    break

                datalist2 = []
                ret = myMCUControl.ReadXAngleAndYAngle(datalist2)
                if ret != 0:
                    self.ErrorMessage = "Read XYAngle error"
                    return -1
                dict_data["Angle1"].append(datalist1[0])
                dict_data["Angle2"].append(datalist2[0])
                dict_data["diff"].append(abs(round(datalist1[0]-datalist2[0],2)))
                datalist1 = []
                datalist1 = datalist2


            data_Angle = pd.DataFrame(dict_data)

            data_Angle.to_excel(excel_writer=self.writer,sheet_name="data"+str(self.count),index=True)
            self.angle_validation_end = True


        except Exception as e:
            self.ErrorMessage = "StepValidationThread except fail"


    def ShowAngleTimer(self):
        try:
            if self.ErrorMessage != '':
                self.ui.labelError.setText(self.ErrorMessage)
                self.ui.BtSetToZero.setEnabled(1)
                self.ui.BtAngleValidation.setEnabled(1)
                self.ui.BtStepValidation.setEnabled(1)
                self.timer_angle.stop()
            if self.angle_validation_end == True:
                self.ui.labelError.setText("angle validation pass")
                self.ui.labelError.setStyleSheet("background-color: rgb(0, 255, 0);")
                self.timer_step.stop()
        except:
            self.ui.labelError.setText("ShowAngleTimer except fail")
            self.ui.labelError.setStyleSheet("background-color: rgb(255, 0, 0);")
            return -1
# ********************************Angle Validation*********************************************

# ********************************Show Error Message*********************************************
    def ShowErrorMessage(self, message):
        try:
            myMessageBox = QMessageBox()
            myMessageBox.information(self, "Warning", message, myMessageBox.Ok)
            return 0
        except:
            self.ShowErrorMessage("ShowErrorMessage except Fail")
            return 1

# ********************************Show Error Message*********************************************
    def Burning1(self):
        try:

            ThreadTemp = threading.Thread(target=self.TemperatureValidationThread)
            ThreadTemp.start()

            DataTimeStart = datetime.datetime.now().strftime('%Y%m%d-%H-%M-%S')

            path1 = os.getcwd() + "/BojayLogs/PIR-AZIZ/AngleValidation/StepValidation/"
            if not os.path.exists(path1):
                os.makedirs(path1)

            path2 = os.getcwd() + "/BojayLogs/PIR-AZIZ/AngleValidation/StepValidation2/"
            if not os.path.exists(path2):
                os.makedirs(path2)

            list_Step = [120,110,90, 70, 50, 30, 10, 0, -10, -30, -50, -70, -89,-90,-110,-120]
            # list_Step = [-10, 30]
            anglefile = open(path1 + DataTimeStart + ".csv", 'ab+')
            string = " count,120,110,90, 70, 50, 30, 10, 0, -10, -30, -50, -70, -89,-90,-110,-120\n"
            if myMCUControl.Interpreter == 3:
                string = string.encode('utf-8')
            anglefile.write(string)


            # list_Step_x = []
            # for i in range(0,91,1):
            #     list_Step_x.append(i)
            #     anglefile_x = open(path2 + DataTimeStart + ".csv", 'wb')
            #     string = " count,0,1,2,3\n"
            #     if myMCUControl.Interpreter == 3:
            #         string = string.encode('utf-8')
            #     anglefile_x.write(string)

            list_Step_x = [0,10,15,30,55,75,80,90]
            # list_Step_x = [0, 10]
            anglefile_x = open(path2 + DataTimeStart + ".csv", 'ab+')
            string = " count,0,10,15,30,55,75,80,90\n"
            if myMCUControl.Interpreter == 3:
                string = string.encode('utf-8')
            anglefile_x.write(string)

            if self.ui.EditBurnTimes.text() == '':
                self.ShowErrorMessage('please input the digital')
                return -1

            # reset

            # file
            count = int(self.ui.EditBurnTimes.text())

            wait_time = 2
            anglefile_x.close()
            anglefile.close()
            for i in range(count):
                anglefile_x = open(path2 + DataTimeStart + ".csv", 'ab+')
                anglefile = open(path1 + DataTimeStart + ".csv", 'ab+')
                print(i + 1)
                if self.ui.radioGQ.isChecked():
                    ret = myMCUControl.Set_DutState2(myMCUControl.Dutlock)
                    if ret != 0:
                        self.ShowErrorMessage('Set_DutState2 out error')
                        return -1
                    time.sleep(0.5)

                    ret = myMCUControl.Set_DutState1(myMCUControl.Dutlock)
                    if ret != 0:
                        self.ShowErrorMessage('Set_DutState1 out error')
                        return -1
                    time.sleep(0.5)



                # ******************************
                string = str(i + 1) + ','
                if myMCUControl.Interpreter == 3:
                    string = string.encode('utf-8')
                anglefile.write(string)

                for angle in list_Step:
                    datalist = []
                    ret = myMCUControl.MoveToCoordinates(angle, 98)
                    if ret != 0:
                        self.ErrorMessage = 'Set absolute movement fail'
                        return -1
                    starttime = time.time()
                    while (time.time() - starttime) < wait_time:
                        ret = myMCUControl.ReadXAngleAndYAngle(datalist)
                        if ret != 0:
                            self.ErrorMessage = "Read XYAngle error"
                            return -1
                        print("datalist[0] = {0},angle = {1},diff = {2}".format(datalist[0], angle,abs(datalist[0] - angle)))
                        if abs(datalist[0]-angle) < 0.2:
                            break
                    string = str(datalist[0]) + ','
                    if myMCUControl.Interpreter == 3:
                        string = string.encode('utf-8')
                    anglefile.write(string)


                string = str('\n')
                if myMCUControl.Interpreter == 3:
                    string = string.encode('utf-8')
                anglefile.write(string)



                ret = myMCUControl.MoveToCoordinates(0, 98)
                if ret != 0:
                    self.ErrorMessage = 'Set absolute movement fail'
                    return -1



                # ****************************
                string = str(i + 1) + ','
                if myMCUControl.Interpreter == 3:
                    string = string.encode('utf-8')
                anglefile_x.write(string)

                for angle in list_Step_x:
                    datalist1 = []
                    ret = myMCUControl.MoveToCoordinates_X(angle, 100)
                    if ret != 0:
                        self.ErrorMessage = 'Set absolute_X movement fail'
                        return -1
                    time.sleep(0.5)
                    starttime = time.time()
                    while (time.time() - starttime) < wait_time:
                        ret = myMCUControl.ReadXAngleAndYAngle_X(datalist1)
                        if ret != 0:
                            self.ErrorMessage = "Read XYAngle error"
                            return -1
                        print("datalist1[0] = {0},angle = {1},diff = {2}".format(datalist1[0], angle,
                                                                                 abs(datalist1[0] - angle)))
                        if abs(datalist1[0] - angle) < 0.2:
                            break
                    string = str(datalist1[0]) + ','
                    if myMCUControl.Interpreter == 3:
                        string = string.encode('utf-8')
                    anglefile_x.write(string)
                string = str('\n')
                if myMCUControl.Interpreter == 3:
                    string = string.encode('utf-8')
                anglefile_x.write(string)
                ret = myMCUControl.MoveToCoordinates_X(0, 100)
                if ret != 0:
                    self.ErrorMessage = 'Set absolute_x movement fail'
                    return -1
                time.sleep(1)


                if self.ui.radioGQ.isChecked():
                    ret = myMCUControl.Set_DutState1(myMCUControl.DutUnlock)
                    if ret != 0:
                        self.ShowErrorMessage('Set_DutState1 out error')
                        return -1
                    time.sleep(0.5)

                    ret = myMCUControl.Set_DutState2(myMCUControl.DutUnlock)
                    if ret != 0:
                        self.ShowErrorMessage('Set_DutState1 out error')
                        return -1
                    time.sleep(0.5)

                    # ret = myMCUControl.Set_DutState2(myMCUControl.Dutlock)
                    # if ret != 0:
                    #     self.ShowErrorMessage('Set_DutState1 out error')
                    #     return -1
                    # time.sleep(0.5)
                    #
                    # ret = myMCUControl.Set_DutState1(myMCUControl.Dutlock)
                    # if ret != 0:
                    #     self.ShowErrorMessage('Set_DutState1 out error')
                    #     return -1
                    # time.sleep(0.5)

                # *************************************
                anglefile_x.close()
                anglefile.close()
        except Exception as e:
            self.ui.labelError.setText("Burning except fail {}".format(e))
            self.ui.labelError.setStyleSheet("background-color: rgb(255,0 , 0);")
# ***************************Burning*******************************************




















app = QtWidgets.QApplication(sys.argv)
myFrame = MuduFrame()
myFrame.exec_()
exit(app.exec_())
