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
    print("usage: python get_cybervision_attributes.py <output csv file>")
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

token = config["CONFIGURATION"]["token"]
server_address = config["CONFIGURATION"]["ServerAddress"]

with requests.Session() as s:
    requests.packages.urllib3.disable_warnings()

    try:

        groups_request = s.get(
            "https://" + server_address + "/api/1.0/group?token=" + token, verify=False)  # Fetch all groups

    except requests.exceptions.HTTPError as err:
        print("HTTP Error getting Groups from Cybervision")
        print(err)
        sys.exit(1)

groups_list = []
# vendor_name_list = []
# fw_version_list = []
# hw_version_list = []
# name_list = []
# serial_number_list = []
# name_s7_plc_list = []
# s7_bootloaderref_list = []
# s7_bootloaderver_list = []
# s7_fwver_list = []
# s7_hwref_list = []
# s7_hwver_list = []
# s7_modulename_list = []
# s7_moduleref_list = []
# s7_modulever_list = []
# s7_plcname_list = []
# s7_rack_list = []
# s7_serial_number_list = []
# s7_slot_list = []

for g in groups_request.json():
    # if 'components' in g:
    #     for c in g['components']:
    #         if 'ip' in c:
    #             ip = c['ip']
    #             if 'properties' in c:
    #
    #                 if 's7-slot' in c['properties']:
    #                     s7_slot = c['properties']['s7-slot']
    #                     s7_slot_list.append((s7_slot, ip))
    #
    #                 if 's7-serialnumber' in c['properties']:
    #                     s7_serialnumber = c['properties']['s7-serialnumber']
    #                     s7_serial_number_list.append((s7_serialnumber, ip))
    #
    #                 if 's7-rack' in c['properties']:
    #                     s7_rack = c['properties']['s7-rack']
    #                     s7_plcname_list.append((s7_rack, ip))
    #
    #                 if 's7-plcname' in c['properties']:
    #                     s7_plcname = c['properties']['s7-plcname']
    #                     s7_plcname_list.append((s7_plcname, ip))
    #
    #                 if 's7-modulever' in c['properties']:
    #                     s7_modulever = c['properties']['s7-modulever']
    #                     s7_modulever_list.append((s7_modulever, ip))
    #
    #                 if 's7-moduleref' in c['properties']:
    #                     s7_moduleref = c['properties']['s7-moduleref']
    #                     s7_moduleref_list.append((s7_moduleref, ip))
    #
    #                 if 's7-modulename' in c['properties']:
    #                     s7_modulename = c['properties']['s7-modulename']
    #                     s7_modulename_list.append((s7_modulename, ip))
    #
    #                 if 's7-hwver' in c['properties']:
    #                     s7_hwver = c['properties']['s7-hwver']
    #                     s7_hwver_list.append((s7_hwver, ip))
    #
    #                 if 's7-hwref' in c['properties']:
    #                     s7_hwref = c['properties']['s7-hwref']
    #                     s7_hwref_list.append((s7_hwref, ip))
    #
    #                 if 's7-fwver' in c['properties']:
    #                     s7_fwver = c['properties']['s7-fwver']
    #                     s7_fwver_list.append((s7_fwver, ip))
    #
    #                 if 's7-bootloaderver' in c['properties']:
    #                     s7_bootloaderver = c['properties']['s7-bootloaderver']
    #                     s7_bootloaderver_list.append((s7_bootloaderver, ip))
    #
    #                 if 's7-bootloaderref' in c['properties']:
    #                     s7_bootloaderref = c['properties']['s7-bootloaderref']
    #                     s7_bootloaderref_list.append((s7_bootloaderref, ip))
    #
    #                 if 'name-s7-plc' in c['properties']:
    #                     name_s7_plc = c['properties']['name-s7-plc']
    #                     name_s7_plc_list.append((name_s7_plc, ip))
    #
    # if 'components' in g:
    #     for c in g['components']:
    #         if 'ip' in c:
    #             ip = c['ip']
    #             if 'serial_number' in c:
    #                 serial_number = c['serial_number']
    #                 serial_number_list.append((serial_number, ip))
    #
    #             if 'vendor_name' in c:
    #                 vendor_name = c['vendor_name']
    #                 vendor_name_list.append((vendor_name, ip))
    #
    #             if 'name' in c:
    #                 name = c['name']
    #                 name_list.append((name, ip))
    #
    #             if 'hw_version' in c:
    #                 hw_version = c['hw_version']
    #                 hw_version_list.append((hw_version, ip))
    #
    #             if 'fw_version' in c:
    #                 fw_version = c['fw_version']
    #                 fw_version_list.append((fw_version, ip))
    #
    #             if 'vendor_name' in c:
    #                 vendor_name = c['vendor_name']
    #                 vendor_name_list.append((vendor_name, ip))

    if 'label' in g:
        if 'components' in g:
            for c in g['components']:
                if 'ip' in c:
                    group_name = g['label']
                    ip_address = c['ip']
                    groups_list.append((group_name, ip_address))

# s7_bootloaderref_list = []
# s7_bootloaderver_list = []
# s7_fwver_list = []
# s7_hwref_list = []
# s7_hwver_list = []
# s7_modulename_list = []
# s7_moduleref_list = []
# s7_modulever_list = []
# s7_plcname_list = []
# s7_rack_list = []
# s7_serial_number_list = []
# s7_slot_list = []

with open(outputCSVPath, 'wb+') as outputF:
    loc_out_writer = csv.writer(outputF)
    for d in groups_list:
        item = [d[0], '-1', d[1], 'By+Group+Name+(auto)/']
        loc_out_writer.writerow(item)
    # for d in fw_version_list:
    #     item = [d[0], '-1', d[1], 'By+FW+Version+(auto)/']
    #     loc_out_writer.writerow(item)
    # for d in hw_version_list:
    #     item = [d[0], '-1', d[1], 'By+HW+Version+(auto)/']
    #     loc_out_writer.writerow(item)
    # for d in name_list:
    #     item = [d[0], '-1', d[1], 'By+Name+(auto)/']
    #     loc_out_writer.writerow(item)
    # for d in serial_number_list:
    #     item = [d[0], '-1', d[1], 'By+Serial+Number+(auto)/']
    #     loc_out_writer.writerow(item)
    # for d in name_s7_plc_list:
    #     item = [d[0], '-1', d[1], 'By+Name-S7-PLC+(auto)/']
    #     loc_out_writer.writerow(item)
    # for d in s7_bootloaderref_list:
    #     item = [d[0], '-1', d[1], 'By+S7-Bootloaderref+(auto)/']
    #     loc_out_writer.writerow(item)
    # for d in s7_bootloaderver_list:
    #     item = [d[0], '-1', d[1], 'By+S7-Bootloaderver+(auto)/']
    #     loc_out_writer.writerow(item)
    # for d in s7_fwver_list:
    #     item = [d[0], '-1', d[1], 'By+S7-Fwver+(auto)/']
    #     loc_out_writer.writerow(item)
    # for d in s7_hwref_list:
    #     item = [d[0], '-1', d[1], 'By+S7-Hwref+(auto)/']
    #     loc_out_writer.writerow(item)
    # for d in s7_hwver_list:
    #     item = [d[0], '-1', d[1], 'By+S7-Hwver+(auto)/']
    #     loc_out_writer.writerow(item)
    # for d in s7_modulename_list:
    #     item = [d[0], '-1', d[1], 'By+S7-Modulename+(auto)/']
    #     loc_out_writer.writerow(item)
    # for d in s7_moduleref_list:
    #     item = [d[0], '-1', d[1], 'By+S7-Moduleref+(auto)/']
    #     loc_out_writer.writerow(item)
    # for d in s7_modulever_list:
    #     item = [d[0], '-1', d[1], 'By+S7-Modulever+(auto)/']
    #     loc_out_writer.writerow(item)
    # for d in s7_plcname_list:
    #     item = [d[0], '-1', d[1], 'By+S7-Plcname+(auto)/']
    #     loc_out_writer.writerow(item)
    # for d in s7_rack_list:
    #     item = [d[0], '-1', d[1], 'By+S7-Rack+(auto)/']
    #     loc_out_writer.writerow(item)
    # for d in s7_serial_number_list:
    #     item = [d[0], '-1', d[1], 'By+S7-SerialNumber+(auto)/']
    #     loc_out_writer.writerow(item)
    # for d in s7_slot_list:
    #     item = [d[0], '-1', d[1], 'By+S7-Slot+(auto)/']
    #     loc_out_writer.writerow(item)