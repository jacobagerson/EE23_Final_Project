import serial
import time

ser = serial.Serial("COM7", 115200)

while True:
    ser.write(bytes([0x90, 60, 50]))  # NOTE ON
    print("sent ON")
    time.sleep(0.1)

    ser.write(bytes([0x80, 60, ]))    # NOTE OFF
    print("sent OFF")
    time.sleep(0.1)
