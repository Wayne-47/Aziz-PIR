# -*- coding: utf-8 -*-
# 开发团队：
# 开发人员：
# 开发时间：2020/8/2513:59
# 文件名称：testdemo
# 开发工具：PyCharm

import threading


def GOEInterface(self, argv):
    try:
        # if (argv.__len__() != 1):
        #     return

        # 单步动作
        if (argv.__len__() == 2):
            Event = str(argv[1])

            if Event == "open":
                ret = self.Set_DoorState(self.DoorOpen)
            if Event == "close":
                ret = self.Set_DoorState(self.DoorClose)
            if Event == "out":
                ret = self.Set_CylinderFunction_1(self.Out)
            if Event == "in":
                ret = self.Set_CylinderFunction_1(self.In)
            if Event == "lock":
                ret = self.Set_DutState1(self.DutUnlock)
            if Event == "unlock":
                ret = self.Set_DutState1(self.Dutlock)
            if Event == "reset":
                ret = self.SignalReSet()


        # 单步移动
        elif (argv.__len__() == 5):
            Axid = str(argv[1])
            Move = int(argv[2])
            Speed = int(argv[3])
            Delay = float(argv[4])
            Delay = Delay / 1000

            if Axid == "R":
                # ret = self.SetSpeed(Speed)
                time.sleep(Delay)
                ret = self.MoveToCoordinates(value=Move, speed=Speed)
            if Axid == "X":
                # ret = self.SetSpeed_X(Speed)
                time.sleep(Delay)
                ret = self.MoveToCoordinates_X(value=Move, speed=Speed)

        # 边跑边抓数据
        elif (argv.__len__() > 6):
            # if(argv.__len__() == 7):
            TotalTime = float(argv[1])
            TotalTime = TotalTime / 1000.00
            frequency = float(argv[2])
            frequency = frequency / 1000.00
            fileName = str(argv[3])
            filePath = str(argv[4])
            Move1 = int(argv[5])
            Delay1 = float(argv[6])
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
            # Stride = int(argv[7])

            try:
                time.sleep(Delay1)
                acionThread = threading.Thread(target=self.TestMove, args=(Move1,))
                acionThread.start()
                recordThread = threading.Thread(target=self.GetAngleAndTemperature,
                                                args=(TotalTime, frequency, fileName, filePath))
                recordThread.start()
            except Exception as e:
                print("Error: unable to start thread {}".format(e))

            # wait_time = 2
            # timeout = 0
            # angle_device = []
            # angle_target = []
            #
            # list_Step_x = []
            # Move = Move + 1
            # time.sleep(Delay)
            #
            # while (TotalTime > timeout):
            #     for i in range(0,Move,Stride):
            #         list_Step = list_Step.append(i)
            #         anglefile = open(filePath + fileName + ".txt")
            #         string = " 时戳，标靶角度，标靶温度，室温\n"
            #         if self.Interpreter == 3:
            #             string = string.encode('utf-8')
            #         anglefile_x.write(string)
            #
            #     # string = str(i + 1) + ','
            #     if self.Interpreter == 3:
            #         string = string.encode('utf-8')
            #     anglefile.write(string)
            #     for angle in list_Step:
            #         #时戳获取
            #         Time_stamp = round(time.time(),3)
            #         Time_stamp = int((Time_stamp * 1000))
            #
            #         datalist = []
            #         temperature = []
            #         ret = self.MoveToCoordinates(angle, 65)
            #         if ret != 0:
            #             self.ErrorMessage = 'Set absolute movement fail about API'
            #             return -1
            #         starttime = time.time()
            #         while (time.time() - starttime) < wait_time:
            #             ret = self.ReadXAngleAndYAngle(datalist)
            #             if ret != 0:
            #                 self.ErrorMessage = "Read XYAngle error timeout about API"
            #                 return -1
            #             room_temperature = self.GetCurrentTemperature(self.LCD4)
            #             target_temperature = self.GetCurrentTemperature(self.LCD1)
            #             print("Time_stamp[0] = {0}, Target_angle = {1}, Target_temperature= {2} ,Room_temperature = {3}".format(Time_stamp, datalist[0],
            #                                                                   target_temperature,room_temperature))
            #         string = str(Time_stamp) + ',' + str(datalist[0])  + ',' + str(target_temperature)  + ',' + str(room_temperature) + ','
            #         if self.Interpreter == 3:
            #             string = string.encode('utf-8')
            #         anglefile.write(string)
            #     string = str('\n')
            #     if self.Interpreter == 3:
            #         string = string.encode('utf-8')
            #     anglefile.write(string)
            #     timeout = timeout + frequency
            #
            # ret = self.MoveToCoordinates(0, 65)
            # if ret != 0:
            #     self.ErrorMessage = 'Set absolute movement fail about API'
            #     return -1

    except Exception as e:
        print("GOE Interface except fail {}".format(e))
        return e


# ********************************************************************#
def GetAngleAndTemperature(self, TotalTime, frequency, fileName, filePath):
    print('hello, this is get sensor value thread')
    timeout = 0
    angle_device = []
    angle_target = []

    while (True):
        print('hello, this is while true')
        if (self.RotateAxisThreadingFinish == True):
            self.RotateAxisThreadingFinish = False
            self.ThreadingFinish = True
            break
        else:
            self.ReadXAngleAndYAngle(angle_device)  # 标靶轴
            self.ReadXAngleAndYAngle_X(angle_target)  # Dut轴
            # 时戳获取
            Time_stamp = round(time.time(), 3)
            Time_stamp = int((Time_stamp * 1000))

            # temperature = []
            # for i in range(4):
            #     temperature.append(self.GetCurrentTemperature(i))
            target_temperature = self.GetCurrentTemperature(self.LCD1)
            room_temperature = self.GetCurrentTemperature(self.LCD4)

            fileName = fileName + ".txt"
            data_path_file = os.path.join(filePath, fileName)
            with open(data_path_file, "w") as f:
                string = " 时戳，标靶角度，标靶温度，室温\n"
                f.writelines(string)
                f.writelines(str(Time_stamp) + "," + str(angle_device[0]) + "," + str(target_temperature)
                             + "," + str(room_temperature) + "\n")
                f.close()
            timeout = timeout + frequency
            time.sleep(frequency)


# ********************************************************************#
def TestMove(self, Move1):
    if (self.RotateAxisThreadingFinish == False):
        Speed = 60
        ret = self.MoveToCoordinates(value=Move1, speed=Speed)
        self.RotateAxisThreadingFinish = True


# ********************************************************************#


if __name__== '__main__':
    GOE.GOEInterface(sys.argv)