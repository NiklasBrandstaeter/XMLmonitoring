import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDialog, QLabel, QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer,QDateTime, QObject, QThread, pyqtSignal, QRunnable, Qt, QThreadPool
import time
import datetime
import socket
import json
import select
from monitoring import Ui_MainWindow
import xml.etree.ElementTree as ET
from xml.dom import minidom
import xmltodict
from typing import OrderedDict
import timeit
from netifaces import interfaces, ifaddresses, AF_INET
import threading
import concurrent.futures



class WorkerUDP(QObject):
    def __init__(self):
        super(WorkerUDP, self).__init__()
        self.serialCounter = 4
        self.config_list = []
        self.config_i = 0
        self.XML_sensors_list = []
        self.XML_inverter_list = []
        self.XML_error_list = []
        self.XML_math_list = []
        self.XML_controls_list = []
        self.XML_fpga_error_list = []
        self.sensors_list_index = 0
        self.sensors_i = 0
        self.elementName = "None"
        self.elementValue = "None"
        self.elementChoiceElements = "None"
        self.elementDatatype = "None"

        self.jsonSensor_i = 0
        self.jsonConfig_i = 0
        self.jsonInverter_i = 0
        self.inverter_i = 0
        self.jsonErrors_i = 0
        self.errors_i = 0
        self.jsonMath_i = 0
        self.math_i = 0
        self.jsonControls_i = 0
        self.controls_i = 0
        self.jsonFPGA_Error_i = 0
        self.fpga_error_i = 0

        # json iteration
        self.json_sensor_dict = []
        self.json_sensor_dict_counter = 0

        self.json_config_dict = []
        self.json_inverter_dict = []
        self.json_errors_dict = []
        self.json_math_dict = []
        self.json_controls_dict = []
        self.json_fpga_error_dict = []


        self.json_sensor_dict_element_1 = "None"
        self.json_sensor_dict_element_2 = "None"
        self.json_sensor_dict_element_3 = "None"
        self.searchXMLLevel = 0
        self.XMLElementFound = False
        self.XML_dict_element_1 = "None"
        self.XML_dict_element_2 = "None"
        self.XML_dict_element_3 = "None"
        self.XMLElement = None
        self.cluster2 = False
        self.clusterName2 = "None"
        self.clusterName1 = "None"
        self.val = 0

    signal_Config_Values = pyqtSignal(dict) #Signal for setting new values XML
    signal_Sensors = pyqtSignal(dict)
    signal_Inverter = pyqtSignal(dict)
    signal_Errors = pyqtSignal(dict)
    signal_Math = pyqtSignal(dict)
    signal_Controls = pyqtSignal(dict)
    signal_FPGA_Error = pyqtSignal(dict)
    signal_Timestamp = pyqtSignal(dict)

    signal_Config_Values_json = pyqtSignal(dict)  # Signal for setting new values JSON
    signal_Sensors_json = pyqtSignal(dict)
    signal_Inverter_json = pyqtSignal(dict)

    signal_Config_Values_serial = pyqtSignal(bytes) #serial Values for monitoring
    signal_Config_Values_init = pyqtSignal(dict)    #for setting the structure of the cluster
    signal_Sensors_serial = pyqtSignal(bytes)
    signal_Sensors_init = pyqtSignal(dict)
    signal_Sensors_update = pyqtSignal(dict)

    signal_set_Text = pyqtSignal(tuple)
    signal_set_LED = pyqtSignal(tuple)

    # def int_litleE_to_bigE(self, oldString):    #not in use
    #
    #     oldString_binary = bin(oldString)
    #     oldString_binary = oldString_binary.replace('0b', '')
    #     newString_binary = '0b' + oldString_binary[::-1]
    #
    #     return int(newString_binary, 2)

    def serial_to_float(self, byte1, byte2, byte3, byte4):
        str_byte1 = bin(byte1)
        str_byte2 = bin(byte2)
        str_byte3 = bin(byte3)
        str_byte4 = bin(byte4)
        while (len(str_byte1) < 10):
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
        mantisse = 1 + int(value[9]) * 2 ** (-1) + int(value[10]) * 2 ** (-2) + int(value[11]) * 2 ** (-3) + \
                   int(value[12]) * 2 ** (-4) + int(value[13]) * 2 ** (-5) + int(value[14]) * 2 ** (-6) + \
                   int(value[15]) * 2 ** (-7) + int(value[16]) * 2 ** (-8) + int(value[17]) * 2 ** (-9) + \
                   int(value[18]) * 2 ** (-10) + int(value[19]) * 2 ** (-11) + int(value[20]) * 2 ** (-12) + \
                   int(value[21]) * 2 ** (-13) + int(value[22]) * 2 ** (-14) + int(value[23]) * 2 ** (-15) + \
                   int(value[24]) * 2 ** (-16) + int(value[25]) * 2 ** (-17) + int(value[26]) * 2 ** (-18) + \
                   int(value[27]) * 2 ** (-19) + int(value[28]) * 2 ** (-20) + int(value[29]) * 2 ** (-21) + \
                   int(value[30]) * 2 ** (-22) + int(value[31]) * 2 ** (-23)
        exp_int = int(exp, 2) - 127
        if (exp_int <= -127):
            exp_int = 0
            mantisse = 0
        # print("Mantisse:", mantisse)
        # print("Exponent:", exp_int)
        value_float = float((2 ** exp_int) * mantisse)
        if (value[0] == '1'):
            value_float = -value_float
        return value_float

    # def show(self, elem, level=0):
    #     #print("Element:" ,elem.tag)
    #     #print("Attr.:", elem.attrib)
    #     #print("text:", elem.text)
    #     #print("Level:", level)
    #     i=0
    #     for child in elem.findall('*'):
    #         i=i+1
    #         #print("i:",i)
    #         self.show(child, level+1)

    def run(self):

        UDP_IP = "192.168.178.20"#"192.168.178.30" #"192.168.178.20"
        UDP_PORT = 1005

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))
        sock.setblocking(0)

        #e = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        mt = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        while True:
            i = 0

            ready = select.select([sock], [], [], 0.1)
            if ready[0]:
                data, addr = sock.recvfrom(8*2048)


                mt.submit(self.analyseByteStream(data))

    def analyseByteStream(self, data):

        str = data.decode("utf-8", errors="ignore")


        if(str[0] == "J"):          #seperate Json model at the beginning of the connection. Json is used for
                                    #the structure of the seriel byte stream
            #print("JSON")
            jsonStr = str[1:]
            jsonObject = json.loads(jsonStr)
            print("Json:", jsonStr)
            if ('Vehicle Mode' in jsonObject):
                if (self.jsonConfig_i < 1):
                    self.json_config_dict = jsonObject
                    #self.signal_Config_Values_json.emit(jsonObject)
                    self.jsonConfig_i = self.jsonConfig_i + 1
                #self.signal_Config_Values_json.emit(jsonStr)
            elif('Analog' and 'Akku/HV' and 'SC' and 'Fuses' in jsonObject):
                if(self.jsonSensor_i < 1):
                    self.json_sensor_dict = jsonObject
                    self.jsonSensor_i = self.jsonSensor_i + 1
                    #self.signal_Sensors_json.emit(jsonObject)
            elif ('VR' and 'VL' and 'HR' and 'HL' in jsonObject):
                if (self.jsonInverter_i < 1):
                    self.json_inverter_dict = jsonObject
                    self.jsonInverter_i = self.jsonInverter_i + 1
                    #self.signal_Sensors_json.emit(jsonObject)
            elif ('Timeout CAN' and 'Wert' and 'Latching' in jsonObject):
                if (self.jsonErrors_i < 1):
                    self.json_errors_dict = jsonObject
                    self.jsonErrors_i = self.jsonErrors_i + 1
                    #self.signal_Sensors_json.emit(jsonObject)
            elif ('General' and 'TV/KF' and 'Energy Control' in jsonObject):
                if (self.jsonMath_i < 1):
                    self.json_math_dict = jsonObject
                    self.jsonMath_i = self.jsonMath_i + 1
            elif ('Switches' in jsonObject):
                if (self.jsonControls_i < 1):
                    self.json_controls_dict = jsonObject
                    self.jsonControls_i = self.jsonControls_i + 1
            elif ('Input Error Code' and 'Output Error Code' and 'Transmit Error Counter' and 'Error Counter' in jsonStr):
                if (self.jsonFPGA_Error_i < 1):
                    self.json_fpga_error_dict = jsonObject
                    self.jsonFPGA_Error_i = self.jsonFPGA_Error_i + 1
        elif(str[0] == "X"):
            XMLStr = str[1:]
            XMLObject = xmltodict.parse(XMLStr)
            print(XMLObject)
            if (XMLObject['Cluster']['Name'] == 'Config-Values'):
                if (self.config_i < 1):
                    #print("-", XMLObject.get("Cluster").get("SGL"))
                    self.XML_config_list = XMLObject
                    self.signal_Config_Values_init.emit(XMLObject)
                    self.config_i = self.config_i + 1
                # self.signal_Config_Values.emit(XMLObject)
                # self.signal_Config_Values_init.emit(XMLObject)
            elif (XMLObject['Cluster']['Name'] == 'Sensors'):
                #print(XMLObject)
                # self.signal_Sensors.emit(XMLObject)
                if(self.sensors_i < 1):
                    self.XML_sensors_list = XMLObject
                    self.sensors_i = self.sensors_i + 1
                    #self.signal_Sensors_init.emit(XMLObject)
            elif (XMLObject['Cluster']['Name'] == 'Inverter'):
                if (self.inverter_i < 1):
                    self.XML_inverter_list = XMLObject
                    self.inverter_i = self.inverter_i + 1
                    #self.signal_Sensors_init.emit(XMLObject)
                # self.signal_Inverter.emit(XMLObject)
            elif (XMLObject['Cluster']['Name'] == 'Errors'):
                if (self.errors_i < 1):
                    self.XML_error_list = XMLObject
                    self.errors_i = self.errors_i + 1
                # self.signal_Errors.emit(XMLObject)
            elif (XMLObject['Cluster']['Name'] == 'Math'):
                if (self.math_i < 1):
                    self.XML_math_list = XMLObject
                    self.math_i = self.math_i + 1
                # self.signal_Math.emit(XMLObject)
            elif (XMLObject['Cluster']['Name'] == 'Controls'):
                if (self.controls_i < 1):
                    self.XML_controls_list = XMLObject
                    self.controls_i = self.controls_i + 1
                # self.signal_Controls.emit(XMLObject)
            elif (XMLObject['Cluster']['Name'] == 'FPGA Error'):
                if (self.fpga_error_i < 1):
                    self.XML_fpga_error_list = XMLObject
                    self.fpga_error_i = self.fpga_error_i + 1
                #self.signal_FPGA_Error.emit(XMLObject)
            elif (XMLObject['Cluster']['Name'] == 'Timestamp'):
                pass
                # self.signal_Timestamp.emit(XMLObject)
        elif(data[3] == 1):
            if (self.jsonConfig_i > 0 and self.config_i > 0):
                # e = concurrent.futures.ThreadPoolExecutor(max_workers=100)
                #e.submit(self.jsonIteration, self.json_config_dict, 0, data, 4)
                self.jsonIteration(self.json_config_dict, self.XML_config_list, 0, data, 4)
                self.recieve_Config_Valuesx(self.XML_config_list)

        elif(data[3] == 2):
            #self.signal_Sensors_serial.emit(data)
            if(self.jsonSensor_i > 0 and self.sensors_i > 0):

                #mt.submit(self.jsonIteration, self.json_sensor_dict, 0, data, 4)
                self.jsonIteration(self.json_sensor_dict, self.XML_sensors_list, 0, data, 4)
                #print(self.XML_sensors_list)
                self.recieve_Sensorsx(self.XML_sensors_list)
                #self.jsonIteration(self.json_sensor_dict, 0, data)
                #mt.submit(self.recieve_Sensorsx, self.XML_sensors_list)
                #self.signal_Sensors_update.emit(self.XML_sensors_list)
        elif (data[3] == 3):
            if (self.jsonInverter_i > 0 and self.inverter_i > 0):
                self.jsonIteration(self.json_inverter_dict, self.XML_inverter_list, 0, data, 4)
                self.recieve_Inverterx(self.XML_inverter_list)
        elif (data[3] == 4):
            if (self.jsonErrors_i > 0 and self.errors_i > 0):
                self.jsonIteration(self.json_errors_dict, self.XML_error_list, 0, data, 4)
                self.recieve_Errorsx(self.XML_error_list)
        elif (data[3] == 5):
            if (self.jsonMath_i > 0 and self.math_i > 0):
                self.jsonIteration(self.json_math_dict, self.XML_math_list, 0, data, 4)
                self.recieve_Mathx(self.XML_math_list)
        elif (data[3] == 6):
            if (self.jsonControls_i > 0 and self.controls_i > 0):
                self.jsonIteration(self.json_controls_dict, self.XML_controls_list, 0, data, 4)
                self.recieve_Controlsx(self.XML_controls_list)
        elif (data[3] == 7):
            if (self.jsonFPGA_Error_i > 0 and self.fpga_error_i > 0):
                self.jsonIteration(self.json_fpga_error_dict, self.XML_fpga_error_list, 0, data, 4)
                self.recieve_FPGA_Errorx(self.XML_fpga_error_list)


    def jsonIteration(self, jsonDict, xmlDict, iteration_level, serialElements, serialCounter, json_sensor_dict_element_1 = "None", json_sensor_dict_element_2 = "None", json_sensor_dict_element_3 = "None"):
        #self.val = 0
        searchXMLLevel = 0
        iteration_level = iteration_level + 1
        #print("Jso:", type(jsonDict), jsonDict)
        for key in jsonDict:
            if(isinstance(jsonDict[key], dict)):
                if(iteration_level == 1):
                    #self.json_sensor_dict_element_1 = key
                    json_sensor_dict_element_1 = key
                elif(iteration_level == 2):
                    #self.json_sensor_dict_element_2 = key
                    json_sensor_dict_element_2 = key
                elif (iteration_level == 3):
                    #self.json_sensor_dict_element_3 = key
                    json_sensor_dict_element_3 = key
                serialCounter = self.jsonIteration(jsonDict[key], xmlDict, iteration_level, serialElements, serialCounter, json_sensor_dict_element_1, json_sensor_dict_element_2, json_sensor_dict_element_3)
            elif (isinstance(jsonDict[key], list)):
                serialCounter = self.jsonIteration(jsonDict[key], xmlDict, iteration_level, serialElements, serialCounter, json_sensor_dict_element_1, json_sensor_dict_element_2, json_sensor_dict_element_3)
            else:
                if(json_sensor_dict_element_2 == "None"):
                    #self.searchXMLLevel = 0
                    searchXMLLevel = 0
                    #self.XMLElementFound = False
                    #self.elementDatatype = "None"
                    elementDatatype = "None"
                    serialCounter, searchXMLLevel = self.searchXMLdatatype(xmlDict, key, elementDatatype, serialElements, serialCounter, json_sensor_dict_element_1, searchXMLLevel) #for checking the datatype

                elif(json_sensor_dict_element_3 == "None"):
                    #print("3:", key, self.json_sensor_dict_element_1, self.json_sensor_dict_element_2)
                    #self.searchXMLLevel = 0
                    searchXMLLevel = 0
                    #self.XMLElementFound = False
                    #self.elementDatatype = "None"
                    elementDatatype = "None"
                    serialCounter, searchXMLLevel = self.searchXMLdatatype(xmlDict, key, elementDatatype, serialElements, serialCounter, json_sensor_dict_element_1, searchXMLLevel, json_sensor_dict_element_2)  # for checking the datatype

        iteration_level = iteration_level - 1
        if (iteration_level == 1):
            #self.json_sensor_dict_element_1 = "None"
            json_sensor_dict_element_1 = "None"
        elif (iteration_level == 2):
            #self.json_sensor_dict_element_2 = "None"
            json_sensor_dict_element_2 = "None"
        elif (iteration_level == 3):
            #self.json_sensor_dict_element_3 = "None"
            json_sensor_dict_element_3 = "None"
        return serialCounter

    def searchXMLdatatype(self, dataList, listElement, dataType, serialElements, serialCounter, json_sensor_dict_element_1, searchXMLLevel, listElement2d = 'empty', listElement3d = 'empty', indexes = 0):
        ElementXMLCompare = listElement.replace("°", "")
        ElementXMLCompare = ElementXMLCompare.replace("²", "")
        ElementXMLCompare = ElementXMLCompare.replace("ü", "")
        ElementXMLCompare = ElementXMLCompare.replace("ä", "")
        ElementXMLCompare = ElementXMLCompare.replace("ö", "")
        ElementXMLCompare2d = listElement2d.replace("°", "")
        ElementXMLCompare2d = ElementXMLCompare2d.replace("²", "")
        ElementXMLCompare2d = ElementXMLCompare2d.replace("ü", "")
        ElementXMLCompare2d = ElementXMLCompare2d.replace("ä", "")
        ElementXMLCompare2d = ElementXMLCompare2d.replace("ö", "")
        # ElementXMLCompare3d = listElement3d.replace("°", "")
        # ElementXMLCompare3d = ElementXMLCompare3d.replace("²", "")
        # ElementXMLCompare3d = ElementXMLCompare3d.replace("ü", "")
        # ElementXMLCompare3d = ElementXMLCompare3d.replace("ä", "")
        # ElementXMLCompare3d = ElementXMLCompare3d.replace("ö", "")
        if (ElementXMLCompare[0] == " "):
            ElementXMLCompare = ElementXMLCompare[1:]
        if (ElementXMLCompare[len(ElementXMLCompare) - 1] == " "):
            ElementXMLCompare = ElementXMLCompare[:len(ElementXMLCompare) - 1]
        if(listElement2d == "empty"):
            #self.dictBool(dataList, listElement, 'Cluster', listElement)
            if(dataList != []):
                if(dataList.get('Cluster').get("Name") == "Config-Values"):
                    serialCounter, elementDatatype, searchXMLLevel = self.searchElementandDatatype(dataList.get('Cluster'), ElementXMLCompare, dataType, serialElements, serialCounter, json_sensor_dict_element_1, 0, "None")
                else:
                    serialCounter, elementDatatype, searchXMLLevel = self.searchElementandDatatype(dataList.get('Cluster', 'None').values(), ElementXMLCompare, dataType, serialElements, serialCounter, json_sensor_dict_element_1, 0, "None")
            else:
                print("Dict empty")
            #print("N:",self.elementName,":",len(self.elementName), self.elementName.encode())
            #print(dataList)
            #print(self.elementName == ElementXMLCompare)
            # if (self.elementName == ElementXMLCompare):
            #     datatype = type(0)#type(self.elementValue)
            #     #print(listElement + ": " + self.elementValue)
            #     if(isinstance(self.elementValue, str)):
            #         #print(self.elementValue, self.elementValue.find('.'))
            #         # print(ElementXMLCompare)
            #         # print(self.elementName, self.elementValue)
            #         if(self.elementValue.find('.') != -1 and any(chr.isdigit() for chr in (self.elementValue))):
            #             datatype = type(0.0)
            #         elif(self.elementValue == "0"):
            #             datatype = type(0)
            #         else:
            #             datatype = type(0)
            #
            #     return datatype
            # else:
            #     print(self.elementName, listElement, ElementXMLCompare, listElement[0],ElementXMLCompare[0])
        elif(listElement3d == "empty"):
            #print("EL:", listElement, listElement2d, listElement3d)
            serialCounter, elementDatatype, searchXMLLevel = self.searchElementandDatatype(dataList.get('Cluster', 'None').values(), ElementXMLCompare, dataType, serialElements, serialCounter, json_sensor_dict_element_1, 0, "None", wantedElement2 = ElementXMLCompare2d)
        #print("2:", dataList)
        #self.XML_sensors_list = dataList
        #print(dataList)
        return serialCounter, searchXMLLevel

    def searchElementandDatatype(self, listofElements, wantedElement, dataType, serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1, searchXMLLevel, wantedElement2 = None, wantedElement3 = None):
        elementDatatype = dataType
        # if(elementDatatype != self.elementDatatype):
        #     print("T:", elementDatatype, self.elementDatatype, listofElements)
        # elementDatatype = self.elementDatatype
        #elementDatatype = "None"
        #elementDatatype = dataType

        #print("tttt", type(listofElements), listofElements)
        if (isinstance(listofElements, OrderedDict)):
            #print("+++++++++++++++++++++++++++++++++++++++++++")
            #self.XML_dict_element_1 = "None" #listofElements.get("Name")
            XML_dict_element_1 = "None"
            DBLElement = listofElements.get('DBL')
            SGLElement = listofElements.get('SGL')
            boolElement = listofElements.get('Boolean')
            U8Element = listofElements.get('U8')
            U16Element = listofElements.get('U16')
            U32Element = listofElements.get('U32')
            I8Element = listofElements.get('I8')
            EBElement = listofElements.get('EB')
            #print("$$$$", elementDatatype, SGLElement)
            if (boolElement != None and elementDatatype == "None"):
                #print("boolElement")
                serialCounter, elementDatatype = self.searchDatatypeElement(boolElement, wantedElement,
                                                                            "Boolean", serialElements,
                                                                            serialCounter, json_sensor_dict_element_1, XML_dict_element_1,
                                                                            wantedElement2=listofElements.get("Name"))
                #print("boolElement2")
            if (DBLElement != None and elementDatatype == "None"):
                #print(DBLElement)
                serialCounter, elementDatatype = self.searchDatatypeElement(DBLElement, wantedElement, "DBL",
                                                                            serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1,

                                                                            wantedElement2=listofElements.get("Name"))
            if (SGLElement != None and elementDatatype == "None"):
                #print("SGLElement", SGLElement)
                serialCounter, elementDatatype = self.searchDatatypeElement(SGLElement, wantedElement, "SGL",
                                                                            serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1,

                                                                            wantedElement2=listofElements.get("Name"))
                #print("SGLElement2")
            if (U8Element != None and elementDatatype == "None"):
                serialCounter, elementDatatype = self.searchDatatypeElement(U8Element, wantedElement, "U8",
                                                                            serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1,

                                                                            wantedElement2=listofElements.get("Name"))
            if (U16Element != None and elementDatatype == "None"):
                serialCounter, elementDatatype = self.searchDatatypeElement(U16Element, wantedElement, "U16",
                                                                            serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1,

                                                                            wantedElement2=listofElements.get("Name"))
            if (U32Element != None and elementDatatype == "None"):
                serialCounter, elementDatatype = self.searchDatatypeElement(U32Element, wantedElement, "U32",
                                                                            serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1,

                                                                            wantedElement2=listofElements.get("Name"))
            if (I8Element != None and elementDatatype == "None"):
                serialCounter, elementDatatype = self.searchDatatypeElement(I8Element, wantedElement, "I8",
                                                                            serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1,

                                                                            wantedElement2=listofElements.get("Name"))
            if (EBElement != None and elementDatatype == "None"):
                #print("EBElement")
                serialCounter, elementDatatype = self.searchDatatypeElement(EBElement, wantedElement, "EB",
                                                                            serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1,

                                                                            wantedElement2=listofElements.get("Name"))
            #print("RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
        else:
            for element in listofElements:
                #print(type(element), element)
                #print("Level:", self.searchXMLLevel, searchXMLLevel)
                if(wantedElement2 == None or searchXMLLevel == 1):
                    if(isinstance(element, OrderedDict)):
                        if(wantedElement2 == None):
                            #self.XML_dict_element_1 = element.get("Name")
                            XML_dict_element_1 = element.get("Name")
                        DBLElement = element.get('DBL')
                        SGLElement = element.get('SGL')
                        boolElement = element.get('Boolean')
                        U8Element = element.get('U8')
                        U16Element = element.get('U16')
                        U32Element = element.get('U32')
                        I8Element = element.get('I8')
                        EBElement = element.get('EB')

                        #print("kkkk", SGLElement)

                        #dataType = "None"

                        #print("####", type(listofElements), listofElements)
                        #print("++++", element)
                        #print(element, wantedElement)
                        if(boolElement != None and elementDatatype == "None"):
                            serialCounter, elementDatatype = self.searchDatatypeElement(boolElement, wantedElement, "Boolean", serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1, wantedElement2 = element.get("Name"))

                        if(DBLElement != None and elementDatatype == "None"):
                            serialCounter, elementDatatype = self.searchDatatypeElement(DBLElement, wantedElement, "DBL", serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1, wantedElement2 = element.get("Name"))

                        if(SGLElement != None and elementDatatype == "None"):
                            serialCounter, elementDatatype = self.searchDatatypeElement(SGLElement, wantedElement, "SGL", serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1, wantedElement2 = element.get("Name"))

                        if(U8Element != None and elementDatatype == "None"):
                            serialCounter, elementDatatype = self.searchDatatypeElement(U8Element, wantedElement, "U8", serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1, wantedElement2 = element.get("Name"))

                        if(U16Element != None and elementDatatype == "None"):
                            serialCounter, elementDatatype = self.searchDatatypeElement(U16Element, wantedElement, "U16", serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1, wantedElement2 = element.get("Name"))

                        if(U32Element != None and elementDatatype == "None"):
                            serialCounter, elementDatatype = self.searchDatatypeElement(U32Element, wantedElement, "U32", serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1, wantedElement2 = element.get("Name"))

                        if(I8Element != None and elementDatatype == "None"):
                            serialCounter, elementDatatype = self.searchDatatypeElement(I8Element, wantedElement, "I8", serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1, wantedElement2 = element.get("Name"))

                        if(EBElement != None and elementDatatype == "None"):
                            serialCounter, elementDatatype = self.searchDatatypeElement(EBElement, wantedElement, "EB", serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1, wantedElement2 = element.get("Name"))

                        # if(element.get('Name') == wantedElement and element.get('Val') != 'None'):
                        #     self.elementName = element.get('Name')
                        #     if(element.get('Choice')):
                        #         print("Choice")
                        #         self.elementValue = element.get('Choice')[int(element.get('Val'))]
                        #         self.elementChoiceElements = element.get('Choice')
                        #         self.elementDatatype = "EB"
                        #     else:
                        #         self.elementChoiceElements = "None"
                        #         self.elementValue = element.get('Val')
                        # else:
                        #     self.searchElement(element.values(), wantedElement, listofElements)

                    elif(isinstance(element, list)):
                        serialCounter, elementDatatype, searchXMLLevel = self.searchElementandDatatype(element, wantedElement, elementDatatype, serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1, searchXMLLevel)
                elif(wantedElement2 != None):
                    for element in listofElements:
                        #print("Element and wanted Element2:", wantedElement2)
                        if(isinstance(element, OrderedDict)):
                            if(element.get("Name") == json_sensor_dict_element_1):
                                #self.XML_dict_element_1 = element.get("Name")
                                XML_dict_element_1 = element.get("Name")

                                #self.searchXMLLevel = 1
                                searchXMLLevel = 1
                                #print("XXXXX:", element)
                                #self.cluster2 = True
                                #self.clusterName = (element.get("Cluster")).get("Name")
                                serialCounter, elementDatatype, searchXMLLevel = self.searchElementandDatatype(element.get("Cluster"), wantedElement, elementDatatype, serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1, searchXMLLevel, wantedElement2 = wantedElement2)
                                #print("-------", element.get("Cluster"))
                            # elif(element.get("Name") == self.json_sensor_dict_element_2):
                            #     self.searchXMLLevel = 2
                            #     print("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
                            #print("Dict Element:", element.get("Name"), wantedElement2 ,self.json_sensor_dict_element_1, self.json_sensor_dict_element_2)
                        elif(isinstance(element, list)):
                            #print("List Element:", element)
                            serialCounter, elementDatatype, searchXMLLevel = self.searchElementandDatatype(element, wantedElement, elementDatatype, serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1, searchXMLLevel, wantedElement2 = wantedElement2)
                            #self.searchElementandDatatype(element, wantedElement)

        #self.recieve_Sensorsx(listofElements)
        #self.searchXMLLevel = 0
        searchXMLLevel = 0
        return serialCounter, elementDatatype, searchXMLLevel


    def searchDatatypeElement(self, datatypeElement, wantedElement, dataType, serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1, wantedElement2 = None, wantedElement3 = None):
        if(isinstance(datatypeElement, list)):
            for datatypeElements in datatypeElement:
                serialCounter, elementDatatype = self.searchDatatypeElement(datatypeElements, wantedElement, dataType, serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1, wantedElement2 = wantedElement2)
                if(elementDatatype != "None"):
                    return serialCounter, elementDatatype

        elif (isinstance(datatypeElement, OrderedDict)):
            #print("2", wantedElement, datatypeElement.get('Name'), self.json_sensor_dict_element_1, self.XML_dict_element_1)
            #print("datatypeElement:", datatypeElement, dataType)
            #print(wantedElement, datatypeElement.get('Name'), self.json_sensor_dict_element_1, self.XML_dict_element_1)
            # if(self.json_sensor_dict_element_1 != json_sensor_dict_element_1):
            #     print("1:", self.json_sensor_dict_element_1, json_sensor_dict_element_1, self.XML_dict_element_1)
            # if (self.XML_dict_element_1 != XML_dict_element_1):
            #     print("2:", self.XML_dict_element_1, XML_dict_element_1)
            if(wantedElement == datatypeElement.get('Name') and json_sensor_dict_element_1 == XML_dict_element_1): #wantedElement == datatypeElement.get('Name') and self.json_sensor_dict_element_1 == self.XML_dict_element_1
                #print("3", serialCounter)
                #self.elementDatatype = dataType
                elementDatatype = dataType
                # self.XMLElementFound = True
                # self.XMLElement = datatypeElement
                # self.clusterName2 = wantedElement2
                # self.clusterName = self.XML_dict_element_1
                #print("4", dataType)

                if (dataType == "EB"):
                    #print("5")
                    datatypeElement['Val'] = str(serialElements[serialCounter])
                    serialCounter = serialCounter + 1
                    #print("serialCounter:", wantedElement, dataType, str(serialElements[serialCounter-1]), serialCounter)
                    return serialCounter, elementDatatype
                elif (dataType == "U32"):  # is checking the datatype for serial datastream
                    # intValue = serialElements[self.serialCounter] * 256 + serialElements[self.serialCounter + 1]
                    # print("U32 L2:", key)
                    datatypeElement['Val'] = "-"
                    serialCounter = serialCounter + 4
                    #print("serialCounter:", wantedElement, dataType, serialCounter)
                    return serialCounter, elementDatatype
                elif (dataType == "U16"):  # is checking the datatype for serial datastream
                    intValue = serialElements[serialCounter] * 256 + serialElements[serialCounter + 1]
                    # print("U16 L1:", key, intValue)
                    datatypeElement['Val'] = str(intValue)
                    serialCounter = serialCounter + 2
                    #print("serialCounter:", wantedElement, dataType, serialCounter)
                    return serialCounter, elementDatatype
                elif (dataType == "U8"):  # is checking the datatype for serial datastream
                    # print("U8 L1:", key, serialElements[self.serialCounter])
                    datatypeElement['Val'] = str(serialElements[serialCounter])
                    serialCounter = serialCounter + 1
                    #print("serialCounter:", wantedElement, dataType, serialCounter)
                    return serialCounter, elementDatatype
                elif (dataType == "I8"):  # is checking the datatype for serial datastream
                    # print("I8 L1:", key, serialElements[self.serialCounter])
                    datatypeElement['Val'] = str(serialElements[serialCounter])
                    serialCounter = serialCounter + 1
                    #print("serialCounter:", wantedElement, dataType, serialCounter)
                    return serialCounter, elementDatatype
                elif (dataType == "Boolean"):
                    # print("Boolean L1:", key, serialElements[self.serialCounter])
                    datatypeElement['Val'] = str(serialElements[serialCounter])
                    serialCounter = serialCounter + 1
                    #print("serialCounter:", wantedElement, dataType, serialCounter)
                    return serialCounter, elementDatatype
                elif (dataType == "DBL"):
                    datatypeElement['Val'] = ":"#str(self.serial_to_float(serialElements[serialCounter],
                                             #    serialElements[serialCounter + 1],
                                             #    serialElements[serialCounter + 2],
                                             #    serialElements[serialCounter + 3]))
                    # print("DBL L1:", key, value)
                    serialCounter = serialCounter + 8
                    #print("serialCounter:", wantedElement, dataType, serialCounter)
                    return serialCounter, elementDatatype
                elif (dataType == "SGL"):
                    #print("5", wantedElement, serialCounter, len(serialElements))
                    value = str(self.serial_to_float(serialElements[serialCounter],
                                                 serialElements[serialCounter + 1],
                                                 serialElements[serialCounter + 2],
                                                 serialElements[serialCounter + 3]))
                    #print("6")
                    datatypeElement['Val'] = value
                    print("K:", wantedElement, datatypeElement['Val'])
                    #print("SGL L1:", key, value)
                    serialCounter = serialCounter + 4
                    #print("serialCounter:", datatypeElement.get('Name'), wantedElement, dataType, serialCounter)
                    return serialCounter, elementDatatype
            else:
                elementDatatype = "None"
                return serialCounter, elementDatatype
        return serialCounter, elementDatatype
        #print(serialCounter, dataType)
        #return (serialCounter, dataType);
        #return

    # def searchElement(self, listofElements, wantedElement, oldElement):
    #     for element in listofElements:
    #         if (isinstance(element, OrderedDict)):
    #             if(element.get('Name') == wantedElement and element.get('Val') != 'None'):
    #                 self.elementName = element.get('Name')
    #                 # print("----------------------------------------------------------")
    #                 if(element.get('Choice')):
    #                     self.elementValue = element.get('Choice')[int(element.get('Val'))]
    #                     self.elementChoiceElements = element.get('Choice')
    #                     self.elementDatatype = "EB"
    #                     self.clusterName = self.XML_dict_element_1
    #                 else:
    #                     self.elementChoiceElements = "None"
    #                     self.elementValue = element.get('Val')
    #             else:
    #                 self.searchElement(element.values(), wantedElement, listofElements)
    #         if(isinstance(element, list)):
    #             self.searchElement(element, wantedElement, listofElements)

    def recieve_Config_Valuesx(self, json_config):
        self.set_lineEdit("lineEdit_Vehicle_Mode", json_config, 'Vehicle Mode')
        self.set_lineEdit("lineEdit_APPS1_min", json_config, 'APPS1_min[]')
        self.set_lineEdit("lineEdit_APPS1_max", json_config, 'APPS1_max[]')
        self.set_lineEdit("lineEdit_APPS2_min", json_config, 'APPS2_min[]')
        self.set_lineEdit("lineEdit_APPS2_max", json_config, 'APPS2_max[]')
        self.set_lineEdit("lineEdit_maxTorque_plus", json_config, 'maxTorque+[Nm]')
        self.set_lineEdit("lineEdit_maxTorque_minus", json_config, 'maxTorque-[Nm]')
        self.set_lineEdit("lineEdit_Leistungslimit", json_config, 'Leistungslimit[kW]')
        self.set_lineEdit("lineEdit_maxRPM", json_config, 'maxRPM[1/min]')
        self.set_lineEdit("lineEdit_Accelslip", json_config, 'Accelslip [%/100]')
        self.set_lineEdit("lineEdit_Brakeslip", json_config, 'Brakeslip [%/100]')
        self.set_btn_LED("btn_LED_Rekuperation", json_config, 'Rekuperation')
        self.set_btn_LED("btn_LED_ASR", json_config, 'ASR')
        self.set_btn_LED("btn_LED_BSR", json_config, 'BSR')
        self.set_btn_LED("btn_LED_TV", json_config, 'TV')
        self.set_btn_LED("btn_LED_DRS", json_config, 'DRS')
        self.set_btn_LED("btn_LED_Energiesparmodus", json_config, 'Energiesparmodus')
        self.set_btn_LED("btn_LED_Backupload", json_config, 'Backupload')
        self.set_btn_LED("btn_LED_Config_locked", json_config, 'Config locked')
        self.set_btn_LED("btn_LED_InverterVR_active", json_config, 'InverterVR-active')
        self.set_btn_LED("btn_LED_InverterVL_active", json_config, 'InverterVL-active')
        self.set_btn_LED("btn_LED_InverterHR_active", json_config, 'InverterHR-active')
        self.set_btn_LED("btn_LED_InverterHL_active", json_config, 'InverterHL-active')

    def recieve_Sensorsx(self, json_Sensors):
        if(self.sensors_i > 0):
            #json_Sensors = self.XML_sensors_list
            #print(lineEdit_APPS1, json_Sensors, 'Analog', 'APPS1[]')
            self.set_lineEdit("lineEdit_APPS1", json_Sensors, 'Analog', listElement2d='APPS1[]')
            self.set_lineEdit("lineEdit_APPS2", json_Sensors, 'Analog', listElement2d='APPS2[]')
            self.set_lineEdit("lineEdit_Bremsdruck_vorne", json_Sensors, 'Analog', listElement2d='Bremsdruck vorne [bar]')
            self.set_lineEdit("lineEdit_Bremsdruck_hinten", json_Sensors, 'Analog', listElement2d='Bremsdruck hinten [bar]')
            self.set_lineEdit("lineEdit_Bremskraft", json_Sensors, 'Analog', listElement2d='Bremskraft[N]')
            self.set_lineEdit("lineEdit_Lenkwinkel", json_Sensors, 'Analog', listElement2d='Lenkwinkel[]')
            self.set_lineEdit("lineEdit_WT_Motor_high", json_Sensors, 'Analog', listElement2d='WT_Motor_high[C]')
            self.set_lineEdit("lineEdit_WT_Motor_Low", json_Sensors, 'Analog', listElement2d='WT_Motor_Low[C]')
            self.set_lineEdit("lineEdit_LT_Inv_FrR", json_Sensors, 'Analog', listElement2d='LT_Inv_FrR[C]')
            self.set_lineEdit("lineEdit_LT_Inv_FrL", json_Sensors, 'Analog', listElement2d='LT_Inv_FrL[C]')
            self.set_lineEdit("lineEdit_LT_Inv_ReR", json_Sensors, 'Analog', listElement2d='LT_Inv_ReR[C]')
            self.set_lineEdit("lineEdit_LT_Inv_ReL", json_Sensors, 'Analog', listElement2d='LT_Inv_ReL[C]')
            self.set_lineEdit("lineEdit_Ambient_Temp", json_Sensors, 'Analog', listElement2d='Ambient_Temp[C]')
            self.set_lineEdit("lineEdit_ST_FR", json_Sensors, 'Analog', listElement2d='ST_FR[mm}')
            self.set_lineEdit("lineEdit_ST_FL", json_Sensors, 'Analog', listElement2d='ST_FL[mm]')
            self.set_lineEdit("lineEdit_ST_RR", json_Sensors, 'Analog', listElement2d='ST_RR[mm]')
            self.set_lineEdit("lineEdit_ST_RL", json_Sensors, 'Analog', listElement2d='ST_RL[mm]')
            self.set_lineEdit("lineEdit_Temp_Fusebox", json_Sensors, 'Analog', listElement2d='Temp_Fusebox [C]')

            self.set_lineEdit("lineEdit_HV_Current", json_Sensors, 'Akku/HV', listElement2d='HV_Current[A]')
            self.set_lineEdit("lineEdit_IC_Voltage", json_Sensors, 'Akku/HV', listElement2d='IC_Voltage[V]')
            self.set_lineEdit("lineEdit_Charge", json_Sensors, 'Akku/HV', listElement2d='Charge[Ah]')
            self.set_lineEdit("lineEdit_AMS_State", json_Sensors, 'Akku/HV', listElement2d='AMS-State')
            self.set_btn_LED("btn_LED_State_SC", json_Sensors, 'Akku/HV', listElement2d='State SC')
            self.set_lineEdit("lineEdit_Akku_Voltage", json_Sensors, 'Akku/HV', listElement2d='Akku-Voltage[V]')
            self.set_lineEdit("lineEdit_SOC", json_Sensors, 'Akku/HV', listElement2d='SOC[%]')
            self.set_lineEdit("lineEdit_CVH", json_Sensors, 'Akku/HV', listElement2d='CVH[V]')
            self.set_lineEdit("lineEdit_CVL", json_Sensors, 'Akku/HV', listElement2d='CVL[V]')
            self.set_lineEdit("lineEdit_CVL_2", json_Sensors, 'Akku/HV', listElement2d='CVL[V] 20s')
            self.set_lineEdit("lineEdit_CVL_3", json_Sensors, 'Akku/HV', listElement2d='CVL[V] 60s')
            self.set_lineEdit("lineEdit_CTH", json_Sensors, 'Akku/HV', listElement2d='CTH[C]')
            self.set_lineEdit("lineEdit_CTL", json_Sensors, 'Akku/HV', listElement2d='CTL[C]')
            self.set_lineEdit("lineEdit_State_IMD", json_Sensors, 'Akku/HV', listElement2d='State IMD')
            self.set_lineEdit("lineEdit_Isolationswiderstand", json_Sensors, 'Akku/HV',
                              listElement2d='Isolationswider\nstand[kOhm]')

            self.set_lineEdit("lineEdit_SC_after_Motors_Rear", json_Sensors, 'SC', listElement2d='SC Messungen',
                              listElement3d='SC after Motors Rear [V]')
            self.set_lineEdit("lineEdit_SC_after_Motors_Front", json_Sensors, 'SC', listElement2d='SC Messungen',
                              listElement3d='SC after Motors Front [V]')
            self.set_lineEdit("lineEdit_SC_after_BOTS", json_Sensors, 'SC', listElement2d='SC Messungen',
                              listElement3d='SC after BOTS [V]')
            self.set_lineEdit("lineEdit_SC_after_Akku", json_Sensors, 'SC', listElement2d='SC Messungen',
                              listElement3d='SC after Akku [V]')
            self.set_lineEdit("lineEdit_SC_Voltage_AMS_1", json_Sensors, 'SC', listElement2d='SC Messungen',
                              listElement3d='SC Voltage AMS 1')
            self.set_lineEdit("lineEdit_SC_Voltage_AMS_2", json_Sensors, 'SC', listElement2d='SC Messungen',
                              listElement3d='SC Voltage AMS 2')
            self.set_btn_LED("btn_LED_SC_Motors_Front", json_Sensors, 'SC', listElement2d='SC Errors',
                              listElement3d='SC Motors Front')
            self.set_btn_LED("btn_LED_SC_Motors_Rear", json_Sensors, 'SC', listElement2d='SC Errors',
                             listElement3d='SC Motors Rear')
            self.set_btn_LED("btn_LED_SC_BOTS", json_Sensors, 'SC', listElement2d='SC Errors',
                             listElement3d='SC BOTS')
            self.set_btn_LED("btn_LED_SC_Akku", json_Sensors, 'SC', listElement2d='SC Errors',
                             listElement3d='SC Akku')

            self.set_btn_LED("btn_LED_Fuse1", json_Sensors, 'Fuses', listElement2d='Fuse1[b]')
            self.set_btn_LED("btn_LED_Fuse2_SSB", json_Sensors, 'Fuses', listElement2d='Fuse2_SSB[b]')
            self.set_btn_LED("btn_LED_Fuse3_IMD", json_Sensors, 'Fuses', listElement2d='Fuse3_IMD[b]')
            self.set_btn_LED("btn_LED_Fuse4_Inv", json_Sensors, 'Fuses', listElement2d='Fuse4_Inv[b]')
            self.set_btn_LED("btn_LED_Fuse5_GPS", json_Sensors, 'Fuses', listElement2d='Fuse5_GPS[b]')
            self.set_btn_LED("btn_LED_Fuse6_VCU", json_Sensors, 'Fuses', listElement2d='Fuse6_VCU[b]')
            self.set_btn_LED("btn_LED_Fuse7_BSE", json_Sensors, 'Fuses', listElement2d='Fuse7_BSE[b]')
            self.set_btn_LED("btn_LED_Fuse8_DIS", json_Sensors, 'Fuses', listElement2d='Fuse8_DIS[b]')
            self.set_btn_LED("btn_LED_Fuse9_SWS", json_Sensors, 'Fuses', listElement2d='Fuse9_SWS[b]')
            self.set_btn_LED("btn_LED_Fuse10_TPMS", json_Sensors, 'Fuses', listElement2d='Fuse10_TPMS[b]')
            self.set_btn_LED("btn_LED_Fuse11", json_Sensors, 'Fuses', listElement2d='Fuse11[b]')
            self.set_btn_LED("btn_LED_Fuse12", json_Sensors, 'Fuses', listElement2d='Fuse12[b]')
            self.set_btn_LED("btn_LED_Fuse1A_1_RTDS", json_Sensors, 'Fuses', listElement2d='Fuse1A_1_RTDS')
            self.set_btn_LED("btn_LED_Fuse1A_2_Brakelight", json_Sensors, 'Fuses',
                             listElement2d='Fuse1A_2_Brakelight')
            self.set_btn_LED("btn_LED_Fuse1A_3", json_Sensors, 'Fuses', listElement2d='Fuse1A_3')
            self.set_btn_LED("btn_LED_Fuse1A_4", json_Sensors, 'Fuses', listElement2d='Fuse1A_4')
            self.set_btn_LED("btn_LED_Fuse6A_1_Motor_Fans", json_Sensors, 'Fuses',
                             listElement2d='Fuse6A_1_Motor_Fans')
            self.set_btn_LED("btn_LED_Fuse6A_2_DRS", json_Sensors, 'Fuses',
                             listElement2d='Fuse6A_2_DRS')
            self.set_btn_LED("btn_LED_Fuse6A_3_SC", json_Sensors, 'Fuses',
                             listElement2d='Fuse6A_3_SC')
            self.set_btn_LED("btn_LED_Fuse6A_4_Vectorbox", json_Sensors, 'Fuses',
                             listElement2d='Fuse6A_4_Vectorbox')
            self.set_btn_LED("btn_LED_Fuse6A_5_Mot_Pumps", json_Sensors, 'Fuses',
                             listElement2d='Fuse6A_5_Mot_Pumps')
            self.set_btn_LED("btn_LED_Fuse6A_6", json_Sensors, 'Fuses',
                             listElement2d='Fuse6A_6')
            self.set_btn_LED("btn_LED_Fuse12A_1_Inv_Fans_Fr", json_Sensors, 'Fuses',
                             listElement2d='Fuse12A_1_Inv_Fans_Fr')
            self.set_btn_LED("btn_LED_Fuse12A_2_Inv_Fans_Re", json_Sensors, 'Fuses',
                             listElement2d='Fuse12A_2_Inv_Fans_Re')
            self.set_lineEdit("lineEdit_TunKnob_1", json_Sensors, 'Buttons/Knobs', listElement2d='TunKnob 1[%]')
            self.set_lineEdit("lineEdit_TunKnob_2", json_Sensors, 'Buttons/Knobs', listElement2d='TunKnob 2[%]')
            self.set_btn_LED("btn_LED_Start_Button", json_Sensors, 'Buttons/Knobs', listElement2d='Start-Button')
            self.set_btn_LED("btn_LED_HV_Button", json_Sensors, 'Buttons/Knobs', listElement2d='HV-Button')
            self.set_btn_LED("btn_LED_Reku_Button", json_Sensors, 'Buttons/Knobs', listElement2d='Reku-Button')
            self.set_btn_LED("btn_LED_Lenkrad_1", json_Sensors, 'Buttons/Knobs', listElement2d='Lenkrad 1')
            self.set_btn_LED("btn_LED_Lenkrad_2", json_Sensors, 'Buttons/Knobs', listElement2d='Lenkrad 2')
            self.set_btn_LED("btn_LED_Lenkrad_3", json_Sensors, 'Buttons/Knobs', listElement2d='Lenkrad 3')
            self.set_btn_LED("btn_LED_Lenkrad_4", json_Sensors, 'Buttons/Knobs', listElement2d='Lenkrad 4')
            self.set_btn_LED("btn_LED_Lenkrad_5", json_Sensors, 'Buttons/Knobs', listElement2d='Lenkrad 5')
            self.set_btn_LED("btn_LED_Lenkrad_6", json_Sensors, 'Buttons/Knobs', listElement2d='Lenkrad 6')

            self.set_lineEdit("lineEdit_V_GPS", json_Sensors, 'GPS/9-axis Front', listElement2d='V_GPS[km/h]')
            self.set_lineEdit("lineEdit_Course_GPS", json_Sensors, 'GPS/9-axis Front', listElement2d='Course_GPS[]')
            self.set_lineEdit("lineEdit_Latitude", json_Sensors, 'GPS/9-axis Front', listElement2d='Latitude[]')
            self.set_lineEdit("lineEdit_Longitude", json_Sensors, 'GPS/9-axis Front', listElement2d='Longitude[]')
            self.set_lineEdit("lineEdit_HDOP", json_Sensors, 'GPS/9-axis Front', listElement2d='HDOP')
            self.set_lineEdit("lineEdit_Quality_of_Fix", json_Sensors, 'GPS/9-axis Front',
                              listElement2d='Quality of Fix')
            self.set_lineEdit("lineEdit_Satellites", json_Sensors, 'GPS/9-axis Front', listElement2d='Satellites')
            self.set_lineEdit("lineEdit_Odometer", json_Sensors, 'GPS/9-axis Front', listElement2d='Odometer[km]')
            self.set_lineEdit("lineEdit_ACC_X_Fr", json_Sensors, 'GPS/9-axis Front', listElement2d='ACC_X_Fr[m/s]')
            self.set_lineEdit("lineEdit_ACC_Y_Fr", json_Sensors, 'GPS/9-axis Front', listElement2d='ACC_Y_Fr[m/s]')
            self.set_lineEdit("lineEdit_ACC_Z_Fr", json_Sensors, 'GPS/9-axis Front', listElement2d='ACC_Z_Fr[m/s]')
            self.set_lineEdit("lineEdit_ROT_X_Fr", json_Sensors, 'GPS/9-axis Front', listElement2d='ROT_X_Fr[/s]')
            self.set_lineEdit("lineEdit_ROT_Y_Fr", json_Sensors, 'GPS/9-axis Front', listElement2d='ROT_Y_Fr[/s]')
            self.set_lineEdit("lineEdit_ROT_Z_Fr", json_Sensors, 'GPS/9-axis Front', listElement2d='ROT_Z_Fr[/s]')
            self.set_lineEdit("lineEdit_MAG_X_Fr", json_Sensors, 'GPS/9-axis Front', listElement2d='MAG_X_Fr[b]')
            self.set_lineEdit("lineEdit_MAG_Y_Fr", json_Sensors, 'GPS/9-axis Front', listElement2d='MAG_Y_Fr[b]')
            self.set_lineEdit("lineEdit_MAG_Z_Fr", json_Sensors, 'GPS/9-axis Front', listElement2d='MAG_Z_Fr[b]')
            self.set_lineEdit("lineEdit_MAG_Z_Fr", json_Sensors, 'GPS/9-axis Front', listElement2d='MAG_Z_Fr[b]')

            self.set_lineEdit("lineEdit_V_GPS_Rear", json_Sensors, 'GPS/9-axis Rear', listElement2d='V_GPS[km/h]')
            self.set_lineEdit("lineEdit_Course_GPS_Rear", json_Sensors, 'GPS/9-axis Rear', listElement2d='Course_GPS[]')
            self.set_lineEdit("lineEdit_Latitude_Rear", json_Sensors, 'GPS/9-axis Rear', listElement2d='Latitude[]')
            self.set_lineEdit("lineEdit_Longitude_Rear", json_Sensors, 'GPS/9-axis Rear', listElement2d='Longitude[]')
            self.set_lineEdit("lineEdit_HDOP_Rear", json_Sensors, 'GPS/9-axis Rear', listElement2d='HDOP')
            self.set_lineEdit("lineEdit_Quality_of_Fix_Rear", json_Sensors, 'GPS/9-axis Rear',
                              listElement2d='Quality of Fix')
            self.set_lineEdit("lineEdit_Satellites_Rear", json_Sensors, 'GPS/9-axis Front', listElement2d='Satellites')
            self.set_lineEdit("lineEdit_Odometer_Rear", json_Sensors, 'GPS/9-axis Rear', listElement2d='Odometer[km]')
            self.set_lineEdit("lineEdit_ACC_X_Re", json_Sensors, 'GPS/9-axis Rear', listElement2d='ACC_X_Re[m/s]')
            self.set_lineEdit("lineEdit_ACC_Y_Re", json_Sensors, 'GPS/9-axis Rear', listElement2d='ACC_Y_Re[m/s]')
            self.set_lineEdit("lineEdit_ACC_Z_Re", json_Sensors, 'GPS/9-axis Rear', listElement2d='ACC_Z_Re[m/s]')
            self.set_lineEdit("lineEdit_ROT_X_Re", json_Sensors, 'GPS/9-axis Rear', listElement2d='ROT_X_Re[/s]')
            self.set_lineEdit("lineEdit_ROT_Y_Re", json_Sensors, 'GPS/9-axis Rear', listElement2d='ROT_Y_Re[/s]')
            self.set_lineEdit("lineEdit_ROT_Z_Re", json_Sensors, 'GPS/9-axis Rear', listElement2d='ROT_Z_Re[/s]')
            self.set_lineEdit("lineEdit_MAG_X_Re", json_Sensors, 'GPS/9-axis Rear', listElement2d='MAG_X_Re[b]')
            self.set_lineEdit("lineEdit_MAG_Y_Re", json_Sensors, 'GPS/9-axis Rear', listElement2d='MAG_Y_Re[b]')
            self.set_lineEdit("lineEdit_MAG_Z_Re", json_Sensors, 'GPS/9-axis Rear', listElement2d='MAG_Z_Re[b]')
            self.set_lineEdit("lineEdit_MAG_Z_Re", json_Sensors, 'GPS/9-axis Rear', listElement2d='MAG_Z_Re[b]')

            self.set_lineEdit("lineEdit_1A_1", json_Sensors, 'Fusebox Currents', listElement2d='1A_1')
            self.set_lineEdit("lineEdit_1A_2", json_Sensors, 'Fusebox Currents', listElement2d='1A_ 2')
            self.set_lineEdit("lineEdit_1A_3", json_Sensors, 'Fusebox Currents', listElement2d='1A_3')
            self.set_lineEdit("lineEdit_1A_4", json_Sensors, 'Fusebox Currents', listElement2d='1A_4')
            self.set_lineEdit("lineEdit_6A_1", json_Sensors, 'Fusebox Currents', listElement2d='6A_1')
            self.set_lineEdit("lineEdit_6A_2", json_Sensors, 'Fusebox Currents', listElement2d='6A_2')
            self.set_lineEdit("lineEdit_6A_3", json_Sensors, 'Fusebox Currents', listElement2d='6A_3')
            self.set_lineEdit("lineEdit_6A_4", json_Sensors, 'Fusebox Currents', listElement2d='6A_4')
            self.set_lineEdit("lineEdit_6A_5", json_Sensors, 'Fusebox Currents', listElement2d='6A_5')
            self.set_lineEdit("lineEdit_6A_6", json_Sensors, 'Fusebox Currents', listElement2d='6A_6')
            self.set_lineEdit("lineEdit_12A_1", json_Sensors, 'Fusebox Currents', listElement2d='12A_1')
            self.set_lineEdit("lineEdit_12A_2", json_Sensors, 'Fusebox Currents', listElement2d='12A_2')

            self.set_lineEdit("lineEdit_Timestamp", json_Sensors, 'Kistler', listElement2d='Timestamp [4ms]')
            self.set_lineEdit("lineEdit_IVI", json_Sensors, 'Kistler', listElement2d='IVI [10^-2 m/s]')
            self.set_lineEdit("lineEdit_Weg", json_Sensors, 'Kistler', listElement2d='Weg [m]')
            self.set_lineEdit("lineEdit_V_lon", json_Sensors, 'Kistler', listElement2d='V_lon [m/s]')
            self.set_lineEdit("lineEdit_V_lat", json_Sensors, 'Kistler', listElement2d='V_lat [m/s]')
            self.set_lineEdit("lineEdit_Winkel", json_Sensors, 'Kistler', listElement2d='Winkel []')
            self.set_lineEdit("lineEdit_SerienNr", json_Sensors, 'Kistler', listElement2d='SerienNr')
            self.set_lineEdit("lineEdit_SensorNr", json_Sensors, 'Kistler', listElement2d='SensorNr')
            self.set_lineEdit("lineEdit_Temp", json_Sensors, 'Kistler', listElement2d='Temp [C]')
            self.set_lineEdit("lineEdit_LED_Strom", json_Sensors, 'Kistler', listElement2d='LED Strom [0,01A]')
            self.set_lineEdit("lineEdit_Statusbyte1", json_Sensors, 'Kistler', listElement2d='Statusbyte1')
            self.set_lineEdit("lineEdit_Statusbyte2", json_Sensors, 'Kistler', listElement2d='Statusbyte2')

            self.set_lineEdit("lineEdit_Status", json_Sensors, 'Datalogger', listElement2d='Status')
            self.set_lineEdit("lineEdit_Voltage", json_Sensors, 'Datalogger', listElement2d='Voltage[V]')
            self.set_lineEdit("lineEdit_Current", json_Sensors, 'Datalogger', listElement2d='Current[A]')
            self.set_lineEdit("lineEdit_Power", json_Sensors, 'Datalogger', listElement2d='Power[kW]')
            self.set_lineEdit("lineEdit_Message_Counter", json_Sensors, 'Datalogger',
                              listElement2d='Message\nCounter')
    def recieve_Inverterx(self, json_Inverter):

        #Inverter VR
        self.set_lineEdit("lineEdit_AMK_Control_VR", json_Inverter, 'VR', listElement2d='AMK_Control[b]')
        self.set_lineEdit("lineEdit_Drehzahlsollwert_VR", json_Inverter, 'VR',
                          listElement2d='Drehzahlsollwert[1/min]')
        self.set_lineEdit("lineEdit_Momentsollwert_VR", json_Inverter, 'VR', listElement2d='Momentsollwert[Nm]')
        self.set_lineEdit("lineEdit_Momentsollwert_VR", json_Inverter, 'VR', listElement2d='Momentsollwert[Nm]')
        self.set_btn_LED("btn_LED_System_bereit_VR", json_Inverter, 'VR', listElement2d='System bereit')
        self.set_btn_LED("btn_LED_Warnung_VR", json_Inverter, 'VR', listElement2d='Warnung')
        self.set_btn_LED("btn_LED_Fehler_VR", json_Inverter, 'VR', listElement2d='Fehler')
        self.set_btn_LED("btn_LED_Derating_VR", json_Inverter, 'VR', listElement2d='Derating')
        self.set_btn_LED("btn_LED_Spiegel_HV_VR", json_Inverter, 'VR', listElement2d='Spiegel HV')
        self.set_btn_LED("btn_LED_Quit_HV_VR", json_Inverter, 'VR', listElement2d='Quit HV')
        self.set_btn_LED("btn_LED_Spiegel_Regelerfeigabe_VR", json_Inverter, 'VR',
                         listElement2d='Spiegel Regelerfeigabe')
        self.set_btn_LED("btn_LED_Quit_Reglerfreigabe_VR", json_Inverter, 'VR',
                         listElement2d='Quit Reglerfreigabe')
        self.set_lineEdit("lineEdit_Drehzahlistwert_VR", json_Inverter, 'VR',
                          listElement2d='Drehzahlistwert[U/min]')
        self.set_lineEdit("lineEdit_Momentistwert_VR", json_Inverter, 'VR', listElement2d='Momentistwert[Nm]')
        self.set_lineEdit("lineEdit_Drehzahlistwert_VR", json_Inverter, 'VR',
                          listElement2d='Drehzahlistwert[U/min]')
        self.set_lineEdit("lineEdit_Momentistwert_VR", json_Inverter, 'VR', listElement2d='Momentistwert[Nm]')
        self.set_lineEdit("lineEdit_Diagnosenummer_VR", json_Inverter, 'VR', listElement2d='Diagnosenummer')
        self.set_lineEdit("lineEdit_Motortemp_VR", json_Inverter, 'VR', listElement2d='Motortemp[C]')
        self.set_lineEdit("lineEdit_Kuehlplattentemp_VR", json_Inverter, 'VR',
                          listElement2d='Khlplattentemp[C]')
        self.set_lineEdit("lineEdit_IGBTtemp_VR", json_Inverter, 'VR', listElement2d='IGBTtemp[C]')
        self.set_lineEdit("lineEdit_I_q_VR", json_Inverter, 'VR', listElement2d='I_q[A]')
        self.set_lineEdit("lineEdit_I_d_VR", json_Inverter, 'VR', listElement2d='I_d[A]')
        self.set_lineEdit("lineEdit_Wirkleistung_VR", json_Inverter, 'VR', listElement2d='Wirkleistung [kW]')
        self.set_lineEdit("lineEdit_Blindleistung_VR", json_Inverter, 'VR', listElement2d='Blindleistung [kvar]')
        self.set_lineEdit("lineEdit_Fehlerzusatznr_1_VR", json_Inverter, 'VR', listElement2d='Fehlerzusatznr. 1')
        self.set_lineEdit("lineEdit_Fehlerzusatznr_2_VR", json_Inverter, 'VR', listElement2d='Fehlerzusatznr. 2')
        self.set_lineEdit("lineEdit_Fehlerzusatznr_3_VR", json_Inverter, 'VR', listElement2d='Fehlerzusatznr. 3')

        # Inverter VL
        self.set_lineEdit("lineEdit_AMK_Control_VL", json_Inverter, 'VL', listElement2d='AMK_Control[b]')
        self.set_lineEdit("lineEdit_Drehzahlsollwert_VL", json_Inverter, 'VL',
                          listElement2d='Drehzahlsollwert[1/min]')
        self.set_lineEdit("lineEdit_Momentsollwert_VL", json_Inverter, 'VL', listElement2d='Momentsollwert[Nm]')
        self.set_lineEdit("lineEdit_Momentsollwert_VL", json_Inverter, 'VL', listElement2d='Momentsollwert[Nm]')
        self.set_btn_LED("btn_LED_System_bereit_VL", json_Inverter, 'VL', listElement2d='System bereit')
        self.set_btn_LED("btn_LED_Warnung_VL", json_Inverter, 'VL', listElement2d='Warnung')
        self.set_btn_LED("btn_LED_Fehler_VL", json_Inverter, 'VL', listElement2d='Fehler')
        self.set_btn_LED("btn_LED_Derating_VL", json_Inverter, 'VL', listElement2d='Derating')
        self.set_btn_LED("btn_LED_Spiegel_HV_VL", json_Inverter, 'VL', listElement2d='Spiegel HV')
        self.set_btn_LED("btn_LED_Quit_HV_VL", json_Inverter, 'VL', listElement2d='Quit HV')
        self.set_btn_LED("btn_LED_Spiegel_Regelerfeigabe_VL", json_Inverter, 'VL',
                         listElement2d='Spiegel Regelerfeigabe')
        self.set_btn_LED("btn_LED_Quit_Reglerfreigabe_VL", json_Inverter, 'VL',
                         listElement2d='Quit Reglerfreigabe')
        self.set_lineEdit("lineEdit_Drehzahlistwert_VL", json_Inverter, 'VL',
                          listElement2d='Drehzahlistwert[U/min]')
        self.set_lineEdit("lineEdit_Momentistwert_VL", json_Inverter, 'VL', listElement2d='Momentistwert[Nm]')
        self.set_lineEdit("lineEdit_Drehzahlistwert_VL", json_Inverter, 'VL',
                          listElement2d='Drehzahlistwert[U/min]')
        self.set_lineEdit("lineEdit_Momentistwert_VL", json_Inverter, 'VL', listElement2d='Momentistwert[Nm]')
        self.set_lineEdit("lineEdit_Diagnosenummer_VL", json_Inverter, 'VL', listElement2d='Diagnosenummer')
        self.set_lineEdit("lineEdit_Motortemp_VL", json_Inverter, 'VL', listElement2d='Motortemp[C]')
        self.set_lineEdit("lineEdit_Kuehlplattentemp_VL", json_Inverter, 'VL',
                          listElement2d='Khlplattentemp[C]')
        self.set_lineEdit("lineEdit_IGBTtemp_VL", json_Inverter, 'VL', listElement2d='IGBTtemp[C]')
        self.set_lineEdit("lineEdit_I_q_VL", json_Inverter, 'VL', listElement2d='I_q[A]')
        self.set_lineEdit("lineEdit_I_d_VL", json_Inverter, 'VL', listElement2d='I_d[A]')
        self.set_lineEdit("lineEdit_Wirkleistung_VL", json_Inverter, 'VL', listElement2d='Wirkleistung [kW]')
        self.set_lineEdit("lineEdit_Blindleistung_VL", json_Inverter, 'VL', listElement2d='Blindleistung [kvar]')
        self.set_lineEdit("lineEdit_Fehlerzusatznr_1_VL", json_Inverter, 'VL', listElement2d='Fehlerzusatznr. 1')
        self.set_lineEdit("lineEdit_Fehlerzusatznr_2_VL", json_Inverter, 'VL', listElement2d='Fehlerzusatznr. 2')
        self.set_lineEdit("lineEdit_Fehlerzusatznr_3_VL", json_Inverter, 'VL', listElement2d='Fehlerzusatznr. 3')

        #Inverter HR
        self.set_lineEdit("lineEdit_AMK_Control_HR", json_Inverter, 'HR', listElement2d='AMK_Control[b]')
        self.set_lineEdit("lineEdit_Drehzahlsollwert_HR", json_Inverter, 'HR',
                          listElement2d='Drehzahlsollwert[1/min]')
        self.set_lineEdit("lineEdit_Momentsollwert_HR", json_Inverter, 'HR', listElement2d='Momentsollwert[Nm]')
        self.set_lineEdit("lineEdit_Momentsollwert_HR", json_Inverter, 'HR', listElement2d='Momentsollwert[Nm]')
        self.set_btn_LED("btn_LED_System_bereit_HR", json_Inverter, 'HR', listElement2d='System bereit')
        self.set_btn_LED("btn_LED_Warnung_HR", json_Inverter, 'HR', listElement2d='Warnung')
        self.set_btn_LED("btn_LED_Fehler_HR", json_Inverter, 'HR', listElement2d='Fehler')
        self.set_btn_LED("btn_LED_Derating_HR", json_Inverter, 'HR', listElement2d='Derating')
        self.set_btn_LED("btn_LED_Spiegel_HV_HR", json_Inverter, 'HR', listElement2d='Spiegel HV')
        self.set_btn_LED("btn_LED_Quit_HV_HR", json_Inverter, 'HR', listElement2d='Quit HV')
        self.set_btn_LED("btn_LED_Spiegel_Regelerfeigabe_HR", json_Inverter, 'HR',
                         listElement2d='Spiegel Regelerfeigabe')
        self.set_btn_LED("btn_LED_Quit_Reglerfreigabe_HR", json_Inverter, 'HR',
                         listElement2d='Quit Reglerfreigabe')
        self.set_lineEdit("lineEdit_Drehzahlistwert_HR", json_Inverter, 'HR',
                          listElement2d='Drehzahlistwert[U/min]')
        self.set_lineEdit("lineEdit_Momentistwert_HR", json_Inverter, 'HR', listElement2d='Momentistwert[Nm]')
        self.set_lineEdit("lineEdit_Drehzahlistwert_HR", json_Inverter, 'HR',
                          listElement2d='Drehzahlistwert[U/min]')
        self.set_lineEdit("lineEdit_Momentistwert_HR", json_Inverter, 'HR', listElement2d='Momentistwert[Nm]')
        self.set_lineEdit("lineEdit_Diagnosenummer_HR", json_Inverter, 'HR', listElement2d='Diagnosenummer')
        self.set_lineEdit("lineEdit_Motortemp_HR", json_Inverter, 'HR', listElement2d='Motortemp[C]')
        self.set_lineEdit("lineEdit_Kuehlplattentemp_HR", json_Inverter, 'HR',
                          listElement2d='Khlplattentemp[C]')
        self.set_lineEdit("lineEdit_IGBTtemp_HR", json_Inverter, 'HR', listElement2d='IGBTtemp[C]')
        self.set_lineEdit("lineEdit_I_q_HR", json_Inverter, 'HR', listElement2d='I_q[A]')
        self.set_lineEdit("lineEdit_I_d_HR", json_Inverter, 'HR', listElement2d='I_d[A]')
        self.set_lineEdit("lineEdit_Wirkleistung_HR", json_Inverter, 'HR', listElement2d='Wirkleistung [kW]')
        self.set_lineEdit("lineEdit_Blindleistung_HR", json_Inverter, 'HR', listElement2d='Blindleistung [kvar]')
        self.set_lineEdit("lineEdit_Fehlerzusatznr_1_HR", json_Inverter, 'HR', listElement2d='Fehlerzusatznr. 1')
        self.set_lineEdit("lineEdit_Fehlerzusatznr_2_HR", json_Inverter, 'HR', listElement2d='Fehlerzusatznr. 2')
        self.set_lineEdit("lineEdit_Fehlerzusatznr_3_HR", json_Inverter, 'HR', listElement2d='Fehlerzusatznr. 3')

        # Inverter HL
        self.set_lineEdit("lineEdit_AMK_Control_HL", json_Inverter, 'HL', listElement2d='AMK_Control[b]')
        self.set_lineEdit("lineEdit_Drehzahlsollwert_HL", json_Inverter, 'HL',
                          listElement2d='Drehzahlsollwert[1/min]')
        self.set_lineEdit("lineEdit_Momentsollwert_HL", json_Inverter, 'HL', listElement2d='Momentsollwert[Nm]')
        self.set_lineEdit("lineEdit_Momentsollwert_HL", json_Inverter, 'HL', listElement2d='Momentsollwert[Nm]')
        self.set_btn_LED("btn_LED_System_bereit_HL", json_Inverter, 'HL', listElement2d='System bereit')
        self.set_btn_LED("btn_LED_Warnung_HL", json_Inverter, 'HL', listElement2d='Warnung')
        self.set_btn_LED("btn_LED_Fehler_HL", json_Inverter, 'HL', listElement2d='Fehler')
        self.set_btn_LED("btn_LED_Derating_HL", json_Inverter, 'HL', listElement2d='Derating')
        self.set_btn_LED("btn_LED_Spiegel_HV_HL", json_Inverter, 'HL', listElement2d='Spiegel HV')
        self.set_btn_LED("btn_LED_Quit_HV_HL", json_Inverter, 'HL', listElement2d='Quit HV')
        self.set_btn_LED("btn_LED_Spiegel_Regelerfeigabe_HL", json_Inverter, 'HL',
                         listElement2d='Spiegel Regelerfeigabe')
        self.set_btn_LED("btn_LED_Quit_Reglerfreigabe_HL", json_Inverter, 'HL',
                         listElement2d='Quit Reglerfreigabe')
        self.set_lineEdit("lineEdit_Drehzahlistwert_HL", json_Inverter, 'HL',
                          listElement2d='Drehzahlistwert[U/min]')
        self.set_lineEdit("lineEdit_Momentistwert_HL", json_Inverter, 'HL', listElement2d='Momentistwert[Nm]')
        self.set_lineEdit("lineEdit_Drehzahlistwert_HL", json_Inverter, 'HL',
                          listElement2d='Drehzahlistwert[U/min]')
        self.set_lineEdit("lineEdit_Momentistwert_HL", json_Inverter, 'HL', listElement2d='Momentistwert[Nm]')
        self.set_lineEdit("lineEdit_Diagnosenummer_HL", json_Inverter, 'HL', listElement2d='Diagnosenummer')
        self.set_lineEdit("lineEdit_Motortemp_HL", json_Inverter, 'HL', listElement2d='Motortemp[C]')
        self.set_lineEdit("lineEdit_Kuehlplattentemp_HL", json_Inverter, 'HL',
                          listElement2d='Khlplattentemp[C]')
        self.set_lineEdit("lineEdit_IGBTtemp_HL", json_Inverter, 'HL', listElement2d='IGBTtemp[C]')
        self.set_lineEdit("lineEdit_I_q_HL", json_Inverter, 'HL', listElement2d='I_q[A]')
        self.set_lineEdit("lineEdit_I_d_HL", json_Inverter, 'HL', listElement2d='I_d[A]')
        self.set_lineEdit("lineEdit_Wirkleistung_HL", json_Inverter, 'HL', listElement2d='Wirkleistung [kW]')
        self.set_lineEdit("lineEdit_Blindleistung_HL", json_Inverter, 'HL', listElement2d='Blindleistung [kvar]')
        self.set_lineEdit("lineEdit_Fehlerzusatznr_1_HL", json_Inverter, 'HL', listElement2d='Fehlerzusatznr. 1')
        self.set_lineEdit("lineEdit_Fehlerzusatznr_2_HL", json_Inverter, 'HL', listElement2d='Fehlerzusatznr. 2')
        self.set_lineEdit("lineEdit_Fehlerzusatznr_3_HL", json_Inverter, 'HL', listElement2d='Fehlerzusatznr. 3')

    def recieve_Errorsx(self, json_Errors):

        #Timeout CAN
        self.set_btn_LED("btn_LED_SSB_Front", json_Errors, 'Timeout CAN' ,listElement2d='SSB Front')
        self.set_btn_LED("btn_LED_BSE", json_Errors, 'Timeout CAN' ,listElement2d='BSE')
        self.set_btn_LED("btn_LED_SSB_Rear", json_Errors, 'Timeout CAN' ,listElement2d='SSB Rear')
        self.set_btn_LED("btn_LED_GPS_Front", json_Errors, 'Timeout CAN' ,listElement2d='GPS Front')
        self.set_btn_LED("btn_LED_9_Achs_ACC_Front", json_Errors, 'Timeout CAN' ,listElement2d='9-Achs_ACC Front')
        self.set_btn_LED("btn_LED_9_Achs_ROT_Front", json_Errors, 'Timeout CAN' ,listElement2d='9-Achs_ROT Front')
        self.set_btn_LED("btn_LED_9_Achs_MAG_Front", json_Errors, 'Timeout CAN' ,listElement2d='9-Achs_MAG Front')
        self.set_btn_LED("btn_LED_GPS_Rear", json_Errors, 'Timeout CAN' ,listElement2d='GPS Rear')
        self.set_btn_LED("btn_LED_9_Achs_ACC_Rear", json_Errors, 'Timeout CAN' ,listElement2d='9-Achs_ACC Rear')
        self.set_btn_LED("btn_LED_9_Achs_ROT_Rear", json_Errors, 'Timeout CAN' ,listElement2d='9-Achs_ROT Rear')
        self.set_btn_LED("btn_LED_9_Achs_MAG_Rear", json_Errors, 'Timeout CAN' ,listElement2d='9-Achs_MAG Rear')
        self.set_btn_LED("btn_LED_9_Achs_MAG_Rear", json_Errors, 'Timeout CAN' ,listElement2d='9-Achs_MAG Rear')
        self.set_btn_LED("btn_LED_AMS", json_Errors, 'Timeout CAN' ,listElement2d='AMS')
        self.set_btn_LED("btn_LED_Energymeter", json_Errors, 'Timeout CAN' ,listElement2d='Energymeter')
        self.set_btn_LED("btn_LED_PDU", json_Errors, 'Timeout CAN' ,listElement2d='PDU')
        self.set_btn_LED("btn_LED_DIS", json_Errors, 'Timeout CAN' ,listElement2d='DIS')
        self.set_btn_LED("btn_LED_DIS_Param", json_Errors, 'Timeout CAN' ,listElement2d='DIS_Param')
        self.set_btn_LED("btn_LED_Inverter_FR", json_Errors, 'Timeout CAN' ,listElement2d='Inverter FR')
        self.set_btn_LED("btn_LED_Inverter_FL", json_Errors, 'Timeout CAN' ,listElement2d='Inverter FL')
        self.set_btn_LED("btn_LED_Inverter_RR", json_Errors, 'Timeout CAN' ,listElement2d='Inverter RR')
        self.set_btn_LED("btn_LED_Inverter_RL", json_Errors, 'Timeout CAN' ,listElement2d='Inverter RL')

        # Wert
        self.set_btn_LED("btn_LED_Pedale_implausibel_Wert", json_Errors, 'Wert' ,
                         listElement2d='Pedale implausibel')
        self.set_btn_LED("btn_LED_APPS_implausibel_Wert", json_Errors, 'Wert' ,listElement2d='APPS implausibel')
        self.set_btn_LED("btn_LED_APPS1_Wert", json_Errors, 'Wert' ,listElement2d='APPS1')
        self.set_btn_LED("btn_LED_APPS2_Wert", json_Errors, 'Wert' ,listElement2d='APPS2')
        self.set_btn_LED("btn_LED_Bremsdruck_vorne", json_Errors, 'Wert' ,listElement2d='Bremsdruck_vorne')
        self.set_btn_LED("btn_LED_Bremsdruck_hinten", json_Errors, 'Wert' ,listElement2d='Bremsdruck_hinten')
        self.set_btn_LED("btn_LED_Bremskraftsensor", json_Errors, 'Wert' ,listElement2d='Bremskraftsensor')
        self.set_btn_LED("btn_LED_Lenkwinkel", json_Errors, 'Wert' ,listElement2d='Lenkwinkel')
        self.set_btn_LED("btn_LED_ACC_X", json_Errors, 'Wert' ,listElement2d='ACC_X')
        self.set_btn_LED("btn_LED_ACC_Y", json_Errors, 'Wert' ,listElement2d='ACC_Y')
        self.set_btn_LED("btn_LED_ROT_Z", json_Errors, 'Wert' ,listElement2d='ROT_Z')
        self.set_btn_LED("btn_LED_V_GPS", json_Errors, 'Wert' ,listElement2d='V_GPS')
        self.set_btn_LED("btn_LED_Invertertemp_FrR", json_Errors, 'Wert' ,listElement2d='Invertertemp_FrR')
        self.set_btn_LED("btn_LED_Invertertemp_FrL", json_Errors, 'Wert' ,listElement2d='Invertertemp_FrL')
        self.set_btn_LED("btn_LED_Invertertemp_ReR", json_Errors, 'Wert' ,listElement2d='Invertertemp_ReR')
        self.set_btn_LED("btn_LED_Invertertemp_ReL", json_Errors, 'Wert' ,listElement2d='Invertertemp_ReL')
        self.set_btn_LED("btn_LED_Invertertemp_ReL", json_Errors, 'Wert' ,listElement2d='Invertertemp_ReL')

        # Latching
        self.set_btn_LED("btn_LED_Pedale_implausibel_Latching", json_Errors, 'Latching',
                         listElement2d='Pedale implausibel')
        self.set_btn_LED("btn_LED_APPS_implausibel_Latching", json_Errors, 'Latching', listElement2d='APPS implausibel')
        self.set_btn_LED("btn_LED_APPS1_Latching", json_Errors, 'Latching', listElement2d='APPS1')
        self.set_btn_LED("btn_LED_APPS2_Latching", json_Errors, 'Latching', listElement2d='APPS2')

    def recieve_Mathx(self, json_Math):

        #General
        self.set_lineEdit("lineEdit_desiredTorque", json_Math, 'General', listElement2d='desiredTorque[Nm]')
        self.set_lineEdit("lineEdit_Gaspedal", json_Math, 'General', listElement2d='Gaspedal[%/100]')
        self.set_lineEdit("lineEdit_Rekupedal", json_Math, 'General', listElement2d='Rekupedal[%/100]')
        self.set_lineEdit("lineEdit_Implausibilitaet_APPS", json_Math, 'General',
                          listElement2d='Implausibilitt\nAPPS[%]')
        self.set_lineEdit("lineEdit_Bremsbal", json_Math, 'General', listElement2d='Bremsbal[Fr/Total]')
        self.set_lineEdit("lineEdit_Accelbal", json_Math, 'General', listElement2d='Accelbal[Fr/Total]')
        self.set_lineEdit("lineEdit_allowedPower_General", json_Math, 'General', listElement2d='allowedPower[kW]')
        self.set_lineEdit("lineEdit_actualPower", json_Math, 'General', listElement2d='actualPower[kW]')
        self.set_btn_LED("btn_LED_Energiesparmodus_General", json_Math, 'General',
                         listElement2d='Energiesparmodus')
        self.set_lineEdit("lineEdit_Odometer_General", json_Math, 'General', listElement2d='Odometer')
        self.set_lineEdit("lineEdit_Wirkungsgrad", json_Math, 'General', listElement2d='Wirkungsgrad[%/100]')
        self.set_lineEdit("lineEdit_T_Control", json_Math, 'General', listElement2d='T_Control[us]')

        #TV/KF
        self.set_lineEdit("lineEdit_KF_Velocity", json_Math, 'TV/KF', listElement2d='KF_Velocity[km/h]')
        self.set_lineEdit("lineEdit_KF_ACC_X", json_Math, 'TV/KF', listElement2d='KF_ACC_X[m/s]')
        self.set_lineEdit("lineEdit_KF_slip_ist_FR", json_Math, 'TV/KF', listElement2d='KF_slip_ist_FR[%/100]')
        self.set_lineEdit("lineEdit_KF_slip_ist_FL", json_Math, 'TV/KF', listElement2d='KF_slip_ist_FL[%/100]')
        self.set_lineEdit("lineEdit_KF_slip_ist_RR", json_Math, 'TV/KF', listElement2d='KF_slip_ist_RR[%/100]')
        self.set_lineEdit("lineEdit_KF_slip_ist_RL", json_Math, 'TV/KF', listElement2d='KF_slip_ist_RL[%/100]')
        self.set_lineEdit("lineEdit_slip_soll_Fr", json_Math, 'TV/KF', listElement2d='slip_soll_Fr[%/100]')
        self.set_lineEdit("lineEdit_slip_soll_Re", json_Math, 'TV/KF', listElement2d='slip_soll_Re[%/100]')
        self.set_lineEdit("lineEdit_slip_soll_Re", json_Math, 'TV/KF', listElement2d='slip_soll_Re[%/100]')
        self.set_lineEdit("lineEdit_TV_Regler", json_Math, 'TV/KF', listElement2d='TV_Regler[Giermoment]')
        self.set_lineEdit("lineEdit_TV_Lenk", json_Math, 'TV/KF', listElement2d='TV_Lenk[Giermoment]')
        self.set_lineEdit("lineEdit_SOC_Soll_TV_KF", json_Math, 'TV/KF', listElement2d='SOC-Soll[%]')
        self.set_lineEdit("lineEdit_SOC_Ist_TV_KF", json_Math, 'TV/KF', listElement2d='SOC-Ist[%]')
        self.set_lineEdit("lineEdit_MomentSollVR", json_Math, 'TV/KF', listElement2d='MomentSollVR[Nm]')
        self.set_lineEdit("lineEdit_MomentSollVL", json_Math, 'TV/KF', listElement2d='MomentSollVL[Nm]')
        self.set_lineEdit("lineEdit_MomentSollHR", json_Math, 'TV/KF', listElement2d='MomentSollHR[Nm]')
        self.set_lineEdit("lineEdit_MomentSollHL", json_Math, 'TV/KF', listElement2d='MomentSollHL[Nm]')
        self.set_lineEdit("lineEdit_Reglerausgang_TV_KF", json_Math, 'TV/KF', listElement2d='Reglerausgang')

        #Energy Control
        self.set_lineEdit("lineEdit_allowedPower_Energy_Control", json_Math, 'Energy Control',
                          listElement2d='allowedPower[kW]')
        self.set_lineEdit("lineEdit_Rundenanzahl", json_Math, 'Energy Control', listElement2d='Rundenanzahl')
        self.set_lineEdit("lineEdit_SOC_Soll_Energy_Control", json_Math, 'Energy Control',
                          listElement2d='SOC-Soll[%]')
        self.set_lineEdit("lineEdit_SOC_Ist_Energy_Control", json_Math, 'Energy Control',
                          listElement2d='SOC-Ist[%]')
        self.set_lineEdit("lineEdit_SOC_Ist_Energy_Control", json_Math, 'Energy Control',
                          listElement2d='SOC-Ist[%]')
        self.set_lineEdit("lineEdit_Rundenlaenge", json_Math, 'Energy Control', listElement2d='Rundenlnge[m]')
        self.set_lineEdit("lineEdit_Reglerausgang_Energy_Control", json_Math, 'Energy Control',
                          listElement2d='Reglerausgang')
        self.set_lineEdit("lineEdit_Toleranz_Rundenlaenge", json_Math, 'Energy Control',
                          listElement2d='Toleranz Rundenlnge [%/100]')
        self.set_lineEdit("lineEdit_Strecke", json_Math, 'Energy Control', listElement2d='Strecke')
        self.set_lineEdit("lineEdit_Start_SOC", json_Math, 'Energy Control', listElement2d='Start-SOC[%]')
        self.set_lineEdit("lineEdit_Ziel_SOC", json_Math, 'Energy Control', listElement2d='Ziel-SOC[%]')
        self.set_lineEdit("lineEdit_Energie_Akku", json_Math, 'Energy Control', listElement2d='Energie Akku[kWh]')
        self.set_lineEdit("lineEdit_Maximalleistung", json_Math, 'Energy Control',
                          listElement2d='Maximalleistung[kW]')
        self.set_lineEdit("lineEdit_Start_Leistungsgrenze", json_Math, 'Energy Control',
                          listElement2d='Start-Leistungsgrenze')

    def recieve_Controlsx(self, json_Controls):

        #Switches
        self.set_btn_LED("btn_LED_1A_1_RTDS", json_Controls, 'Switches', listElement2d='1A 1 RTDS')
        self.set_btn_LED("btn_LED_1A_2_Brakelight", json_Controls, 'Switches', listElement2d='1A 2 Brakelight')
        self.set_btn_LED("btn_LED_1A_3_Switches", json_Controls, 'Switches', listElement2d='1A 3')
        self.set_btn_LED("btn_LED_1A_4_Switches", json_Controls, 'Switches', listElement2d='1A 4')
        self.set_btn_LED("btn_LED_6A_1_Motor_Fans", json_Controls, 'Switches', listElement2d='6A 1 Motor Fans')
        self.set_btn_LED("btn_LED_6A_2_DRS", json_Controls, 'Switches', listElement2d='6A 2 DRS')
        self.set_btn_LED("btn_LED_6A_3_SC", json_Controls, 'Switches', listElement2d='6A 3 SC')
        self.set_btn_LED("btn_LED_6A_4_Vectorbox", json_Controls, 'Switches', listElement2d='6A 4 Vectorbox')
        self.set_btn_LED("btn_LED_6A_5_Motor_Pump", json_Controls, 'Switches', listElement2d='6A 5 Motor Pump')
        self.set_btn_LED("btn_LED_6A_6_Switches", json_Controls, 'Switches', listElement2d='6A 6')
        self.set_btn_LED("btn_LED_12A_1_Inv_Fans_Fr", json_Controls, 'Switches',
                         listElement2d='12A 1 Inv Fans Fr')
        self.set_btn_LED("btn_LED_12A_2_Inv_Fans_Re", json_Controls, 'Switches',
                         listElement2d='12A 2 Inv Fans Re')

        # Controls
        self.set_lineEdit("lineEdit_Vehicle_State", json_Controls, 'Vehicle State')
        self.set_lineEdit("lineEdit_DRS_Position", json_Controls, 'DRS Position[%/100]')
        self.set_lineEdit("lineEdit_Fan_Motor", json_Controls, 'Fan Motor[%/100]')
        self.set_lineEdit("lineEdit_Fan_Akku", json_Controls, 'Fan Akku[%/100]')
        self.set_btn_LED("btn_LED_HV_Freigabe", json_Controls, 'HV Freigabe')
        self.set_btn_LED("btn_LED_IC_Voltage_OK", json_Controls, 'IC Voltage OK')

    def recieve_FPGA_Errorx(self, json_FPGA_Error):

        self.set_lineEdit("lineEdit_Input_Error_Code", json_FPGA_Error, 'Input Error Code')
        self.set_lineEdit("lineEdit_Output_Error_Code", json_FPGA_Error, 'Output Error Code')
        self.set_lineEdit("lineEdit_Transmit_Error_Counter", json_FPGA_Error, 'Transmit Error Counter')
        self.set_lineEdit("lineEdit_Error_Counter", json_FPGA_Error, 'Error Counter')

    def set_lineEdit(self, name_lineEdit, dataList, listElement, listElement2d = 'empty', listElement3d = 'empty', indexes = 0):
        if(listElement2d == "empty"):
            #self.dictBool(dataList, listElement, 'Cluster', listElement)
            self.searchElement(dataList.get('Cluster', 'None').values(), listElement, dataList.get('Cluster', 'None'))
            if (self.elementName == listElement):
                self.signal_set_Text.emit((name_lineEdit, self.elementValue))
                #name_lineEdit.setText(self.elementValue)
        elif(listElement3d == "empty"):
            self.searchElementLevel2(dataList.get('Cluster', 'None').values(), listElement2d, listElement,dataList.get('Cluster', 'None'))
            if (self.elementName == listElement2d):
                self.signal_set_Text.emit((name_lineEdit, self.elementValue))
                #name_lineEdit.setText(self.elementValue)
        else:
            pass
            self.searchElementLevel3(dataList.get('Cluster', 'None').values(), listElement3d, listElement2d, listElement, dataList.get('Cluster', 'None'))
            if (self.elementName == listElement3d):
                self.signal_set_Text.emit((name_lineEdit, self.elementValue))
                #name_lineEdit.setText(self.elementValue)




    def set_btn_LED(self, name_btn_LED, dataList, listElement, listElement2d = 'empty', listElement3d = 'empty'):
        if(listElement2d=="empty"):
            self.searchElement(dataList.get('Cluster', 'None').values(), listElement, dataList.get('Cluster', 'None'))
            if(self.elementName == listElement):
                self.signal_set_LED.emit((name_btn_LED, self.elementValue))
                # if (self.elementValue == "0"):
                #     name_btn_LED.setStyleSheet('border: none; border-radius: 10px; background-color: red')
                # elif (self.elementValue == "1"):
                #     name_btn_LED.setStyleSheet(
                #         'border: none; border-radius: 10px; background-color: rgb(38, 255, 0);')
                # else:
                #     name_btn_LED.setStyleSheet(
                #         'border: none; border-radius: 10px; background-color: rgb(100, 100, 100);')
        elif (listElement3d == "empty"):
            self.searchElementLevel2(dataList.get('Cluster', 'None').values(), listElement2d, listElement, dataList.get('Cluster', 'None'))
            if (self.elementName == listElement2d):
                self.signal_set_LED.emit((name_btn_LED, self.elementValue))
                # if (self.elementValue == "0"):
                #     name_btn_LED.setStyleSheet('border: none; border-radius: 10px; background-color: red')
                # elif (self.elementValue == "1"):
                #     name_btn_LED.setStyleSheet(
                #         'border: none; border-radius: 10px; background-color: rgb(38, 255, 0);')
                # else:
                #     name_btn_LED.setStyleSheet(
                #         'border: none; border-radius: 10px; background-color: rgb(100, 100, 100);')
        else:
            self.searchElementLevel3(dataList.get('Cluster', 'None').values(), listElement3d, listElement2d, listElement, dataList.get('Cluster', 'None'))
            if (self.elementName == listElement3d):
                self.signal_set_LED.emit((name_btn_LED, self.elementValue))
                # if (self.elementValue == "0"):
                #     name_btn_LED.setStyleSheet('border: none; border-radius: 10px; background-color: red')
                # elif (self.elementValue == "1"):
                #     name_btn_LED.setStyleSheet(
                #         'border: none; border-radius: 10px; background-color: rgb(38, 255, 0);')
                # else:
                #     name_btn_LED.setStyleSheet(
                #         'border: none; border-radius: 10px; background-color: rgb(100, 100, 100);')

    def searchElement(self, listofElements, wantedElement, oldElement):
        for element in listofElements:
            if (isinstance(element, OrderedDict)):
                if(element.get('Name') == wantedElement and element.get('Val') != 'None'):
                    self.elementName = element.get('Name')
                    # print("----------------------------------------------------------")
                    if(element.get('Choice')):
                        self.elementValue = element.get('Choice')[int(element.get('Val'))]
                        self.elementChoiceElements = element.get('Choice')
                        self.elementDatatype = "EB"
                        self.clusterName = self.XML_dict_element_1
                    else:
                        self.elementChoiceElements = "None"
                        self.elementValue = element.get('Val')
                else:
                    self.searchElement(element.values(), wantedElement, listofElements)
            if(isinstance(element, list)):
                self.searchElement(element, wantedElement, listofElements)

    def searchElementLevel2(self, listofElements, wantedElement, elementLevelbefore, oldElement, level=0):
        for element in listofElements:
            if (isinstance(element, OrderedDict)):
                if(element.get('Name') == elementLevelbefore and level == 0):
                    if (isinstance(element, OrderedDict)):
                        self.searchElementLevel2(element.values(), wantedElement, elementLevelbefore, listofElements, level=2)
                    elif (isinstance(element, list)):
                        self.searchElementLevel2(element, wantedElement, elementLevelbefore, listofElements, level=2)
                elif(element.get('Name') == wantedElement and element.get('Val') != 'None' and level == 2):
                    self.elementName = element.get('Name')
                    if(element.get('Choice')):
                        self.elementValue = element.get('Choice')[int(element.get('Val'))]
                    else:
                        self.elementValue = element.get('Val')
                else:
                    self.searchElementLevel2(element.values(), wantedElement, elementLevelbefore, listofElements, level=level)
            elif(isinstance(element, list)):
                self.searchElementLevel2(element, wantedElement, elementLevelbefore, listofElements, level=level)

    def searchElementLevel3(self, listofElements, wantedElement, elementLevelbefore, elementLevelbeforebefore, oldElement, level=0):
        for element in listofElements:
            if (isinstance(element, OrderedDict)):
                if (element.get('Name') == elementLevelbeforebefore and level == 0):
                    if (isinstance(element, OrderedDict)):
                        self.searchElementLevel3(element.values(), wantedElement, elementLevelbefore, elementLevelbeforebefore, listofElements,
                                                 level=2)
                    elif (isinstance(element, list)):
                        self.searchElementLevel3(element, wantedElement, elementLevelbefore, elementLevelbeforebefore, listofElements, level=2)
                if (element.get('Name') == elementLevelbefore and level == 2):
                    #print("Level 2")
                    if (isinstance(element, OrderedDict)):
                        self.searchElementLevel3(element.values(), wantedElement, elementLevelbefore, elementLevelbeforebefore, listofElements,
                                                 level=3)
                    elif (isinstance(element, list)):
                        self.searchElementLevel3(element, wantedElement, elementLevelbefore, elementLevelbeforebefore, listofElements, level=3)
                elif (element.get('Name') == wantedElement and element.get('Val') != 'None' and level == 3):
                    self.elementName = element.get('Name')
                    if (element.get('Choice')):
                        self.elementValue = element.get('Choice')[int(element.get('Val'))]
                    else:
                        self.elementValue = element.get('Val')
                else:
                    self.searchElementLevel3(element.values(), wantedElement, elementLevelbefore, elementLevelbeforebefore, listofElements, level=level)
            elif (isinstance(element, list)):
                self.searchElementLevel3(element, wantedElement, elementLevelbefore, elementLevelbeforebefore, listofElements, level=level)







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

        self.thread = QThread()
        self.worker = WorkerUDP()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.signal_Sensors_set = pyqtSignal(dict)
        #Signals for XML
        #self.worker.signal_Config_Values.connect(lambda json_config: self.recieve_Config_Values(json_config), Qt.QueuedConnection)
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
        self.worker.signal_Sensors_update.connect(
            lambda json_Sensors: self.recieve_Sensorsx(json_Sensors))

        #Signals for JSON
        self.worker.signal_Sensors_json.connect(
            lambda json_Sensors_dict: self.set_Sensors_json_dict(json_Sensors_dict))
        self.worker.signal_Inverter_json.connect(
            lambda json_Inverter_dict: self.set_Inverter_json_dict(json_Inverter_dict))


        #Signals for setting GUI
        self.worker.signal_set_Text.connect(lambda dataTuple: self.set_Text(dataTuple))
        self.worker.signal_set_LED.connect(lambda dataTuple: self.set_LED(dataTuple))

        self.thread.start()


        self.serialCounter = 0
        self.config_list = []
        self.config_i = 0
        self.XML_sensors_list = []
        self.sensors_list_index = 0
        self.sensors_i = 0
        self.elementName = "None"
        self.elementValue = "None"
        self.elementChoiceElements = "None"
        self.elementDatatype = "None"

        self.json_inverter_dict_counter = 0
        self.json_inverter_dict = []

        #json iteration
        self.json_sensor_dict = []
        self.json_sensor_dict_counter = 0
        self.json_sensor_dict_element_1 = "None"
        self.json_sensor_dict_element_2 = "None"
        self.json_sensor_dict_element_3 = "None"
        self.searchXMLLevel = 0
        self.XMLElementFound = False
        self.XML_dict_element_1 = "None"
        self.XML_dict_element_2 = "None"
        self.XML_dict_element_3 = "None"
        self.XMLElement = None
        self.cluster2 = False
        self.clusterName2 = "None"
        self.clusterName1 = "None"
        self.val = 0

    def set_Text(self, dataTuple):
        getattr(self.ui, dataTuple[0]).setText(dataTuple[1])

    def set_LED(self, dataTuple):
        if (dataTuple[1] == "0"):
            getattr(self.ui, dataTuple[0]).setStyleSheet('border: none; border-radius: 10px; background-color: red')
        elif (dataTuple[1] == "1"):
            getattr(self.ui, dataTuple[0]).setStyleSheet(
                'border: none; border-radius: 10px; background-color: rgb(38, 255, 0);')
        else:
            getattr(self.ui, dataTuple[0]).setStyleSheet(
                'border: none; border-radius: 10px; background-color: rgb(100, 100, 100);')

    def set_Sensors_json_dict(self, json_Sensors_dict):
        #print("Json Sensonrs type" ,type(json_Sensors_dict))
        if(self.json_sensor_dict_counter < 1):
            #print(self.json_sensor_dict_counter)
            self.json_sensor_dict = json_Sensors_dict
            self.json_sensor_dict_counter = self.json_sensor_dict_counter + 1
            #print(self.json_sensor_dict_counter)

    def set_Inverter_json_dict(self, json_Inverter_dict):
        if (self.json_inverter_dict_counter < 1):
            self.json_inverter_dict = json_Inverter_dict
            self.json_inverter_dict_counter = self.json_inverter_dict_counter + 1

        #self.jsonIteration(json_Sensors_dict, 0, serialElements)

    def jsonIteration(self, jsonDict, iteration_level, serialElements):
        self.val = 0
        iteration_level = iteration_level + 1
        for key in jsonDict:
            if(isinstance(jsonDict[key], dict)):
                if(iteration_level == 1):
                    self.json_sensor_dict_element_1 = key
                elif(iteration_level == 2):
                    self.json_sensor_dict_element_2 = key
                elif (iteration_level == 3):
                    self.json_sensor_dict_element_3 = key
                self.jsonIteration(jsonDict[key], iteration_level, serialElements)
            elif (isinstance(jsonDict[key], list)):
                self.jsonIteration(jsonDict[key], iteration_level, serialElements)
            else:
                if(self.json_sensor_dict_element_2 == "None" and self.sensors_i > 0):
                    self.searchXMLLevel = 0
                    self.XMLElementFound = False
                    self.elementDatatype = "None"
                    strdataType = str(self.searchXMLdatatype(self.XML_sensors_list, key)) #for checking the datatype
                    if(self.elementChoiceElements != "None"):
                        #print("Choice L1:", key, self.elementChoiceElements[serialElements[self.serialCounter]])
                        self.val = self.elementChoiceElements[serialElements[self.serialCounter]]
                        self.serialCounter = self.serialCounter + 1
                    elif (self.elementDatatype == "U32"):  # is checking the datatype for serial datastream
                        # intValue = serialElements[self.serialCounter] * 256 + serialElements[self.serialCounter + 1]
                        #print("U32 L2:", key)
                        self.val = key
                        self.serialCounter = self.serialCounter + 4
                    elif(self.elementDatatype == "U16"):  #is checking the datatype for serial datastream
                        intValue = serialElements[self.serialCounter] * 256 + serialElements[self.serialCounter+1]
                        #print("U16 L1:", key, intValue)
                        self.val = intValue
                        self.serialCounter = self.serialCounter + 2
                    elif(self.elementDatatype == "U8"):  # is checking the datatype for serial datastream
                        #print("U8 L1:", key, serialElements[self.serialCounter])
                        self.val = serialElements[self.serialCounter]
                        self.serialCounter = self.serialCounter + 1
                    elif (self.elementDatatype == "I8"):  # is checking the datatype for serial datastream
                        #print("I8 L1:", key, serialElements[self.serialCounter])
                        self.val = serialElements[self.serialCounter]
                        self.serialCounter = self.serialCounter + 1
                    elif(self.elementDatatype == "Boolean"):
                        #print("Boolean L1:", key, serialElements[self.serialCounter])
                        self.val = serialElements[self.serialCounter]
                        self.serialCounter = self.serialCounter + 1
                    elif (self.elementDatatype == "DBL"):
                        value = self.serial_to_float(serialElements[self.serialCounter],
                                                   serialElements[self.serialCounter + 1],
                                                   serialElements[self.serialCounter + 2],
                                                   serialElements[self.serialCounter + 3])
                        #print("DBL L1:", key, value)
                        self.val = value
                        self.serialCounter = self.serialCounter + 8
                    elif(self.elementDatatype == "SGL"):
                        value = self.serial_to_float(serialElements[self.serialCounter],
                                                     serialElements[self.serialCounter + 1],
                                                     serialElements[self.serialCounter + 2],
                                                     serialElements[self.serialCounter + 3])
                        #print("SGL L1:", key, value)
                        self.val = value
                        self.serialCounter = self.serialCounter + 4
                    elif (self.elementDatatype == "EB"):
                        print(self.XMLElement)
                        self.serialCounter = self.serialCounter + 1
                    elif(strdataType == "<class 'float'>"):  # is checking the datatype for serial datastream
                        print("Aus recieve_Sensors_serial L1:", key,
                              self.serial_to_float(serialElements[self.serialCounter],
                                                   serialElements[self.serialCounter + 1],
                                                   serialElements[self.serialCounter + 2],
                                                   serialElements[self.serialCounter + 3]))
                        self.serialCounter = self.serialCounter + 4
                    else:
                        #print("Ungeklärter Datentyp L1:",key)
                        self.serialCounter = self.serialCounter + 1
                elif(self.json_sensor_dict_element_3 == "None" and self.sensors_i > 0):
                    #print("3:", key, self.json_sensor_dict_element_1, self.json_sensor_dict_element_2)
                    self.searchXMLLevel = 0
                    self.XMLElementFound = False
                    self.elementDatatype = "None"
                    strdataType = str(self.searchXMLdatatype(self.XML_sensors_list, key, self.json_sensor_dict_element_2))  # for checking the datatype
                    if(self.XMLElementFound):
                        #print("Datentyp:",self.elementDatatype, self.XMLElementFound)
                        if (self.elementChoiceElements != "None"):
                            #print("Choice L2:", key, self.elementChoiceElements[serialElements[self.serialCounter]])
                            self.val = self.elementChoiceElements[serialElements[self.serialCounter]]
                            self.serialCounter = self.serialCounter + 1
                        elif (self.elementDatatype == "U32"):  # is checking the datatype for serial datastream
                            #intValue = serialElements[self.serialCounter] * 256 + serialElements[self.serialCounter + 1]
                            #print("U32 L2:", key)
                            self.val = key
                            self.serialCounter = self.serialCounter + 4
                        elif (self.elementDatatype == "U16"):  # is checking the datatype for serial datastream
                            intValue = serialElements[self.serialCounter] * 256 + serialElements[self.serialCounter + 1]
                            #print("U16 L2:", key, intValue)
                            self.val = intValue
                            self.serialCounter = self.serialCounter + 2
                        elif (self.elementDatatype == "U8"):  # is checking the datatype for serial datastream
                            #print("U8 L2:", key, serialElements[self.serialCounter])
                            self.val = serialElements[self.serialCounter]
                            self.serialCounter = self.serialCounter + 1
                        elif (self.elementDatatype == "I8"):  # is checking the datatype for serial datastream
                            #print("I8 L2:", key, serialElements[self.serialCounter])
                            self.val = serialElements[self.serialCounter]
                            self.serialCounter = self.serialCounter + 1
                        elif (self.elementDatatype == "Boolean"):
                            #print("Boolean L2:", key, serialElements[self.serialCounter])
                            self.val = serialElements[self.serialCounter]
                            self.serialCounter = self.serialCounter + 1
                        elif (self.elementDatatype == "DBL"):
                            value = self.serial_to_float(serialElements[self.serialCounter],
                                                       serialElements[self.serialCounter + 1],
                                                       serialElements[self.serialCounter + 2],
                                                       serialElements[self.serialCounter + 3])
                            #print("DBL L2:", key, value)
                            self.val = value
                            self.serialCounter = self.serialCounter + 8
                        elif (self.elementDatatype == "SGL"):
                            value = self.serial_to_float(serialElements[self.serialCounter],
                                                         serialElements[self.serialCounter + 1],
                                                         serialElements[self.serialCounter + 2],
                                                         serialElements[self.serialCounter + 3])
                            #print("SGL L2:", key, value)
                            self.val = value
                            self.serialCounter = self.serialCounter + 4
                        elif (self.elementDatatype == "EB"):
                            print(self.XMLElement)
                            self.serialCounter = self.serialCounter + 1
                        elif (strdataType == "<class 'float'>"):  # is checking the datatype for serial datastream
                            print("Aus recieve_Sensors_serial:", key,
                                  self.serial_to_float(serialElements[self.serialCounter],
                                                       serialElements[self.serialCounter + 1],
                                                       serialElements[self.serialCounter + 2],
                                                       serialElements[self.serialCounter + 3]))
                            self.serialCounter = self.serialCounter + 4
                        else:
                            print("Ungeklärter Datentyp:", key)
                            self.serialCounter = self.serialCounter + 1
                #print("XMLElement:", self.XMLElement)
                #print("XML List", self.XML_sensors_list)
                #print("XML:", self.XML_sensors_list.get("Cluster"))
            if(self.elementDatatype == "EB"):
                pass
                #print(self.XMLElement)

            self.XMLElement["Val"] = "1"#str(self.val) #"-3.00000"

        iteration_level = iteration_level - 1
        if (iteration_level == 1):
            self.json_sensor_dict_element_1 = "None"
        elif (iteration_level == 2):
            self.json_sensor_dict_element_2 = "None"
        elif (iteration_level == 3):
            self.json_sensor_dict_element_3 = "None"


    def searchXMLdatatype(self, dataList, listElement, listElement2d = 'empty', listElement3d = 'empty', indexes = 0):
        ElementXMLCompare = listElement.replace("°", "")
        ElementXMLCompare = ElementXMLCompare.replace("²", "")
        ElementXMLCompare2d = listElement2d.replace("°", "")
        ElementXMLCompare2d = ElementXMLCompare2d.replace("²", "")
        ElementXMLCompare3d = listElement3d.replace("°", "")
        ElementXMLCompare3d = ElementXMLCompare3d.replace("²", "")
        if (ElementXMLCompare[0] == " "):
            ElementXMLCompare = ElementXMLCompare[1:]
        if (ElementXMLCompare[len(ElementXMLCompare) - 1] == " "):
            ElementXMLCompare = ElementXMLCompare[:len(ElementXMLCompare) - 1]
        if(listElement2d == "empty"):
            #self.dictBool(dataList, listElement, 'Cluster', listElement)
            self.searchElementandDatatype(dataList.get('Cluster', 'None').values(), ElementXMLCompare)
            #print("N:",self.elementName,":",len(self.elementName), self.elementName.encode())
            #print(dataList)
            #print(self.elementName == ElementXMLCompare)
            if (self.elementName == ElementXMLCompare):
                datatype = type(0)#type(self.elementValue)
                #print(listElement + ": " + self.elementValue)
                if(isinstance(self.elementValue, str)):
                    #print(self.elementValue, self.elementValue.find('.'))
                    # print(ElementXMLCompare)
                    # print(self.elementName, self.elementValue)
                    if(self.elementValue.find('.') != -1 and any(chr.isdigit() for chr in (self.elementValue))):
                        datatype = type(0.0)
                    elif(self.elementValue == "0"):
                        datatype = type(0)
                    else:
                        datatype = type(0)

                return datatype
            else:
                print(self.elementName, listElement, ElementXMLCompare, listElement[0],ElementXMLCompare[0])
        elif(listElement3d == "empty"):
            #print("EL:", listElement, listElement2d, listElement3d)
            self.searchElementandDatatype(dataList.get('Cluster', 'None').values(), ElementXMLCompare, wantedElement2 = ElementXMLCompare2d)
        # elif(listElement3d == "empty"):
        #     self.searchElementLevel2(dataList.get('Cluster', 'None').values(), listElement2d, listElement,dataList.get('Cluster', 'None'))
        #     if (self.elementName == listElement2d):
        #         datatype = type(self.elementValue)
        #         return type(0)
        # else:
        #     self.searchElementLevel3(dataList.get('Cluster', 'None').values(), listElement3d, listElement2d, listElement, dataList.get('Cluster', 'None'))
        #     if (self.elementName == listElement3d):
        #         datatype = type(self.elementValue)
        #         return type(0)
        #
    # def searchXMLdatatypeLevel2(self, dataList, listElement, listElement2d = 'empty', listElement3d = 'empty', level = 0, indexes = 0):
    #     if(listElement2d == "empty" and level == 0):
    #         #self.dictBool(dataList, listElement, 'Cluster', listElement)
    #         ElementXMLCompare = listElement.replace("°", "")
    #         ElementXMLCompare = ElementXMLCompare.replace("²", "")
    #         ElementXMLCompare2d = listElement2d.replace("°", "")
    #         ElementXMLCompare2d = ElementXMLCompare2d.replace("²", "")
    #         ElementXMLCompare3d = listElement3d.replace("°", "")
    #         ElementXMLCompare3d = ElementXMLCompare3d.replace("²", "")
    #         if(ElementXMLCompare2d[0] == " "):
    #             ElementXMLCompare2d = ElementXMLCompare2d[1:]
    #         if (ElementXMLCompare2d[len(ElementXMLCompare2d)-1] == " "):
    #             ElementXMLCompare2d = ElementXMLCompare2d[:len(ElementXMLCompare2d)-1]
    #         self.searchElementandDatatype(dataList.get('Cluster', 'None').values(), ElementXMLCompare2d)
    #         #print("N:",self.elementName,":",len(self.elementName), self.elementName.encode())
    #         #print(dataList)
    #         #print(self.elementName == ElementXMLCompare)
    #         if (self.elementName == ElementXMLCompare):
    #             datatype = type(0)#type(self.elementValue)
    #             #print(listElement + ": " + self.elementValue)
    #             if(isinstance(self.elementValue, str)):
    #                 #print(self.elementValue, self.elementValue.find('.'))
    #                 # print(ElementXMLCompare)
    #                 # print(self.elementName, self.elementValue)
    #                 if(self.elementValue.find('.') != -1 and any(chr.isdigit() for chr in (self.elementValue))):
    #                     datatype = type(0.0)
    #                 elif(self.elementValue == "0"):
    #                     datatype = type(0)
    #                 else:
    #                     datatype = type(0)
    #
    #             return datatype
    #         else:
    #             print(self.elementName, listElement, ElementXMLCompare, listElement[0],ElementXMLCompare[0])
    #     elif(listElement3d == "empty"):
    #         self.searchElementLevel2(dataList.get('Cluster', 'None').values(), listElement2d, listElement,dataList.get('Cluster', 'None'))
    #         if (self.elementName == listElement2d):
    #             datatype = type(self.elementValue)
    #             return type(0)
    #     else:
    #         self.searchElementLevel3(dataList.get('Cluster', 'None').values(), listElement3d, listElement2d, listElement, dataList.get('Cluster', 'None'))
    #         if (self.elementName == listElement3d):
    #             datatype = type(self.elementValue)
    #             return type(0)

    def set_config_list(self, json_config_init):
        if(self.config_i < 1):
            self.config_list = json_config_init
            self.config_i = self.config_i + 1

    def set_Sensors_list(self, json_sensors_init):
        if (self.sensors_i < 1):
            self.XML_sensors_list = json_sensors_init
            self.sensors_i = self.sensors_i + 1
#        #print("Index: ", self.sensors_list_index)
        #if (self.sensors_list_index == 0):
     #   self.sensors_list = json_sensors_init
        #else:
        #    self.sensors_list_index = self.sensors_list_index + 1


    #def set_lineEdit(self, name_lineEdit, dataList, listElement, listElement2d = 'empty', listElement3d = 'empty'):
    #    if (listElement2d == 'empty'):
    #        if (listElement in dataList):
    #            name_lineEdit.setText(str(dataList[listElement]))
    #        else:
    #            name_lineEdit.setText('Element not in the Cluster')
    #    elif(listElement3d == 'empty'):
    #        if (listElement2d in dataList[listElement]):
    #            name_lineEdit.setText(str(dataList[listElement][listElement2d]))
    #        else:
    #            name_lineEdit.setText('Element not in the Cluster')
    #    else:
    #        if (listElement3d in dataList[listElement][listElement2d]):
    #            name_lineEdit.setText(str(dataList[listElement][listElement2d][listElement3d]))
    #        else:
    #            name_lineEdit.setText('Element not in the Cluster')
    def searchDatatypeElement(self, datatypeElement, wantedElement, dataType, level = 0, wantedElement2 = None, wantedElement3 = None): #Hier weiter machen
        if(isinstance(datatypeElement, list)):
            for datatypeElements in datatypeElement:                    #if (self.searchXMLLevel == 1):
                    #print("datatypeElements:", wantedElement, type(datatypeElements), datatypeElements.get("Name"))
                self.searchDatatypeElement(datatypeElements, wantedElement, dataType, level = level, wantedElement2 = wantedElement2)
        elif (isinstance(datatypeElement, OrderedDict)):
            # print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            # print(wantedElement, datatypeElement.get('Name'), self.json_sensor_dict_element_1, self.XML_dict_element_1)
            if(wantedElement == datatypeElement.get('Name') and self.json_sensor_dict_element_1 == self.XML_dict_element_1): # and self.json_sensor_dict_element_2 == self.XML_dict_element_2):
                self.elementDatatype = dataType
                self.XMLElementFound = True
                self.XMLElement = datatypeElement
                self.clusterName2 = wantedElement2
                self.clusterName = self.XML_dict_element_1
                # datatypeElement['Val'] = 400
                # print("SSSS:",datatypeElement.get('Name'), datatypeElement.get('Val'))
                # print(self.XML_sensors_list)
                # print("YYYY:", self.clusterName)
                # print("XXYY:", wantedElement2)
                # if (level == 1):
                # self.XML_dict_element_2 = element.get("Name")
                # self.clusterName = element.get("Name")

                #print("DataType:", dataType, wantedElement)
            # elif (isinstance(datatypeElement.get('Name'), list)):
            #     for datatypeElements in datatypeElement:
            #         self.searchDatatypeElement(datatypeElements, wantedElement, dataType)
            #     print("öööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööö")


    def searchElementandDatatype(self, listofElements, wantedElement, wantedElement2 = None, wantedElement3 = None):
        for element in listofElements:
            if(wantedElement2 == None or self.searchXMLLevel == 1):
                if(isinstance(element, OrderedDict)):
                    if(wantedElement2 == None):
                        self.XML_dict_element_1 = element.get("Name")
                        #self.searchXMLLevel = 0
                    #print("RRRR:", element.get("Name"))
                    DBLElement = element.get('DBL')
                    SGLElement = element.get('SGL')
                    boolElement = element.get('Boolean')
                    U8Element = element.get('U8')
                    U16Element = element.get('U16')
                    U32Element = element.get('U32')
                    I8Element = element.get('I8')
                    EBElement = element.get('EB')
                    #if (self.searchXMLLevel == 1):
                        #print("22222222222", element)

                    if(boolElement != None and self.elementDatatype == "None"):
                        self.searchDatatypeElement(boolElement, wantedElement, "Boolean", self.searchXMLLevel, wantedElement2 = element.get("Name"))
                    if(DBLElement != None and self.elementDatatype == "None"):
                        self.searchDatatypeElement(DBLElement, wantedElement, "DBL", self.searchXMLLevel, wantedElement2 = element.get("Name"))
                    if(SGLElement != None and self.elementDatatype == "None"):
                        #if (self.searchXMLLevel == 1):
                            #print("111111", wantedElement, type(SGLElement), SGLElement)
                        self.searchDatatypeElement(SGLElement, wantedElement, "SGL", self.searchXMLLevel, wantedElement2 = element.get("Name"))
                    if(U8Element != None and self.elementDatatype == "None"):
                        self.searchDatatypeElement(U8Element, wantedElement, "U8", self.searchXMLLevel, wantedElement2 = element.get("Name"))
                    if(U16Element != None and self.elementDatatype == "None"):
                        self.searchDatatypeElement(U16Element, wantedElement, "U16", self.searchXMLLevel, wantedElement2 = element.get("Name"))
                    if(U32Element != None and self.elementDatatype == "None"):
                        self.searchDatatypeElement(U32Element, wantedElement, "U32", self.searchXMLLevel, wantedElement2 = element.get("Name"))
                    if(I8Element != None and self.elementDatatype == "None"):
                        self.searchDatatypeElement(I8Element, wantedElement, "I8", self.searchXMLLevel, wantedElement2 = element.get("Name"))
                    if(EBElement != None and self.elementDatatype == "None"):
                        pass
                        #print("####", EBElement)

                    if(element.get('Name') == wantedElement and element.get('Val') != 'None'):
                        self.elementName = element.get('Name')
                        if(element.get('Choice')):
                            self.elementValue = element.get('Choice')[int(element.get('Val'))]
                            self.elementChoiceElements = element.get('Choice')
                            self.elementDatatype = "EB"
                        else:
                            self.elementChoiceElements = "None"
                            self.elementValue = element.get('Val')
                    else:
                        self.searchElement(element.values(), wantedElement, listofElements)
                elif(isinstance(element, list)):
                    self.searchElementandDatatype(element, wantedElement)
            elif(wantedElement2 != None):
                for element in listofElements:
                    #print("Element and wanted Element2:", wantedElement2)
                    if(isinstance(element, OrderedDict)):
                        if(element.get("Name") == self.json_sensor_dict_element_1):
                            self.XML_dict_element_1 = element.get("Name")
                            self.searchXMLLevel = 1
                            #print("XXXXX:", element)
                            self.cluster2 = True
                            #self.clusterName = (element.get("Cluster")).get("Name")
                            self.searchElementandDatatype(element.get("Cluster"), wantedElement, wantedElement2 = wantedElement2)
                            #print("-------", element.get("Cluster"))
                        # elif(element.get("Name") == self.json_sensor_dict_element_2):
                        #     self.searchXMLLevel = 2
                        #     print("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
                        #print("Dict Element:", element.get("Name"), wantedElement2 ,self.json_sensor_dict_element_1, self.json_sensor_dict_element_2)
                    elif(isinstance(element, list)):
                        #print("List Element:", element)
                        self.searchElementandDatatype(element, wantedElement, wantedElement2 = wantedElement2)
                        #self.searchElementandDatatype(element, wantedElement)

        self.searchXMLLevel = 0

    def searchElement(self, listofElements, wantedElement, oldElement):
        for element in listofElements:
            if (isinstance(element, OrderedDict)):
                if(element.get('Name') == wantedElement and element.get('Val') != 'None'):
                    self.elementName = element.get('Name')
                    # print("----------------------------------------------------------")
                    if(element.get('Choice')):
                        self.elementValue = element.get('Choice')[int(element.get('Val'))]
                        self.elementChoiceElements = element.get('Choice')
                        self.elementDatatype = "EB"
                        self.clusterName = self.XML_dict_element_1
                    else:
                        self.elementChoiceElements = "None"
                        self.elementValue = element.get('Val')
                else:
                    self.searchElement(element.values(), wantedElement, listofElements)
            if(isinstance(element, list)):
                self.searchElement(element, wantedElement, listofElements)

    def searchElementLevel2(self, listofElements, wantedElement, elementLevelbefore, oldElement, level=0):
        for element in listofElements:
            if (isinstance(element, OrderedDict)):
                if(element.get('Name') == elementLevelbefore and level == 0):
                    if (isinstance(element, OrderedDict)):
                        self.searchElementLevel2(element.values(), wantedElement, elementLevelbefore, listofElements, level=2)
                    elif (isinstance(element, list)):
                        self.searchElementLevel2(element, wantedElement, elementLevelbefore, listofElements, level=2)
                elif(element.get('Name') == wantedElement and element.get('Val') != 'None' and level == 2):
                    self.elementName = element.get('Name')
                    if(element.get('Choice')):
                        self.elementValue = element.get('Choice')[int(element.get('Val'))]
                    else:
                        self.elementValue = element.get('Val')
                else:
                    self.searchElementLevel2(element.values(), wantedElement, elementLevelbefore, listofElements, level=level)
            elif(isinstance(element, list)):
                self.searchElementLevel2(element, wantedElement, elementLevelbefore, listofElements, level=level)

    def searchElementLevel3(self, listofElements, wantedElement, elementLevelbefore, elementLevelbeforebefore, oldElement, level=0):
        for element in listofElements:
            if (isinstance(element, OrderedDict)):
                if (element.get('Name') == elementLevelbeforebefore and level == 0):
                    if (isinstance(element, OrderedDict)):
                        self.searchElementLevel3(element.values(), wantedElement, elementLevelbefore, elementLevelbeforebefore, listofElements,
                                                 level=2)
                    elif (isinstance(element, list)):
                        self.searchElementLevel3(element, wantedElement, elementLevelbefore, elementLevelbeforebefore, listofElements, level=2)
                if (element.get('Name') == elementLevelbefore and level == 2):
                    #print("Level 2")
                    if (isinstance(element, OrderedDict)):
                        self.searchElementLevel3(element.values(), wantedElement, elementLevelbefore, elementLevelbeforebefore, listofElements,
                                                 level=3)
                    elif (isinstance(element, list)):
                        self.searchElementLevel3(element, wantedElement, elementLevelbefore, elementLevelbeforebefore, listofElements, level=3)
                elif (element.get('Name') == wantedElement and element.get('Val') != 'None' and level == 3):
                    self.elementName = element.get('Name')
                    if (element.get('Choice')):
                        self.elementValue = element.get('Choice')[int(element.get('Val'))]
                    else:
                        self.elementValue = element.get('Val')
                else:
                    self.searchElementLevel3(element.values(), wantedElement, elementLevelbefore, elementLevelbeforebefore, listofElements, level=level)
            elif (isinstance(element, list)):
                self.searchElementLevel3(element, wantedElement, elementLevelbefore, elementLevelbeforebefore, listofElements, level=level)


    def set_lineEdit(self, name_lineEdit, dataList, listElement, listElement2d = 'empty', listElement3d = 'empty', indexes = 0):
        if(listElement2d == "empty"):
            #self.dictBool(dataList, listElement, 'Cluster', listElement)
            self.searchElement(dataList.get('Cluster', 'None').values(), listElement, dataList.get('Cluster', 'None'))
            if (self.elementName == listElement):
                name_lineEdit.setText(self.elementValue)
        elif(listElement3d == "empty"):
            self.searchElementLevel2(dataList.get('Cluster', 'None').values(), listElement2d, listElement,dataList.get('Cluster', 'None'))
            if (self.elementName == listElement2d):
                name_lineEdit.setText(self.elementValue)
        else:
            pass
            self.searchElementLevel3(dataList.get('Cluster', 'None').values(), listElement3d, listElement2d, listElement, dataList.get('Cluster', 'None'))
            if (self.elementName == listElement3d):
                name_lineEdit.setText(self.elementValue)




    def set_btn_LED(self, name_btn_LED, dataList, listElement, listElement2d = 'empty', listElement3d = 'empty'):
        if(listElement2d=="empty"):
            self.searchElement(dataList.get('Cluster', 'None').values(), listElement, dataList.get('Cluster', 'None'))
            if(self.elementName == listElement):
                if (self.elementValue == "0"):
                    name_btn_LED.setStyleSheet('border: none; border-radius: 10px; background-color: red')
                elif (self.elementValue == "1"):
                    name_btn_LED.setStyleSheet(
                        'border: none; border-radius: 10px; background-color: rgb(38, 255, 0);')
                else:
                    name_btn_LED.setStyleSheet(
                        'border: none; border-radius: 10px; background-color: rgb(100, 100, 100);')
        elif (listElement3d == "empty"):
            self.searchElementLevel2(dataList.get('Cluster', 'None').values(), listElement2d, listElement, dataList.get('Cluster', 'None'))
            if (self.elementName == listElement2d):
                if (self.elementValue == "0"):
                    name_btn_LED.setStyleSheet('border: none; border-radius: 10px; background-color: red')
                elif (self.elementValue == "1"):
                    name_btn_LED.setStyleSheet(
                        'border: none; border-radius: 10px; background-color: rgb(38, 255, 0);')
                else:
                    name_btn_LED.setStyleSheet(
                        'border: none; border-radius: 10px; background-color: rgb(100, 100, 100);')
        else:
            self.searchElementLevel3(dataList.get('Cluster', 'None').values(), listElement3d, listElement2d, listElement, dataList.get('Cluster', 'None'))
            if (self.elementName == listElement3d):
                if (self.elementValue == "0"):
                    name_btn_LED.setStyleSheet('border: none; border-radius: 10px; background-color: red')
                elif (self.elementValue == "1"):
                    name_btn_LED.setStyleSheet(
                        'border: none; border-radius: 10px; background-color: rgb(38, 255, 0);')
                else:
                    name_btn_LED.setStyleSheet(
                        'border: none; border-radius: 10px; background-color: rgb(100, 100, 100);')


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
        mantisse = 1 + int(value[9]) * 2 ** (-1) + int(value[10]) * 2 ** (-2) + int(value[11]) * 2 ** (-3) + \
                  int(value[12]) * 2 ** (-4) + int(value[13]) * 2 ** (-5) + int(value[14]) * 2 ** (-6) + \
                  int(value[15]) * 2 ** (-7) + int(value[16]) * 2 ** (-8) + int(value[17]) * 2 ** (-9) + \
                  int(value[18]) * 2 ** (-10) + int(value[19]) * 2 ** (-11) + int(value[20]) * 2 ** (-12) + \
                  int(value[21]) * 2 ** (-13) + int(value[22]) * 2 ** (-14) + int(value[23]) * 2 ** (-15) + \
                  int(value[24]) * 2 ** (-16) + int(value[25]) * 2 ** (-17) + int(value[26]) * 2 ** (-18) + \
                  int(value[27]) * 2 ** (-19) + int(value[28]) * 2 ** (-20) + int(value[29]) * 2 ** (-21) + \
                  int(value[30]) * 2 ** (-22) + int(value[31]) * 2 ** (-23)
        exp_int = int(exp, 2) - 127
        if(exp_int <= -127):
            exp_int = 0
            mantisse = 0
        #print("Mantisse:", mantisse)
        #print("Exponent:", exp_int)
        value_float = float((2 ** exp_int) * mantisse)
        if (value[0] == '1'):
            value_float = -value_float
        return value_float


    def recieve_Config_Values_serial(self, config_serial):
            pass


    def writeSerialElement(self, wantedElement, listofElements, serialElements):
        for element in listofElements:
            if (isinstance(element, OrderedDict)):
                if (element.get('Name') and element.get('Val')):
                    if (element.get('Choice')):
                        #print("Choice:", element.get('Choice')[int(element.get('Val'))])
                        self.serialCounter = self.serialCounter + 1
                    elif((element.get('Val')).find('.') != -1 and any(chr.isdigit() for chr in (element.get('Val')))): #check if it contains number and . => double
                        #print("Aus recieve_Sensors_serial:",
                            #self.serial_to_float(serialElements[self.serialCounter], serialElements[self.serialCounter+1], serialElements[self.serialCounter+2],
                                               #serialElements[self.serialCounter+3]))
                        self.serialCounter = self.serialCounter + 4
                        #print("double:", element.get('Val'))
                    elif (isinstance(element, OrderedDict)):
                        self.writeSerialElement(wantedElement, element.values(), serialElements)
                elif (element.get('Choice')):
                    pass
                    #print("Choice:", element.get('Choice')[int(element.get('Val'))])
                else:
                    self.writeSerialElement(wantedElement, element.values(), serialElements)
            if (isinstance(element, list)):
                self.writeSerialElement(wantedElement, element, serialElements)


    def recieve_Sensors_serial(self, Sensors_serial):
        if(self.sensors_i > 0):
            #print(self.sensors_list)
            self.serialCounter = 4  #Counter for counting bytes in recieved serial data
            #self.writeSerialElement(self.sensors_list ,self.sensors_list.get('Cluster', 'None').values(), Sensors_serial)   #Function for writing new values from serial data in to the xml-framework
            if(self.json_sensor_dict_counter > 0 and self.sensors_i > 0):
                self.jsonIteration( self.json_sensor_dict, 0, Sensors_serial)
    #    print("Aus recieve_Sensors_serial:" ,self.serial_to_float(Sensors_serial[4], Sensors_serial[5], Sensors_serial[6], Sensors_serial[7]))
        #print("Sensors_serial: ", Sensors_serial)
    #    print("Aus recieve_Sensors_serial:" ,self.serial_to_float(Sensors_serial[4], Sensors_serial[5], Sensors_serial[6], Sensors_serial[7]))
        #print("Aus recieve_Sensors_serial config_list", self.config_list.get('Cluster', 'None').values())




    def recieve_Config_Values(self, json_config):
        self.set_lineEdit(self.ui.lineEdit_Vehicle_Mode, json_config, 'Vehicle Mode')
        self.set_lineEdit(self.ui.lineEdit_APPS1_min, json_config, 'APPS1_min[]')
        self.set_lineEdit(self.ui.lineEdit_APPS1_max, json_config, 'APPS1_max[]')
        self.set_lineEdit(self.ui.lineEdit_APPS2_min, json_config, 'APPS2_min[]')
        self.set_lineEdit(self.ui.lineEdit_APPS2_max, json_config, 'APPS2_max[]')
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


        #print(str(json_config))

    def recieve_Sensors(self, json_Sensors):
        self.set_lineEdit(self.ui.lineEdit_APPS1, json_Sensors, 'Analog', listElement2d='APPS1[]')
        self.set_lineEdit(self.ui.lineEdit_APPS2, json_Sensors, 'Analog', listElement2d='APPS2[]')
        self.set_lineEdit(self.ui.lineEdit_Bremsdruck_vorne, json_Sensors, 'Analog', listElement2d='Bremsdruck vorne [bar]')
        self.set_lineEdit(self.ui.lineEdit_Bremsdruck_hinten, json_Sensors, 'Analog', listElement2d='Bremsdruck hinten [bar]')
        self.set_lineEdit(self.ui.lineEdit_Bremskraft, json_Sensors, 'Analog', listElement2d='Bremskraft[N]')
        self.set_lineEdit(self.ui.lineEdit_Lenkwinkel, json_Sensors, 'Analog', listElement2d='Lenkwinkel[]')
        self.set_lineEdit(self.ui.lineEdit_WT_Motor_high, json_Sensors, 'Analog', listElement2d='WT_Motor_high[C]')
        self.set_lineEdit(self.ui.lineEdit_WT_Motor_Low, json_Sensors, 'Analog', listElement2d='WT_Motor_Low[C]')
        self.set_lineEdit(self.ui.lineEdit_LT_Inv_FrR, json_Sensors, 'Analog', listElement2d='LT_Inv_FrR[C]')
        self.set_lineEdit(self.ui.lineEdit_LT_Inv_FrL, json_Sensors, 'Analog', listElement2d='LT_Inv_FrL[C]')
        self.set_lineEdit(self.ui.lineEdit_LT_Inv_ReR, json_Sensors, 'Analog', listElement2d='LT_Inv_ReR[C]')
        self.set_lineEdit(self.ui.lineEdit_LT_Inv_ReL, json_Sensors, 'Analog', listElement2d='LT_Inv_ReL[C]')
        self.set_lineEdit(self.ui.lineEdit_Ambient_Temp, json_Sensors, 'Analog', listElement2d='Ambient_Temp[C]')
        self.set_lineEdit(self.ui.lineEdit_ST_FR, json_Sensors, 'Analog', listElement2d='ST_FR[mm}')
        self.set_lineEdit(self.ui.lineEdit_ST_FL, json_Sensors, 'Analog', listElement2d='ST_FL[mm]')
        self.set_lineEdit(self.ui.lineEdit_ST_RR, json_Sensors, 'Analog', listElement2d='ST_RR[mm]')
        self.set_lineEdit(self.ui.lineEdit_ST_RL, json_Sensors, 'Analog', listElement2d='ST_RL[mm]')
        self.set_lineEdit(self.ui.lineEdit_Temp_Fusebox, json_Sensors, 'Analog', listElement2d='Temp_Fusebox [C]')

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
        self.set_lineEdit(self.ui.lineEdit_CTH, json_Sensors, 'Akku/HV', listElement2d='CTH[C]')
        self.set_lineEdit(self.ui.lineEdit_CTL, json_Sensors, 'Akku/HV', listElement2d='CTL[C]')
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
        self.set_lineEdit(self.ui.lineEdit_Course_GPS, json_Sensors, 'GPS/9-axis Front', listElement2d='Course_GPS[]')
        self.set_lineEdit(self.ui.lineEdit_Latitude, json_Sensors, 'GPS/9-axis Front', listElement2d='Latitude[]')
        self.set_lineEdit(self.ui.lineEdit_Longitude, json_Sensors, 'GPS/9-axis Front', listElement2d='Longitude[]')
        self.set_lineEdit(self.ui.lineEdit_HDOP, json_Sensors, 'GPS/9-axis Front', listElement2d='HDOP')
        self.set_lineEdit(self.ui.lineEdit_Quality_of_Fix, json_Sensors, 'GPS/9-axis Front',
                          listElement2d='Quality of Fix')
        self.set_lineEdit(self.ui.lineEdit_Satellites, json_Sensors, 'GPS/9-axis Front', listElement2d='Satellites')
        self.set_lineEdit(self.ui.lineEdit_Odometer, json_Sensors, 'GPS/9-axis Front', listElement2d='Odometer[km]')
        self.set_lineEdit(self.ui.lineEdit_ACC_X_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='ACC_X_Fr[m/s]')
        self.set_lineEdit(self.ui.lineEdit_ACC_Y_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='ACC_Y_Fr[m/s]')
        self.set_lineEdit(self.ui.lineEdit_ACC_Z_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='ACC_Z_Fr[m/s]')
        self.set_lineEdit(self.ui.lineEdit_ROT_X_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='ROT_X_Fr[/s]')
        self.set_lineEdit(self.ui.lineEdit_ROT_Y_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='ROT_Y_Fr[/s]')
        self.set_lineEdit(self.ui.lineEdit_ROT_Z_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='ROT_Z_Fr[/s]')
        self.set_lineEdit(self.ui.lineEdit_MAG_X_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='MAG_X_Fr[b]')
        self.set_lineEdit(self.ui.lineEdit_MAG_Y_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='MAG_Y_Fr[b]')
        self.set_lineEdit(self.ui.lineEdit_MAG_Z_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='MAG_Z_Fr[b]')
        self.set_lineEdit(self.ui.lineEdit_MAG_Z_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='MAG_Z_Fr[b]')

        self.set_lineEdit(self.ui.lineEdit_V_GPS_Rear, json_Sensors, 'GPS/9-axis Rear', listElement2d='V_GPS[km/h]')
        self.set_lineEdit(self.ui.lineEdit_Course_GPS_Rear, json_Sensors, 'GPS/9-axis Rear', listElement2d='Course_GPS[]')
        self.set_lineEdit(self.ui.lineEdit_Latitude_Rear, json_Sensors, 'GPS/9-axis Rear', listElement2d='Latitude[]')
        self.set_lineEdit(self.ui.lineEdit_Longitude_Rear, json_Sensors, 'GPS/9-axis Rear', listElement2d='Longitude[]')
        self.set_lineEdit(self.ui.lineEdit_HDOP_Rear, json_Sensors, 'GPS/9-axis Rear', listElement2d='HDOP')
        self.set_lineEdit(self.ui.lineEdit_Quality_of_Fix_Rear, json_Sensors, 'GPS/9-axis Rear',
                          listElement2d='Quality of Fix')
        self.set_lineEdit(self.ui.lineEdit_Satellites_Rear, json_Sensors, 'GPS/9-axis Front', listElement2d='Satellites')
        self.set_lineEdit(self.ui.lineEdit_Odometer_Rear, json_Sensors, 'GPS/9-axis Rear', listElement2d='Odometer[km]')
        self.set_lineEdit(self.ui.lineEdit_ACC_X_Re, json_Sensors, 'GPS/9-axis Rear', listElement2d='ACC_X_Re[m/s]')
        self.set_lineEdit(self.ui.lineEdit_ACC_Y_Re, json_Sensors, 'GPS/9-axis Rear', listElement2d='ACC_Y_Re[m/s]')
        self.set_lineEdit(self.ui.lineEdit_ACC_Z_Re, json_Sensors, 'GPS/9-axis Rear', listElement2d='ACC_Z_Re[m/s]')
        self.set_lineEdit(self.ui.lineEdit_ROT_X_Re, json_Sensors, 'GPS/9-axis Rear', listElement2d='ROT_X_Re[/s]')
        self.set_lineEdit(self.ui.lineEdit_ROT_Y_Re, json_Sensors, 'GPS/9-axis Rear', listElement2d='ROT_Y_Re[/s]')
        self.set_lineEdit(self.ui.lineEdit_ROT_Z_Re, json_Sensors, 'GPS/9-axis Rear', listElement2d='ROT_Z_Re[/s]')
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

        self.set_lineEdit(self.ui.lineEdit_Timestamp, json_Sensors, 'Kistler', listElement2d='Timestamp [4ms]')
        self.set_lineEdit(self.ui.lineEdit_IVI, json_Sensors, 'Kistler', listElement2d='IVI [10^-2 m/s]')
        self.set_lineEdit(self.ui.lineEdit_Weg, json_Sensors, 'Kistler', listElement2d='Weg [m]')
        self.set_lineEdit(self.ui.lineEdit_V_lon, json_Sensors, 'Kistler', listElement2d='V_lon [m/s]')
        self.set_lineEdit(self.ui.lineEdit_V_lat, json_Sensors, 'Kistler', listElement2d='V_lat [m/s]')
        self.set_lineEdit(self.ui.lineEdit_Winkel, json_Sensors, 'Kistler', listElement2d='Winkel []')
        self.set_lineEdit(self.ui.lineEdit_SerienNr, json_Sensors, 'Kistler', listElement2d='SerienNr')
        self.set_lineEdit(self.ui.lineEdit_SensorNr, json_Sensors, 'Kistler', listElement2d='SensorNr')
        self.set_lineEdit(self.ui.lineEdit_Temp, json_Sensors, 'Kistler', listElement2d='Temp [C]')
        self.set_lineEdit(self.ui.lineEdit_LED_Strom, json_Sensors, 'Kistler', listElement2d='LED Strom [0,01A]')
        self.set_lineEdit(self.ui.lineEdit_Statusbyte1, json_Sensors, 'Kistler', listElement2d='Statusbyte1')
        self.set_lineEdit(self.ui.lineEdit_Statusbyte2, json_Sensors, 'Kistler', listElement2d='Statusbyte2')

        self.set_lineEdit(self.ui.lineEdit_Status, json_Sensors, 'Datalogger', listElement2d='Status')
        self.set_lineEdit(self.ui.lineEdit_Voltage, json_Sensors, 'Datalogger', listElement2d='Voltage[V]')
        self.set_lineEdit(self.ui.lineEdit_Current, json_Sensors, 'Datalogger', listElement2d='Current[A]')
        self.set_lineEdit(self.ui.lineEdit_Power, json_Sensors, 'Datalogger', listElement2d='Power[kW]')
        self.set_lineEdit(self.ui.lineEdit_Message_Counter, json_Sensors, 'Datalogger',
                          listElement2d='Message\nCounter')

        #print(json_Sensors)

    def recieve_Sensorsx(self, json_Sensors):
        if(self.sensors_i > 0):
            #json_Sensors = self.XML_sensors_list
            self.set_lineEdit(self.ui.lineEdit_APPS1, json_Sensors, 'Analog', listElement2d='APPS1[]')
            self.set_lineEdit(self.ui.lineEdit_APPS2, json_Sensors, 'Analog', listElement2d='APPS2[]')
            self.set_lineEdit(self.ui.lineEdit_Bremsdruck_vorne, json_Sensors, 'Analog', listElement2d='Bremsdruck vorne [bar]')
            self.set_lineEdit(self.ui.lineEdit_Bremsdruck_hinten, json_Sensors, 'Analog', listElement2d='Bremsdruck hinten [bar]')
            self.set_lineEdit(self.ui.lineEdit_Bremskraft, json_Sensors, 'Analog', listElement2d='Bremskraft[N]')
            self.set_lineEdit(self.ui.lineEdit_Lenkwinkel, json_Sensors, 'Analog', listElement2d='Lenkwinkel[]')
            self.set_lineEdit(self.ui.lineEdit_WT_Motor_high, json_Sensors, 'Analog', listElement2d='WT_Motor_high[C]')
            self.set_lineEdit(self.ui.lineEdit_WT_Motor_Low, json_Sensors, 'Analog', listElement2d='WT_Motor_Low[C]')
            self.set_lineEdit(self.ui.lineEdit_LT_Inv_FrR, json_Sensors, 'Analog', listElement2d='LT_Inv_FrR[C]')
            self.set_lineEdit(self.ui.lineEdit_LT_Inv_FrL, json_Sensors, 'Analog', listElement2d='LT_Inv_FrL[C]')
            self.set_lineEdit(self.ui.lineEdit_LT_Inv_ReR, json_Sensors, 'Analog', listElement2d='LT_Inv_ReR[C]')
            self.set_lineEdit(self.ui.lineEdit_LT_Inv_ReL, json_Sensors, 'Analog', listElement2d='LT_Inv_ReL[C]')
            self.set_lineEdit(self.ui.lineEdit_Ambient_Temp, json_Sensors, 'Analog', listElement2d='Ambient_Temp[C]')
            self.set_lineEdit(self.ui.lineEdit_ST_FR, json_Sensors, 'Analog', listElement2d='ST_FR[mm}')
            self.set_lineEdit(self.ui.lineEdit_ST_FL, json_Sensors, 'Analog', listElement2d='ST_FL[mm]')
            self.set_lineEdit(self.ui.lineEdit_ST_RR, json_Sensors, 'Analog', listElement2d='ST_RR[mm]')
            self.set_lineEdit(self.ui.lineEdit_ST_RL, json_Sensors, 'Analog', listElement2d='ST_RL[mm]')
            self.set_lineEdit(self.ui.lineEdit_Temp_Fusebox, json_Sensors, 'Analog', listElement2d='Temp_Fusebox [C]')

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
            self.set_lineEdit(self.ui.lineEdit_CTH, json_Sensors, 'Akku/HV', listElement2d='CTH[C]')
            self.set_lineEdit(self.ui.lineEdit_CTL, json_Sensors, 'Akku/HV', listElement2d='CTL[C]')
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
            self.set_lineEdit(self.ui.lineEdit_Course_GPS, json_Sensors, 'GPS/9-axis Front', listElement2d='Course_GPS[]')
            self.set_lineEdit(self.ui.lineEdit_Latitude, json_Sensors, 'GPS/9-axis Front', listElement2d='Latitude[]')
            self.set_lineEdit(self.ui.lineEdit_Longitude, json_Sensors, 'GPS/9-axis Front', listElement2d='Longitude[]')
            self.set_lineEdit(self.ui.lineEdit_HDOP, json_Sensors, 'GPS/9-axis Front', listElement2d='HDOP')
            self.set_lineEdit(self.ui.lineEdit_Quality_of_Fix, json_Sensors, 'GPS/9-axis Front',
                              listElement2d='Quality of Fix')
            self.set_lineEdit(self.ui.lineEdit_Satellites, json_Sensors, 'GPS/9-axis Front', listElement2d='Satellites')
            self.set_lineEdit(self.ui.lineEdit_Odometer, json_Sensors, 'GPS/9-axis Front', listElement2d='Odometer[km]')
            self.set_lineEdit(self.ui.lineEdit_ACC_X_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='ACC_X_Fr[m/s]')
            self.set_lineEdit(self.ui.lineEdit_ACC_Y_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='ACC_Y_Fr[m/s]')
            self.set_lineEdit(self.ui.lineEdit_ACC_Z_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='ACC_Z_Fr[m/s]')
            self.set_lineEdit(self.ui.lineEdit_ROT_X_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='ROT_X_Fr[/s]')
            self.set_lineEdit(self.ui.lineEdit_ROT_Y_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='ROT_Y_Fr[/s]')
            self.set_lineEdit(self.ui.lineEdit_ROT_Z_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='ROT_Z_Fr[/s]')
            self.set_lineEdit(self.ui.lineEdit_MAG_X_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='MAG_X_Fr[b]')
            self.set_lineEdit(self.ui.lineEdit_MAG_Y_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='MAG_Y_Fr[b]')
            self.set_lineEdit(self.ui.lineEdit_MAG_Z_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='MAG_Z_Fr[b]')
            self.set_lineEdit(self.ui.lineEdit_MAG_Z_Fr, json_Sensors, 'GPS/9-axis Front', listElement2d='MAG_Z_Fr[b]')

            self.set_lineEdit(self.ui.lineEdit_V_GPS_Rear, json_Sensors, 'GPS/9-axis Rear', listElement2d='V_GPS[km/h]')
            self.set_lineEdit(self.ui.lineEdit_Course_GPS_Rear, json_Sensors, 'GPS/9-axis Rear', listElement2d='Course_GPS[]')
            self.set_lineEdit(self.ui.lineEdit_Latitude_Rear, json_Sensors, 'GPS/9-axis Rear', listElement2d='Latitude[]')
            self.set_lineEdit(self.ui.lineEdit_Longitude_Rear, json_Sensors, 'GPS/9-axis Rear', listElement2d='Longitude[]')
            self.set_lineEdit(self.ui.lineEdit_HDOP_Rear, json_Sensors, 'GPS/9-axis Rear', listElement2d='HDOP')
            self.set_lineEdit(self.ui.lineEdit_Quality_of_Fix_Rear, json_Sensors, 'GPS/9-axis Rear',
                              listElement2d='Quality of Fix')
            self.set_lineEdit(self.ui.lineEdit_Satellites_Rear, json_Sensors, 'GPS/9-axis Front', listElement2d='Satellites')
            self.set_lineEdit(self.ui.lineEdit_Odometer_Rear, json_Sensors, 'GPS/9-axis Rear', listElement2d='Odometer[km]')
            self.set_lineEdit(self.ui.lineEdit_ACC_X_Re, json_Sensors, 'GPS/9-axis Rear', listElement2d='ACC_X_Re[m/s]')
            self.set_lineEdit(self.ui.lineEdit_ACC_Y_Re, json_Sensors, 'GPS/9-axis Rear', listElement2d='ACC_Y_Re[m/s]')
            self.set_lineEdit(self.ui.lineEdit_ACC_Z_Re, json_Sensors, 'GPS/9-axis Rear', listElement2d='ACC_Z_Re[m/s]')
            self.set_lineEdit(self.ui.lineEdit_ROT_X_Re, json_Sensors, 'GPS/9-axis Rear', listElement2d='ROT_X_Re[/s]')
            self.set_lineEdit(self.ui.lineEdit_ROT_Y_Re, json_Sensors, 'GPS/9-axis Rear', listElement2d='ROT_Y_Re[/s]')
            self.set_lineEdit(self.ui.lineEdit_ROT_Z_Re, json_Sensors, 'GPS/9-axis Rear', listElement2d='ROT_Z_Re[/s]')
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

            self.set_lineEdit(self.ui.lineEdit_Timestamp, json_Sensors, 'Kistler', listElement2d='Timestamp [4ms]')
            self.set_lineEdit(self.ui.lineEdit_IVI, json_Sensors, 'Kistler', listElement2d='IVI [10^-2 m/s]')
            self.set_lineEdit(self.ui.lineEdit_Weg, json_Sensors, 'Kistler', listElement2d='Weg [m]')
            self.set_lineEdit(self.ui.lineEdit_V_lon, json_Sensors, 'Kistler', listElement2d='V_lon [m/s]')
            self.set_lineEdit(self.ui.lineEdit_V_lat, json_Sensors, 'Kistler', listElement2d='V_lat [m/s]')
            self.set_lineEdit(self.ui.lineEdit_Winkel, json_Sensors, 'Kistler', listElement2d='Winkel []')
            self.set_lineEdit(self.ui.lineEdit_SerienNr, json_Sensors, 'Kistler', listElement2d='SerienNr')
            self.set_lineEdit(self.ui.lineEdit_SensorNr, json_Sensors, 'Kistler', listElement2d='SensorNr')
            self.set_lineEdit(self.ui.lineEdit_Temp, json_Sensors, 'Kistler', listElement2d='Temp [C]')
            self.set_lineEdit(self.ui.lineEdit_LED_Strom, json_Sensors, 'Kistler', listElement2d='LED Strom [0,01A]')
            self.set_lineEdit(self.ui.lineEdit_Statusbyte1, json_Sensors, 'Kistler', listElement2d='Statusbyte1')
            self.set_lineEdit(self.ui.lineEdit_Statusbyte2, json_Sensors, 'Kistler', listElement2d='Statusbyte2')

            self.set_lineEdit(self.ui.lineEdit_Status, json_Sensors, 'Datalogger', listElement2d='Status')
            self.set_lineEdit(self.ui.lineEdit_Voltage, json_Sensors, 'Datalogger', listElement2d='Voltage[V]')
            self.set_lineEdit(self.ui.lineEdit_Current, json_Sensors, 'Datalogger', listElement2d='Current[A]')
            self.set_lineEdit(self.ui.lineEdit_Power, json_Sensors, 'Datalogger', listElement2d='Power[kW]')
            self.set_lineEdit(self.ui.lineEdit_Message_Counter, json_Sensors, 'Datalogger',
                              listElement2d='Message\nCounter')

            #print(json_Sensors)

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
        self.set_lineEdit(self.ui.lineEdit_Motortemp_VR, json_Inverter, 'VR', listElement2d='Motortemp[C]')
        self.set_lineEdit(self.ui.lineEdit_Kuehlplattentemp_VR, json_Inverter, 'VR',
                          listElement2d='Khlplattentemp[C]')
        self.set_lineEdit(self.ui.lineEdit_IGBTtemp_VR, json_Inverter, 'VR', listElement2d='IGBTtemp[C]')
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
        self.set_lineEdit(self.ui.lineEdit_Motortemp_VL, json_Inverter, 'VL', listElement2d='Motortemp[C]')
        self.set_lineEdit(self.ui.lineEdit_Kuehlplattentemp_VL, json_Inverter, 'VL',
                          listElement2d='Khlplattentemp[C]')
        self.set_lineEdit(self.ui.lineEdit_IGBTtemp_VL, json_Inverter, 'VL', listElement2d='IGBTtemp[C]')
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
        self.set_lineEdit(self.ui.lineEdit_Motortemp_HR, json_Inverter, 'HR', listElement2d='Motortemp[C]')
        self.set_lineEdit(self.ui.lineEdit_Kuehlplattentemp_HR, json_Inverter, 'HR',
                          listElement2d='Khlplattentemp[C]')
        self.set_lineEdit(self.ui.lineEdit_IGBTtemp_HR, json_Inverter, 'HR', listElement2d='IGBTtemp[C]')
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
        self.set_lineEdit(self.ui.lineEdit_Motortemp_HL, json_Inverter, 'HL', listElement2d='Motortemp[C]')
        self.set_lineEdit(self.ui.lineEdit_Kuehlplattentemp_HL, json_Inverter, 'HL',
                          listElement2d='Khlplattentemp[C]')
        self.set_lineEdit(self.ui.lineEdit_IGBTtemp_HL, json_Inverter, 'HL', listElement2d='IGBTtemp[C]')
        self.set_lineEdit(self.ui.lineEdit_I_q_HL, json_Inverter, 'HL', listElement2d='I_q[A]')
        self.set_lineEdit(self.ui.lineEdit_I_d_HL, json_Inverter, 'HL', listElement2d='I_d[A]')
        self.set_lineEdit(self.ui.lineEdit_Wirkleistung_HL, json_Inverter, 'HL', listElement2d='Wirkleistung [kW]')
        self.set_lineEdit(self.ui.lineEdit_Blindleistung_HL, json_Inverter, 'HL', listElement2d='Blindleistung [kvar]')
        self.set_lineEdit(self.ui.lineEdit_Fehlerzusatznr_1_HL, json_Inverter, 'HL', listElement2d='Fehlerzusatznr. 1')
        self.set_lineEdit(self.ui.lineEdit_Fehlerzusatznr_2_HL, json_Inverter, 'HL', listElement2d='Fehlerzusatznr. 2')
        self.set_lineEdit(self.ui.lineEdit_Fehlerzusatznr_3_HL, json_Inverter, 'HL', listElement2d='Fehlerzusatznr. 3')

        #print(str(json_Inverter))

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

        #print(str(json_Errors))


    def recieve_Math(self, json_Math):

        #General
        self.set_lineEdit(self.ui.lineEdit_desiredTorque, json_Math, 'General', listElement2d='desiredTorque[Nm]')
        self.set_lineEdit(self.ui.lineEdit_Gaspedal, json_Math, 'General', listElement2d='Gaspedal[%/100]')
        self.set_lineEdit(self.ui.lineEdit_Rekupedal, json_Math, 'General', listElement2d='Rekupedal[%/100]')
        self.set_lineEdit(self.ui.lineEdit_Implausibilitaet_APPS, json_Math, 'General',
                          listElement2d='Implausibilitt\nAPPS[%]')
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
        self.set_lineEdit(self.ui.lineEdit_KF_ACC_X, json_Math, 'TV/KF', listElement2d='KF_ACC_X[m/s]')
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
        self.set_lineEdit(self.ui.lineEdit_Rundenlaenge, json_Math, 'Energy Control', listElement2d='Rundenlnge[m]')
        self.set_lineEdit(self.ui.lineEdit_Reglerausgang_Energy_Control, json_Math, 'Energy Control',
                          listElement2d='Reglerausgang')
        self.set_lineEdit(self.ui.lineEdit_Toleranz_Rundenlaenge, json_Math, 'Energy Control',
                          listElement2d='Toleranz Rundenlnge [%/100]')
        self.set_lineEdit(self.ui.lineEdit_Strecke, json_Math, 'Energy Control', listElement2d='Strecke')
        self.set_lineEdit(self.ui.lineEdit_Start_SOC, json_Math, 'Energy Control', listElement2d='Start-SOC[%]')
        self.set_lineEdit(self.ui.lineEdit_Ziel_SOC, json_Math, 'Energy Control', listElement2d='Ziel-SOC[%]')
        self.set_lineEdit(self.ui.lineEdit_Energie_Akku, json_Math, 'Energy Control', listElement2d='Energie Akku[kWh]')
        self.set_lineEdit(self.ui.lineEdit_Maximalleistung, json_Math, 'Energy Control',
                          listElement2d='Maximalleistung[kW]')
        self.set_lineEdit(self.ui.lineEdit_Start_Leistungsgrenze, json_Math, 'Energy Control',
                          listElement2d='Start-Leistungsgrenze')

        #print(str(json_Math))

    def recieve_Controls(self, json_Controls):

        #Switches
        self.set_btn_LED(self.ui.btn_LED_1A_1_RTDS, json_Controls, 'Switches', listElement2d='1A 1 RTDS')
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
        self.set_btn_LED(self.ui.btn_LED_HV_Freigabe, json_Controls, 'HV Freigabe')
        self.set_btn_LED(self.ui.btn_LED_IC_Voltage_OK, json_Controls, 'IC Voltage OK')

        #print(str(json_Controls))

    def recieve_FPGA_Error(self, json_FPGA_Error):

        self.set_lineEdit(self.ui.lineEdit_Input_Error_Code, json_FPGA_Error, 'Input Error Code')
        self.set_lineEdit(self.ui.lineEdit_Output_Error_Code, json_FPGA_Error, 'Output Error Code')
        self.set_lineEdit(self.ui.lineEdit_Transmit_Error_Counter, json_FPGA_Error, 'Transmit Error Counter')
        self.set_lineEdit(self.ui.lineEdit_Error_Counter, json_FPGA_Error, 'Error Counter')

        #print(str(json_FPGA_Error))





    def recieve_Timestamp(self, json_Timestamp):

        self.set_lineEdit(self.ui.lineEdit_Timestamp_Timestamp, json_Timestamp, 'None', indexes = 3)

        #print(str(json_Timestamp))


    def show_page_config_values(self):
        self.ui.Pages.setCurrentWidget(self.ui.page_config_values)
        self.ui.btn_config_values.setStyleSheet('border: none; border-radius: 0px; background-color: rgb(171, 171, 171, 255);color: rgb(255, 255, 255)')
        self.ui.btn_sensors.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_inverter.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_errors.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_math.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_controls.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_fpga_error.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_timestamp.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')

    def show_page_sensors(self):
        self.ui.Pages.setCurrentWidget(self.ui.page_sensors)
        self.ui.btn_sensors.setStyleSheet(
            'border: none; border-radius: 0px; background-color: rgb(171, 171, 171, 255);color: rgb(255, 255, 255)')
        self.ui.btn_config_values.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_inverter.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_errors.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_math.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_controls.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_fpga_error.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_timestamp.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')

    def show_page_inverter(self):
        self.ui.Pages.setCurrentWidget(self.ui.page_inverter)
        self.ui.btn_inverter.setStyleSheet(
            'border: none; border-radius: 0px; background-color: rgb(171, 171, 171, 255);color: rgb(255, 255, 255)')
        self.ui.btn_sensors.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_config_values.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_errors.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_math.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_controls.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_fpga_error.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_timestamp.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')

    def show_page_errors(self):
        self.ui.Pages.setCurrentWidget(self.ui.page_errors)
        self.ui.btn_errors.setStyleSheet(
            'border: none; border-radius: 0px; background-color: rgb(171, 171, 171, 255);color: rgb(255, 255, 255)')
        self.ui.btn_sensors.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_inverter.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_config_values.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_math.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_controls.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_fpga_error.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_timestamp.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')

    def show_page_math(self):
        self.ui.Pages.setCurrentWidget(self.ui.page_math)
        self.ui.btn_math.setStyleSheet(
            'border: none; border-radius: 0px; background-color: rgb(171, 171, 171, 255);color: rgb(255, 255, 255)')
        self.ui.btn_sensors.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_inverter.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_errors.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_config_values.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_controls.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_fpga_error.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_timestamp.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')

    def show_page_controls(self):
        self.ui.Pages.setCurrentWidget(self.ui.page_controls)
        self.ui.btn_controls.setStyleSheet(
            'border: none; border-radius: 0px; background-color: rgb(171, 171, 171, 255);color: rgb(255, 255, 255)')
        self.ui.btn_sensors.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_inverter.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_errors.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_math.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_config_values.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_fpga_error.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_timestamp.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')

    def show_page_fpga_error(self):
        self.ui.Pages.setCurrentWidget(self.ui.page_fpga_error)
        self.ui.btn_fpga_error.setStyleSheet(
            'border: none; border-radius: 0px; background-color: rgb(171, 171, 171, 255);color: rgb(255, 255, 255)')
        self.ui.btn_sensors.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_inverter.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_errors.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_math.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_controls.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_config_values.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_timestamp.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')

    def show_page_timestamp(self):
        self.ui.Pages.setCurrentWidget(self.ui.page_timestamp)
        self.ui.btn_timestamp.setStyleSheet(
            'border: none; border-radius: 0px; background-color: rgb(171, 171, 171, 255);color: rgb(255, 255, 255)')
        self.ui.btn_sensors.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_inverter.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_errors.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_math.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_controls.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_fpga_error.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')
        self.ui.btn_config_values.setStyleSheet(
            'QPushButton {\nbackground-color: none;\nborder:  none;\ncolor: rgb(255, 255, 255);\n}\nQPushButton:hover {\nbackground-color: rgba(171, 171, 171, 255);\nborder:  none;\ncolor: rgb(255, 255, 255);\n}')



    def recieve(self):
        UDP_IP = "192.168.178.20"
        UDP_PORT = 3005

        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        sock.bind((UDP_IP, UDP_PORT))

        while True:
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            self.recvData = json.loads(data)
            #print(self.recvData)
            #print((self.recvData['Vehicle Mode']))
            self.ui.lineEdit_Vehicle_Mode.setText(self.recvData['Vehicle Mode'])
            self.ui.lineEdit_APPS1_max.setText(str(self.recvData['APPS1_max[]']))

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
        #print("sdfgdsg")


   # timer = QTimer()
   # timer.timeout.connect(lambda: (update_label(main_window)))
   # timer.start(1000)  # every 10,000 milliseconds

    sys.exit(app.exec_())
