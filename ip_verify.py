#!/usr/bin/env python3

#
# Script to check if a given ip is in the https://www.spamhaus.org/drop/drop.txt blacklist
#

# Modules Import
import sys
import os
import requests
import ipaddress
from datetime import datetime, timezone


# Variables & Configs
nets_url = 'https://www.spamhaus.org/drop/drop.txt'
store_file = '/tmp/spamhaus.drop.txt'


# Functions
def get_nets_from_url(url, store_file):
    '''Get the information from the given url and store it to the store_file'''
    resp = requests.get(url, timeout=5)
    if resp.status_code == 200:
        with open(store_file, 'wb') as f:
            f.write(resp.content)
        return
    else:
        print(f'ERROR: Download from {url} and write to {store_file} failed!')
        sys.exit(1)


def get_nets_from_file(f):
    '''Read from the given file the information and get back a list with all the lines'''
    try:
        with open(f) as f:
            content = f.read().split('\n')
            return list(filter(None, content)) # Filter out empty items in the list and return it
    except:
        print(f'ERROR: Unable to deal with file {f}')
        sys.exit(1)



# MAIN
# Check if argument is passed 
try:
    ip_to_check = sys.argv[1] # Read command line argument 
except:
    print(f'Argument is missing!')
    print(f'  Usage example: {sys.argv[0]} 148.133.18.2')
    sys.exit(1)

# If store file exist open it and put every line as an item in a list
if os.path.isfile(store_file):
    content_list_from_file = get_nets_from_file(store_file)
else:
    # If file not there yet download it
    get_nets_from_url(nets_url, store_file)
    content_list_from_file = get_nets_from_file(store_file)


# Check if information in the stored file are up-to-date
now = datetime.now(timezone.utc).replace(tzinfo=None) # Set current date/time
expiration_date_string = content_list_from_file[3].split(',')[1].strip() # Extract expiration string from file/list
expiration_date = datetime.strptime(expiration_date_string, "%d %b %Y %H:%M:%S %Z") # Convert expiration string to datetime object

if now > expiration_date:
    # If expired download the new file and load the fresh content_list
    get_nets_from_url(nets_url, store_file)
    content_list_from_file = get_nets_from_file(store_file)


# Create a new list with only the relevant network information
nets_list = []
for net in content_list_from_file[4:]:
    net = net.split(';')[0].strip()
    nets_list.append(net)

# Check if ip is valid
try:
    ipaddress.ip_address(ip_to_check)
except:
    print(f'ERROR: {ip_to_check} is not a valid ip!')
    sys.exit(1)

# Check if ip is part of one of the blacklisted subnet
for net in nets_list:
    if ipaddress.ip_address(ip_to_check) in ipaddress.ip_network(net):
        print('Matching')
        sys.exit(0)

# Print if not matching
print('Not matching')
sys.exit(1)

