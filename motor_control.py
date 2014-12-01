import ctypes
c_uint8 = ctypes.c_uint8
c_uint16 = ctypes.c_uint16


class Packet(ctypes.Union):
    class Packet_Fields(ctypes.LittleEndianStructure):
         _fields_ = [("header", c_uint8),
                     ("mode",   c_uint8, 4),
                     ("spare",  c_uint8, 2),
                     ("stall",  c_uint8, 1),
                     ("dir",    c_uint8, 1),
                     ("speed",  c_uint16),
                     ("ticks",  c_uint16),
                     ("xsum",   c_uint8)]
    
    _fields_ = [("bytes", c_uint8 * 7),
                ("fields", Packet_Fields) ]
    
    MODE_LEFT = x
    MODE_RIGHT = y

    DIR_FORWARD = z
    DIR_BACKWARD = u

    def __init__(self,
                 mode,
                 stall,
                 dir,
                 speed,
                 ticks):
        super(self).__init__()
        self.fields.mode = mode
        self.fields.stall = stall
        self.fields.dir = dir
        self.fields.speed = speed
        self.fields.ticks = ticks

class Motion(object):

    LEFT = 1
    RIGHT = 2
    FORWARD = 3
    BACKWARD = 4
    
    def __init__(self, comms):
        self.comms = comms
    
    def _rotate_move(self, direction, quantity, speed):
        assert direction == LEFT or direction == RIGHT
        assert quantity >= 0
        left_packet = Packet(mode=PACKET.LEFT,
                             stall=0,
                             dir=[PACKET.DIR_BACKWARD, PACKET.DIR_FORWARD][direction == self.LEFT],
                             speed = speed
                             quantity = speed * some_factor)
        right_packet = Packet(mode=PACKET.RIGHT,
                              stall=0,
                              dir=[PACKET.DIR_BACKWARD, PACKET.DIR_FORWARD][direction == self.RIGHT],
                              speed = speed
                              quantity = speed * some_factor)
        comms.write(left_packet.bytes)
        comms.write(left_packet.bytes)

    def _linear_move(self, direction, quantity, speed):
        assert direction == FORWARD or direction == BACKWARD
        assert quantity >= 0
        left_packet = Packet(mode=PACKET.LEFT,
                             stall=0,
                             dir=[PACKET.DIR_BACKWARD, PACKET.DIR_FORWARD][direction == self.FORWARD],
                             speed = speed
                             quantity = speed * some_factor)
        right_packet = Packet(mode=PACKET.RIGHT,
                              stall=0,
                              dir=[PACKET.DIR_BACKWARD, PACKET.DIR_FORWARD][direction == self.FORWARD],
                              speed = speed
                              quantity = speed * some_factor)
        comms.write(left_packet.bytes)
        comms.write(left_packet.bytes)
    
    def rotate_left(self, quantity, speed):
        self._rotate_move(LEFT, quantity, speed)
    
    def rotate_right(self, quantity, speed):
        self._rotate_move(RIGHT, quantity, speed)

    def forward(self, quantity, speed):
        self._linear_move(FORWARD, quantity, speed)

    def backward(self, quantity, speed):
        self._linear_move(BACKWARD, quantity, speed)

    def stop(self):
        self._linear_move(FORWARD, 0, 0)

# UNIT TEST!!
if __name__ == '__main__':
    pack = Packet()
    pack.fields.header = 0xAB
    pack.fields.mode   = 0x5
    pack.fields.spare  = 0x1
    pack.fields.stall  = 0x0
    pack.fields.dir    = 0x1
    pack.fields.speed  = 0xCDEF
    pack.fields.ticks  = 0x89AB
    pack.fields.xsum   = 0x67
    
    assert pack.bytes[0] == 0xAB
    assert pack.bytes[1] == 0b10010101
    assert pack.bytes[2] == 0xEF
    assert pack.bytes[3] == 0xCD
    assert pack.bytes[4] == 0xAB
    assert pack.bytes[5] == 0x89
    assert pack.bytes[6] == 0x67

