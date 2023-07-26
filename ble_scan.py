import asyncio
from bleak import BleakScanner
from datetime import datetime
import pymysql
import time
import subprocess

# Add MySQL database credentials
db_host = '209.126.1.228'
db_user = 'blenextinqu_drearystate'
db_password = 'Silverbook224!'
db_name = 'blenextinqu_devices'

# Function to get Raspberry Pi's serial number (which will be used as hostname)
def get_serial():
    try:
        cpuinfo = subprocess.run(['cat', '/proc/cpuinfo'], capture_output=True, text=True).stdout
        for line in cpuinfo.split("\n"):
            if line.startswith('Serial'):
                serial = line.split(":")[1].strip()
                return serial
    except:
        return "ERROR"
    
# Set hostname
hostname = get_serial()

# Function to write data to the MySQL database
def write_to_mysql(timestamp, device_address, rssi, device_name, metadata, hostname):
    try:
        # Connect to the database
        connection = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)

        # Create a cursor to interact with the database
        cursor = connection.cursor()

        # SQL query to insert data into the database
        insert_query = """INSERT INTO devices (timestamp, device_address, rssi, device_name, metadata, device_hostname) 
                          VALUES (%s, %s, %s, %s, %s, %s)"""

        # Data to insert
        data = (timestamp, device_address, rssi, device_name, str(metadata), hostname)

        # Execute the SQL query with the data
        cursor.execute(insert_query, data)

        # Commit the changes to the database
        connection.commit()

    except Exception as e:
        print(f"Error inserting to MySQL: {e}")

    finally:
        # Close the database connection
        if connection:
            connection.close()

async def discover():
    # Initialize the BleakScanner
    scanner = BleakScanner()

    # Discover devices
    devices = await scanner.discover()

    for device in devices:
        timestamp = datetime.now()
        device_address = device.address
        rssi = device.rssi
        device_name = device.name
        metadata = device.metadata
        write_to_mysql(timestamp, device_address, rssi, device_name, metadata, hostname)

# Run the device discovery in a loop
while True:
    asyncio.run(discover())
    time.sleep(60)
