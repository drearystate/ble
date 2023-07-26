import os
import csv
import asyncio
from bleak import BleakScanner
from datetime import datetime, timedelta
import time
import logging
import pymysql
import requests
import subprocess

# Add MySQL database credentials
db_host = '209.126.1.228'
db_user = 'blenextinqu_drearystate'
db_password = 'Silverbook224!'
db_name = 'blenextinqu_devices'

git_repo = 'https://github.com/drearystate/ble.git'

# Get the hostname (which is the Raspberry Pi's serial)
hostname = subprocess.check_output(['cat', '/proc/cpuinfo', '|', 'grep', 'Serial', '|', 'cut', '-d', ' ', '-f', '2']).decode().strip()

def check_for_updates():
    # Check for updates every 6 hours
    response = requests.get(git_repo)
    if response.status_code == 200:
        with open(__file__ + '.new', 'wb') as f:
            f.write(response.content)
        os.rename(__file__, __file__ + '.old')  # rename the current script
        os.rename(__file__ + '.new', __file__)  # rename the new script to the old script's name
        os.execv(__file__, [])  # restart the script

# Function to write data to the MySQL database
def write_to_mysql(device):
    connection = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = connection.cursor()
    insert_query = """INSERT INTO devices (device_hostname, device_address, device_name, rssi, timestamp) VALUES (%s, %s, %s, %s, %s)"""
    cursor.execute(insert_query, (hostname, device.address, device.name, device.rssi, datetime.now()))
    connection.commit()
    connection.close()

async def discover():
    scanner = BleakScanner()
    devices = await scanner.discover()
    for device in devices:
        write_to_mysql(device)

while True:
    check_for_updates()
    asyncio.run(discover())
    time.sleep(60)
