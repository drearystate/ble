import asyncio
from bleak import BleakScanner
from datetime import datetime
import pymysql
import time

# Add MySQL database credentials
db_host = '209.126.1.228'
db_user = 'blenextinqu_drearystate'
db_password = 'Silverbook224!'
db_name = 'blenextinqu_devices'
# Set hostname
hostname = "JCI_Nissan_Service"

# Function to write data to the MySQL database
def write_to_mysql(timestamp, device_address, rssi, device_name, metadata, hostname):
    try:
        # Connect to the database
        connection = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)

        # Create a cursor to interact with the database
        cursor = connection.cursor()
        
        # SQL query to insert data into the database
        insert_query = """INSERT INTO devices (timestamp, device_address, rssi, device_name, metadata, hostname) 
                          VALUES (%s, %s, %s, %s, %s, %s)"""
        
        # Data to insert
        data = (timestamp, device_address, rssi, device_name, metadata, hostname)

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

# Discovery function
async def discover():
    # Initialize the BleakScanner
    scanner = BleakScanner()

    # Discover devices
    devices = await scanner.discover()

    # Update device info
    for device in devices:
        timestamp = datetime.now()
        write_to_mysql(timestamp, device.address, device.rssi, device.name, str(device.metadata), hostname)

# Continually discover devices and write to database
while True:
    asyncio.run(discover())
    time.sleep(60)  # Delay for 1 minute
