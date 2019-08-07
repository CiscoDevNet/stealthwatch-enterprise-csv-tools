#!/usr/bin/env python

"""

FOR DETAILS AND INSTRUCTIONS, PLEASE VISIT: https://github.com/CiscoDevNet/stealthwatch-csv-tools/csv-to-subtree-xml


Copyright (c) 2019, Cisco Systems, Inc. All rights reserved.
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


import logging
import re
import os
import sys
import csv
import urllib
import configparser
from xml.sax.saxutils import escape

version = "1.2.0"
releaseDate = "8/7/2019"

class HostGroup(object):
    id = None
    name = None
    childHostGroups = None
    childHostGroupNames = None
    ipAddresses = None
    path = None
    touched = None
    parentID = None

    def __init__(self, hostGroupID, name, path, parentID):
        self.id = hostGroupID
        self.name = name
        self.childHostGroups = set()
        self.childHostGroupNames = set()
        self.ipAddresses = {}
        self.path = path
        self.touched = False
        self.parentID = parentID

    def addChildHostGroup(self, childHostGroup):
        self.childHostGroups.add(childHostGroup)
        self.childHostGroupNames.add(childHostGroup.name)

    def addIpAddress(self, ipAddress, lineNumber):
        self.ipAddresses[ipAddress] = lineNumber

    def hasChild(self, childName):
        for child in set(self.childHostGroups):
            if child.name == childName:
                return True
        return False

    def equals(self, otherHostGroup):
        if otherHostGroup is None:
            return False
        if self.name != otherHostGroup.name:
            return False
        if self.id != otherHostGroup.id:
            return False
        if self.path != otherHostGroup.path:
            return False
        if self.parentID != otherHostGroup.parentID:
            return False
        if self.ipAddresses.keys() != otherHostGroup.ipAddresses.keys():
            return False
        if self.childHostGroupNames != otherHostGroup.childHostGroupNames and self.name != urllib.parse.quote_plus("[inside-hosts]") and self.name != urllib.parse.quote_plus("[outside-hosts]"):
            return False
        return True

    def getChild(self, childName):
        for child in set(self.childHostGroups):
            if child.name == childName:
                return child
        return None

class Utility(object):
    defaultID = None
    fileDir = None
    prefix = None
    continueWithErrors = None
    primaryLog = None
    beginParseAtRow = None
    beginParseAtColumn = None
    removeHostGroups = None
    error = None
    severeError = None
    debug = None

    def __init__(self, defaultID):
        self.defaultID = int(defaultID)
        self.fileDir = None
        self.prefix = None
        self.continueWithErrors = None
        self.primaryLog = None
        self.beginParseAtRow = None
        self.beginParseAtColumn = None
        self.removeHostGroups = None
        self.error = None
        self.severeError = None
        self.debug = None

    def printDataForHostGroupWithLog(self, parentHG, logger):
        tree = "\n"
        tree += "ID = " + repr(parentHG.id) + " :: NAME = " + parentHG.name + " :: path = " + parentHG.path + " :: ParentID = " + repr( parentHG.parentID) + " :: touched = " + repr(parentHG.touched) + " :: # of IPaddresses = " + repr(len(parentHG.ipAddresses)) + "\n"
        tree += self.printChildrenWithLog(parentHG, 1, logger)
        logger.info(tree)

    def printChildrenWithLog(self, parentHG, tabSize, logger):
        branch = ""
        for childHG in set(parentHG.childHostGroups):
            tabs = ""
            for i in range(0, tabSize):
                tabs += "\t"
            branch += tabs + "ID = " + repr(childHG.id) + " :: NAME = " + childHG.name + " :: path = " + childHG.path + " :: ParentID = " + repr(childHG.parentID) + " :: touched = " + repr(childHG.touched) + " :: # of IPaddresses = " + repr(len(childHG.ipAddresses)) + "\n"
            branch += self.printChildrenWithLog(childHG, tabSize + 1, logger)
        return branch

    def printDataForHostGroup(self, parentHG):
        print("ID = " + repr(parentHG.id) + " :: NAME = " + parentHG.name + " :: path = " + parentHG.path + " :: ParentID = " + repr(parentHG.parentID) + " :: touched = " + repr(parentHG.touched) + " :: # of IPaddresses = " + repr(len(parentHG.ipAddresses)))
        self.printChildren(parentHG, 1)

    def printChildren(self, parentHG, tabSize):
        for childHG in set(parentHG.childHostGroups):
            tabs = ""
            for i in range(0, tabSize):
                tabs += "\t"
            print(tabs + "ID = " + repr(childHG.id) + " :: NAME = " + childHG.name + " :: path = " + childHG.path + " :: ParentID = " + repr(childHG.parentID) + " :: touched = " + repr(childHG.touched) + " :: # of IPaddresses = " + repr(len(childHG.ipAddresses)))
            self.printChildren(childHG, tabSize + 1)

    def preCheckHostGroupsFromCSV(self, topLevelHostGroup):
        hostGroupStack = []
        hostGroupStack.append(topLevelHostGroup)
        errorInPreCheck = ""
        while hostGroupStack:
            thisHostGroup = hostGroupStack.pop()
            errorInPreCheck += self.checkHostGroupName(thisHostGroup.name)
            errorInPreCheck += self.checkHostGroupIPAddresses(thisHostGroup.ipAddresses)
            for child in set(thisHostGroup.childHostGroups):
                hostGroupStack.append(child)
        return errorInPreCheck

    @staticmethod
    def checkHostGroupIPAddresses(ipAddresses):
        errorInIPCheck = ""
        for ip in set(ipAddresses.keys()):
            matchFound = False
            # for n.n.n.n or n.n.n. or n.n.n or n.n. or n.n or n. or n
            # also for n.n.n.n/n or n.n.n./n or n.n.n/n or n.n./n or n.n/n or
            # n./n or n/n
            pattern = re.compile("^([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.?([01]?\\d\\d?|2[0-4]\\d|25[0-5])?\\.?([01]?\\d\\d?|2[0-4]\\d|25[0-5])?\\.?([01]?\\d\\d?|2[0-4]\\d|25[0-5])?(/[1-3]?[0-9])?$")
            if pattern.match(ip):
                matchFound = True
            # for n.n.n.n-n.n.n.n
            pattern = re.compile("^([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])-([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])$")
            if pattern.match(ip):
                matchFound = True
            # for IPv6
            pattern = re.compile("^(?:[0-9a-fA-F]{1,4}:)?(?:[0-9a-fA-F]{1,4}:)?(?:[0-9a-fA-F]{1,4}:)?(?:[0-9a-fA-F]{1,4}:)?(?:[0-9a-fA-F]{1,4}:)?(?:[0-9a-fA-F]{1,4}:)?(?:[0-9a-fA-F]{1,4}:)?[0-9a-fA-F]{1,4}(::)?(/[1]?[0-9]?[0-9])?$")
            if pattern.match(ip):
                matchFound = True
            if matchFound is False:
                errorInIPCheck += " - IP address range at line " + repr((int(ipAddresses.get(ip)) + 1)) + " (\"" + ip + "\") does not comply with the expected format\n"
        return errorInIPCheck

    @staticmethod
    def checkHostGroupName(name):
        errorInNameCheck = ""
        for ch in list(urllib.parse.unquote_plus(name)):
            if ord(ch) < 32:
                errorInNameCheck += " - Name '" + name + "' CANNOT contain lower control characters\n"
            if ord(ch) >= 127:
                errorInNameCheck += " - Name '" + name + "' CANNOT contain extended ASCII characters '" + repr(ord(ch)) + "'\n"
        return errorInNameCheck

    @staticmethod
    def readFile(filename):
        f = open(filename, "r")
        lines = f.readlines()
        f.close()
        return lines

    def getNewHostGroupID(self, fileName):
        response = self.readFile(fileName)
        for line in list(response):
            if line.__contains__(" id=\"") is True:
                return int(line.split(" id=\"")[1].split("\"")[0])
        return -1

    @staticmethod
    def initializeLogger(logFile, logName):
        logger = logging.getLogger(logName)
        logger.setLevel(logging.INFO)
        # create the logging file handler
        fh = logging.FileHandler(logFile)
        formatter = logging.Formatter('%(asctime)s: %(levelname)s: %(message)s')
        fh.setFormatter(formatter)
        # add handler to logger object
        logger.addHandler(fh)
        return logger

    def createLocalXMLFile(self, topLevelHostGroup, csvFilePath, isInsideHosts):
        filePath = csvFilePath.replace(".csv", ".xml")
        xmlFile = open(filePath, "w")
        xmlFile.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n<sub-group-tree>\n")
        self.printSingleHostGroupToXMLFile(topLevelHostGroup, topLevelHostGroup, isInsideHosts, xmlFile, 0)
        xmlFile.write("</sub-group-tree>")
        xmlFile.close()

    def printSingleHostGroupToXMLFile(self, thisHostGroup, topLevelHostGroup, isInsideHosts, xmlFile, tabSize):
        if thisHostGroup.equals(topLevelHostGroup) is False:
            for i in range(0, tabSize):
                xmlFile.write("\t")
            if thisHostGroup.id == -1:
                thisHostGroup.id = self.defaultID
                self.defaultID += 1
            if isInsideHosts is True:
                xmlFile.write("<host-group id=\"" + escape(repr(thisHostGroup.id)) + "\" name=\"" + escape(urllib.parse.unquote_plus(thisHostGroup.name)) + "\" host-baselines=\"true\" suppress-excluded-services=\"true\" inverse-suppression=\"false\" host-trap=\"false\">\n")
            else:
                xmlFile.write("<host-group id=\"" + escape(repr(thisHostGroup.id)) + "\" name=\"" + escape(urllib.parse.unquote_plus(thisHostGroup.name)) + "\" host-baselines=\"false\" suppress-excluded-services=\"true\" inverse-suppression=\"false\" host-trap=\"false\">\n")
            for ip in set(thisHostGroup.ipAddresses.keys()):
                for i in range(0, tabSize + 1):
                    xmlFile.write("\t")
                xmlFile.write("<ip-address-ranges>" + escape(ip) + "</ip-address-ranges>\n")
        for child in set(thisHostGroup.childHostGroups):
            self.printSingleHostGroupToXMLFile(child, topLevelHostGroup, isInsideHosts, xmlFile, tabSize + 1)
        if thisHostGroup.equals(topLevelHostGroup) is False:
            for i in range(0, tabSize):
                xmlFile.write("\t")
            xmlFile.write("</host-group>\n")

    def getCSVHostGroups(self, topLevelGroupName, csvFile, columnMapping):
        if topLevelGroupName.startswith("/") is True:
            topLevelGroupName = topLevelGroupName[1:]
        topLevelGroupNameSplit = topLevelGroupName.split("/")
        topLevelGroupPath = ""
        for i in range(0, len(topLevelGroupNameSplit) - 1):
            if i > 0:
                topLevelGroupPath += "/"
            topLevelGroupPath += topLevelGroupNameSplit[i]
        topLevelHostGroup = HostGroup(-1, urllib.parse.quote_plus(topLevelGroupNameSplit[len(topLevelGroupNameSplit) - 1]), topLevelGroupPath, -1)
        if topLevelHostGroup.name == urllib.parse.quote_plus("[inside-hosts]"):
            topLevelHostGroup.id = 1
            self.removeHostGroups = False
        elif topLevelHostGroup.name == urllib.parse.quote_plus("[outside-hosts]"):
            topLevelHostGroup.id = 0
            self.removeHostGroups = False
        with open(csvFile) as f:
            reader = csv.reader(f)
            rowCount = 0
            for row in reader:
                if rowCount >= self.beginParseAtRow:
                    ipRange = row[int(columnMapping[0 + self.beginParseAtColumn])].replace("\"", "").strip()
                    rawGroup = row[int(columnMapping[1 + self.beginParseAtColumn])].replace("\"", "")
                    #hostGroupName = urllib.parse.quote_plus(urllib.parse.unquote_plus(row[int(columnMapping[1 + self.beginParseAtColumn])].replace("\"", "").strip()))
                    if len(rawGroup) > 0:
                        rawGroup = rawGroup.strip()
                    if rawGroup.startswith("/"):
                        rawGroup = rawGroup[1:].strip()
                    if rawGroup.endswith("/"):
                        rawGroup = rawGroup[:- 1].strip()
                    if rawGroup.__contains__("//"):
                        rawGroup.replace("//", "/").strip()

                    hostGroupName = ""
                    path = ""
                    if rawGroup.__contains__("/"):
                        hostGroupName = urllib.parse.quote_plus(urllib.parse.unquote_plus(rawGroup[rawGroup.rfind("/") + 1:]))
                        path = rawGroup[:rawGroup.rfind("/")]
                    else:
                        hostGroupName = urllib.parse.quote_plus(urllib.parse.unquote_plus(rawGroup))
                        path = ""
                    hostGroupsInPath = path.split("/")
                    tmpHG = topLevelHostGroup
                    for subGroupName in hostGroupsInPath:
                        subGroupName = urllib.parse.quote_plus(urllib.parse.unquote_plus(subGroupName.strip()))
                        if subGroupName != "":
                            if tmpHG.hasChild(subGroupName) is False:
                                tmpPath = tmpHG.path
                                if tmpPath == "":
                                    tmpPath = tmpHG.name
                                else:
                                    tmpPath += "/" + tmpHG.name
                                if tmpPath.__contains__("//") is True:
                                    tmpPath = tmpPath.replace("//", "/")
                                child = HostGroup(-1, subGroupName, tmpPath, -1)
                                tmpHG.addChildHostGroup(child)
                            tmpHG = tmpHG.getChild(subGroupName)
                    if hostGroupName != "" and tmpHG.hasChild(hostGroupName) is False:
                        tmpPath = tmpHG.path
                        if tmpPath == "":
                            tmpPath = tmpHG.name
                        else:
                            tmpPath += "/" + tmpHG.name
                        if tmpPath.__contains__("//") is True:
                            tmpPath = tmpPath.replace("//", "/")
                        child = HostGroup(-1, hostGroupName, tmpPath, -1)
                        tmpHG.addChildHostGroup(child)
                    if hostGroupName != "":
                        child = tmpHG.getChild(hostGroupName)
                        ipRangeSplit = ipRange.split(",")
                        for individualIP in ipRangeSplit:
                            child.addIpAddress(individualIP, rowCount)
                        tmpHG.addChildHostGroup(child)
                rowCount += 1
        return topLevelHostGroup

    def run(self, csvFile, configFile, actionsLogFile):
        primaryLogFile = actionsLogFile[:actionsLogFile.rfind("/") + 1] + csvFile[csvFile.rfind("/") + 1:].replace(".csv", ".log")
        self.fileDir = os.path.dirname(os.path.realpath(__file__))
        if self.fileDir.endswith(os.pathsep) is False:
            self.fileDir += os.pathsep
        self.beginParseAtRow = 0
        self.beginParseAtColumn = 0
        self.prefix = ""
        self.continueWithErrors = False
        columnMapping = None

        self.primaryLog = self.initializeLogger(primaryLogFile, "Primary Log")
        self.primaryLog.info("Begin Generating Sub-Tree XML")
        print("Begin Generating Sub-Tree XML")

        self.error = False
        self.severeError = False
        self.debug = False

        self.primaryLog.info("Processing schema file: " + configFile)
        print("Processing schema file: " + configFile)
        configFileSplit = self.readFile(configFile)
        requiredFieldsPresent = [False, False, False]
        for configLine in configFileSplit:
            parameter = configLine.split("=")[0].strip()
            value = configLine.split("=")[1].strip()
            if parameter == "BeginParseAtRow":
                self.beginParseAtRow = int(value)
                requiredFieldsPresent.pop()
            elif parameter == "BeginParseAtColumn":
                self.beginParseAtColumn = int(value)
                requiredFieldsPresent.pop()
            elif parameter == "Prefix":
                self.prefix = value
                requiredFieldsPresent.pop()
            elif parameter == "ColumnMapping":
                columnMapping = value.split(",")
            elif parameter == "SkipWithNoErrorOnBogusEntries":
                if value.lower() == "true":
                    self.continueWithErrors = True
            elif parameter == "debug":
                if value.lower() == "true":
                    self.debug = True

        if len(requiredFieldsPresent) != 0:
            self.primaryLog.critical("Error processing schema file: " + configFile)
            self.primaryLog.critical("Required fields missing from schema file.")
            self.primaryLog.critical("Aborting Process.")
            print("Error processing schema file: " + configFile)
            print("Required fields missing from schema file.")
            print("Aborting Process.")
            self.error = True

        if self.error is False or self.continueWithErrors is True:
            self.primaryLog.info("Done processing schema file")
            self.primaryLog.info("Processing CSV input file: " + csvFile)
            print("Done processing schema file")
            print("Processing CSV input file: " + csvFile)

            topLevelHostGroupFromCSV = self.getCSVHostGroups(self.prefix, csvFile, columnMapping)
            # self.printDataForHostGroup(topLevelHostGroupFromCSV)
            if topLevelHostGroupFromCSV is None:
                self.primaryLog.critical("Error: processing CSV file: " + csvFile)
                self.primaryLog.critical("ERROR: Either the CSV file is empty or BeginParseAtRow is not set correctly.")
                self.primaryLog.critical("Aborting Process")
                print("Error: processing CSV file: " + csvFile)
                print("ERROR: Either the CSV file is empty or BeginParseAtRow is not set correctly.")
                print("Aborting Process")
                sys.exit()

            self.primaryLog.info("Done processing CSV input file")
            self.primaryLog.info("Running pre-check on processed CSV data")
            print("Done processing CSV input file")
            print("Running pre-check on processed CSV data")

            errorFound = self.preCheckHostGroupsFromCSV(topLevelHostGroupFromCSV)
            if len(errorFound) > 0:
                self.primaryLog.critical("Error In Pre-Check!")
                self.primaryLog.critical(errorFound)
                print("Error In Pre-Check!")
                print(errorFound)
            else:
                self.primaryLog.info("No Error In Pre-Check...")
                print("No Error In Pre-Check...")

            if len(errorFound) == 0 or self.continueWithErrors is True:
                if len(errorFound) > 0 and self.continueWithErrors is True:
                    self.primaryLog.info("Continuing process despite errors...")
                    print("Continuing process despite errors...")
                if self.debug is True:
                    self.primaryLog.info("DEBUG: printing CSV Host Group tree structure.")
                    self.printDataForHostGroupWithLog(topLevelHostGroupFromCSV, self.primaryLog)

                self.primaryLog.info("Creating local XML File")
                print("Creating local XML File")
                self.createLocalXMLFile(topLevelHostGroupFromCSV, csvFile, self.prefix.__contains__("[inside-hosts]"))

                self.primaryLog.info("Done Generating Sub-Tree XML.")
                print("Done Generating Sub-Tree XML.")
            else:
                self.primaryLog.critical("Process aborted due to error(s). If you wish to continue despite errors, please configure process_groups.sh to allow this.")
                print("Process aborted due to error(s). If you wish to continue despite errors, please configure process_groups.sh to allow this.")
                sys.exit()



csvFile = None;

fileDir = os.path.dirname(os.path.realpath(__file__))
workingDir = os.getcwd()

if len(sys.argv) == 2:
    if sys.argv[1] == "--version":
        print("Version: " + version)
        print("Release Date: " + releaseDate)
        sys.exit()
    else:
        # accepts IP address as a parameter
        csvFile = sys.argv[1]
        if csvFile.startswith(".."):
            print("ERROR: please try again with full directory path")
            sys.exit()
        # if "." passed, replace with fileDir
        if csvFile.startswith("."):
            csvFile = csvFile.replace(".", workingDir, 1)
        # if relative path given, add full path
        if not csvFile.startswith("/"):
            csvFile = workingDir + "/" + csvFile
        # removes a "/" from the end of the file to normalize
        if csvFile.endswith("/"):
            csvFile = csvFile[:-1]
        if not os.path.isfile(csvFile):
            print("ERROR: The file " + csvFile + " does not exist")
            sys.exit()
else:
    # if incorrect number of parameters given
    print("usage: python csv-to-subtree-xml.py <csv_file>")
    sys.exit()

config_file = "csv-to-subtree-xml.conf"
if os.path.isfile(config_file) and config_file.upper().endswith('.CONF'):
    config = configparser.ConfigParser()
    config.read(config_file)

schemaFile = fileDir + "/" + csvFile[csvFile.rfind("/") + 1:].replace(".csv", ".schema")
if os.path.isfile(schemaFile) is True:
    os.remove(schemaFile)

f = open(schemaFile, "w")
f.write("SkipWithNoErrorOnBogusEntries=" + config["CONFIGURATION"]["SkipWithNoErrorOnBogusEntries"] + "\n")
f.write("ColumnMapping=" + config["CONFIGURATION"]["ColumnMapping"] + "\n")
f.write("BeginParseAtRow=" + config["CONFIGURATION"]["BeginParseAtRow"] + "\n")
f.write("BeginParseAtColumn=" + config["CONFIGURATION"]["BeginParseAtColumn"] + "\n")
f.write("debug=" + config["CONFIGURATION"]["DEBUG"] + "\n")
f.write("Prefix=/[domain]/[host-group-tree]/" + config["CONFIGURATION"]["InsideOrOutsideHosts"] + "\n")
f.close()

print("Configuration Parameters:")
print(" - SkipWithNoErrorOnBogusEntries=" + config["CONFIGURATION"]["SkipWithNoErrorOnBogusEntries"])
print(" - ColumnMapping=" + config["CONFIGURATION"]["ColumnMapping"])
print(" - BeginParseAtRow=" + config["CONFIGURATION"]["BeginParseAtRow"])
print(" - BeginParseAtColumn=" + config["CONFIGURATION"]["BeginParseAtColumn"])
print(" - debug=" + config["CONFIGURATION"]["DEBUG"])
print(" - Prefix=" + config["CONFIGURATION"]["InsideOrOutsideHosts"])

util = Utility(config["CONFIGURATION"]["StartingID"])
util.run(csvFile, schemaFile, fileDir + "/" + csvFile[csvFile.rfind("/") + 1:].replace(".csv", ".actions"))

if os.path.isfile(schemaFile) is True:
    os.remove(schemaFile)
