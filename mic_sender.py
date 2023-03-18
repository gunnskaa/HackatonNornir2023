import serial
import time
import requests
import datetime

# For recieving form Microbit
ser = serial.Serial('COM8', 115200, bytesize=8,parity='N', stopbits=1, timeout=100, rtscts=1)

# For sending to Erling
headers = {
            'Synx-Cat': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

i = 0
j = 0
t0 = time.time()
soundSum = 0
soundSumCnt = 0
while True:    
    s = ser.readline().decode("UTF-8").strip()
    if(s):
        print(s)
        try:
            if s == 'loud':
                i += 1
            elif s == 'quiet':
                j += 1
            else:
                soundSum += int(s)
                soundSumCnt += 1
        except:
            continue
        if time.time()-t0 > 2:
            # message = "loud" if i>j else "quiet"
            # print(i/(i+j))
            # print(soundSum/(soundSumCnt))
            data = {'token':'aToken_36d8715e3531fd8e8c01fcbfd26bf5af1908e14f15014d2d14817b568bc0bb0e',
                    'objectID':'2',
                    'sender' :'MicrobitGunnar',
                    'Loudness' :str(1.2*soundSum/(soundSumCnt*255)),
                    'TimeStamp': datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")}
            response = requests.post('https://8group.cioty.com/loudnessMonitor', headers=headers, data=data, verify=False)
            i = 0
            j = 0
            soundSum   = 0
            soundSumCnt = 0
            t0 = time.time()