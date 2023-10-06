from bluepy.btle import Scanner, DefaultDelegate, Peripheral, UUID
import time

TARGET_DEVICE_NAME = "HMSoft"
HM_UART_SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
HM_TX_CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

class MyDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if TARGET_DEVICE_NAME == dev.getValueText(9):
            print("Found", dev.addr)

class BlueModule():

    target_device = None
    peripheral = None
    tx_char = None

    def find_dev(self):
        scanner = Scanner()
        scanner.withDelegate(MyDelegate())
        devices = scanner.scan(timeout=10.0)

        for dev in devices:
            if TARGET_DEVICE_NAME == dev.getValueText(9):
                self.target_device = dev
                break

        if not self.target_device:
            print("Target device not found")
            exit(1)

    def connect_dev(self):
        self.find_dev()
        
        success = False
        while not success:
            try:
                self.peripheral = Peripheral(self.target_device)
                success = True
            except:
                time.sleep(2)
                print("Retrying connection..")

        print("Bluetooth Connection Established.")

        uart_service = self.peripheral.getServiceByUUID(UUID(HM_UART_SERVICE_UUID))
        self.tx_char = uart_service.getCharacteristics(UUID(HM_TX_CHARACTERISTIC_UUID))[0]

    def disconnect_dev(self):
        print("Bluetooth Connection Disconnected.")
        self.peripheral.disconnect()


    def transmit(self,message):
        self.tx_char.write(message.encode('ascii'))
        
