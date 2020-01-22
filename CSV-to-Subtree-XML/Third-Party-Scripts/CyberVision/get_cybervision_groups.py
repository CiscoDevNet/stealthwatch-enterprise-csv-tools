#!/usr/bin/env python

"""

FOR DETAILS AND INSTRUCTIONS, PLEASE VISIT: https://github.com/CiscoDevNet/stealthwatch-csv-tools/csv-to-subtree-xml


Copyright (c) 2020, Cisco Systems, Inc. All rights reserved.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import csv
import os
import sys
import requests
import configparser

# Sets directory info
workingDir = os.path.dirname(os.path.realpath(__file__))

if len(sys.argv) == 2:

    outputCSVPath = sys.argv[1]
    if outputCSVPath.startswith(".."):
        print("ERROR: please try again with full directory path")
        sys.exit()

else:
    # if incorrect number of parameters given
    print("usage: python get_cybervision_groups.py <output csv file>")
    sys.exit()

if os.path.isfile(outputCSVPath):
    os.remove(outputCSVPath)

config_file = "cybervision.conf"
if os.path.isfile(config_file) and config_file.upper().endswith('.CONF'):
    config = configparser.ConfigParser()
    config.read(config_file)
else:
    print('No Config File found. Exiting.')
    sys.exit()

# Extract Token and Server address from config file
token = config["CONFIGURATION"]["token"]
server_address = config["CONFIGURATION"]["ServerAddress"]

with requests.Session() as s:
    requests.packages.urllib3.disable_warnings()

    try:

        # Fetch all group objects from Cybervision
        groups_request = s.get(
            "https://" + server_address + "/api/1.0/group?token=" + token, verify=False)

    except requests.exceptions.HTTPError as err:
        print("HTTP Error getting Groups from Cybervision")
        print(err)
        sys.exit(1)

groups_list = []

# Parse group['label'] and IP address from object
for g in groups_request.json():
    if 'label' in g:
        if 'components' in g:
            for c in g['components']:
                if 'ip' in c:
                    group_name = g['label']
                    ip_address = c['ip']
                    groups_list.append((group_name, ip_address))

# Write the Group name in HG form: IP Address, 'HG Path'
with open(outputCSVPath, 'w+') as outputF:
    loc_out_writer = csv.writer(outputF)
    for d in groups_list:
        item = [d[1], 'By+Group+Name+(auto)/' + d[0]]
        print(item)
        loc_out_writer.writerow(item)
