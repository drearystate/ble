import asyncio
import os
import subprocess
import pymysql
from bleak import BleakScanner, BleakClient

# Add MySQL database credentials
db_host = '209.126.1.228'
db_user = 'blenextinqu_drearystate'
db_password = 'Silverbook224!'
db_name = 'blenextinqu_devices'

# Function to get the device's hostname (serial)
def get_hostname():
    return subprocess.check_output('cat /proc/cpuinfo | grep Serial | cut -d \' \' -f 2', shell=True).decode().strip()

hostname = get_hostname()

# Function to write data to the MySQL database
def write_to_mysql(device_hostname, device_address, device_name, device_rssi, metadata, services, characteristics, descriptors, read_value, write_value):
    try:
        # Connect to the database
        connection = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)

        # Create a cursor to interact with the database
        cursor = connection.cursor()

        # SQL query to insert data into the database
        insert_query = """INSERT INTO devices 
                          (device_hostname, device_address, device_name, device_rssi, metadata, services, characteristics, descriptors, read_value, write_value) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        # Data to insert
        data = (device_hostname, device_address, device_name, device_rssi, metadata, services, characteristics, descriptors, read_value, write_value)

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
    scanner = BleakScanner()
    devices = await scanner.discover()

    for device in devices:
        try:
            client = BleakClient(device)
            await client.connect()

            services = await client.get_services()
            characteristics = [str(char.uuid) for service in services for char in service.characteristics]
            descriptors = [str(desc.uuid) for service in services for char in service.characteristics for desc in char.descriptors]
            
            # Replace this UUID with your actual characteristic's UUID
            characteristic_uuid = "00002a37-0000-1000-8000-00805f9b34fb"
            read_value = await client.read_gatt_char(characteristic_uuid)
            await client.write_gatt_char(characteristic_uuid, bytearray([0x01, 0x00]))
            write_value = await client.read_gatt_char(characteristic_uuid)

            # Insert data into the database
            write_to_mysql(hostname, device.address, device.name, device.rssi, device.metadata, services, characteristics, descriptors, read_value, write_value)

            await client.disconnect()

        except Exception as e:
            print(f"Error with device {device.address}: {e}")

# Schedule the script to run every minute
while True:
    asyncio.run(discover())
    time.sleep(60)
