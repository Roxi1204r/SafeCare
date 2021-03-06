#!/usr/bin/env python3

'''
Pymodbus Server With Updating Thread
--------------------------------------------------------------------------

This is an example of having a background thread updating the
context while the server is operating. This can also be done with
a python thread::

    from threading import Thread

    thread = Thread(target=updating_writer, args=(context,))
    thread.start()
'''
#---------------------------------------------------------------------------# 
# import the modbus libraries we need
#---------------------------------------------------------------------------# 
from pymodbus.server.asynchronous import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer

#---------------------------------------------------------------------------# 
# import the twisted libraries we need
#---------------------------------------------------------------------------# 
from twisted.internet.task import LoopingCall

#---------------------------------------------------------------------------# 
# configure the service logging
#---------------------------------------------------------------------------# 
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

#---------------------------------------------------------------------------# 
# DHT sensor configuration
#---------------------------------------------------------------------------#
import busio
import board
import adafruit_dht
import adafruit_ads1x15.ads1115 as ADS

from board import *
from time import sleep
from adafruit_ads1x15.analog_in import AnalogIn

import paho.mqtt.publish as publicare
import json

MQTT_HOST = 'mqtt.beia-telemetrie.ro'
MQTT_TOPIC = 'odsi/modbus/server'
logfile="/home/pi/Desktop/data.txt"

flag = 0

def local_save(data):
    file=open(logfile, "a+")
    file.write(data+"\r\n")
    file.close()

i2c = busio.I2C(board.SCL, board.SDA)

ads = ADS.ADS1115(i2c)

SENSOR_PIN = D18

dht22 = adafruit_dht.DHT22(SENSOR_PIN, use_pulseio=False)
 
#---------------------------------------------------------------------------# 
# define your callback process
#---------------------------------------------------------------------------# 
def updating_writer(a):
    ''' A worker process that runs every so often and
    updates live values of the context. It should be noted
    that there is a race condition for the update.

    :param arguments: The input arguments to the call
    '''
    log.debug("updating the context")
    context  = a[0]
    register = 3
    slave_id = 0x00
    address  = 0x00
    values   = context[slave_id].getValues(register, address, count=2)

    try:
        temperature = dht22.temperature
        values[0] = temperature
        
        payload_temp={"temperature":temperature}
        publicare.single(MQTT_TOPIC,qos = 1,hostname = MQTT_HOST,payload = json.dumps(payload_temp))
    except:
        pass
    
    chan = AnalogIn(ads, ADS.P0)
    values[1] = round(chan.voltage, 2)
    
    message="Voltage "+str(round(chan.voltage, 2))
    local_save(message)
    
    payload_v={"voltage":round(chan.voltage, 2)}
    publicare.single(MQTT_TOPIC,qos = 1,hostname = MQTT_HOST,payload = json.dumps(payload_v))
    
    log.debug("new values: " + str(values))
    context[slave_id].setValues(register, address, values)
    

def run_dbstore_update_server():
    #---------------------------------------------------------------------------# 
    # initialize your data store
    #---------------------------------------------------------------------------# 
    store = ModbusSlaveContext(
        di = ModbusSequentialDataBlock(0, [1]*100),
        co = ModbusSequentialDataBlock(0, [2]*100),
        hr = ModbusSequentialDataBlock(0, [3]*100),
        ir = ModbusSequentialDataBlock(0, [4]*100))
    context = ModbusServerContext(slaves=store, single=True)

    #---------------------------------------------------------------------------# 
    # initialize the server information
    #---------------------------------------------------------------------------# 
    identity = ModbusDeviceIdentification()
    identity.VendorName  = 'pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl   = 'http://github.com/bashwork/pymodbus/'
    identity.ProductName = 'pymodbus Server'
    identity.ModelName   = 'pymodbus Server'
    identity.MajorMinorRevision = '1.0'

    #---------------------------------------------------------------------------# 
    # run the server you want
    #---------------------------------------------------------------------------# 
    time = 30 # 30 seconds delay
    loop = LoopingCall(f=updating_writer, a=(context,))
    loop.start(time) # initially delay by time
    StartTcpServer(context, identity=identity, address=("", 5020))
    
if __name__ == "__main__":
   
    while True:
        run_dbstore_update_server()
        sleep(5)
