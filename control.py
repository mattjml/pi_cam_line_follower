import sys

import line_analysis
import fysom

class Control(object):
    
    def on_init(self, e):
        print(dir(e))
        #print 'thanks to ' + e.msg + ' done by ' + e.args[0]
    
    def on_out(self, e):
        print("OUT")
        lines = e.args[0]
        centre_row = e.args[1]
        if len(centre_row) == 0:
            self.motion.backward(XXSTEPS, YYSPEED)
            self.fsm.ev_reversing()
        else if len(centre_row) == 1:
            if centre_row[0][1] < 50:
                self.motion.rotate_left(XXSTEPS, YYSPEED)
            else:
                self.motion.rotate_right(XXSTEPS, YYSPEED)

    def on_in(self, e):
        self.motion.forward(XXSTEPS, YYSPEED)
        print("IN")

    def on_finding_bend(self, e):
        centre_row = e.args[0]
        dist_left = abs(centre_row[0] - 50)
        dist_right = abs(centre_row[1] - 50)
        if dist_left > (dist_right + self.bend_thresh):
            self.motion.rotate_left(XXSTEPS, YYSPEED)
            pass
        elif dist_right > (dist_left + self.bend_thresh):
            self.motion.rotate_right(XXSTEPS, YYSPEED)
            #rotate_right_quite_a_bit
            pass
        else:
            self.fsm.ev_reversing()
        print("FINDING BEND")
 
    def __init__(self, motion):
        self.motion = motion
        self.fsm = \
            fysom.Fysom(
                {'initial': 'init',
                 'events':
                     [{'name': 'ev_in', 'src': 'init', 'dst': 'in'},
                      {'name': 'ev_out', 'src': 'init', 'dst': 'out'},
                      {'name': 'ev_in', 'src': 'out', 'dst': 'in'},
                      {'name': 'ev_out', 'src': 'out', 'dst': 'out'},
                      {'name': 'ev_reversing', 'src': 'out', 'dst': 'reversing'},
                      {'name': 'ev_out', 'src': 'reversing', 'dst': 'reversing'},
                      {'name': 'ev_in', 'src': 'reversing', 'dst': 'finding_bend'},
                      {'name': 'ev_in', 'src': 'in', 'dst': 'in'},
                      {'name': 'ev_out', 'src': 'in', 'dst': 'out'}],
                 'callbacks': 
                     {'oninit'        : self.on_init,
                      'onreversing'   : self.on_reversing,
                      'onfinding_bend': self.on_finding_bend,
                      'onout'         : self.on_out,
                      'onin'          : self.on_in}})

        def log(e):
            print 'event: %s, src: %s, dst: %s' % (e.event, e.src, e.dst)
        self.fsm.onchangestate = log
    
    def progress(self, lines):
        centre_row = lines[0]
        if len(centre_row) == 0:
            pass # We are blind, do something
        else:
            centre_line = [line for line in centre_row if line[0] <= 51 and line[1] >= 49] 
            if len(centre_line) == 1:
                self.fsm.ev_in(centre_line, lines)
            else:
                self.fsm.ev_out(centre_row, lines)
if __name__ == '__main__':
    # TODO
    pass

