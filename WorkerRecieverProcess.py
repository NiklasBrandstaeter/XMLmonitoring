import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt, QCoreApplication
import time
import socket
import json
from monitoring import Ui_MainWindow
import xmltodict
from typing import OrderedDict
import concurrent.futures
import multiprocessing
from collections import OrderedDict
from WorkerUDP import WorkerUDP

class WorkerRecieverProcess(QObject):
    signal_Config_Values = pyqtSignal(dict)  # Signal for setting new values XML
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
    signal_Config_Values_serial = pyqtSignal(bytes)  # serial Values for monitoring
    signal_Config_Values_init = pyqtSignal(dict)  # for setting the structure of the cluster
    signal_Sensors_serial = pyqtSignal(bytes)
    signal_Sensors_init = pyqtSignal(dict)
    signal_Sensors_update = pyqtSignal(dict)
    signal_set_Text = pyqtSignal(tuple)
    signal_set_LED = pyqtSignal(tuple)
    signal_set_gui = pyqtSignal(list)
    signal_connection = pyqtSignal(bool)

    def __init__(self, conn):
        super(WorkerRecieverProcess, self).__init__()
        self.sleep = False
        self.conn = conn
        self.textSets = []
        self.ledSets = []

    def readFromReciever(self):
        start_time = time.time()
        interval = 5
        start_time_connection = time.time()
        interval_connection = 1
        while True:
            current_time = time.time()
            if current_time - start_time >= interval:
                start_time = time.time()
                self.setText = []
            if current_time - start_time_connection >= interval_connection:
                start_time_connection = time.time()
                self.signal_connection.emit(False)


            if self.conn.poll():
                msg = self.conn.recv()
                if isinstance(msg, dict):
                    if (msg['Cluster']['Name'] == 'Config-Values'):
                        self.recieve_Config_Valuesx(msg)
                        self.signal_connection.emit(True)
                        start_time_connection = time.time()
                    elif (msg['Cluster']['Name'] == 'Sensors'):
                        self.recieve_Sensorsx(msg)
                        self.signal_connection.emit(True)
                        start_time_connection = time.time()
                    elif (msg['Cluster']['Name'] == 'Inverter'):
                        self.recieve_Inverterx(msg)
                        self.signal_connection.emit(True)
                        start_time_connection = time.time()
                    elif (msg['Cluster']['Name'] == 'Errors'):
                        self.recieve_Errorsx(msg)
                        self.signal_connection.emit(True)
                        start_time_connection = time.time()
                    elif (msg['Cluster']['Name'] == 'Math'):
                        self.recieve_Mathx(msg)
                        self.signal_connection.emit(True)
                        start_time_connection = time.time()
                    elif (msg['Cluster']['Name'] == 'Controls'):
                        self.recieve_Controlsx(msg)
                        self.signal_connection.emit(True)
                        start_time_connection = time.time()
                    elif (msg['Cluster']['Name'] == 'FPGA Error'):
                        self.recieve_FPGA_Errorx(msg)
                        self.signal_connection.emit(True)
                        start_time_connection = time.time()
                    elif (msg['Cluster']['Name'] == 'Timestamp'):
                        self.recieve_Timestampx(msg)
                        self.signal_connection.emit(True)
                        start_time_connection = time.time()

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

    def recieve_Timestampx(self, json_Timestamp):

        self.set_lineEdit("lineEdit_Timestamp_Timestamp", json_Timestamp, 'Timestamp', indexes = 3)

    def set_lineEdit(self, name_lineEdit, dataList, listElement, listElement2d = 'empty', listElement3d = 'empty', indexes = 0):
        if(listElement2d == "empty"):
            name, value = self.searchElement(dataList.get('Cluster', 'None').values(), listElement, dataList.get('Cluster', 'None'))
            if (name == listElement):
                self.signal_set_Text.emit((name_lineEdit, value))
        elif(listElement3d == "empty"):
            name, value = self.searchElementLevel2(dataList.get('Cluster', 'None').values(), listElement2d, listElement,dataList.get('Cluster', 'None'))
            if (name == listElement2d):
                self.signal_set_Text.emit((name_lineEdit, value))
        else:
            name, value = self.searchElementLevel3(dataList.get('Cluster', 'None').values(), listElement3d, listElement2d, listElement, dataList.get('Cluster', 'None'))
            if (name == listElement3d):
                self.signal_set_Text.emit((name_lineEdit, value))

    def set_btn_LED(self, name_btn_LED, dataList, listElement, listElement2d = 'empty', listElement3d = 'empty'):
        if(listElement2d=="empty"):
            name, value = self.searchElement(dataList.get('Cluster', 'None').values(), listElement, dataList.get('Cluster', 'None'))
            if(name == listElement):
                self.signal_set_LED.emit((name_btn_LED, value))
        elif (listElement3d == "empty"):
            name, value = self.searchElementLevel2(dataList.get('Cluster', 'None').values(), listElement2d, listElement, dataList.get('Cluster', 'None'))
            if (name == listElement2d):
                self.signal_set_LED.emit((name_btn_LED, value))
        else:
            name, value = self.searchElementLevel3(dataList.get('Cluster', 'None').values(), listElement3d, listElement2d, listElement, dataList.get('Cluster', 'None'))
            if (name == listElement3d):
                self.signal_set_LED.emit((name_btn_LED, value))

    def searchElement(self, listofElements, wantedElement, oldElement):
        name = "None"
        value = "None"
        for element in listofElements:
            if (isinstance(element, OrderedDict)):
                if(element.get('Name') == wantedElement and element.get('Val') != 'None'):
                    name = element.get('Name')
                    if(element.get('Choice')):
                        value = element.get('Choice')[int(element.get('Val'))]
                    else:
                        value = element.get('Val')
                    return name, value
                else:
                    name, value = self.searchElement(element.values(), wantedElement, listofElements)
                    if(name != "None" and value != "None"):
                        return name, value
            if(isinstance(element, list)):
                name, value = self.searchElement(element, wantedElement, listofElements)
                if (name != "None" and value != "None"):
                    return name, value
        return name, value

    def searchElementLevel2(self, listofElements, wantedElement, elementLevelbefore, oldElement, level=0):
        name = "None"
        value = "None"
        for element in listofElements:
            if (isinstance(element, OrderedDict)):
                if(element.get('Name') == elementLevelbefore and level == 0):
                    if (isinstance(element, OrderedDict)):
                        name, value = self.searchElementLevel2(element.values(), wantedElement, elementLevelbefore, listofElements, level=2)
                        if (name != "None" and value != "None"):
                            return name, value
                    elif (isinstance(element, list)):
                        name, value = self.searchElementLevel2(element, wantedElement, elementLevelbefore, listofElements, level=2)
                        if (name != "None" and value != "None"):
                            return name, value
                elif(element.get('Name') == wantedElement and element.get('Val') != 'None' and level == 2):
                    self.elementName = element.get('Name')
                    name = element.get('Name')
                    if(element.get('Choice')):
                        value = element.get('Choice')[int(element.get('Val'))]
                    else:
                        value = element.get('Val')
                    return name, value
                else:
                    name, value = self.searchElementLevel2(element.values(), wantedElement, elementLevelbefore, listofElements, level=level)
                    if (name != "None" and value != "None"):
                        return name, value
            elif(isinstance(element, list)):
                name, value = self.searchElementLevel2(element, wantedElement, elementLevelbefore, listofElements, level=level)
                if (name != "None" and value != "None"):
                    return name, value
        return name, value

    def searchElementLevel3(self, listofElements, wantedElement, elementLevelbefore, elementLevelbeforebefore, oldElement, level=0):
        name = "None"
        value = "None"
        for element in listofElements:
            if (isinstance(element, OrderedDict)):
                if (element.get('Name') == elementLevelbeforebefore and level == 0):
                    if (isinstance(element, OrderedDict)):
                        name, value = self.searchElementLevel3(element.values(), wantedElement, elementLevelbefore, elementLevelbeforebefore, listofElements, level=2)
                        if (name != "None" and value != "None"):
                            return name, value
                    elif (isinstance(element, list)):
                        name, value = self.searchElementLevel3(element, wantedElement, elementLevelbefore, elementLevelbeforebefore, listofElements, level=2)
                        if (name != "None" and value != "None"):
                            return name, value
                if (element.get('Name') == elementLevelbefore and level == 2):
                    if (isinstance(element, OrderedDict)):
                        name, value = self.searchElementLevel3(element.values(), wantedElement, elementLevelbefore, elementLevelbeforebefore, listofElements, level=3)
                        if (name != "None" and value != "None"):
                            return name, value
                    elif (isinstance(element, list)):
                        name, value = self.searchElementLevel3(element, wantedElement, elementLevelbefore, elementLevelbeforebefore, listofElements, level=3)
                        if (name != "None" and value != "None"):
                            return name, value
                elif (element.get('Name') == wantedElement and element.get('Val') != 'None' and level == 3):
                    name = element.get('Name')
                    if (element.get('Choice')):
                        value = element.get('Choice')[int(element.get('Val'))]
                    else:
                        value = element.get('Val')
                    return name, value
                else:
                    name, value = self.searchElementLevel3(element.values(), wantedElement, elementLevelbefore, elementLevelbeforebefore, listofElements, level=level)
                    if (name != "None" and value != "None"):
                        return name, value
            elif (isinstance(element, list)):
                name, value = self.searchElementLevel3(element, wantedElement, elementLevelbefore, elementLevelbeforebefore, listofElements, level=level)
                if (name != "None" and value != "None"):
                    return name, value
        return name, value