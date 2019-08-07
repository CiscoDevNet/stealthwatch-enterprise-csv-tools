
# CSV-to-Subtree-XML
This bundle allows you to convert a CSV file with Host Group information into an XML file that you can import into StealthWatch as a Host Group Sub-Tree.

### Requirements
* Python (version 3.0+)
* a CSV file in the expected format

### Installation
1. Ensure Python 3 is installed.
   * To download and install Python 3, please visit https://www.python.org.
2. Download the `.py` files located in this directory.
    * <sub>Alternatively, advanced users can also use git to checkout / clone this project.</sub>

### CSV File Format
The CSV file should be formatted as follows:

```
"<IP-Addresses-or-Ranges>","<Host-Group-Path>"
```

Example CSV File:

```
"192.168.1.0/24","/HGA Test Group/TestParentA"
"192.168.2.0/24","/HGA Test Group/TestParentA"
"192.168.3.0/24","/HGA Test Group/TestParentA"
"192.168.4.0/24","/HGA Test Group/TestParentA"
"192.168.5.0/24","/HGA Test Group/TestParentB"
"192.168.6.0/24","/HGA Test Group/TestParentB"
"192.168.7.0/24","/HGA Test Group/TestParentB"
"192.168.8.0/24","/HGA Test Group/TestParentB"
"192.168.8.0/24,10.10.10.0/24","/HGA Test Group/TestParentC"
"10.10.2.1,10.10.5.3,10.10.0.0/16","/HGA Test Group/TestParentC%2FD"
```

<sub>NOTE: If you want to use a "/" or any other special character in your host group name or parent path, please use URL encoding (ex. "/" becomes "%2F").</sub>

<br/>

IP range entries may be in any of the following formats:

```
"n.n.n.n"
"n" OR "n.n" OR "n.n.n"
"n." OR "n.n." OR "n.n.n."
"n.n.n.n-n.n.n.n" OR " any number of ordinals separated by dash
"n.n.n.n/n"
"n/n" OR "n.n/n" OR "n.n.n/n"
"n./n" OR "n.n./n" OR n.n.n./n"
"nnnn::/n"
"nnnn:nnnn::" OR any sub-set of ordinals terminated in "::" or a full IPv6 literal address
```

### Configuration File
Before running the script, please ensure the configuration file `csv-to-subtree-xml.conf` has been modified with the correct settings. The configuration file contains the following parameters:
* `InsideOrOutsideHosts`
    * Inside or Outside Hosts: Select either [inside-hosts] or [outside-hosts], depending on where you plan to import the Host Groups
* `BeginParseAtRow`
    * Begin parsing the CSV file at the following row
* `BeginParseAtColumn`
    * Begin parsing the CSV file at the following column
* `StartingID`
    * Begin auto-incrementing HostGroupID from this value (Recommended is 20000)
* `DEBUG`
    * Set DEBUG=true to see verbose debugging messages.
* `ColumnMapping`
    * Used to map the columns of the CSV file to the expected format
        * <sub>Example 1: if first column represents IP ranges, and second column represents host group path, then: `ColumnMapping = 0,1`</sub>
        * <sub>Example 2: if first column represents host group path, and second column represents IP ranges, then: `ColumnMapping = 1,0`</sub>
* `SkipWithNoErrorOnBogusEntries`
    * If there is malformed data in the CSV file, set to true to continue the process anyways despite errors 
        * <sub>(Note: process will still stop if severe error occurs)</sub>

### Usage

1. Open up your command line
    * For Windows: open `cmd.exe`
        * For Mac: open `terminal`
        * For Linux: if you are on Linux, then you need no explanation
2. Ensure you have Python installed
    * run the command: `python --version`
        * if a version number is returned, then you already have Python installed
        * if an error is returned, then you need to install Python
            * Download Python at: https://www.python.org/downloads/
3. Navigate to the `csv-to-subtree-xml` directory where you saved and unzip the original zip file
    * run the command: `cd <your-csv-to-subtree-xml-directory>`
4. If necessary, edit the config file: `config.json`
    * <sub>NOTE: ensure you have selected \[inside-hosts\] or \[outside-hosts\] as your desired import location</sub>
5. Run the `csv-to-subtree-xml.py` script (with the CSV file's path as an argument) to generate your XML file
    * if you are in `<your-csv-to-subtree-xml-directory>` then you can run:
        * `python csv-to-subtree-xml.py <csv_file>`
    * if you are no longer in `<your-csv-to-subtree-xml-directory>` then you can run:
        * `python <your-csv-to-subtree-xml-directory>/csv-to-subtree-xml.py <csv_file>`
    * Examples:
        * `python csv-to-subtree-xml.py example.csv`
        * `python /usr/local/csv-to-subtree-xml.py /usr/local/example.csv`
6. An XML file will now appear in the same directory as your CSV file. To use in StealthWatch:
    1. Open the SMC Java Client
    2. Open the Host Group Editor (cntl-e)
    3. Right-click on the existing host group that you want to import the new host groups into
        * NOTE: If necessary, please create a new Host Group as a container for the host groups that are about to be imported
    4. Select `Import Host Group Sub Tree...` and import the newly created XML file

### Known issues
No known issues.

### Getting help
Use this project at your own risk (support not provided). *If you need technical support with Cisco Stealthwatch APIs, do one of the following:*

* Browse the Forum
    * Check out our [forum](https://community.cisco.com/t5/custom/page/page-id/customFilteredByMultiLabel?board=j-disc-dev-security&labels=stealthwatch) to pose a question or to see if any questions have already been answered by our community. We monitor these forums on a best effort basis and will periodically post answers. 
* Open A Case
    * To open a case by web: http://www.cisco.com/c/en/us/support/index.html
    * To open a case by email: tac@cisco.com
    * For phone support: 1-800-553-2447 (U.S.)
    * For worldwide support numbers: www.cisco.com/en/US/partner/support/tsd_cisco_worldwide_contacts.html

## Licensing info
This code is licensed under the BSD 3-Clause License. See [LICENSE](../LICENSE) for details. 


