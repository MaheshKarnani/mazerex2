import time, libcamera
from picamera2 import Picamera2, Preview

picam2 = Picamera2()

# config = picam.create_preview_configuration()
config = picam2.create_preview_configuration(main={"size": (1600, 1200)}, controls={"FrameDurationLimits": (200000, 200000)}) #10hz durations are in us
config["transform"] = libcamera.Transform(hflip=1, vflip=1)
picam2.configure(config)

picam2.start_preview(Preview.QTGL)
picam2.start()
# last_timestamp = 0
# while True:
#     timestamp = picam2.capture_metadata()['SensorTimestamp']  # nanoseconds
#     print(round((timestamp - last_timestamp) / 1000000)) 
#     last_timestamp = timestamp