from dynamixel_sdk import *
from controltable import *


class ModelT:
    port_handler: PortHandler
    packet_handler: Protocol2PacketHandler

    device_name = 'COM5'
    baudrate = 1000000
    dxl_id = 1
    default_current_limit = 400

    torque = False
    debug_msg = False
    

    def connect(self):
        if not self._open_port():
            print("Connection failed.")
            return False        
        print("Model T has been successfully connected.")
        return True
    
    def disconnect(self):
        self.port_handler.closePort()

    def set_current_limit(self, value):
        if self.torque:
            print("[ERROR] Torque is currently enabled. Disable torque before setting current limit.")
            return False
        if self._write_2byte_tx_rx(ADDR_PRO_CURRENT_LIMIT, value):
            print(f"Current limit has been set to {value}.")
            return True
        else:
            print("[ERROR] Failed to set current limit.")
            return False

    def set_defaults(self):
        if not self.set_current_limit(self.default_current_limit):
            return False
        if self._write_1byte_tx_rx(ADDR_PRO_OPERATING_MODE, OP_CURRENT_CONTROL_MODE):
            print("Operating mode has been set to current control mode.")
            print("Defaults have been successfully set.")
            return True
        else:
            print("[ERROR] Failed to set operating mode.")
            return False

    def torque_on(self):
        if not self.torque:
            self.torque = self._write_1byte_tx_rx(ADDR_PRO_TORQUE_ENABLE, TORQUE_ENABLE)
        return self.torque

    def torque_off(self):
        if self.torque:
            self.torque = self._write_1byte_tx_rx(ADDR_PRO_TORQUE_ENABLE, TORQUE_DISABLE)
        return self.torque

    def reboot(self):
        self.packet_handler.reboot(self.port_handler, self.dxl_id)
    
    def check_hw_error(self):
        comm_state = False
        data, dxl_comm_result, dxl_error = self.packet_handler.read1ByteTxRx(self.port_handler, self.dxl_id, ADDR_PRO_HW_ERR_STATES)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0 and dxl_error != ERRBIT_ALERT:
            print("%s" % self.packet_handler.getRxPacketError(dxl_error))
        elif dxl_error == ERRBIT_ALERT:
            self._print_debug(f"Read 1 byte from {ADDR_PRO_HW_ERR_STATES}")
            comm_state = True
            err_state = True
            if data >> 0 & 1:
                print("[ERROR] Shutdown due to input voltage error.")
            elif data >> 2 & 1:
                print("[ERROR] Shutdown due to overheating error.")
            elif data >> 3 & 1:
                print("[ERROR] Shutdown due to motor encoder error.")
            elif data >> 4 & 1:
                print("[ERROR] Shutdown due to electric shock error.")
            elif data >> 5 & 1:
                print("[ERROR] Shutdown due to overload error.")
        else:            
            comm_state = True
            err_state = False
        return err_state, comm_state

    def latch_gripping(self, seconds=5, current_goal=200):
        print("Gripping...")
        self.torque_on()
        self._write_2byte_tx_rx(ADDR_PRO_GOAL_CURRENT, current_goal)
        time.sleep(seconds)
        self._write_2byte_tx_rx(ADDR_PRO_GOAL_CURRENT, 0)
        print("Released...")

    def open_gripper(self):
        self.torque_on()
        self._write_2byte_tx_rx(ADDR_PRO_GOAL_CURRENT, -100)
        time.sleep(0.5)
        self._write_2byte_tx_rx(ADDR_PRO_GOAL_CURRENT, 0)
        print("Gripper opened...")

    def close_gripper(self, current_goal=400):
        self.torque_on()
        self._write_2byte_tx_rx(ADDR_PRO_GOAL_CURRENT, current_goal)
        print("Gripper closed...")

    def _open_port(self):
        self.port_handler = PortHandler(self.device_name)
        self.packet_handler = PacketHandler(2.0)

        if self.port_handler.openPort():
            print("Succeeded to open the port")
        else:
            print("[ERROR] Failed to open the port")
            input("Press any key to terminate...")
            quit()

        if self.port_handler.setBaudRate(self.baudrate):
            print("Succeeded to change the baudrate")
        else:
            print("[ERROR] Failed to change the baudrate")
            input("Press any key to terminate...")
            quit()
        return True

    def _write_1byte_tx_rx(self, addr, value):
        dxl_comm_result, dxl_error = self.packet_handler.write1ByteTxRx(self.port_handler, self.dxl_id, addr, value)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"[ERROR] {self.packet_handler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            print(f"[ERROR] {self.packet_handler.getRxPacketError(dxl_error)}")
            if dxl_error == ERRBIT_ALERT:
                self.check_hw_error()
        else:
            self._print_debug(f"Write 1 byte: {value} to {addr}")
            return True
        return False

    def _write_2byte_tx_rx(self, addr, value):
        dxl_comm_result, dxl_error = self.packet_handler.write2ByteTxRx(self.port_handler, self.dxl_id, addr, value)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"[ERROR] {self.packet_handler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            print(f"[ERROR] {self.packet_handler.getRxPacketError(dxl_error)}")
            if dxl_error == ERRBIT_ALERT:
                self.check_hw_error()
        else:
            self._print_debug(f"Write 2 byte: {value} to {addr}")
            return True
        return False

    def _print_debug(self, msg):
        if self.debug_msg:
            print(f"[DEBUG] {msg}")