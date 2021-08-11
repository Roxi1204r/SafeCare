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
MQTT_TOPIC = 'odsi.safecare'
logfile="data.txt"

def local_save(data):
    file=open(logfile, "a+")
    file.write(data+"\r\n")
    file.close()


i2c = busio.I2C(board.SCL, board.SDA)

ads = ADS.ADS1115(i2c)

SENSOR_PIN = D18

dht22 = adafruit_dht.DHT22(SENSOR_PIN, use_pulseio=False)
 
while True:
    
    chan = AnalogIn(ads, ADS.P0)
    
    try:
        temperature = dht22.temperature
        humidity = dht22.humidity
        payload_dict={"temperature":temperature,
                 "Voltage":chan.voltage}
        print(json.dumps(payload_dict))
#     message="Gas detected "+str(Gas)+", Warning "+str(Atentionare)
#     try:
        publicare.single(MQTT_TOPIC,qos = 1,hostname = MQTT_HOST,payload = json.dumps(payload_dict))
#         local_save(message)
#     except:
#         pass
    except RuntimeError:
        pass
    
    
#     print(f"Humidity = {humidity:.2f}%")
#     print(f"Temperature = {temperature:.2f}°C")
#     
#     print(f"chan.value = {chan.value:.4f}")
#     print(f"chan.voltage = {chan.voltage:.4f}\n")
    sleep(2)
