import serial
import pynmea2
import time

import sys
import paho.mqtt.client as paho
import threading

#from colorama import Fore, Back, Style

import datetime as dt
import csv
print ("select your GPS port:")

heading = 0

message_time = 0
message_time_prev = 0

knot = 0

current_time = dt.datetime.now()

day = current_time.day
day_prev = current_time.day

fields = ['time', 'lat', 'long']
filename = str("GPS CALIB " ) + str(current_time.day)+str("-")+str(current_time.month)+str("-")+str(current_time.year) + str(".csv")    
with open(filename, 'a') as csvfile:
    # creating a csv writer object
    csvwriter = csv.writer(csvfile)
    # writing the fields
    csvwriter.writerow(fields)



def serial_ports():
   
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result
print(str(serial_ports()))

port = input("write port : ")

ser = serial.Serial(port, 9600)


broker = input("broker ip: ")
port = 1883

lat = 0
long = 0


if ser.is_open:
    print(f'Port {ser.port} terbuka.')

def gps_calc(num):
    global heading
    global message_time
    global message_time_prev
    global knot
    while True:
        nmea_data = ser.readline().decode('utf-8', 'ignore').strip()
        if nmea_data.startswith('$GNRMC'):
            #print(nmea_data)
            try:
                msg = pynmea2.parse(nmea_data)
            except:
                pass
            #print(msg)
           
            if isinstance(msg, pynmea2.types.talker.RMC):
                #print(f"Waktu: {msg.timestamp}")
                #print(f"Status Perangkat: {msg.status}")
                try:
                    lat = float(msg.latitude)
                except:
                    pass
               
               
                print("")
                try:
                    long = float(msg.longitude)
                except:
                    pass

                try:
                    knot = float(msg.spd_over_grnd)
                   
                except:
                    pass

               
                try:
                    heading = int(msg.true_course)
                except :
                    pass
               
                #print(f"heading : {msg.true_course}  | ", heading)
                print(f"latitude: ", lat, "longitude :", long)
               
                lat_nmea_integer = int(lat)
                lat_nmea_fractional = float(lat) - lat_nmea_integer
               
               
                long_nmea_integer = int(long)
                long_nmea_fractional = float(long) - long_nmea_integer
               
                client.publish("lat_nmea_integer_pc", str(round(lat_nmea_integer,6)))
                client.publish("lat_nmea_fractional_pc", str(round(lat_nmea_fractional,8)))
               
                client.publish("long_nmea_integer_pc", str(round(long_nmea_integer,6)))
                client.publish("long_nmea_fractional_pc", str(round(long_nmea_fractional,8)))
                client.publish("speed_nmea", str(round(knot,2)))
               
                '''
                if (heading != "None"):
                    client.publish("yaw_actual", str((heading)))
                '''
                message_time = time.time() - message_time_prev
                if (message_time > 1):
                   
                    waktu = dt.datetime.now()
                    filename = str("GPS CALIB " ) + str(current_time.day)+str("-")+str(current_time.month)+str("-")+str(current_time.year) + str(".csv")
                    with open(filename, 'a') as csvfile:
                            csvwriter = csv.writer(csvfile)
                            rows = [ [str(str(waktu.hour) + str(":") + str(waktu.minute)+ str(":") + str(waktu.second)),str(lat),
                                    str(long) ]]
                            csvwriter.writerows(rows)
               
                   
                   
                    message_time_prev = time.time()
               
            else:
                print("Tipe pesan NMEA tidak didukung.")
           
            if (day != day_prev):
                filename = str("GPS CALIB " ) + str(current_time.day)+str("-")+str(current_time.month)+str("-")+str(current_time.year) + str(".csv")    
                with open(filename, 'a') as csvfile:
                    # creating a csv writer object
                    csvwriter = csv.writer(csvfile)
                    # writing the fields
                    csvwriter.writerow(fields)
           
 
def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    t = str(message.topic)

    if(msg[0] == 'c'):
        val =  1
    else:
        val = (msg)
       
       
if __name__ == "__main__":
    ##Mosquitto Mqtt Configuration
    client= paho.Client("NMEA_GPS_PC")
    client.on_message=on_message

    print("connecting to broker ",broker)
    client.connect(broker,port)#connect
    print(broker," connected")
   
    client.loop_start()
    print("Subscribing")
   
    t1 = threading.Thread(target=gps_calc, args=(10,))
    t1.start()
