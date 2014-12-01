import picamera
import picamera.array
from datetime import datetime
import time
import cv2

import motor_control
import comms
import control
import line_analysis

with picamera.PiCamera() as camera:
    camera.resolution = (80,60)# (320, 240)
    read_fifo = "read.fifo"
    write_fifo = "write.fifo"
    with comms.Fifo_Comms(read_fifo, write_fifo) as fifo_comms:
        motion = motor_control.Motion(fifo_comms)
        control = control.Control(motion)
        analyser = line_analysis.Line_Analyser()
        time.sleep(2)
        #Use the video-port for captures...
        start = datetime.now()
        img_num = 1
        with picamera.array.PiRGBArray(camera) as stream:
            for foo in camera.capture_continuous(stream, 'bgr',
                                                 use_video_port=True):
                diff = datetime.now() - start
                print(diff)
                start = datetime.now()
                #stream.seek(0)
                image = stream.array
                lines = analyser.get_lines(image,10)
                control.progress(lines)
                #print(stream.read())
                stream.seek(0)
                stream.truncate()
                img_num += 1
        
