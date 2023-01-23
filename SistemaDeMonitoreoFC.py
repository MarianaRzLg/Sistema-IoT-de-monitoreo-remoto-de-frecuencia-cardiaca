from max30102 import MAX30102
from machine import sleep, I2C, Pin, Timer 
from utime import ticks_diff, ticks_us
from time import sleep
import machine as mn
import network
from umqtt.simple import MQTTClient

import gc
gc.collect()


global bpmenvio
global valgdds
led_p = Pin(32, Pin.OUT)
led_c = Pin(33, Pin.OUT)
beats = 0
valgdds_2=[]
valgdds=[]

bpmgdds=[]
bpmenvio=[]
long = 5
long_2 =100
pulso = True

i2c = I2C(1,sda=Pin(21),scl=Pin(22),freq=400000)
sensor = MAX30102(i2c=i2c)
i2c.scan()
sensor.check_part_id()
sensor.setup_sensor()

def connect(self):
    global bpmenvio
    global valgdds
    ssid     = 'bluetele547B'
    password = 'B89DBD20'
    station = network.WLAN(network.STA_IF)
    if not station.isconnected():
        station.active(True)
        station.connect(ssid,password)            
        while not station.isconnected():           
            pass
    SERVER = "192.168.0.118"
    mqtt_client = MQTTClient("umqtt_client",SERVER,keepalive=60)
    mqtt_client.connect()
    #print(bpmenvio)
    mqtt_client.publish("BPM",str(bpmenvio))
    mqtt_client.publish("grafica",str(valgdds))
    #led_c.value(1)
    #sleep(1)
    #led_c.value(0)

#def enviodegrafica(self):
 #   global valgdds
  #  ssid     = 'Casa 56'
  #  password = '26f4dd8ae1'
  #  station = network.WLAN(network.STA_IF)
  #  if not station.isconnected():
   #     station.active(True)
   #     station.connect(ssid,password)            
   #     while not station.isconnected():           
    #        pass
   # SERVER = "192.168.10.135"
   # mqtt_client = MQTTClient("umqtt_client",SERVER,keepalive=60)
   # mqtt_client.connect()
   # mqtt_client.publish("grafica",str(valgdds))
    
timer = Timer(1)
timer.init(period=5000,mode=Timer.PERIODIC,callback=connect)
#timer.init(period=150,mode=Timer.PERIODIC,callback=enviodegrafica)

t_start = ticks_us()    
while True:
    sensor.check()
    if sensor.available():
        red_reading = sensor.pop_red_from_storage()
        #valores =
        ir_reading = sensor.pop_ir_from_storage()
         #Se guardan los ultimos 32 valores recolectados
        valgdds_2.append(red_reading)
        valgdds_2 = valgdds_2[-long:]
        lim = (min(valgdds_2)+max(valgdds_2)*3)//4 #Se selecciona un límite para contar cada pulso
    
        if red_reading > 10000: #Un valor menor indica que no se esta reciviendo informacion util
            valgdds.append(red_reading)
            valgdds = valgdds[-long_2:]
            if pulso and red_reading > lim:
                bpm = (1/(ticks_diff(ticks_us(), t_start)/1000000))*60
                t_start = ticks_us()
                bpmgdds.append(bpm)
                bpmgdds= bpmgdds[-long:]
                beat = round(sum(bpmgdds)/len(bpmgdds))
                #led_p.value(1)
                if beat < 150:
                    #beats = beat
                    bpmenvio.append(beat)
                    bpmenvio= bpmenvio[-long:]
                #else:
                    #beats = 1
                    #bpmenvio.append(1)
                    #bpmenvio= bpmenvio[-long:]
                pulso = False
            if red_reading < lim:
                pulso = True
                #led_p.value(0)
        else:
            #beats = 0
            valgdds.append(0)
            valgdds = valgdds[-long_2:]
            bpmenvio.append(0)
            bpmenvio= bpmenvio[-long:]
             