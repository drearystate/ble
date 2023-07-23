import os
import csv
import asyncio
from bleak import BleakScanner
from datetime import datetime, timedelta
from collections import defaultdict
import time
import logging
import pymysql
import requests  # added import statement for 'requests'

# Configure logging
log_file = 'ble_scan.log'
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file, 'a', 'utf-8', delay=False)
    ]
)

# Variables to handle device list and dates seen
device_dict = defaultdict(lambda: defaultdict(lambda: {'first_seen': None, 'last_seen': None, 'ignore': False}))
dates_seen = defaultdict(list)

# Variables to handle grouping of devices with similar signal strengths discovered at the same time
device_cache = []
cache_time_window = timedelta(seconds=5)
signal_strength_window = 5

# Add MySQL database credentials
db_host = '209.126.1.228'  # Replace with your database host (e.g., 'localhost' if the database is on the same server)
db_user = 'blenextinqu_drearystate'  # Replace with your database username
db_password = 'Silverbook224!'  # Replace with your database password
db_name = 'blenextinqu_devices'  # Replace with your database name

# Device Identifier (Replace 'JCI_Nissan_Service' with the desired device name)
device_identifier = 'JCI_Nissan_Service'

# Function to write data to the MySQL database
def write_to_mysql(date, address, first_seen, last_seen, ignore, device_name):
    try:
        # Connect to the database
        connection = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)

        # Create a cursor to interact with the database
        cursor = connection.cursor()

        # SQL query to insert data into the database
        insert_query = "INSERT INTO devices (date, address, first_seen, last_seen, ignore, device_name) VALUES (%s, %s, %s, %s, %s, %s)"

        # Data to insert
        data = (date, address, first_seen, last_seen, ignore, device_name)

        # Execute the SQL query with the data
        cursor.execute(insert_query, data)

        # Commit the changes to the database
        connection.commit()

        print("Data inserted successfully!")

    except Exception as e:
        print("Error:", e)

    finally:
        # Close the database connection
        if connection:
            connection.close()

# Function to check for script updates
def check_for_updates():
    try:
        response = requests.head(update_url)
        if response.status_code == 200 and 'Last-Modified' in response.headers:
            last_modified_str = response.headers['Last-Modified']
            last_modified = datetime.strptime(last_modified_str, '%a, %d %b %Y %H:%M:%S %Z')
            return last_modified
    except requests.exceptions.RequestException as e:
        print("Error checking for updates:", e)
    return None

# Function to update the script
def update_script():
    try:
        response = requests.get(update_url)
        if response.status_code == 200:
            with open(__file__, 'wb') as f:
                f.write(response.content)
            print("Script updated successfully!")
    except requests.exceptions.RequestException as e:
        print("Error updating script:", e)

# Check for updates and update the script
last_modified = check_for_updates()
if last_modified:
    current_last_modified = datetime.fromtimestamp(os.path.getmtime(__file__))
    if last_modified > current_last_modified:
        update_script()

async def discover():
    # Initialize the BleakScanner
    scanner = BleakScanner()

    # Discover devices
    devices = await scanner.discover()

    # Further code to handle discovered devices...

# Schedule the script to run every day
while True:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(discover())

    # Append the devices to a CSV file
    with open('devices.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Address", "First Seen", "Last Seen", "Ignore"])

        for date, devices in device_dict.items():
            for address, data in devices.items():
                writer.writerow([date, address, data['first_seen'], data['last_seen'], data['ignore']])

                # Write data to the MySQL database
                write_to_mysql(date, address, data['first_seen'], data['last_seen'], data['ignore'], device_identifier)

    time.sleep(60)

