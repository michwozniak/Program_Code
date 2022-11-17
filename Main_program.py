#!/usr/bin/env python3

from ctypes import *
import math
import time
import matplotlib.pyplot as plt
import numpy as np
import sys
import scipy
import Adafruit_BBIO.GPIO as GPIO
import time
import dwf


out = "P9_14"
 
GPIO.setup(out, GPIO.OUT)
 

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

hdwf = c_int()
sts = c_byte()
hzAcq = c_double(8192)
nSamples = 4000
rgdSamples = (c_double*nSamples)()
cValid = c_int(0)

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))
print("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf)) # -1 automatycznie podłącza 1 napotkane urządzenie

if hdwf.value == 0:                        # jeśli 2 arg DeviceOpen zwróci 0 to sie nie połączył
    type_error = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(type_error)
    print(str(type_error.value))
    print("failed to open device")
    quit()

#set up acquisition
dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(0), c_bool(True))
dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(0), c_double(3))  # zakres w woltach
dwf.FDwfAnalogInAcquisitionModeSet(hdwf, c_int(1)) # Tryb akwizycji danych oscyloskopu
dwf.FDwfAnalogInFrequencySet(hdwf, hzAcq)  # Częstotliwosć próbkowania
dwf.FDwfAnalogInBufferSizeSet(hdwf, c_int(nSamples))  # Ilość próbek


# 0 - nie konfiguruje nic / 1 - start akwizycji
#dwf.FDwfAnalogInConfigure(hdwf, c_int(0), c_int(1))

plt.axis([0, len(rgdSamples), -3, 3])  # wielkosć wykresu
plt.ion()  # tryb interaktywny

# tworzenie ddanych do wykresu
hl1, = plt.plot([], [])
# hl2, = plt.plot([], []) # Napięcie
hl1.set_xdata(range(0, len(rgdSamples)))  # uzupełnienia odrazu osi X 0-sample
# hl2.set_xdata(range(0, len(rgdSamples)))  # uzupełnienia odrazu osi X 0-sample
print("Press Ctrl+C to stop")
a = (c_double*nSamples)()

try:
    while True:
        dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts)) # 1-odczytywanie danych / sts - odczytywany stan akwizycji do sts
        dwf.FDwfAnalogInStatusSamplesValid(hdwf, byref(cValid)) # cValid - numer próbki
        # 0-kanał / rgdSamples-pointer na miejsce zapisu odczytanej próbki / cValid - numer próbki
        dwf.FDwfAnalogInStatusData(hdwf, c_int(0), byref(rgdSamples), cValid)
        dwf.FDwfAnalogInStatusData(hdwf, c_int(1), byref(a), cValid)
        hl1.set_ydata(rgdSamples)
        #a.append(rgdSamples)
        # hl2.set_ydata(a)
        plt.draw()
        plt.pause(0.1)
except KeyboardInterrupt:
    pass

#from scipy import signal

#plt.title("FFT")
#window = signal.windows.cosine(nSamples)
#plt.plot(np.fromiter(rgdSamples*window, dtype=c_double), color='orange', label='C1')
#plt.plot(np.fromiter(fft(rgdSamples*window), dtype=c_double), color='red', label='C1')
#plt.plot(np.fromiter(window, dtype=c_double), color='blue', label='C2')
#plt.show()


for x in range(len(a)):
    print(a[x])

#dwf.FDwfAnalogOutConfigure(hdwf, c_int(0), c_bool(False))
#dwf.FDwfDeviceCloseAll()

while True:
    GPIO.output(out, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(out, GPIO.LOW)
    time.sleep(0.5)