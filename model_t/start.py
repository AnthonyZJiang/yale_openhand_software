import os
import time
import sys
from modelt import ModelT

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def initiate_gripper(port, baudrate, dxl_id, current_limit):
    gripper = ModelT()
    gripper.device_name = port
    gripper.baudrate = baudrate
    gripper.dxl_id = dxl_id
    gripper.default_current_limit = current_limit
    print(f"Using port: {port}")
    print(f"Using baud rate: {baudrate}")
    print(f"Using dxl id: {dxl_id}")
    print(f"Using current limit: {current_limit}")
    if not gripper.connect():
        exit(0)
    if gripper.check_hw_error()[1]:
        gripper.reboot()
        time.sleep(1)
    gripper.set_defaults()
    return gripper

def run(gripper:ModelT, upper_current_limit):
    current = 300
    current_limit = (0, upper_current_limit)
    while True:
        print("========================================")
        print(f"Current gripping current: {current}. Press 'q' to increase and 'a' to reduce. \nclose gripper: 'l' | open gripper: 'o' | reboot: 'r' | quit: 'ESC'\nAny other key to latch closed state for 5 seconds!")
        keyboard = getch()
        print(keyboard)
        if keyboard == chr(0x1b):
            exit(0)
        if keyboard == 'o':
            gripper.open_gripper()
            continue
        if keyboard == 'l':
            gripper.close_gripper(current_goal=current)
            continue
        if keyboard == 'r':
            gripper.reboot()
            continue
        if keyboard == 'q':
            current = min(current+50, current_limit[1])
            continue
        if keyboard == 'a':
            current = max(current-50, current_limit[0])
            continue
        gripper.latch_gripping(seconds=5, current_goal=current)


if __name__ == "__main__":
    port = 'COM5'
    baudrate = 1000000
    dxl_id = 1
    current_limit = 400
    for arg in sys.argv:
        if not arg.startswith("-"):
            continue
        if arg == "-h" or arg=="--help":
            print("\nusage: python start.py [-p=<port_name>] [-b=<baudrate>] [-i=<dxl_id>] [-c=<current_limit>]")
            print("   or: python start.py -h | --help")
            print("\nAvailable arguments:\n")
            print("     -h, --help:          Show this help message")
            print("     -p, --port:          Port name of the Dynamixel device (default: COM5)")
            print("     -b, --baudrate:      Baudrate of the Dynamixel device (default: 1000000)")
            print("     -i, --dxl_id:        Dynamixel ID of the gripper (default: 1)")
            print("     -c, --current_limit: Current limit of the gripper (default: 400)")
            print("")
            exit(0)
        if arg.startswith("-p=") or arg.startswith("--port="):
            port = arg.split("=")[1]
        elif arg.startswith("-b=") or arg.startswith("--baudrate="):
            baudrate = arg.split("=")[1]
        elif arg.startswith("-i=") or arg.startswith("--dxl_id="):
            dxl_id = arg.split("=")[1]
        elif arg.startswith("-c=") or arg.startswith("--current_limit="):
            current_limit = arg.split("=")[1]
        else:
            print(f"Unknown argument: {arg}")
            exit(0)
    
    gripper = initiate_gripper(port, baudrate, dxl_id, current_limit)
    run(gripper, current_limit)
    
        