import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDialog, QLabel, QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer,QDateTime, QObject, QThread, pyqtSignal, QRunnable, Qt, QThreadPool
import datetime
import socket
import json
import select
from monitoring import Ui_MainWindow
import xml.etree.ElementTree as ET
from xml.dom import minidom
import xmltodict



class WorkerUDP(QObject):
    signal_Config_Values = pyqtSignal(dict)
    signal_Sensors = pyqtSignal(dict)
    signal_Inverter = pyqtSignal(dict)
    signal_Errors = pyqtSignal(dict)
    signal_Math = pyqtSignal(dict)
    signal_Controls = pyqtSignal(dict)
    signal_FPGA_Error = pyqtSignal(dict)
    signal_Timestamp = pyqtSignal(dict)

    signal_Config_Values_serial = pyqtSignal(bytes)
    signal_Config_Values_init = pyqtSignal(dict)
    signal_Sensors_serial = pyqtSignal(bytes)
    signal_Sensors_init = pyqtSignal(dict)

    def int_litleE_to_bigE(self, oldString):

        oldString_binary = bin(oldString)
        oldString_binary = oldString_binary.replace('0b', '')
        newString_binary = '0b' + oldString_binary[::-1]

        return int(newString_binary, 2)

    def serial_to_float(self, byte1, byte2, byte3, byte4):
        str_byte1 = bin(byte1)
        str_byte2 = bin(byte2)
        str_byte3 = bin(byte3)
        str_byte4 = bin(byte4)
        while(len(str_byte1) < 10):
            str_byte1 = '0' + str_byte1
        while (len(str_byte2) < 10):
            str_byte2 = '0' + str_byte2
        while (len(str_byte3) < 10):
            str_byte3 = '0' + str_byte3
        while (len(str_byte4) < 10):
            str_byte4 = '0' + str_byte4
        value = str_byte1 + str_byte2 + str_byte3 + str_byte4
        value = value.replace('0b', '')
        exp = '0b' + value[1] + value[2] + value[3] + value[4] + value[5] + value[6] + value[7] + value[8]
        matisse = 1 + int(value[9]) * 2 ** (-1) + int(value[10]) * 2 ** (-2) + int(value[11]) * 2 ** (-3) + \
                  int(value[12]) * 2 ** (-4) + int(value[13]) * 2 ** (-5) + int(value[14]) * 2 ** (-6) + \
                  int(value[15]) * 2 ** (-7) + int(value[16]) * 2 ** (-8) + int(value[17]) * 2 ** (-9) + \
                  int(value[18]) * 2 ** (-10) + int(value[19]) * 2 ** (-11) + int(value[20]) * 2 ** (-12) + \
                  int(value[21]) * 2 ** (-13) + int(value[22]) * 2 ** (-14) + int(value[23]) * 2 ** (-15) + \
                  int(value[24]) * 2 ** (-16) + int(value[25]) * 2 ** (-17) + int(value[26]) * 2 ** (-18) + \
                  int(value[27]) * 2 ** (-19) + int(value[28]) * 2 ** (-20) + int(value[29]) * 2 ** (-21) + \
                  int(value[30]) * 2 ** (-22) + int(value[31]) * 2 ** (-23)
        exp_int = int(exp, 2) - 127
        value_float = float((2 ** exp_int) * matisse)
        if (value[0] == '1'):
            value_float = -value_float
        return value_float

    def show(self, elem, level=0):
        print("Element:" ,elem.tag)
        print("Attr.:", elem.attrib)
        print("text:", elem.text)
        print("Level:", level)
        i=0
        for child in elem.findall('*'):
            i=i+1
            print("i:",i)
            self.show(child, level+1)

    def run(self):
        UDP_IP = "192.168.178.20"
        UDP_PORT = 1005

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))
        sock.setblocking(0)


        while True:

            ready = select.select([sock], [], [], 2)
            if ready[0]:
                data, addr = sock.recvfrom(4096)
                #print("print data:",data)
                #print("Type:",type(data))
                str = data.decode("utf-8", errors="ignore")
                #print("str:", str)
                #test = str(data,'utf-8')
                #print("String:", str(data,'utf-8'))
                #xmldoc = minidom.parseString(data)
                #mldict = self.XmlDictConfig(root)
                #print("root:", root)

                if(data[3] == 1):
                    """self.signal_Config_Values_serial.emit(data)
                    #print(data)
                    #print(type(data))
                    test = self.serial_to_float(data[4], data[5], data[6], data[7])
                    #print(test)"""
                    pass

                elif(data[3] == 2):
                    """print(data)
                    print(type(data))

                    self.signal_Sensors_serial.emit(data)"""
                    pass


                else:

                    doc = xmltodict.parse(str)
                    xmljson = json.dumps(xmltodict.parse(str))
                    xmljsonload = json.loads(xmljson)
                    print("xmlJson:", xmljson)
                    #print(xmljson["Cluster"]["Name"])
                    print("xmljsonload:", xmljsonload)
                    print(xmljsonload['Cluster']['Name'])
                    print("doc:", doc)
                    print("doc1:", doc['Cluster']['Name'])
                    print("doc1:", doc['Cluster']['EB']['Name'])
                    print("doc1:", doc['Cluster']['EB']['Choice'][int(doc['Cluster']['EB']['Val'])])
                    print("doc:",doc.items())
                    for key, value in doc.items():  # accessing keys
                        print("key")
                        print(key, end=',')
                    root = ET.fromstring(str)
                    #print(type(root))
                    print("root:",root.tag)
                    #print(root.find("Config-Values").tag)
                    #self.show(root)
                    print("Name:",root.find("Cluster"))
                    print("items:", root.items())
                    for attrName, attrValue in root.items():
                        print("Name and attribute:",attrName + '=' + attrValue)
                    #testtest=list(root)
                    #print(type(testtest))
                    #print(testtest)

                    #for x in root.findall('Cluster'):
                    #    item = x.find('Val').text
                    #    price = x.find('BSR').text
                    #    print(item, price)
                    #for child in root:
                    #    print("Child: ", child.tag)
                    #    print("Attribut: ",  child.attrib)
                    #print(root)

                    """"#time.sleep(0.3)
                    if ('Vehicle Mode' in recvData):
                        self.signal_Config_Values.emit(recvData)
                        self.signal_Config_Values_init.emit(recvData)
                    elif('Analog' and 'Akku/HV' and 'SC' and 'Fuses' in recvData):
                        self.signal_Sensors.emit(recvData)
                        self.signal_Sensors_init.emit(recvData)
                    elif('VR' and 'VL' and 'HR' and 'HL' in recvData):
                        self.signal_Inverter.emit(recvData)
                    elif ('Timeout CAN' and 'Wert' and 'Latching' in recvData):
                        self.signal_Errors.emit(recvData)
                    elif ('General' and 'TV/KF' and 'Energy Control' in recvData):
                        self.signal_Math.emit(recvData)
                    elif ('Switches' in recvData):
                        self.signal_Controls.emit(recvData)
                    elif ('Input Error Code' and 'Output Error Code' and 'Transmit Error Counter' and ' Error Counter' in recvData):
                        self.signal_FPGA_Error.emit(recvData)
                    elif ('Timestamp' in recvData):
                        self.signal_Timestamp.emit(recvData)
            else:
                #Reset value if the connection is lost
                data = '{"Vehicle Mode": " ", "APPS1_min[°]": " ", "APPS1_max[°]": " ", "APPS2_min[°]": " ",' \
                       ' "APPS2_max[°]": " ", "maxTorque+[Nm]": " ", "maxTorque-[Nm]": " ", "Leistungslimit[kW]": " ",' \
                       ' "maxRPM[1/min]": " ", "Rekuperation": " ", "ASR": " ", "BSR": " ", "TV": " ", "DRS": " ",' \
                       ' "Energiesparmodus": " ", "Accelslip [%/100]": " ", "Brakeslip [%/100]": " ",' \
                       ' "Backupload": " ", "Config locked": " ", "InverterVR-active": " ", "InverterVL-active": " ",' \
                       ' "InverterHR-active": " ", "InverterHL-active": " "}'
                recvData = json.loads(data)
                self.signal_Config_Values.emit(recvData)"""


class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        self.main_window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.main_window)

        self.ui.Pages.setCurrentWidget(self.ui.page_config_values)

        self.ui.btn_config_values.clicked.connect(lambda: self.show_page_config_values())
        self.ui.btn_sensors.clicked.connect(lambda: self.show_page_sensors())
        self.ui.btn_inverter.clicked.connect(lambda: self.show_page_inverter())
        self.ui.btn_errors.clicked.connect(lambda: self.show_page_errors())
        self.ui.btn_math.clicked.connect(lambda: self.show_page_math())
        self.ui.btn_controls.clicked.connect(lambda: self.show_page_controls())
        self.ui.btn_fpga_error.clicked.connect(lambda: self.show_page_fpga_error())
        self.ui.btn_timestamp.clicked.connect(lambda: self.show_page_timestamp())

        self.thread = QThread()#WorkerUDP()
        self.worker = WorkerUDP()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        self.worker.signal_Config_Values.connect(lambda json_config: self.recieve_Config_Values(json_config))
        self.worker.signal_Sensors.connect(lambda json_Sensors: self.recieve_Sensors(json_Sensors))
        self.worker.signal_Inverter.connect(lambda json_Inverter: self.recieve_Inverter(json_Inverter))
        self.worker.signal_Errors.connect(lambda json_Errors: self.recieve_Errors(json_Errors))
        self.worker.signal_Math.connect(lambda json_Math: self.recieve_Math(json_Math))
        self.worker.signal_Controls.connect(lambda json_Controls: self.recieve_Controls(json_Controls))
        self.worker.signal_FPGA_Error.connect(lambda json_FPGA_Error: self.recieve_FPGA_Error(json_FPGA_Error))
        self.worker.signal_Timestamp.connect(lambda json_Timestamp: self.recieve_Timestamp(json_Timestamp))
        self.worker.signal_Config_Values_init.connect(
            lambda json_config_init: self.set_config_list(json_config_init))
        self.worker.signal_Config_Values_serial.connect(
            lambda json_config_serial: self.recieve_Config_Values_serial(json_config_serial))
        self.worker.signal_Sensors_init.connect(
            lambda json_sensors_init: self.set_Sensors_list(json_sensors_init))
        self.worker.signal_Sensors_serial.connect(
            lambda Sensors_serial: self.recieve_Sensors_serial(Sensors_serial))
        self.thread.start()



        self.config_list = []
        self.sensors_list = []
        self.sensors_list_index = 0

    def set_config_list(self, json_config_init):
        self.config_list = json_config_init

    def set_Sensors_list(self, json_sensors_init):
        print("Index: ", self.sensors_list_index)
        #if (self.sensors_list_index == 0):
        self.sensors_list = json_sensors_init
        #else:
        #    self.sensors_list_index = self.sensors_list_index + 1


    def set_lineEdit(self, name_lineEdit, dataList, listElement, listElement2d = 'empty', listElement3d = 'empty'):
        if (listElement2d == 'empty'):
            if (listElement in dataList):
                name_lineEdit.setText(str(dataList[listElement]))
            else:
                name_lineEdit.setText('Element not in the Cluster')
        elif(listElement3d == 'empty'):
            if (listElement2d in dataList[listElement]):
                name_lineEdit.setText(str(dataList[listElement][listElement2d]))
            else:
                name_lineEdit.setText('Element not in the Cluster')
        else:
            if (listElement3d in dataList[listElement][listElement2d]):
                name_lineEdit.setText(str(dataList[listElement][listElement2d][listElement3d]))
            else:
                name_lineEdit.setText('Element not in the Cluster')

    def set_btn_LED(self, name_btn_LED, dataList, listElement, listElement2d = 'empty', listElement3d = 'empty'):
        if(listElement2d == 'empty'):
            if(listElement in dataList):
                if (dataList[listElement] == False):
                    name_btn_LED.setStyleSheet('border: none; border-radius: 10px; background-color: red')
                elif (dataList[listElement] == True):
                    name_btn_LED.setStyleSheet(
                        'border: none; border-radius: 10px; background-color: rgb(38, 255, 0);')
                else:
                    name_btn_LED.setStyleSheet(
                        'border: none; border-radius: 10px; background-color: rgb(100, 100, 100);')
            else:
                name_btn_LED.setText('Element not in the Cluster')
        elif(listElement3d == 'empty'):
            if (listElement2d in dataList[listElement]):
                if (dataList[listElement][listElement2d] == False):
                    name_btn_LED.setStyleSheet('border: none; border-radius: 10px; background-color: red')
                elif (dataList[listElement][listElement2d] == True):
                    name_btn_LED.setStyleSheet(
                        'border: none; border-radius: 10px; background-color: rgb(38, 255, 0);')
                else:
                    name_btn_LED.setStyleSheet(
                        'border: none; border-radius: 10px; background-color: rgb(100, 100, 100);')
            else:
                name_btn_LED.setText('Element not in the Cluster')
        else:
            if (listElement3d in dataList[listElement][listElement2d]):
                if (dataList[listElement][listElement2d][listElement3d] == False):
                    name_btn_LED.setStyleSheet('border: none; border-radius: 10px; background-color: red')
                elif (dataList[listElement][listElement2d][listElement3d] == True):
                    name_btn_LED.setStyleSheet(
                        'border: none; border-radius: 10px; background-color: rgb(38, 255, 0);')
                else:
                    name_btn_LED.setStyleSheet(
                        'border: none; border-radius: 10px; background-color: rgb(100, 100, 100);')
            else:
                name_btn_LED.setText('Element not in the Cluster')

    def serial_to_float(self, byte1, byte2, byte3, byte4):
        str_byte1 = bin(byte1)
        str_byte2 = bin(byte2)
        str_byte3 = bin(byte3)
        str_byte4 = bin(byte4)
        while(len(str_byte1) < 10):
            str_byte1 = '0' + str_byte1
        while (len(str_byte2) < 10):
            str_byte2 = '0' + str_byte2
        while (len(str_byte3) < 10):
            str_byte3 = '0' + str_byte3
        while (len(str_byte4) < 10):
            str_byte4 = '0' + str_byte4
        value = str_byte1 + str_byte2 + str_byte3 + str_byte4
        value = value.replace('0b', '')
        exp = '0b' + value[1] + value[2] + value[3] + value[4] + value[5] + value[6] + value[7] + value[8]
        matisse = 1 + int(value[9]) * 2 ** (-1) + int(value[10]) * 2 ** (-2) + int(value[11]) * 2 ** (-3) + \
                  int(value[12]) * 2 ** (-4) + int(value[13]) * 2 ** (-5) + int(value[14]) * 2 ** (-6) + \
                  int(value[15]) * 2 ** (-7) + int(value[16]) * 2 ** (-8) + int(value[17]) * 2 ** (-9) + \
                  int(value[18]) * 2 ** (-10) + int(value[19]) * 2 ** (-11) + int(value[20]) * 2 ** (-12) + \
                  int(value[21]) * 2 ** (-13) + int(value[22]) * 2 ** (-14) + int(value[23]) * 2 ** (-15) + \
                  int(value[24]) * 2 ** (-16) + int(value[25]) * 2 ** (-17) + int(value[26]) * 2 ** (-18) + \
                  int(value[27]) * 2 ** (-19) + int(value[28]) * 2 ** (-20) + int(value[29]) * 2 ** (-21) + \
                  int(value[30]) * 2 ** (-22) + int(value[31]) * 2 ** (-23)
        exp_int = int(exp, 2) - 127
        value_float = float((2 ** exp_int) * matisse)
        if (value[0] == '1'):
            value_float = -value_float
        return value_float


    def recieve_Config_Values_serial(self, config_serial):
        for element in self.config_list:
            print(element)
            print(self.config_list[element])
            #if(type(self.config_list[element]) == 'int'):
            #for element2d in element:
                #print(element2d)

            #self.config_list[i] = int(self.serial_to_float(json_config_serial[4], json_config_serial[5], json_config_serial[6], json_config_serial[7]))
        #test = self.serial_to_float(json_config_serial[4], json_config_serial[5], json_config_serial[6], json_config_serial[7])
        print("Listeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee:")
        print(self.config_list)
        #pass
    def recieve_Sensors_serial(self, Sensors_serial):
        print(self.serial_to_float(Sensors_serial[4], Sensors_serial[5], Sensors_serial[6], Sensors_serial[7]))
        #print("Sensors_serial: ", Sensors_serial)
        print(self.serial_to_float(Sensors_serial[4], Sensors_serial[5], Sensors_serial[6], Sensors_serial[7]))
        i = 0
        for element in self.sensors_list:

            #print(self.serial_to_float(Sensors_serial[4], Sensors_serial[5], Sensors_serial[6],
             #                    Sensors_serial[7]))
            #print(element)
            #print(self.sensors_list[element])
            #print(type(self.sensors_list[element]))
            #print(element)
            print(element)
            print("Type of element: ", element)
            if (isinstance((self.sensors_list[element]), dict)):
                for element2 in self.sensors_list[element]:
                    print(element2)
                    print("Type of element: ", element2)
                    print(type(self.sensors_list[element][element2]))
                    if (isinstance((self.sensors_list[element][element2]), dict)):
                        for element3 in self.sensors_list[element][element2]:
                            if (isinstance((self.sensors_list[element][element2][element3]), float) and not isinstance((self.sensors_list[element][element2][element3]), bool)):
                                # print("Sensors_serial: " ,Sensors_serial)
                                # print(self.serial_to_float(Sensors_serial[4], Sensors_serial[5], Sensors_serial[6], Sensors_serial[7]))
                                print("Wert vor der Zuweisung: ", self.serial_to_float(Sensors_serial[4 + i], Sensors_serial[5 + i], Sensors_serial[6 + i], Sensors_serial[7 + i]))
                                self.sensors_list[element][element2][element3] = int(self.serial_to_float(Sensors_serial[4 + i], Sensors_serial[5 + i], Sensors_serial[6 + i], Sensors_serial[7 + i]))
                                # self.sensors_list['Analog']['APPS1[°]'] = 25
                                # print(self.sensors_list['Analog']['APPS1[°]'])
                                print("Elementname int", element3)
                                print("Elementtype int", type(element3))
                                print("Elementtype int", type(self.sensors_list[element][element2][element3]))
                                print("Element int 3", self.sensors_list[element][element2][element3])
                                i = i + 4
                            else:
                                i = i + 1

                    elif (isinstance((self.sensors_list[element][element2]), int) and not isinstance((self.sensors_list[element][element2]), bool)):
                        #print("Sensors_serial: " ,Sensors_serial)
                        #print(self.serial_to_float(Sensors_serial[4], Sensors_serial[5], Sensors_serial[6], Sensors_serial[7]))
                        self.sensors_list[element][element2] = int(self.serial_to_float(Sensors_serial[4 + i], Sensors_serial[5 + i], Sensors_serial[6 + i], Sensors_serial[7 + i]))
                        #self.sensors_list['Analog']['APPS1[°]'] = 25
                        #print(self.sensors_list['Analog']['APPS1[°]'])
                        print("Elementname mit int", element2)
                        print("Elementtype mit int", type(element2))
                        print("Elementtype mit int", type(self.sensors_list[element][element2]))
                        print("Element mit int", self.sensors_list[element][element2])
                        i = i + 4
                    elif (isinstance((self.sensors_list[element][element2]), bool)):
                        print("bool")
                        print("Size of: ", sys.getsizeof(self.sensors_list[element][element2]))
                        i = i + 1
                    elif (isinstance((self.sensors_list[element][element2]), str)):
                        print("String")
                        print("Size of: ", len(self.sensors_list[element][element2]))
                        i = i + 1
                    else:
                        i = i + 1

        print("Liste:")
        #self.sensors_list['Analog']['APPS1[°]'] = 25
        #print(self.sensors_list['Analog']['APPS1[°]'])
        print(self.sensors_list)
        #pass"""


    def recieve_Config_Values(self, json_config):
        self.set_lineEdit(self.ui.lineEdit_Vehicle_Mode, json_config, 'Vehicle Mode')
        self.set_lineEdit(self.ui.lineEdit_APPS1_min, json_config, 'APPS1_min[°]')
        self.set_lineEdit(self.ui.lineEdit_APPS1_max, json_config, 'APPS1_max[°]')
        self.set_lineEdit(self.ui.lineEdit_APPS2_min, json_config, 'APPS2_min[°]')
        self.set_lineEdit(self.ui.lineEdit_APPS2_max, json_config, 'APPS2_max[°]')
        self.set_lineEdit(self.ui.lineEdit_maxTorque_plus, json_config, 'maxTorque+[Nm]')
        self.set_lineEdit(self.ui.lineEdit_maxTorque_minus, json_config, 'maxTorque-[Nm]')
        self.set_lineEdit(self.ui.lineEdit_Leistungslimit, json_config, 'Leistungslimit[kW]')
        self.set_lineEdit(self.ui.lineEdit_maxRPM, json_config, 'maxRPM[1/min]')
        self.set_lineEdit(self.ui.lineEdit_Accelslip, json_config, 'Accelslip [%/100]')
        self.set_lineEdit(self.ui.lineEdit_Brakeslip, json_config, 'Brakeslip [%/100]')
        self.set_btn_LED(self.ui.btn_LED_Rekuperation, json_config, 'Rekuperation')
        self.set_btn_LED(self.ui.btn_LED_ASR, json_config, 'ASR')
        self.set_btn_LED(self.ui.btn_LED_BSR, json_config, 'BSR')
        self.set_btn_LED(self.ui.btn_LED_TV, json_config, 'TV')
        self.set_btn_LED(self.ui.btn_LED_DRS, json_config, 'DRS')
        self.set_btn_LED(self.ui.btn_LED_Energiesparmodus, json_config, 'Energiesparmodus')
        self.set_btn_LED(self.ui.btn_LED_Backupload, json_config, 'Backupload')
        self.set_btn_LED(self.ui.btn_LED_Config_locked, json_config, 'Config locked')
        self.set_btn_LED(self.ui.btn_LED_InverterVR_active, json_config, 'InverterVR-active')
        self.set_btn_LED(self.ui.btn_LED_InverterVL_active, json_config, 'InverterVL-active')
        self.set_btn_LED(self.ui.btn_LED_InverterHR_active, json_config, 'InverterHR-active')
        self.set_btn_LED(self.ui.btn_LED_InverterHL_active, json_config, 'InverterHL-active')


        print(str(json_config))

    def recieve_Sensors(self, json_Sensors):
        self.set_lineEdit(self.ui.lineEdit_APPS1, json_Sensors, 'Analog', listElement2d='APPS1[°]')
        self.set_lineEdit(self.ui.lineEdit_APPS2, json_Sensors, 'Analog', listElement2d='APPS2[°]')
        self.set_lineEdit(self.ui.lineEdit_Bremsdruck_vorne, json_Sensors, 'Analog', listElement2d='Bremsdruck vorne [bar]')
        self.set_lineEdit(self.ui.lineEdit_Bremsdruck_hinten, json_Sensors, 'Analog', listElement2d='Bremsdruck hinten [bar]')
        self.set_lineEdit(self.ui.lineEdit_Bremskraft, json_Sensors, 'Analog', listElement2d='Bremskraft[N]')
        self.set_lineEdit(self.ui.lineEdit_Lenkwinkel, json_Sensors, 'Analog', listElement2d='Lenkwinkel[°]')
        self.set_lineEdit(self.ui.lineEdit_WT_Motor_high, json_Sensors, 'Analog', listElement2d='WT_Motor_high[°C]')
        self.set_lineEdit(self.ui.lineEdit_WT_Motor_Low, json_Sensors, 'Analog', listElement2d='WT_Motor_Low[°C]')
        self.set_lineEdit(self.ui.lineEdit_LT_Inv_FrR, json_Sensors, 'Analog', listElement2d='LT_Inv_FrR[°C]')
        self.set_lineEdit(self.ui.lineEdit_LT_Inv_FrL, json_Sensors, 'Analog', listElement2d='LT_Inv_FrL[°C]')
        self.set_lineEdit(self.ui.lineEdit_LT_Inv_ReR, json_Sensors, 'Analog', listElement2d='LT_Inv_ReR[°C]')
        self.set_lineEdit(self.ui.lineEdit_LT_Inv_ReL, json_Sensors, 'Analog', listElement2d='LT_Inv_ReL[°C]')
        self.set_lineEdit(self.ui.lineEdit_Ambient_Temp, json_Sensors, 'Analog', listElement2d='Ambient_Temp[°C]')
        self.set_lineEdit(self.ui.lineEdit_ST_FR, json_Sensors, 'Analog', listElement2d='ST_FR[mm}')
        self.set_lineEdit(self.ui.lineEdit_ST_FL, json_Sensors, 'Analog', listElement2d='ST_FL[mm]')
        self.set_lineEdit(self.ui.lineEdit_ST_RR, json_Sensors, 'Analog', listElement2d='ST_RR[mm]')
        self.set_lineEdit(self.ui.lineEdit_ST_RL, json_Sensors, 'Analog', listElement2d='ST_RL[mm]')
        self.set_lineEdit(self.ui.lineEdit_Temp_Fusebox, json_Sensors, 'Analog', listElement2d='Temp_Fusebox [°C]')

        self.set_lineEdit(self.ui.lineEdit_HV_Current, json_Sensors, 'Akku/HV', listElement2d='HV_Current[A]')
        self.set_lineEdit(self.ui.lineEdit_IC_Voltage, json_Sensors, 'Akku/HV', listElement2d='IC_Voltage[V]')
        self.set_lineEdit(self.ui.lineEdit_Charge, json_Sensors, 'Akku/HV', listElement2d='Charge[Ah]')
        self.set_lineEdit(self.ui.lineEdit_AMS_State, json_Sensors, 'Akku/HV', listElement2d='AMS-State')
        self.set_btn_LED(self.ui.btn_LED_State_SC, json_Sensors, 'Akku/HV', listElement2d='State SC')
        self.set_lineEdit(self.ui.lineEdit_Akku_Voltage, json_Sensors, 'Akku/HV', listElement2d='Akku-Voltage[V]')
        self.set_lineEdit(self.ui.lineEdit_SOC, json_Sensors, 'Akku/HV', listElement2d='SOC[%]')
        self.set_lineEdit(self.ui.lineEdit_CVH, json_Sensors, 'Akku/HV', listElement2d='CVH[V]')
        self.set_lineEdit(self.ui.lineEdit_CVL, json_Sensors, 'Akku/HV', listElement2d='CVL[V]')
        self.set_lineEdit(self.ui.lineEdit_CVL_2, json_Sensors, 'Akku/HV', listElement2d='CVL[V] 20s')
        self.set_lineEdit(self.ui.lineEdit_CVL_3, json_Sensors, 'Akku/HV', listElement2d='CVL[V] 60s')
        self.set_lineEdit(self.ui.lineEdit_CTH, json_Sensors, 'Akku/HV', listElement2d='CTH[°C]')
        self.set_lineEdit(self.ui.lineEdit_CTL, json_Sensors, 'Akku/HV', listElement2d='CTL[°C]')
        self.set_lineEdit(self.ui.lineEdit_State_IMD, json_Sensors, 'Akku/HV', listElement2d='State IMD')
        self.set_lineEdit(self.ui.lineEdit_Isolationswiderstand, json_Sensors, 'Akku/HV',
                          listElement2d='Isolationswider\nstand[kOhm]')

        self.set_lineEdit(self.ui.lineEdit_SC_after_Motors_Rear, json_Sensors, 'SC', listElement2d='SC Messungen',
                          listElement3d='SC after Motors Rear [V]')
        self.set_lineEdit(self.ui.lineEdit_SC_after_Motors_Front, json_Sensors, 'SC', listElement2d='SC Messungen',
                          listElement3d='SC after Motors Front [V]')
        self.set_lineEdit(self.ui.lineEdit_SC_after_BOTS, json_Sensors, 'SC', listElement2d='SC Messungen',
                          listElement3d='SC after BOTS [V]')
        self.set_lineEdit(self.ui.lineEdit_SC_after_Akku, json_Sensors, 'SC', listElement2d='SC Messungen',
                          listElement3d='SC after Akku [V]')
        self.set_lineEdit(self.ui.lineEdit_SC_Voltage_AMS_1, json_Sensors, 'SC', listElement2d='SC Messungen',
                          listElement3d='SC Voltage AMS 1')
        self.set_lineEdit(self.ui.lineEdit_SC_Voltage_AMS_2, json_Sensors, 'SC', listElement2d='SC Messungen',
                          listElement3d='SC Voltage AMS 2')
        self.set_btn_LED(self.ui.btn_LED_SC_Motors_Front, json_Sensors, 'SC', listElement2d='SC Errors',
                          listElement3d='SC Motors Front')
        self.set_btn_LED(self.ui.btn_LED_SC_Motors_Rear, json_Sensors, 'SC', listElement2d='SC Errors',
                         listElement3d='SC Motors Rear')
        self.set_btn_LED(self.ui.btn_LED_SC_BOTS, json_Sensors, 'SC', listElement2d='SC Errors',
                         listElement3d='SC BOTS')
        self.set_btn_LED(self.ui.btn_LED_SC_Akku, json_Sensors, 'SC', listElement2d='SC Errors',
                         listElement3d='SC Akku')

        self.set_btn_LED(self.ui.btn_LED_Fuse1, json_Sensors, 'Fuses', listElement2d='Fuse1[b]')
        self.set_btn_LED(self.ui.btn_LED_Fuse2_SSB, json_Sensors, 'Fuses', listElement2d='Fuse2_SSB[b]')
        self.set_btn_LED(self.ui.btn_LED_Fuse3_IMD, json_Sensors, 'Fuses', listElement2d='Fuse3_IMD[b]')
        self.set_btn_LED(self.ui.btn_LED_Fuse4_Inv, json_Sensors, 'Fuses', listElement2d='Fuse4_Inv[b]')
        self.set_btn_LED(self.ui.btn_LED_Fuse5_GPS, json_Sensors, 'Fuses', listElement2d='Fuse5_GPS[b]')
        self.set_btn_LED(self.ui.btn_LED_Fuse6_VCU, json_Sensors, 'Fuses', listElement2d='Fuse6_VCU[b]')
        self.set_btn_LED(self.ui.btn_LED_Fuse7_BSE, json_Sensors, 'Fuses', listElement2d='Fuse7_BSE[b]')
        self.set_btn_LED(self.ui.btn_LED_Fuse8_DIS, json_Sensors, 'Fuses', listElement2d='Fuse8_DIS[b]')
        self.set_btn_LED(self.ui.btn_LED_Fuse9_SWS, json_Sensors, 'Fuses', listElement2d='Fuse9_SWS[b]')
        self.set_btn_LED(self.ui.btn_LED_Fuse10_TPMS, json_Sensors, 'Fuses', listElement2d='Fuse10_TPMS[b]')
        self.set_btn_LED(self.ui.btn_LED_Fuse11, json_Sensors, 'Fuses', listElement2d='Fuse11[b]')
        self.set_btn_LED(self.ui.btn_LED_Fuse12, json_Sensors, 'Fuses', listElement2d='Fuse12[b]')
        self.set_btn_LED(self.ui.btn_LED_Fuse1A_1_RTDS, json_Sensors, 'Fuses', listElement2d='Fuse1A_1_RTDS')
        self.set_btn_LED(self.ui.btn_LED_Fuse1A_2_Brakelight, json_Sensors, 'Fuses',
                         listElement2d='Fuse1A_2_Brakelight')
        self.set_btn_LED(self.ui.btn_LED_Fuse1A_3, json_Sensors, 'Fuses', listElement2d='Fuse1A_3')
        self.set_btn_LED(self.ui.btn_LED_Fuse1A_4, json_Sensors, 'Fuses', listElement2d='Fuse1A_4')
        self.set_btn_LED(self.ui.btn_LED_Fuse6A_1_Motor_Fans, json_Sensors, 'Fuses',
                         listElement2d='Fuse6A_1_Motor_Fans')
        self.set_btn_LED(self.ui.btn_LED_Fuse6A_2_DRS, json_Sensors, 'Fuses',
                         listElement2d='Fuse6A_2_DRS')
        self.set_btn_LED(self.ui.btn_LED_Fuse6A_3_SC, json_Sensors, 'Fuses',
                         listElement2d='Fuse6A_3_SC')
        self.set_btn_LED(self.ui.btn_LED_Fuse6A_4_Vectorbox, json_Sensors, 'Fuses',
                         listElement2d='Fuse6A_4_Vectorbox')
        self.set_btn_LED(self.ui.btn_LED_Fuse6A_5_Mot_Pumps, json_Sensors, 'Fuses',
                         listElement2d='Fuse6A_5_Mot_Pumps')
        self.set_btn_LED(self.ui.btn_LED_Fuse6A_6, json_Sensors, 'Fuses',
                         listElement2d='Fuse6A_6')
        self.set_btn_LED(self.ui.btn_LED_Fuse12A_1_Inv_Fans_Fr, json_Sensors, 'Fuses',
                         listElement2d='Fuse12A_1_Inv_Fans_Fr')
        self.set_btn_LED(self.ui.btn_LED_Fuse12A_2_Inv_Fans_Re, json_Sensors, 'Fuses',
                         listElement2d='Fuse12A_2_Inv_Fans_Re')

        self.set_lineEdit(self.ui.lineEdit_TunKnob_1, json_Sensors, 'Buttons/Knobs', listElement2d='TunKnob 1[%]')
        self.set_lineEdit(self.ui.lineEdit_TunKnob_2, json_Sensors, 'Buttons/Knobs', listElement2d='TunKnob 2[%]')
        self.set_btn_LED(self.ui.btn_LED_Start_Button, json_Sensors, 'Buttons/Knobs', listElement2d='Start-Button')
        self.set_btn_LED(self.ui.btn_LED_HV_Button, json_Sensors, 'Buttons/Knobs', listElement2d='HV-Button')
        self.set_btn_LED(self.ui.btn_LED_Reku_Button, json_Sensors, 'Buttons/Knobs', listElement2d='Reku-Button')
        self.set_btn_LED(self.ui.btn_LED_Lenkrad_1, json_Sensors, 'Buttons/Knobs', listElement2d='Lenkrad 1')
        self.set_btn_LED(self.ui.btn_LED_Lenkrad_2, json_Sensors, 'Buttons/Knobs', listElement2d='Lenkrad 2')
        self.set_btn_LED(self.ui.btn_LED_Lenkrad_3, json_Sensors, 'Buttons/Knobs', listElement2d='Lenkrad 3')
        self.set_btn_LED(self.ui.btn_LED_Lenkrad_4, json_Sensors, 'Buttons/Knobs', listElement2d='Lenkrad 4')
        self.set_btn_LED(self.ui.btn_LED_Lenkrad_5, json_Sensors, 'Buttons/Knobs', listElement2d='Lenkrad 5')
        self.set_btn_LED(self.ui.btn_LED_Lenkrad_6, json_Sensors, 'Buttons/Knobs', listElement2d='Lenkrad 6')

        self.set_lineEdit(self.ui.lineEdit_V_GPS, json_Sensors, 'GPS/9-axis Front', listElement2d='V_GPS[km/h]')
        self.set_lineEdit(self.ui.lineEdit_Course_GPS, json_Sensors, 'GPS/9-axis Front', listElement2d='Course_GPS[°]')
        self.set_lineEdit(self.ui.lineEdit_Latitude, json_Sensors, 'GPS/9-axis Front', listElement2d='Latitude[°]')
        self.set_lineEdit(self.ui.lineEdit_Longitude, json_Sensors, 'GPS/9-axis Front', listElement2d='Longitude[°]')
        self.set_lineEdit(self.ui.lineEdit_HDOP, json_Sensors, 'GPS/9-axis Front', listElement2d='HDOP')
        self.set_lineEdit(self.ui.lineEdit_Quality_of_Fix, json_Sensors, 'GPS/9-axis Front',
                          listElement2d='Quality of Fix')
        self.set_lineEdit(self.ui.lineEdit_Satellites, json_Sensors, 'GPS/9-axis Front', listElement2d='Satellites')
        self.set_lineEdit(self.ui.lineEdit_Odometer, json_Sensors, 'GPS/9-axis Front', listElement2d='Odometer[km]')
        self.set_lineEdit(self.ui.lineEdit_ACC_X_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='ACC_X_Fr[m/s²]')
        self.set_lineEdit(self.ui.lineEdit_ACC_Y_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='ACC_Y_Fr[m/s²] ')
        self.set_lineEdit(self.ui.lineEdit_ACC_Z_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='ACC_Z_Fr[m/s²]')
        self.set_lineEdit(self.ui.lineEdit_ROT_X_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='ROT_X_Fr[°/s]')
        self.set_lineEdit(self.ui.lineEdit_ROT_Y_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='ROT_Y_Fr[°/s]')
        self.set_lineEdit(self.ui.lineEdit_ROT_Z_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='ROT_Z_Fr[°/s]')
        self.set_lineEdit(self.ui.lineEdit_MAG_X_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='MAG_X_Fr[b]')
        self.set_lineEdit(self.ui.lineEdit_MAG_Y_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='MAG_Y_Fr[b]')
        self.set_lineEdit(self.ui.lineEdit_MAG_Z_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='MAG_Z_Fr[b]')
        self.set_lineEdit(self.ui.lineEdit_MAG_Z_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='MAG_Z_Fr[b]')

        self.set_lineEdit(self.ui.lineEdit_V_GPS_Rear, json_Sensors, 'GPS/9-axis Rear', listElement2d='V_GPS[km/h]')
        self.set_lineEdit(self.ui.lineEdit_Course_GPS_Rear, json_Sensors, 'GPS/9-axis Rear', listElement2d='Course_GPS[°]')
        self.set_lineEdit(self.ui.lineEdit_Latitude_Rear, json_Sensors, 'GPS/9-axis Rear', listElement2d='Latitude[°]')
        self.set_lineEdit(self.ui.lineEdit_Longitude_Rear, json_Sensors, 'GPS/9-axis Rear', listElement2d='Longitude[°]')
        self.set_lineEdit(self.ui.lineEdit_HDOP_Rear, json_Sensors, 'GPS/9-axis Rear', listElement2d='HDOP')
        self.set_lineEdit(self.ui.lineEdit_Quality_of_Fix_Rear, json_Sensors, 'GPS/9-axis Rear',
                          listElement2d='Quality of Fix')
        self.set_lineEdit(self.ui.lineEdit_Satellites_Rear, json_Sensors, 'GPS/9-axis Front', listElement2d='Satellites')
        self.set_lineEdit(self.ui.lineEdit_Odometer_Rear, json_Sensors, 'GPS/9-axis Rear', listElement2d='Odometer[km]')
        self.set_lineEdit(self.ui.lineEdit_ACC_X_Re, json_Sensors, 'GPS/9-axis Rear', listElement2d='ACC_X_Re[m/s²]')
        self.set_lineEdit(self.ui.lineEdit_ACC_Y_Re, json_Sensors, 'GPS/9-axis Rear', listElement2d='ACC_Y_Re[m/s²] ')
        self.set_lineEdit(self.ui.lineEdit_ACC_Z_Re, json_Sensors, 'GPS/9-axis Rear', listElement2d='ACC_Z_Re[m/s²]')
        self.set_lineEdit(self.ui.lineEdit_ROT_X_Re, json_Sensors, 'GPS/9-axis Rear', listElement2d='ROT_X_Re[°/s]')
        self.set_lineEdit(self.ui.lineEdit_ROT_Y_Re, json_Sensors, 'GPS/9-axis Rear', listElement2d='ROT_Y_Re[°/s]')
        self.set_lineEdit(self.ui.lineEdit_ROT_Z_Re, json_Sensors, 'GPS/9-axis Rear', listElement2d='ROT_Z_Re[°/s]')
        self.set_lineEdit(self.ui.lineEdit_MAG_X_Re, json_Sensors, 'GPS/9-axis Rear', listElement2d='MAG_X_Re[b]')
        self.set_lineEdit(self.ui.lineEdit_MAG_Y_Re, json_Sensors, 'GPS/9-axis Rear', listElement2d='MAG_Y_Re[b]')
        self.set_lineEdit(self.ui.lineEdit_MAG_Z_Re, json_Sensors, 'GPS/9-axis Rear', listElement2d='MAG_Z_Re[b]')
        self.set_lineEdit(self.ui.lineEdit_MAG_Z_Re, json_Sensors, 'GPS/9-axis Rear', listElement2d='MAG_Z_Re[b]')

        self.set_lineEdit(self.ui.lineEdit_1A_1, json_Sensors, 'Fusebox Currents', listElement2d='1A_1')
        self.set_lineEdit(self.ui.lineEdit_1A_2, json_Sensors, 'Fusebox Currents', listElement2d='1A_ 2')
        self.set_lineEdit(self.ui.lineEdit_1A_3, json_Sensors, 'Fusebox Currents', listElement2d='1A_3')
        self.set_lineEdit(self.ui.lineEdit_1A_4, json_Sensors, 'Fusebox Currents', listElement2d='1A_4')
        self.set_lineEdit(self.ui.lineEdit_6A_1, json_Sensors, 'Fusebox Currents', listElement2d='6A_1')
        self.set_lineEdit(self.ui.lineEdit_6A_2, json_Sensors, 'Fusebox Currents', listElement2d='6A_2')
        self.set_lineEdit(self.ui.lineEdit_6A_3, json_Sensors, 'Fusebox Currents', listElement2d='6A_3')
        self.set_lineEdit(self.ui.lineEdit_6A_4, json_Sensors, 'Fusebox Currents', listElement2d='6A_4')
        self.set_lineEdit(self.ui.lineEdit_6A_5, json_Sensors, 'Fusebox Currents', listElement2d='6A_5')
        self.set_lineEdit(self.ui.lineEdit_6A_6, json_Sensors, 'Fusebox Currents', listElement2d='6A_6')
        self.set_lineEdit(self.ui.lineEdit_12A_1, json_Sensors, 'Fusebox Currents', listElement2d='12A_1')
        self.set_lineEdit(self.ui.lineEdit_12A_2, json_Sensors, 'Fusebox Currents', listElement2d='12A_2')

        self.set_lineEdit(self.ui.lineEdit_Timestamp, json_Sensors, 'Kistler', listElement2d='Timestamp [4ms] ')
        self.set_lineEdit(self.ui.lineEdit_IVI, json_Sensors, 'Kistler', listElement2d='IVI [10^-2 m/s]')
        self.set_lineEdit(self.ui.lineEdit_Weg, json_Sensors, 'Kistler', listElement2d='Weg [m]')
        self.set_lineEdit(self.ui.lineEdit_V_lon, json_Sensors, 'Kistler', listElement2d='V_lon [m/s]')
        self.set_lineEdit(self.ui.lineEdit_V_lat, json_Sensors, 'Kistler', listElement2d='V_lat [m/s]')
        self.set_lineEdit(self.ui.lineEdit_Winkel, json_Sensors, 'Kistler', listElement2d='Winkel [°]')
        self.set_lineEdit(self.ui.lineEdit_SerienNr, json_Sensors, 'Kistler', listElement2d='SerienNr')
        self.set_lineEdit(self.ui.lineEdit_SensorNr, json_Sensors, 'Kistler', listElement2d='SensorNr')
        self.set_lineEdit(self.ui.lineEdit_Temp, json_Sensors, 'Kistler', listElement2d='Temp [°C]')
        self.set_lineEdit(self.ui.lineEdit_LED_Strom, json_Sensors, 'Kistler', listElement2d='LED Strom [0,01A]')
        self.set_lineEdit(self.ui.lineEdit_Statusbyte1, json_Sensors, 'Kistler', listElement2d='Statusbyte1')
        self.set_lineEdit(self.ui.lineEdit_Statusbyte2, json_Sensors, 'Kistler', listElement2d='Statusbyte2')

        self.set_lineEdit(self.ui.lineEdit_Status, json_Sensors, 'Datalogger', listElement2d='Status')
        self.set_lineEdit(self.ui.lineEdit_Voltage, json_Sensors, 'Datalogger', listElement2d='Voltage[V]')
        self.set_lineEdit(self.ui.lineEdit_Current, json_Sensors, 'Datalogger', listElement2d='Current[A]')
        self.set_lineEdit(self.ui.lineEdit_Power, json_Sensors, 'Datalogger', listElement2d='Power[kW]')
        self.set_lineEdit(self.ui.lineEdit_Message_Counter, json_Sensors, 'Datalogger',
                          listElement2d='Message\nCounter')

        print(json_Sensors)

    def recieve_Inverter(self, json_Inverter):

        #Inverter VR
        self.set_lineEdit(self.ui.lineEdit_AMK_Control_VR, json_Inverter, 'VR', listElement2d='AMK_Control[b]')
        self.set_lineEdit(self.ui.lineEdit_Drehzahlsollwert_VR, json_Inverter, 'VR',
                          listElement2d='Drehzahlsollwert[1/min]')
        self.set_lineEdit(self.ui.lineEdit_Momentsollwert_VR, json_Inverter, 'VR', listElement2d='Momentsollwert[Nm]')
        self.set_lineEdit(self.ui.lineEdit_Momentsollwert_VR, json_Inverter, 'VR', listElement2d='Momentsollwert[Nm]')
        self.set_btn_LED(self.ui.btn_LED_System_bereit_VR, json_Inverter, 'VR', listElement2d='System bereit')
        self.set_btn_LED(self.ui.btn_LED_Warnung_VR, json_Inverter, 'VR', listElement2d='Warnung')
        self.set_btn_LED(self.ui.btn_LED_Fehler_VR, json_Inverter, 'VR', listElement2d='Fehler')
        self.set_btn_LED(self.ui.btn_LED_Derating_VR, json_Inverter, 'VR', listElement2d='Derating')
        self.set_btn_LED(self.ui.btn_LED_Spiegel_HV_VR, json_Inverter, 'VR', listElement2d='Spiegel HV')
        self.set_btn_LED(self.ui.btn_LED_Quit_HV_VR, json_Inverter, 'VR', listElement2d='Quit HV')
        self.set_btn_LED(self.ui.btn_LED_Spiegel_Regelerfeigabe_VR, json_Inverter, 'VR',
                         listElement2d='Spiegel Regelerfeigabe')
        self.set_btn_LED(self.ui.btn_LED_Quit_Reglerfreigabe_VR, json_Inverter, 'VR',
                         listElement2d='Quit Reglerfreigabe')
        self.set_lineEdit(self.ui.lineEdit_Drehzahlistwert_VR, json_Inverter, 'VR',
                          listElement2d='Drehzahlistwert[U/min]')
        self.set_lineEdit(self.ui.lineEdit_Momentistwert_VR, json_Inverter, 'VR', listElement2d='Momentistwert[Nm]')
        self.set_lineEdit(self.ui.lineEdit_Drehzahlistwert_VR, json_Inverter, 'VR',
                          listElement2d='Drehzahlistwert[U/min]')
        self.set_lineEdit(self.ui.lineEdit_Momentistwert_VR, json_Inverter, 'VR', listElement2d='Momentistwert[Nm]')
        self.set_lineEdit(self.ui.lineEdit_Diagnosenummer_VR, json_Inverter, 'VR', listElement2d='Diagnosenummer')
        self.set_lineEdit(self.ui.lineEdit_Motortemp_VR, json_Inverter, 'VR', listElement2d='Motortemp[°C]')
        self.set_lineEdit(self.ui.lineEdit_Kuehlplattentemp_VR, json_Inverter, 'VR',
                          listElement2d='Kühlplattentemp[°C]')
        self.set_lineEdit(self.ui.lineEdit_IGBTtemp_VR, json_Inverter, 'VR', listElement2d='IGBTtemp[°C]')
        self.set_lineEdit(self.ui.lineEdit_I_q_VR, json_Inverter, 'VR', listElement2d='I_q[A]')
        self.set_lineEdit(self.ui.lineEdit_I_d_VR, json_Inverter, 'VR', listElement2d='I_d[A]')
        self.set_lineEdit(self.ui.lineEdit_Wirkleistung_VR, json_Inverter, 'VR', listElement2d='Wirkleistung [kW]')
        self.set_lineEdit(self.ui.lineEdit_Blindleistung_VR, json_Inverter, 'VR', listElement2d='Blindleistung [kvar]')
        self.set_lineEdit(self.ui.lineEdit_Fehlerzusatznr_1_VR, json_Inverter, 'VR', listElement2d='Fehlerzusatznr. 1')
        self.set_lineEdit(self.ui.lineEdit_Fehlerzusatznr_2_VR, json_Inverter, 'VR', listElement2d='Fehlerzusatznr. 2')
        self.set_lineEdit(self.ui.lineEdit_Fehlerzusatznr_3_VR, json_Inverter, 'VR', listElement2d='Fehlerzusatznr. 3')

        # Inverter VL
        self.set_lineEdit(self.ui.lineEdit_AMK_Control_VL, json_Inverter, 'VL', listElement2d='AMK_Control[b]')
        self.set_lineEdit(self.ui.lineEdit_Drehzahlsollwert_VL, json_Inverter, 'VL',
                          listElement2d='Drehzahlsollwert[1/min]')
        self.set_lineEdit(self.ui.lineEdit_Momentsollwert_VL, json_Inverter, 'VL', listElement2d='Momentsollwert[Nm]')
        self.set_lineEdit(self.ui.lineEdit_Momentsollwert_VL, json_Inverter, 'VL', listElement2d='Momentsollwert[Nm]')
        self.set_btn_LED(self.ui.btn_LED_System_bereit_VL, json_Inverter, 'VL', listElement2d='System bereit')
        self.set_btn_LED(self.ui.btn_LED_Warnung_VL, json_Inverter, 'VL', listElement2d='Warnung')
        self.set_btn_LED(self.ui.btn_LED_Fehler_VL, json_Inverter, 'VL', listElement2d='Fehler')
        self.set_btn_LED(self.ui.btn_LED_Derating_VL, json_Inverter, 'VL', listElement2d='Derating')
        self.set_btn_LED(self.ui.btn_LED_Spiegel_HV_VL, json_Inverter, 'VL', listElement2d='Spiegel HV')
        self.set_btn_LED(self.ui.btn_LED_Quit_HV_VL, json_Inverter, 'VL', listElement2d='Quit HV')
        self.set_btn_LED(self.ui.btn_LED_Spiegel_Regelerfeigabe_VL, json_Inverter, 'VL',
                         listElement2d='Spiegel Regelerfeigabe')
        self.set_btn_LED(self.ui.btn_LED_Quit_Reglerfreigabe_VL, json_Inverter, 'VL',
                         listElement2d='Quit Reglerfreigabe')
        self.set_lineEdit(self.ui.lineEdit_Drehzahlistwert_VL, json_Inverter, 'VL',
                          listElement2d='Drehzahlistwert[U/min]')
        self.set_lineEdit(self.ui.lineEdit_Momentistwert_VL, json_Inverter, 'VL', listElement2d='Momentistwert[Nm]')
        self.set_lineEdit(self.ui.lineEdit_Drehzahlistwert_VL, json_Inverter, 'VL',
                          listElement2d='Drehzahlistwert[U/min]')
        self.set_lineEdit(self.ui.lineEdit_Momentistwert_VL, json_Inverter, 'VL', listElement2d='Momentistwert[Nm]')
        self.set_lineEdit(self.ui.lineEdit_Diagnosenummer_VL, json_Inverter, 'VL', listElement2d='Diagnosenummer')
        self.set_lineEdit(self.ui.lineEdit_Motortemp_VL, json_Inverter, 'VL', listElement2d='Motortemp[°C]')
        self.set_lineEdit(self.ui.lineEdit_Kuehlplattentemp_VL, json_Inverter, 'VL',
                          listElement2d='Kühlplattentemp[°C]')
        self.set_lineEdit(self.ui.lineEdit_IGBTtemp_VL, json_Inverter, 'VL', listElement2d='IGBTtemp[°C]')
        self.set_lineEdit(self.ui.lineEdit_I_q_VL, json_Inverter, 'VL', listElement2d='I_q[A]')
        self.set_lineEdit(self.ui.lineEdit_I_d_VL, json_Inverter, 'VL', listElement2d='I_d[A]')
        self.set_lineEdit(self.ui.lineEdit_Wirkleistung_VL, json_Inverter, 'VL', listElement2d='Wirkleistung [kW]')
        self.set_lineEdit(self.ui.lineEdit_Blindleistung_VL, json_Inverter, 'VL', listElement2d='Blindleistung [kvar]')
        self.set_lineEdit(self.ui.lineEdit_Fehlerzusatznr_1_VL, json_Inverter, 'VL', listElement2d='Fehlerzusatznr. 1')
        self.set_lineEdit(self.ui.lineEdit_Fehlerzusatznr_2_VL, json_Inverter, 'VL', listElement2d='Fehlerzusatznr. 2')
        self.set_lineEdit(self.ui.lineEdit_Fehlerzusatznr_3_VL, json_Inverter, 'VL', listElement2d='Fehlerzusatznr. 3')

        #Inverter HR
        self.set_lineEdit(self.ui.lineEdit_AMK_Control_HR, json_Inverter, 'HR', listElement2d='AMK_Control[b]')
        self.set_lineEdit(self.ui.lineEdit_Drehzahlsollwert_HR, json_Inverter, 'HR',
                          listElement2d='Drehzahlsollwert[1/min]')
        self.set_lineEdit(self.ui.lineEdit_Momentsollwert_HR, json_Inverter, 'HR', listElement2d='Momentsollwert[Nm]')
        self.set_lineEdit(self.ui.lineEdit_Momentsollwert_HR, json_Inverter, 'HR', listElement2d='Momentsollwert[Nm]')
        self.set_btn_LED(self.ui.btn_LED_System_bereit_HR, json_Inverter, 'HR', listElement2d='System bereit')
        self.set_btn_LED(self.ui.btn_LED_Warnung_HR, json_Inverter, 'HR', listElement2d='Warnung')
        self.set_btn_LED(self.ui.btn_LED_Fehler_HR, json_Inverter, 'HR', listElement2d='Fehler')
        self.set_btn_LED(self.ui.btn_LED_Derating_HR, json_Inverter, 'HR', listElement2d='Derating')
        self.set_btn_LED(self.ui.btn_LED_Spiegel_HV_HR, json_Inverter, 'HR', listElement2d='Spiegel HV')
        self.set_btn_LED(self.ui.btn_LED_Quit_HV_HR, json_Inverter, 'HR', listElement2d='Quit HV')
        self.set_btn_LED(self.ui.btn_LED_Spiegel_Regelerfeigabe_HR, json_Inverter, 'HR',
                         listElement2d='Spiegel Regelerfeigabe')
        self.set_btn_LED(self.ui.btn_LED_Quit_Reglerfreigabe_HR, json_Inverter, 'HR',
                         listElement2d='Quit Reglerfreigabe')
        self.set_lineEdit(self.ui.lineEdit_Drehzahlistwert_HR, json_Inverter, 'HR',
                          listElement2d='Drehzahlistwert[U/min]')
        self.set_lineEdit(self.ui.lineEdit_Momentistwert_HR, json_Inverter, 'HR', listElement2d='Momentistwert[Nm]')
        self.set_lineEdit(self.ui.lineEdit_Drehzahlistwert_HR, json_Inverter, 'HR',
                          listElement2d='Drehzahlistwert[U/min]')
        self.set_lineEdit(self.ui.lineEdit_Momentistwert_HR, json_Inverter, 'HR', listElement2d='Momentistwert[Nm]')
        self.set_lineEdit(self.ui.lineEdit_Diagnosenummer_HR, json_Inverter, 'HR', listElement2d='Diagnosenummer')
        self.set_lineEdit(self.ui.lineEdit_Motortemp_HR, json_Inverter, 'HR', listElement2d='Motortemp[°C]')
        self.set_lineEdit(self.ui.lineEdit_Kuehlplattentemp_HR, json_Inverter, 'HR',
                          listElement2d='Kühlplattentemp[°C]')
        self.set_lineEdit(self.ui.lineEdit_IGBTtemp_HR, json_Inverter, 'HR', listElement2d='IGBTtemp[°C]')
        self.set_lineEdit(self.ui.lineEdit_I_q_HR, json_Inverter, 'HR', listElement2d='I_q[A]')
        self.set_lineEdit(self.ui.lineEdit_I_d_HR, json_Inverter, 'HR', listElement2d='I_d[A]')
        self.set_lineEdit(self.ui.lineEdit_Wirkleistung_HR, json_Inverter, 'HR', listElement2d='Wirkleistung [kW]')
        self.set_lineEdit(self.ui.lineEdit_Blindleistung_HR, json_Inverter, 'HR', listElement2d='Blindleistung [kvar]')
        self.set_lineEdit(self.ui.lineEdit_Fehlerzusatznr_1_HR, json_Inverter, 'HR', listElement2d='Fehlerzusatznr. 1')
        self.set_lineEdit(self.ui.lineEdit_Fehlerzusatznr_2_HR, json_Inverter, 'HR', listElement2d='Fehlerzusatznr. 2')
        self.set_lineEdit(self.ui.lineEdit_Fehlerzusatznr_3_HR, json_Inverter, 'HR', listElement2d='Fehlerzusatznr. 3')

        # Inverter HL
        self.set_lineEdit(self.ui.lineEdit_AMK_Control_HL, json_Inverter, 'HL', listElement2d='AMK_Control[b]')
        self.set_lineEdit(self.ui.lineEdit_Drehzahlsollwert_HL, json_Inverter, 'HL',
                          listElement2d='Drehzahlsollwert[1/min]')
        self.set_lineEdit(self.ui.lineEdit_Momentsollwert_HL, json_Inverter, 'HL', listElement2d='Momentsollwert[Nm]')
        self.set_lineEdit(self.ui.lineEdit_Momentsollwert_HL, json_Inverter, 'HL', listElement2d='Momentsollwert[Nm]')
        self.set_btn_LED(self.ui.btn_LED_System_bereit_HL, json_Inverter, 'HL', listElement2d='System bereit')
        self.set_btn_LED(self.ui.btn_LED_Warnung_HL, json_Inverter, 'HL', listElement2d='Warnung')
        self.set_btn_LED(self.ui.btn_LED_Fehler_HL, json_Inverter, 'HL', listElement2d='Fehler')
        self.set_btn_LED(self.ui.btn_LED_Derating_HL, json_Inverter, 'HL', listElement2d='Derating')
        self.set_btn_LED(self.ui.btn_LED_Spiegel_HV_HL, json_Inverter, 'HL', listElement2d='Spiegel HV')
        self.set_btn_LED(self.ui.btn_LED_Quit_HV_HL, json_Inverter, 'HL', listElement2d='Quit HV')
        self.set_btn_LED(self.ui.btn_LED_Spiegel_Regelerfeigabe_HL, json_Inverter, 'HL',
                         listElement2d='Spiegel Regelerfeigabe')
        self.set_btn_LED(self.ui.btn_LED_Quit_Reglerfreigabe_HL, json_Inverter, 'HL',
                         listElement2d='Quit Reglerfreigabe')
        self.set_lineEdit(self.ui.lineEdit_Drehzahlistwert_HL, json_Inverter, 'HL',
                          listElement2d='Drehzahlistwert[U/min]')
        self.set_lineEdit(self.ui.lineEdit_Momentistwert_HL, json_Inverter, 'HL', listElement2d='Momentistwert[Nm]')
        self.set_lineEdit(self.ui.lineEdit_Drehzahlistwert_HL, json_Inverter, 'HL',
                          listElement2d='Drehzahlistwert[U/min]')
        self.set_lineEdit(self.ui.lineEdit_Momentistwert_HL, json_Inverter, 'HL', listElement2d='Momentistwert[Nm]')
        self.set_lineEdit(self.ui.lineEdit_Diagnosenummer_HL, json_Inverter, 'HL', listElement2d='Diagnosenummer')
        self.set_lineEdit(self.ui.lineEdit_Motortemp_HL, json_Inverter, 'HL', listElement2d='Motortemp[°C]')
        self.set_lineEdit(self.ui.lineEdit_Kuehlplattentemp_HL, json_Inverter, 'HL',
                          listElement2d='Kühlplattentemp[°C]')
        self.set_lineEdit(self.ui.lineEdit_IGBTtemp_HL, json_Inverter, 'HL', listElement2d='IGBTtemp[°C]')
        self.set_lineEdit(self.ui.lineEdit_I_q_HL, json_Inverter, 'HL', listElement2d='I_q[A]')
        self.set_lineEdit(self.ui.lineEdit_I_d_HL, json_Inverter, 'HL', listElement2d='I_d[A]')
        self.set_lineEdit(self.ui.lineEdit_Wirkleistung_HL, json_Inverter, 'HL', listElement2d='Wirkleistung [kW]')
        self.set_lineEdit(self.ui.lineEdit_Blindleistung_HL, json_Inverter, 'HL', listElement2d='Blindleistung [kvar]')
        self.set_lineEdit(self.ui.lineEdit_Fehlerzusatznr_1_HL, json_Inverter, 'HL', listElement2d='Fehlerzusatznr. 1')
        self.set_lineEdit(self.ui.lineEdit_Fehlerzusatznr_2_HL, json_Inverter, 'HL', listElement2d='Fehlerzusatznr. 2')
        self.set_lineEdit(self.ui.lineEdit_Fehlerzusatznr_3_HL, json_Inverter, 'HL', listElement2d='Fehlerzusatznr. 3')

        print(str(json_Inverter))

    def recieve_Errors(self, json_Errors):

        #Timeout CAN
        self.set_btn_LED(self.ui.btn_LED_SSB_Front, json_Errors, 'Timeout CAN' ,listElement2d='SSB Front')
        self.set_btn_LED(self.ui.btn_LED_BSE, json_Errors, 'Timeout CAN' ,listElement2d='BSE')
        self.set_btn_LED(self.ui.btn_LED_SSB_Rear, json_Errors, 'Timeout CAN' ,listElement2d='SSB Rear')
        self.set_btn_LED(self.ui.btn_LED_GPS_Front, json_Errors, 'Timeout CAN' ,listElement2d='GPS Front')
        self.set_btn_LED(self.ui.btn_LED_9_Achs_ACC_Front, json_Errors, 'Timeout CAN' ,listElement2d='9-Achs_ACC Front')
        self.set_btn_LED(self.ui.btn_LED_9_Achs_ROT_Front, json_Errors, 'Timeout CAN' ,listElement2d='9-Achs_ROT Front')
        self.set_btn_LED(self.ui.btn_LED_9_Achs_MAG_Front, json_Errors, 'Timeout CAN' ,listElement2d='9-Achs_MAG Front')
        self.set_btn_LED(self.ui.btn_LED_GPS_Rear, json_Errors, 'Timeout CAN' ,listElement2d='GPS Rear')
        self.set_btn_LED(self.ui.btn_LED_9_Achs_ACC_Rear, json_Errors, 'Timeout CAN' ,listElement2d='9-Achs_ACC Rear')
        self.set_btn_LED(self.ui.btn_LED_9_Achs_ROT_Rear, json_Errors, 'Timeout CAN' ,listElement2d='9-Achs_ROT Rear')
        self.set_btn_LED(self.ui.btn_LED_9_Achs_MAG_Rear, json_Errors, 'Timeout CAN' ,listElement2d='9-Achs_MAG Rear')
        self.set_btn_LED(self.ui.btn_LED_9_Achs_MAG_Rear, json_Errors, 'Timeout CAN' ,listElement2d='9-Achs_MAG Rear')
        self.set_btn_LED(self.ui.btn_LED_AMS, json_Errors, 'Timeout CAN' ,listElement2d='AMS')
        self.set_btn_LED(self.ui.btn_LED_Energymeter, json_Errors, 'Timeout CAN' ,listElement2d='Energymeter')
        self.set_btn_LED(self.ui.btn_LED_PDU, json_Errors, 'Timeout CAN' ,listElement2d='PDU')
        self.set_btn_LED(self.ui.btn_LED_DIS, json_Errors, 'Timeout CAN' ,listElement2d='DIS')
        self.set_btn_LED(self.ui.btn_LED_DIS_Param, json_Errors, 'Timeout CAN' ,listElement2d='DIS_Param')
        self.set_btn_LED(self.ui.btn_LED_Inverter_FR, json_Errors, 'Timeout CAN' ,listElement2d='Inverter FR')
        self.set_btn_LED(self.ui.btn_LED_Inverter_FL, json_Errors, 'Timeout CAN' ,listElement2d='Inverter FL')
        self.set_btn_LED(self.ui.btn_LED_Inverter_RR, json_Errors, 'Timeout CAN' ,listElement2d='Inverter RR')
        self.set_btn_LED(self.ui.btn_LED_Inverter_RL, json_Errors, 'Timeout CAN' ,listElement2d='Inverter RL')

        # Wert
        self.set_btn_LED(self.ui.btn_LED_Pedale_implausibel_Wert, json_Errors, 'Wert' ,
                         listElement2d='Pedale implausibel')
        self.set_btn_LED(self.ui.btn_LED_APPS_implausibel_Wert, json_Errors, 'Wert' ,listElement2d='APPS implausibel')
        self.set_btn_LED(self.ui.btn_LED_APPS1_Wert, json_Errors, 'Wert' ,listElement2d='APPS1')
        self.set_btn_LED(self.ui.btn_LED_APPS2_Wert, json_Errors, 'Wert' ,listElement2d='APPS2')
        self.set_btn_LED(self.ui.btn_LED_Bremsdruck_vorne, json_Errors, 'Wert' ,listElement2d='Bremsdruck_vorne')
        self.set_btn_LED(self.ui.btn_LED_Bremsdruck_hinten, json_Errors, 'Wert' ,listElement2d='Bremsdruck_hinten')
        self.set_btn_LED(self.ui.btn_LED_Bremskraftsensor, json_Errors, 'Wert' ,listElement2d='Bremskraftsensor')
        self.set_btn_LED(self.ui.btn_LED_Lenkwinkel, json_Errors, 'Wert' ,listElement2d='Lenkwinkel')
        self.set_btn_LED(self.ui.btn_LED_ACC_X, json_Errors, 'Wert' ,listElement2d='ACC_X')
        self.set_btn_LED(self.ui.btn_LED_ACC_Y, json_Errors, 'Wert' ,listElement2d='ACC_Y')
        self.set_btn_LED(self.ui.btn_LED_ROT_Z, json_Errors, 'Wert' ,listElement2d='ROT_Z')
        self.set_btn_LED(self.ui.btn_LED_V_GPS, json_Errors, 'Wert' ,listElement2d='V_GPS')
        self.set_btn_LED(self.ui.btn_LED_Invertertemp_FrR, json_Errors, 'Wert' ,listElement2d='Invertertemp_FrR')
        self.set_btn_LED(self.ui.btn_LED_Invertertemp_FrL, json_Errors, 'Wert' ,listElement2d='Invertertemp_FrL')
        self.set_btn_LED(self.ui.btn_LED_Invertertemp_ReR, json_Errors, 'Wert' ,listElement2d='Invertertemp_ReR')
        self.set_btn_LED(self.ui.btn_LED_Invertertemp_ReL, json_Errors, 'Wert' ,listElement2d='Invertertemp_ReL')
        self.set_btn_LED(self.ui.btn_LED_Invertertemp_ReL, json_Errors, 'Wert' ,listElement2d='Invertertemp_ReL')

        # Latching
        self.set_btn_LED(self.ui.btn_LED_Pedale_implausibel_Latching, json_Errors, 'Latching',
                         listElement2d='Pedale implausibel')
        self.set_btn_LED(self.ui.btn_LED_APPS_implausibel_Latching, json_Errors, 'Latching', listElement2d='APPS implausibel')
        self.set_btn_LED(self.ui.btn_LED_APPS1_Latching, json_Errors, 'Latching', listElement2d='APPS1')
        self.set_btn_LED(self.ui.btn_LED_APPS2_Latching, json_Errors, 'Latching', listElement2d='APPS2')

        print(str(json_Errors))


    def recieve_Math(self, json_Math):

        #General
        self.set_lineEdit(self.ui.lineEdit_desiredTorque, json_Math, 'General', listElement2d='desiredTorque[Nm]')
        self.set_lineEdit(self.ui.lineEdit_Gaspedal, json_Math, 'General', listElement2d='Gaspedal[%/100]')
        self.set_lineEdit(self.ui.lineEdit_Rekupedal, json_Math, 'General', listElement2d='Rekupedal[%/100]')
        self.set_lineEdit(self.ui.lineEdit_Implausibilitaet_APPS, json_Math, 'General',
                          listElement2d='Implausibilität\nAPPS[%]')
        self.set_lineEdit(self.ui.lineEdit_Bremsbal, json_Math, 'General', listElement2d='Bremsbal[Fr/Total]')
        self.set_lineEdit(self.ui.lineEdit_Accelbal, json_Math, 'General', listElement2d='Accelbal[Fr/Total]')
        self.set_lineEdit(self.ui.lineEdit_allowedPower_General, json_Math, 'General', listElement2d='allowedPower[kW]')
        self.set_lineEdit(self.ui.lineEdit_actualPower, json_Math, 'General', listElement2d='actualPower[kW]')
        self.set_btn_LED(self.ui.btn_LED_Energiesparmodus_General, json_Math, 'General',
                         listElement2d='Energiesparmodus')
        self.set_lineEdit(self.ui.lineEdit_Odometer_General, json_Math, 'General', listElement2d='Odometer')
        self.set_lineEdit(self.ui.lineEdit_Wirkungsgrad, json_Math, 'General', listElement2d='Wirkungsgrad[%/100]')
        self.set_lineEdit(self.ui.lineEdit_T_Control, json_Math, 'General', listElement2d='T_Control[us]')

        #TV/KF
        self.set_lineEdit(self.ui.lineEdit_KF_Velocity, json_Math, 'TV/KF', listElement2d='KF_Velocity[km/h]')
        self.set_lineEdit(self.ui.lineEdit_KF_ACC_X, json_Math, 'TV/KF', listElement2d='KF_ACC_X[m/s²]')
        self.set_lineEdit(self.ui.lineEdit_KF_slip_ist_FR, json_Math, 'TV/KF', listElement2d='KF_slip_ist_FR[%/100]')
        self.set_lineEdit(self.ui.lineEdit_KF_slip_ist_FL, json_Math, 'TV/KF', listElement2d='KF_slip_ist_FL[%/100]')
        self.set_lineEdit(self.ui.lineEdit_KF_slip_ist_RR, json_Math, 'TV/KF', listElement2d='KF_slip_ist_RR[%/100]')
        self.set_lineEdit(self.ui.lineEdit_KF_slip_ist_RL, json_Math, 'TV/KF', listElement2d='KF_slip_ist_RL[%/100]')
        self.set_lineEdit(self.ui.lineEdit_slip_soll_Fr, json_Math, 'TV/KF', listElement2d='slip_soll_Fr[%/100]')
        self.set_lineEdit(self.ui.lineEdit_slip_soll_Re, json_Math, 'TV/KF', listElement2d='slip_soll_Re[%/100]')
        self.set_lineEdit(self.ui.lineEdit_slip_soll_Re, json_Math, 'TV/KF', listElement2d='slip_soll_Re[%/100]')
        self.set_lineEdit(self.ui.lineEdit_TV_Regler, json_Math, 'TV/KF', listElement2d='TV_Regler[Giermoment]')
        self.set_lineEdit(self.ui.lineEdit_TV_Lenk, json_Math, 'TV/KF', listElement2d='TV_Lenk[Giermoment]')
        self.set_lineEdit(self.ui.lineEdit_SOC_Soll_TV_KF, json_Math, 'TV/KF', listElement2d='SOC-Soll[%]')
        self.set_lineEdit(self.ui.lineEdit_SOC_Ist_TV_KF, json_Math, 'TV/KF', listElement2d='SOC-Ist[%]')
        self.set_lineEdit(self.ui.lineEdit_MomentSollVR, json_Math, 'TV/KF', listElement2d='MomentSollVR[Nm]')
        self.set_lineEdit(self.ui.lineEdit_MomentSollVL, json_Math, 'TV/KF', listElement2d='MomentSollVL[Nm]')
        self.set_lineEdit(self.ui.lineEdit_MomentSollHR, json_Math, 'TV/KF', listElement2d='MomentSollHR[Nm]')
        self.set_lineEdit(self.ui.lineEdit_MomentSollHL, json_Math, 'TV/KF', listElement2d='MomentSollHL[Nm]')
        self.set_lineEdit(self.ui.lineEdit_Reglerausgang_TV_KF, json_Math, 'TV/KF', listElement2d='Reglerausgang')

        #Energy Control
        self.set_lineEdit(self.ui.lineEdit_allowedPower_Energy_Control, json_Math, 'Energy Control',
                          listElement2d='allowedPower[kW]')
        self.set_lineEdit(self.ui.lineEdit_Rundenanzahl, json_Math, 'Energy Control', listElement2d='Rundenanzahl')
        self.set_lineEdit(self.ui.lineEdit_SOC_Soll_Energy_Control, json_Math, 'Energy Control',
                          listElement2d='SOC-Soll[%]')
        self.set_lineEdit(self.ui.lineEdit_SOC_Ist_Energy_Control, json_Math, 'Energy Control',
                          listElement2d='SOC-Ist[%]')
        self.set_lineEdit(self.ui.lineEdit_SOC_Ist_Energy_Control, json_Math, 'Energy Control',
                          listElement2d='SOC-Ist[%]')
        self.set_lineEdit(self.ui.lineEdit_Rundenlaenge, json_Math, 'Energy Control', listElement2d='Rundenlänge[m]')
        self.set_lineEdit(self.ui.lineEdit_Reglerausgang_Energy_Control, json_Math, 'Energy Control',
                          listElement2d='Reglerausgang')
        self.set_lineEdit(self.ui.lineEdit_Toleranz_Rundenlaenge, json_Math, 'Energy Control',
                          listElement2d='Toleranz Rundenlänge [%/100]')
        self.set_lineEdit(self.ui.lineEdit_Strecke, json_Math, 'Energy Control', listElement2d='Strecke')
        self.set_lineEdit(self.ui.lineEdit_Start_SOC, json_Math, 'Energy Control', listElement2d='Start-SOC[%]')
        self.set_lineEdit(self.ui.lineEdit_Ziel_SOC, json_Math, 'Energy Control', listElement2d='Ziel-SOC[%]')
        self.set_lineEdit(self.ui.lineEdit_Energie_Akku, json_Math, 'Energy Control', listElement2d='Energie Akku[kWh]')
        self.set_lineEdit(self.ui.lineEdit_Maximalleistung, json_Math, 'Energy Control',
                          listElement2d='Maximalleistung[kW]')
        self.set_lineEdit(self.ui.lineEdit_Start_Leistungsgrenze, json_Math, 'Energy Control',
                          listElement2d='Start-Leistungsgrenze')

        print(str(json_Math))

    def recieve_Controls(self, json_Controls):

        #Switches
        self.set_btn_LED(self.ui.btn_LED_1A_1_RTDS, json_Controls, 'Switches', listElement2d='\n1A 1 RTDS')
        self.set_btn_LED(self.ui.btn_LED_1A_2_Brakelight, json_Controls, 'Switches', listElement2d='1A 2 Brakelight')
        self.set_btn_LED(self.ui.btn_LED_1A_3_Switches, json_Controls, 'Switches', listElement2d='1A 3')
        self.set_btn_LED(self.ui.btn_LED_1A_4_Switches, json_Controls, 'Switches', listElement2d='1A 4')
        self.set_btn_LED(self.ui.btn_LED_6A_1_Motor_Fans, json_Controls, 'Switches', listElement2d='6A 1 Motor Fans')
        self.set_btn_LED(self.ui.btn_LED_6A_2_DRS, json_Controls, 'Switches', listElement2d='6A 2 DRS')
        self.set_btn_LED(self.ui.btn_LED_6A_3_SC, json_Controls, 'Switches', listElement2d='6A 3 SC')
        self.set_btn_LED(self.ui.btn_LED_6A_4_Vectorbox, json_Controls, 'Switches', listElement2d='6A 4 Vectorbox')
        self.set_btn_LED(self.ui.btn_LED_6A_5_Motor_Pump, json_Controls, 'Switches', listElement2d='6A 5 Motor Pump')
        self.set_btn_LED(self.ui.btn_LED_6A_6_Switches, json_Controls, 'Switches', listElement2d='6A 6')
        self.set_btn_LED(self.ui.btn_LED_12A_1_Inv_Fans_Fr, json_Controls, 'Switches',
                         listElement2d='12A 1 Inv Fans Fr')
        self.set_btn_LED(self.ui.btn_LED_12A_2_Inv_Fans_Re, json_Controls, 'Switches',
                         listElement2d='12A 2 Inv Fans Re')

        # Controls
        self.set_lineEdit(self.ui.lineEdit_Vehicle_State, json_Controls, 'Vehicle State')
        self.set_lineEdit(self.ui.lineEdit_DRS_Position, json_Controls, 'DRS Position[%/100]')
        self.set_lineEdit(self.ui.lineEdit_Fan_Motor, json_Controls, 'Fan Motor[%/100]')
        self.set_lineEdit(self.ui.lineEdit_Fan_Akku, json_Controls, 'Fan Akku[%/100]')
        self.set_btn_LED(self.ui.btn_LED_HV_Freigabe, json_Controls, 'HV Freigabe ')
        self.set_btn_LED(self.ui.btn_LED_IC_Voltage_OK, json_Controls, 'IC Voltage OK')

        print(str(json_Controls))

    def recieve_FPGA_Error(self, json_FPGA_Error):

        self.set_lineEdit(self.ui.lineEdit_Input_Error_Code, json_FPGA_Error, 'Input Error Code')
        self.set_lineEdit(self.ui.lineEdit_Output_Error_Code, json_FPGA_Error, 'Output Error Code')
        self.set_lineEdit(self.ui.lineEdit_Transmit_Error_Counter, json_FPGA_Error, 'Transmit Error Counter')
        self.set_lineEdit(self.ui.lineEdit_Error_Counter, json_FPGA_Error, ' Error Counter')

        print(str(json_FPGA_Error))





    def recieve_Timestamp(self, json_Timestamp):

        self.set_lineEdit(self.ui.lineEdit_Timestamp_Timestamp, json_Timestamp, 'Timestamp')

        print(str(json_Timestamp))


    def show_page_config_values(self):
        self.ui.Pages.setCurrentWidget(self.ui.page_config_values)

    def show_page_sensors(self):
        self.ui.Pages.setCurrentWidget(self.ui.page_sensors)

    def show_page_inverter(self):
        self.ui.Pages.setCurrentWidget(self.ui.page_inverter)

    def show_page_errors(self):
        self.ui.Pages.setCurrentWidget(self.ui.page_errors)

    def show_page_math(self):
        self.ui.Pages.setCurrentWidget(self.ui.page_math)

    def show_page_controls(self):
        self.ui.Pages.setCurrentWidget(self.ui.page_controls)

    def show_page_fpga_error(self):
        self.ui.Pages.setCurrentWidget(self.ui.page_fpga_error)

    def show_page_timestamp(self):
        self.ui.Pages.setCurrentWidget(self.ui.page_timestamp)


    def recieve(self):
        UDP_IP = "192.168.178.20"
        UDP_PORT = 3005

        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        sock.bind((UDP_IP, UDP_PORT))

        while True:
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            self.recvData = json.loads(data)
            print(self.recvData)
            print((self.recvData['Vehicle Mode']))
            self.ui.lineEdit_Vehicle_Mode.setText(self.recvData['Vehicle Mode'])
            self.ui.lineEdit_APPS1_max.setText(str(self.recvData['APPS1_max[°]']))

    def show(self):
        self.main_window.show()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MyMainWindow()
    #main_window.recieve()
    #tx1 = threading.Thread(target=main_window.recieve, args=())  # Thread für das Empfangen des Video-Streams
    #tx1.start()

    main_window.show()


    def update_label(main_windoww):
        current_time = str(datetime.datetime.now().time())
        main_windoww.ui.lineEdit_Vehicle_Mode.setText(current_time)
        print("sdfgdsg")


   # timer = QTimer()
   # timer.timeout.connect(lambda: (update_label(main_window)))
   # timer.start(1000)  # every 10,000 milliseconds

    sys.exit(app.exec_())
