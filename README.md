# Yale Openhand Software
Software for Yale Openhand

# Install
```shell
$git clone https://github.com/tmxkn1/yale_openhand_software.git
$cd yale_openhand_software/DynamixelSDK

### Make sure you have Python 3.6+
python --version
### or 
python3 --version

$sudo python3 setup.py install
```

# Usage
```shell
$cd ../model_t
$python3 start.py -p=/dev/ttyUSB0
```
To see a list of arguments:
```shell
$python3 start.py -h

usage: python start.py [-p=<port_name>] [-b=<baudrate>] [-i=<dxl_id>] [-c=<current_limit>]
   or: python start.py -h | --help

Available arguments:

     -h, --help:          Show this help message
     -p, --port:          Port name of the Dynamixel device (default: COM5)
     -b, --baudrate:      Baudrate of the Dynamixel device (default: 1000000)
     -i, --dxl_id:        Dynamixel ID of the gripper (default: 1)
     -c, --current_limit: Current limit of the gripper (default: 400)
```
