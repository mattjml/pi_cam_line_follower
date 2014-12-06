import picamera
import picamera.array
import time
import cv2

import util
import motor
import comms
import control
import line_analysis

with picamera.PiCamera() as camera,\
     comms.Socket_Comms('socket.sock') as comms:
    camera.resolution = (80,60)# (320, 240)
    read_fifo = "read.fifo"
    write_fifo = "write.fifo"
    motion = motor.Motion(comms)


    control_params = control.Control_Parameters(forward_steps=2,
                                                forward_speed=140,
                                                reversing_steps=5,
                                                reversing_speed=300,
                                                turning_steps=10,
                                                turning_speed=320,
                                                finding_bend_steps=100,
                                                finding_bend_speed=320)

    control = control.Control(motion, control_params)
    analyser = line_analysis.Line_Analyser()
    time.sleep(2)
    #Use the video-port for captures...
    timeit = util.Time_It('Overall')
    with picamera.array.PiRGBArray(camera) as stream:
        for foo in camera.capture_continuous(stream, 'bgr',
                                             use_video_port=True):
            timeit.finish()
            timeit = util.Time_It('Overall')
            image = stream.array
            lines = analyser.get_lines(image,10)
            control.progress(lines)
            #print(stream.read())
            stream.seek(0)
            stream.truncate()
        
