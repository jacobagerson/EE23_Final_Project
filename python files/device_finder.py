import serial.tools.list_ports

ports = serial.tools.list_ports.comports()

for port in ports:
    print("===")
    print(f"Device      : {port.device}")       # COM3
    print(f"Name        : {port.name}")         # COM3
    print(f"Description : {port.description}")  # Human-readable
    print(f"HWID        : {port.hwid}")         # Hardware ID
    print(f"VID         : {port.vid}")          # Vendor ID
    print(f"PID         : {port.pid}")          # Product ID
    print(f"Serial Num  : {port.serial_number}")
    print(f"Location    : {port.location}")
    print(f"Manufacturer: {port.manufacturer}")
    print(f"Product     : {port.product}")
    print(f"Interface   : {port.interface}")
