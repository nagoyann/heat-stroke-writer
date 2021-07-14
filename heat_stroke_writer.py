import RPi.GPIO as GPIO
import dht11
import time
import datetime
import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials

# initialize GPIO
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

# read data using pin 14
instance = dht11.DHT11(pin=14)

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

base = os.path.dirname(os.path.abspath(__file__))
credentialspath = os.path.normpath(os.path.join(base, 'credentials.json'))

credentials = ServiceAccountCredentials.from_json_keyfile_name(credentialspath, scope)
gc = gspread.authorize(credentials)
ws = gc.open_by_key('1_vJysEBiO_sJld2oq7eV-tFAoqG2gEyyUqr4BAwaDRI').sheet1

try:
    while True:
        result = instance.read()
        if result.is_valid():
            tAlert = result.temperature > 28
            hAlert = result.humidity >= 70
            if tAlert and hAlert:
                remarks = "熱中症の危険があります。"
                status = "9"
            elif tAlert:
                remarks = "室温が高いです。注意してください。"
                status = "1"
            elif hAlert:
                remarks = "湿度が高いです。注意してください。"
                status = "2"
            else:
                remarks = "熱中症の危険はありません。"
                status = "0"

            data = [str(datetime.datetime.now())
                   ,result.temperature
                   ,result.humidity
                   ,remarks
                   ,status]
            ws.insert_row(data,1)
            ws.delete_rows(11)
        time.sleep(10)
except KeyboardInterrupt:
    print("Cleanup")
    GPIO.cleanup()
