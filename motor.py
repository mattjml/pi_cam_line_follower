import ctypes
c_uint8 = ctypes.c_uint8
c_uint16 = ctypes.c_uint16

class Packet(ctypes.Union):

    BYTE_LEN = 5

    HEADER_BYTE = 0xFF
 
    CONTROL_LEFT_FORWARD   = 0x0
    CONTROL_LEFT_BACKWARD  = 0x1
    CONTROL_RIGHT_FORWARD  = 0x2
    CONTROL_RIGHT_BACKWARD = 0x3
    CONTROL_ACK            = 0x4
    CONTROL_STALL          = 0x5
    CONTROL_RHS_CLICKS     = 0x6
    CONTROL_LHS_CLICKS     = 0x7

    class Packet_Fields(ctypes.LittleEndianStructure):
         _fields_ = [("header",  c_uint8),
                     ("control", c_uint8),
                     ("speed",   c_uint8),
                     ("steps",   c_uint8),
                     ("xsum",    c_uint8)]
    
    _fields_ = [("bytes", c_uint8 * BYTE_LEN),
                ("fields", Packet_Fields) ]

    def __init__(self,
                 control,
                 speed,
                 steps):
        super(Packet, self).__init__()
        self.fields.header  = Packet.HEADER_BYTE
        self.fields.control = control
        self.fields.speed   = speed
        self.fields.steps   = steps
        self.fields.xsum    = self.calculate_xsum()

    def calculate_xsum(self):
        xsum = 0
        for byte in self.bytes[:-1]:
            xsum ^= byte 
        return xsum

    def validate(self):
        return self.fields.xsum == self.calculate_xsum()

class Motion(object):

    LEFT = 1
    RIGHT = 2
    FORWARD = 3
    BACKWARD = 4
    
    def __init__(self, comms):
        self.comms = comms
    
    def _rotate_move(self, direction, steps, speed):
        assert direction == Motion.LEFT or direction == Motion.RIGHT
        assert steps >= 0
        l_packet = Packet(control=[Packet.CONTROL_LEFT_FORWARD, Packet.CONTROL_LEFT_BACKWARD][direction == Motion.LEFT],
                          speed = speed >> 1,
                          steps = steps >> 1)
        r_packet = Packet(control=[Packet.CONTROL_RIGHT_FORWARD, Packet.CONTROL_RIGHT_BACKWARD][direction == Motion.RIGHT],
                          speed = speed >> 1,
                          steps = steps >> 1)
        self.comms.write(r_packet.bytes)
        self.comms.write(l_packet.bytes)

    def _linear_move(self, direction, steps, speed):
        assert direction == Motion.FORWARD or direction == Motion.BACKWARD
        assert steps >= 0
        l_packet = Packet(control=[Packet.CONTROL_LEFT_FORWARD, Packet.CONTROL_LEFT_BACKWARD][direction == Motion.BACKWARD],
                          speed = speed >> 1,
                          steps = steps >> 1)
        r_packet = Packet(control=[Packet.CONTROL_RIGHT_FORWARD, Packet.CONTROL_RIGHT_BACKWARD][direction == Motion.BACKWARD],
                          speed = speed >> 1,
                          steps = steps >> 1)
        self.comms.write(l_packet.bytes)
        self.comms.write(r_packet.bytes)

    def specific_move(self, dir_left, steps_left, speed_left, dir_right, steps_right, speed_right):
        l_packet = Packet(control=[Packet.CONTROL_LEFT_FORWARD, Packet.CONTROL_LEFT_BACKWARD][dir_left == Motion.BACKWARD],
                          speed = speed_left >> 1,
                          steps =_steps_left >> 1)
        r_packet = Packet(control=[Packet.CONTROL_RIGHT_FORWARD, Packet.CONTROL_RIGHT_BACKWARD][dir_right == Motion.BACKWARD],
                          speed = speed_right >> 1,
                          steps = steps_right >> 1)
        self.comms.write(l_packet.bytes)
        self.comms.write(r_packet.bytes)
    
    def rotate_left(self, steps, speed):
        self._rotate_move(Motion.LEFT, steps, speed)
    
    def rotate_right(self, steps, speed):
        self._rotate_move(Motion.RIGHT, steps, speed)

    def forward(self, steps, speed):
        self._linear_move(Motion.FORWARD, steps, speed)

    def backward(self, steps, speed):
        self._linear_move(Motion.BACKWARD, steps, speed)

    def stop(self):
        self._linear_move(FORWARD, 0, 0)


