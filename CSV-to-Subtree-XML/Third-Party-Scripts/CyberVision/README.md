
# get-cybervision-groups
The python script 'get_cybervision_groups.py' allows you to fetch the 'Group' objects from Cybervision and convert it into a CSV file that can be used in conjunction with the
CSV-to-Subtree-XML bundle to create an XML file that you can import into StealthWatch as a Host Group Sub-Tree.

### Requirements
* Python (version 3.0+)
* Python `Requests` Module


## Installation
1. Ensure Python 3 is installed.
   * To download and install Python 3, please visit https://www.python.org.
2. Ensure the Python `requests` module is installed.
   * For more information on the Python `requests` module, please visit https://pypi.org/project/requests/.
3. Download the `.py` files located in this directory.
    * <sub>Alternatively, advanced users can also use git to checkout / clone this project.</sub>

### Configuration File
Before running the script, please ensure the configuration file `cybervision.conf` has been modified with the correct settings. The configuration file contains the following parameters:
* `token`
    * This is the authentication token created via the Cybervision Web interface.
* `serverAddress`
    * The IP Address of your Cybervision instance.


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
3. Navigate to the `CyberVision` directory where you saved and unzip the original zip file
    * run the command: `cd <your-CyberVision-directory>`
4. If necessary, edit the config file: `cybervision.conf`
    
5. Run the `get_cybervision_groups.py` script to generate your CSV file
    * if you are in `<your-CyberVision-directory>` then you can run:
        * `python get_cybervision_groups.py <output_csv_file>`
    * if you are no longer in `<your-csv-to-subtree-xml-directory>` then you can run:
        * `python <our-CyberVision-directory>/get_cybervision_groups.py <output_csv_file>`
    * Examples:
        * `python get_cybervision_groups.py example.csv`
        * `python /usr/local/CyberVision/get_cybervision_groups.py /usr/local/CyberVision/example.csv`
6. A CSV file will be created in the path that you supplied i.e `/usr/local/CyberVision/example.csv`
    1. This CSV file is in the format for the CSV-to-SubTree-XML to injest.
    2. Follow the directions to run the csv-to-subtree-xml.py with this CSV file

### Known issues
No known issues.

### Getting help
Use this project at your own risk (support not provided). *If you need technical support with Cisco Stealthwatch, do one of the following:*

* Browse the Forum
    * Check out our [forum](https://community.cisco.com/t5/custom/page/page-id/customFilteredByMultiLabel?board=j-disc-dev-security&labels=stealthwatch) to pose a question or to see if any questions have already been answered by our community. We monitor these forums on a best effort basis and will periodically post answers. 
* Open A Case
    * To open a case by web: http://www.cisco.com/c/en/us/support/index.html
    * To open a case by email: tac@cisco.com
    * For phone support: 1-800-553-2447 (U.S.)
    * For worldwide support numbers: www.cisco.com/en/US/partner/support/tsd_cisco_worldwide_contacts.html

## Licensing info
This code is licensed under the BSD 3-Clause License. See [LICENSE](../../../LICENSE) for details. 


