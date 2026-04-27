import serial
import time

ser = serial.Serial("COM7", 115200)

while True:
    ser.write(bytes([0x90, 0x60, 0x50]))  # NOTE ON
    print("sent ON")
    time.sleep(0.1)

    ser.write(bytes([0x80, 0x60, 0x00]))    # NOTE OFF
    print("sent OFF")
    time.sleep(0.1)
