from PyQt5.QtCore import QObject, QThread, pyqtSignal
import time
import socket
import json
import xmltodict
from typing import OrderedDict
import multiprocessing
from collections import OrderedDict
import struct

class WorkerUDP(QObject):
    def __init__(self, conn):
        multiprocessing.Process.__init__(self)
        super(WorkerUDP, self).__init__()
        self.conn = conn
        self.serialCounter = 4
        self.config_list = []
        self.config_i = 0
        self.XML_sensors_list = []
        self.XML_inverter_list = []
        self.XML_error_list = []
        self.XML_math_list = []
        self.XML_controls_list = []
        self.XML_fpga_error_list = []
        self.XML_timestamp_list = []
        self.sensors_i = 0

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
        self.jsonTimestamp_i = 0
        self.timestapmp_i = 0
        self.gotStructure = False
        self.recievingStructure = False

        self.json_sensor_dict = []

        self.json_config_dict = []
        self.json_inverter_dict = []
        self.json_errors_dict = []
        self.json_math_dict = []
        self.json_controls_dict = []
        self.json_fpga_error_dict = []
        self.json_timstamp_dict = []

        self.sleep = False

    signal_Config_Values = pyqtSignal(dict)
    signal_Sensors = pyqtSignal(dict)
    signal_Inverter = pyqtSignal(dict)
    signal_Errors = pyqtSignal(dict)
    signal_Math = pyqtSignal(dict)
    signal_Controls = pyqtSignal(dict)
    signal_FPGA_Error = pyqtSignal(dict)
    signal_Timestamp = pyqtSignal(dict)

    signal_Config_Values_json = pyqtSignal(dict)
    signal_Sensors_json = pyqtSignal(dict)
    signal_Inverter_json = pyqtSignal(dict)

    signal_Config_Values_serial = pyqtSignal(bytes)
    signal_Config_Values_init = pyqtSignal(dict)
    signal_Sensors_serial = pyqtSignal(bytes)
    signal_Sensors_init = pyqtSignal(dict)
    signal_Sensors_update = pyqtSignal(dict)

    signal_set_Text = pyqtSignal(tuple)
    signal_set_LED = pyqtSignal(tuple)

    def serial_to_float(self, byte1, byte2, byte3, byte4):
        return struct.unpack('>f', bytearray([byte1, byte2, byte3, byte4]))[0] # value_float

    def serial_to_float_64(self, byte1, byte2, byte3, byte4, byte5, byte6, byte7, byte8):
        return struct.unpack('>d', bytearray([byte1, byte2, byte3, byte4, byte5, byte6, byte7, byte8]))[0]

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))

        UDP_IP = s.getsockname()[0]  # "192.168.178.20"#"192.168.178.30" #"192.168.178.20"
        UDP_PORT = 1005

        start_time = time.time()
        interval = 0.05
        flag1 = False
        flag2 = False
        flag3 = False
        flag4 = False
        flag5 = False
        flag6 = False
        flag7 = False
        flag8 = False

        start_time = time.time()
        start_time_ok = time.time()
        interval = 0.1


        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((UDP_IP, UDP_PORT))
            data, addr = sock.recvfrom(8*2048)
            str = data.decode("utf-8", errors="ignore")
            self.analyseByteStream(data, str)
            if str == "sending":
                self.recievingStructure = True

            if not self.gotStructure:
                current_time = time.time()
                if current_time - start_time >= interval:
                    start_time = time.time()
                    sock.sendto(bytes("send structure", "utf-8"), ("192.168.178.20", 2005))
                    print("send structure")

            if (data[3] == 1):
                flag1 = True
            elif (data[3] == 2):
                flag2 = True
            elif (data[3] == 3):
                flag3 = True
            elif (data[3] == 4):
                flag4 = True
            elif (data[3] == 5):
                flag5 = True
            elif (data[3] == 6):
                flag6 = True
            elif (data[3] == 7):
                flag7 = True
            elif (data[3] == 8):
                flag8 = True

            current_time = time.time()
            elapsed_time = current_time - start_time
            if self.conn.poll():
                interval = self.conn.recv()
            if elapsed_time > interval:
                start_time = time.time()
                if (self.jsonConfig_i > 0 and self.config_i > 0 and flag1):
                    flag1 = False
                    self.conn.send(self.XML_config_list)
                if (self.jsonSensor_i > 0 and self.sensors_i > 0 and flag2):
                    flag2 = False
                    self.conn.send(self.XML_sensors_list)
                if (self.jsonInverter_i > 0 and self.inverter_i > 0 and flag3):
                    flag3 = False
                    self.conn.send(self.XML_inverter_list)
                if (self.jsonErrors_i > 0 and self.errors_i > 0 and flag4):
                    flag4 = False
                    self.conn.send(self.XML_error_list)
                if (self.jsonMath_i > 0 and self.math_i > 0 and flag5):
                    flag5 = False
                    self.conn.send(self.XML_math_list)
                if (self.jsonControls_i > 0 and self.controls_i > 0 and flag6):
                    flag6 = False
                    self.conn.send(self.XML_controls_list)
                if (self.jsonFPGA_Error_i > 0 and self.fpga_error_i > 0 and flag7):
                    flag7 = False
                    self.conn.send(self.XML_fpga_error_list)
                if (self.jsonTimestamp_i > 0 and self.timestapmp_i > 0 and flag8):
                    flag8 = False
                    self.conn.send(self.XML_timestamp_list)
            if not self.gotStructure:
                if self.config_i > 0 and self.jsonConfig_i > 0 and self.sensors_i > 0 and self.jsonSensor_i > 0 and \
                        self.inverter_i > 0 and self.jsonInverter_i > 0 and self.errors_i > 0 and \
                        self.jsonErrors_i and self.math_i > 0 and self.jsonMath_i > 0 and self.controls_i > 0 and \
                        self.jsonControls_i > 0 and self.fpga_error_i > 0 and self.jsonFPGA_Error_i > 0:
                    self.gotStructure = True
                    for x in range(1000):
                            sock.sendto(bytes("ok", "utf-8"), ("192.168.178.20", 2005))
                            print("ok")
            sock.close()

    def analyseByteStream(self, data, str):
        if(str[0] == "J"):
            jsonStr = str[1:]
            jsonObject = json.loads(jsonStr)
            if ('Vehicle Mode' in jsonObject):
                if (self.jsonConfig_i < 1):
                    self.json_config_dict = jsonObject
                    self.jsonConfig_i = self.jsonConfig_i + 1
            elif('Analog' and 'Akku/HV' and 'SC' and 'Fuses' in jsonObject):
                if(self.jsonSensor_i < 1):
                    self.json_sensor_dict = jsonObject
                    self.jsonSensor_i = self.jsonSensor_i + 1
            elif ('VR' and 'VL' and 'HR' and 'HL' in jsonObject):
                if (self.jsonInverter_i < 1):
                    self.json_inverter_dict = jsonObject
                    self.jsonInverter_i = self.jsonInverter_i + 1
            elif ('Timeout CAN' and 'Wert' and 'Latching' in jsonObject):
                if (self.jsonErrors_i < 1):
                    self.json_errors_dict = jsonObject
                    self.jsonErrors_i = self.jsonErrors_i + 1
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
            elif('Timestamp' in jsonObject):
                if (self.jsonTimestamp_i < 1):
                    self.json_timstamp_dict = jsonObject
                    self.jsonTimestamp_i = self.jsonTimestamp_i + 1
        elif(str[0] == "X"):
            XMLStr = str[1:]
            XMLObject = xmltodict.parse(XMLStr)
            if (XMLObject['Cluster']['Name'] == 'Config-Values'):
                if (self.config_i < 1):
                    self.XML_config_list = XMLObject
                    self.signal_Config_Values_init.emit(XMLObject)
                    self.config_i = self.config_i + 1
            elif (XMLObject['Cluster']['Name'] == 'Sensors'):
                if(self.sensors_i < 1):
                    self.XML_sensors_list = XMLObject
                    self.sensors_i = self.sensors_i + 1
            elif (XMLObject['Cluster']['Name'] == 'Inverter'):
                if (self.inverter_i < 1):
                    self.XML_inverter_list = XMLObject
                    self.inverter_i = self.inverter_i + 1
            elif (XMLObject['Cluster']['Name'] == 'Errors'):
                if (self.errors_i < 1):
                    self.XML_error_list = XMLObject
                    self.errors_i = self.errors_i + 1
            elif (XMLObject['Cluster']['Name'] == 'Math'):
                if (self.math_i < 1):
                    self.XML_math_list = XMLObject
                    self.math_i = self.math_i + 1
            elif (XMLObject['Cluster']['Name'] == 'Controls'):
                if (self.controls_i < 1):
                    self.XML_controls_list = XMLObject
                    self.controls_i = self.controls_i + 1
            elif (XMLObject['Cluster']['Name'] == 'FPGA Error'):
                if (self.fpga_error_i < 1):
                    self.XML_fpga_error_list = XMLObject
                    self.fpga_error_i = self.fpga_error_i + 1
            elif (XMLObject['Cluster']['Name'] == 'Timestamp'):
                if (self.timestapmp_i < 1):
                    self.XML_timestamp_list = XMLObject
                    self.timestapmp_i = self.timestapmp_i + 1
        elif(data[3] == 1):
            if (self.jsonConfig_i > 0 and self.config_i > 0):
                self.jsonIteration(self.json_config_dict, self.XML_config_list, 0, data, 4)
        elif(data[3] == 2):
            if(self.jsonSensor_i > 0 and self.sensors_i > 0):
                self.jsonIteration(self.json_sensor_dict, self.XML_sensors_list, 0, data, 4)
        elif (data[3] == 3):
            if (self.jsonInverter_i > 0 and self.inverter_i > 0):
                self.jsonIteration(self.json_inverter_dict, self.XML_inverter_list, 0, data, 4)
        elif (data[3] == 4):
            if (self.jsonErrors_i > 0 and self.errors_i > 0):
                self.jsonIteration(self.json_errors_dict, self.XML_error_list, 0, data, 4)
        elif (data[3] == 5):
            if (self.jsonMath_i > 0 and self.math_i > 0):
                self.jsonIteration(self.json_math_dict, self.XML_math_list, 0, data, 4)
        elif (data[3] == 6):
            if (self.jsonControls_i > 0 and self.controls_i > 0):
                self.jsonIteration(self.json_controls_dict, self.XML_controls_list, 0, data, 4)
        elif (data[3] == 7):
            if (self.jsonFPGA_Error_i > 0 and self.fpga_error_i > 0):
                self.jsonIteration(self.json_fpga_error_dict, self.XML_fpga_error_list, 0, data, 4)
        elif (data[3] == 8):
            if (self.jsonTimestamp_i > 0 and self.timestapmp_i > 0):
                self.jsonIteration(self.json_timstamp_dict, self.XML_timestamp_list, 0, data, 4)

    def jsonIteration(self, jsonDict, xmlDict, iteration_level, serialElements, serialCounter, json_sensor_dict_element_1 = "None", json_sensor_dict_element_2 = "None", json_sensor_dict_element_3 = "None"):
        searchXMLLevel = 0
        iteration_level = iteration_level + 1
        start_time = time.time()
        interval = 0.1
        for key in jsonDict:
            current_time = time.time()
            elapsed_time = current_time - start_time
            if elapsed_time > interval:
                QThread.usleep(10)
                start_time = time.time()
            if(isinstance(jsonDict[key], dict)):
                if(iteration_level == 1):
                    json_sensor_dict_element_1 = key
                elif(iteration_level == 2):
                    json_sensor_dict_element_2 = key
                elif (iteration_level == 3):
                    json_sensor_dict_element_3 = key
                else:
                    print("wrong iteration_level")
                serialCounter = self.jsonIteration( jsonDict[key], xmlDict, iteration_level, serialElements, serialCounter, json_sensor_dict_element_1, json_sensor_dict_element_2, json_sensor_dict_element_3)
            elif (isinstance(jsonDict[key], list)):
                serialCounter = self.jsonIteration( jsonDict[key], xmlDict, iteration_level, serialElements, serialCounter, json_sensor_dict_element_1, json_sensor_dict_element_2, json_sensor_dict_element_3)
            else:
                if(json_sensor_dict_element_2 == "None"):
                    searchXMLLevel = 0
                    elementDatatype = "None"
                    seconds = 1
                    serialCounter, searchXMLLevel = self.searchXMLdatatype(xmlDict, key, elementDatatype, serialElements, serialCounter, json_sensor_dict_element_1, searchXMLLevel) #for checking the datatype

                elif(json_sensor_dict_element_3 == "None"):
                    searchXMLLevel = 0
                    elementDatatype = "None"
                    serialCounter, searchXMLLevel = self.searchXMLdatatype(xmlDict, key, elementDatatype, serialElements, serialCounter, json_sensor_dict_element_1, searchXMLLevel, json_sensor_dict_element_2)  # for checking the datatype
                else:
                    print("json_sensor_dict_element_3 != None")

        iteration_level = iteration_level - 1
        if (iteration_level == 1):
            json_sensor_dict_element_1 = "None"
        elif (iteration_level == 2):
            json_sensor_dict_element_2 = "None"
        elif (iteration_level == 3):
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
            if(dataList != []):
                if(dataList.get('Cluster').get("Name") == "Config-Values"): #Sollte jetzt auch ohne gesonderte Behandlung funktionieren
                    serialCounter, elementDatatype, searchXMLLevel = self.searchElementandDatatype(dataList.get('Cluster'), ElementXMLCompare, dataType, serialElements, serialCounter, json_sensor_dict_element_1, 0, "None")
                else:
                    serialCounter, elementDatatype, searchXMLLevel = self.searchElementandDatatype(
                        dataList.get('Cluster', 'None').values(), ElementXMLCompare, dataType, serialElements,
                        serialCounter, json_sensor_dict_element_1, 0, "None")
            else:
                print("Dict empty")
        elif(listElement3d == "empty"):
            serialCounter, elementDatatype, searchXMLLevel = self.searchElementandDatatype(dataList.get('Cluster', 'None').values(), ElementXMLCompare, dataType, serialElements, serialCounter, json_sensor_dict_element_1, 0, "None", wantedElement2 = ElementXMLCompare2d)
        return serialCounter, searchXMLLevel

    def searchElementandDatatype(self, listofElements, wantedElement, dataType, serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1, searchXMLLevel, wantedElement2 = None, wantedElement3 = None):
        elementDatatype = dataType
        if (isinstance(listofElements, OrderedDict)):
            XML_dict_element_1 = "None"
            DBLElement = listofElements.get('DBL')
            SGLElement = listofElements.get('SGL')
            boolElement = listofElements.get('Boolean')
            U8Element = listofElements.get('U8')
            U16Element = listofElements.get('U16')
            U32Element = listofElements.get('U32')
            I8Element = listofElements.get('I8')
            EBElement = listofElements.get('EB')
            if (boolElement != None and elementDatatype == "None"):
                serialCounter, elementDatatype = self.searchDatatypeElement(boolElement, wantedElement,
                                                                            "Boolean", serialElements,
                                                                            serialCounter, json_sensor_dict_element_1, XML_dict_element_1,
                                                                            wantedElement2=listofElements.get("Name"))
            if (DBLElement != None and elementDatatype == "None"):
                serialCounter, elementDatatype = self.searchDatatypeElement(DBLElement, wantedElement, "DBL",
                                                                            serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1,

                                                                            wantedElement2=listofElements.get("Name"))
            if (SGLElement != None and elementDatatype == "None"):
                serialCounter, elementDatatype = self.searchDatatypeElement(SGLElement, wantedElement, "SGL",
                                                                            serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1,

                                                                            wantedElement2=listofElements.get("Name"))
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
                serialCounter, elementDatatype = self.searchDatatypeElement(EBElement, wantedElement, "EB",
                                                                            serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1,

                                                                            wantedElement2=listofElements.get("Name"))
        else:
            for element in listofElements:
                if(wantedElement2 == None or searchXMLLevel == 1):
                    if(isinstance(element, OrderedDict)):
                        if(wantedElement2 == None):
                            XML_dict_element_1 = element.get("Name")
                        DBLElement = element.get('DBL')
                        SGLElement = element.get('SGL')
                        boolElement = element.get('Boolean')
                        U8Element = element.get('U8')
                        U16Element = element.get('U16')
                        U32Element = element.get('U32')
                        I8Element = element.get('I8')
                        EBElement = element.get('EB')

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

                    elif(isinstance(element, list)):
                        serialCounter, elementDatatype, searchXMLLevel = self.searchElementandDatatype(element, wantedElement, elementDatatype, serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1, searchXMLLevel)
                elif(wantedElement2 != None):
                    for element in listofElements:
                        if(isinstance(element, OrderedDict)):
                            if(element.get("Name") == json_sensor_dict_element_1):
                                XML_dict_element_1 = element.get("Name")
                                searchXMLLevel = 1
                                serialCounter, elementDatatype, searchXMLLevel = self.searchElementandDatatype(element.get("Cluster"), wantedElement, elementDatatype, serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1, searchXMLLevel, wantedElement2 = wantedElement2)
                        elif(isinstance(element, list)):
                            serialCounter, elementDatatype, searchXMLLevel = self.searchElementandDatatype(element, wantedElement, elementDatatype, serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1, searchXMLLevel, wantedElement2 = wantedElement2)
        searchXMLLevel = 0
        return serialCounter, elementDatatype, searchXMLLevel


    def searchDatatypeElement(self, datatypeElement, wantedElement, dataType, serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1, wantedElement2 = None, wantedElement3 = None):
        if(isinstance(datatypeElement, list)):
            for datatypeElements in datatypeElement:
                serialCounter, elementDatatype = self.searchDatatypeElement(datatypeElements, wantedElement, dataType, serialElements, serialCounter, json_sensor_dict_element_1, XML_dict_element_1, wantedElement2 = wantedElement2)
                if(elementDatatype != "None"):
                    return serialCounter, elementDatatype

        elif (isinstance(datatypeElement, OrderedDict)):
            if(wantedElement == datatypeElement.get('Name') and json_sensor_dict_element_1 == XML_dict_element_1): #wantedElement == datatypeElement.get('Name') and self.json_sensor_dict_element_1 == self.XML_dict_element_1
                elementDatatype = dataType
                if (dataType == "EB"):
                    datatypeElement['Val'] = str(serialElements[serialCounter])
                    serialCounter = serialCounter + 1
                    return serialCounter, elementDatatype
                elif (dataType == "U32"):  # is checking the datatype for serial datastream
                    datatypeElement['Val'] = "-- U32 --"# str(intValue)
                    serialCounter = serialCounter + 4
                    return serialCounter, elementDatatype
                elif (dataType == "U16"):  # is checking the datatype for serial datastream
                    intValue = serialElements[serialCounter] * 2**8 + serialElements[serialCounter + 1]
                    datatypeElement['Val'] = str(intValue)
                    serialCounter = serialCounter + 2
                    return serialCounter, elementDatatype
                elif (dataType == "U8"):  # is checking the datatype for serial datastream
                    datatypeElement['Val'] = str(serialElements[serialCounter])
                    serialCounter = serialCounter + 1
                    return serialCounter, elementDatatype
                elif (dataType == "I32"):  # is checking the datatype for serial datastream
                    datatypeElement['Val'] = "-- I32 --"#str(serialElements[serialCounter])
                    serialCounter = serialCounter + 4
                    return serialCounter, elementDatatype
                elif (dataType == "I16"):  # is checking the datatype for serial datastream
                    datatypeElement['Val'] = "-- I16 --"#"#"#str(serialElements[serialCounter])
                    serialCounter = serialCounter + 2
                    return serialCounter, elementDatatype
                elif (dataType == "I8"):  # is checking the datatype for serial datastream
                    sIntValue = serialElements[serialCounter]
                    if(sIntValue>127):
                        sIntValue = 256-sIntValue
                    datatypeElement['Val'] = str(sIntValue)
                    serialCounter = serialCounter + 1
                    return serialCounter, elementDatatype
                elif (dataType == "Boolean"):
                    datatypeElement['Val'] = str(serialElements[serialCounter])
                    serialCounter = serialCounter + 1
                    return serialCounter, elementDatatype
                elif (dataType == "DBL"):
                    # datatypeElement['Val'] = "-- DBL --"
                    datatypeElement['Val'] = str(self.serial_to_float_64(serialElements[serialCounter],
                                                 serialElements[serialCounter + 1],
                                                 serialElements[serialCounter + 2],
                                                 serialElements[serialCounter + 3],
                                                 serialElements[serialCounter + 4],
                                                 serialElements[serialCounter + 5],
                                                 serialElements[serialCounter + 6],
                                                 serialElements[serialCounter + 7]))
                    serialCounter = serialCounter + 8
                    return serialCounter, elementDatatype
                elif (dataType == "SGL"):
                    value = round(self.serial_to_float(serialElements[serialCounter],
                                                 serialElements[serialCounter + 1],
                                                 serialElements[serialCounter + 2],
                                                 serialElements[serialCounter + 3]), 6)
                    datatypeElement['Val'] = str(value)
                    serialCounter = serialCounter + 4
                    return serialCounter, elementDatatype
            else:
                elementDatatype = "None"
                return serialCounter, elementDatatype
        return serialCounter, elementDatatype