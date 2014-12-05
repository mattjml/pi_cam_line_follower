import sys

import line_analysis
import fysom

class Control_Parameters(object):
    def __init__(self,
                 forward_steps,
                 forward_speed,
                 reversing_steps,
                 reversing_speed,
                 turning_steps,
                 turning_speed,
                 finding_bend_steps,
                 finding_bend_speed,
                 finding_bend_threshold=10):
        def check_param(param):
            assert 320 > param > 0, 'Param can only be in the range 0-320'
        
        check_param(forward_steps)
        check_param(forward_speed)
        check_param(reversing_steps)
        check_param(reversing_speed)
        check_param(turning_steps)
        check_param(turning_speed)
        check_param(finding_bend_steps)
        check_param(finding_bend_speed)
        assert 0 < finding_bend_threshold < 30

        self.forward_steps       = forward_steps
        self.forward_speed       = forward_speed
        self.reversing_steps     = reversing_steps
        self.reversing_speed     = reversing_speed
        self.turning_steps       = turning_steps
        self.turning_speed       = turning_speed
        self.finding_bend_steps  = finding_bend_steps
        self.finding_bend_speed  = finding_bend_speed
        self.finding_bend_thresh = finding_bend_threshold

class Control(object):
    
    def on_init(self, e):
        pass
    
    def on_out(self, e):
        centre_row = e.args[0]
        lines = e.args[1]
        if len(centre_row) == 0:
            self.current_order = (self.motion.backward,
                                  (self.params.reversing_steps,
                                   self.params.reversing_speed))
        elif len(centre_row) == 1:
            if centre_row[0][1] < 50:
                self.current_order = (self.motion.rotate_left,
                                      (self.params.turning_steps,
                                       self.params.turning_speed))
            else:
                self.current_order = (self.motion.rotate_right,
                                      (self.params.turning_steps,
                                       self.params.turning_speed))

    def on_in(self, e):
        self.current_order = (self.motion.forward,
                              (self.params.forward_steps,
                               self.params.forward_speed))

    def __init__(self, motion, parameters):
        self.motion = motion
        self.params = parameters
        self.current_order = (None, (None, None))
        self.fsm = \
            fysom.Fysom(
                {'initial': 'init',
                 'events':
                     [{'name': 'ev_in',        'src': 'init',         'dst': 'in'},
                      {'name': 'ev_out',       'src': 'init',         'dst': 'out'},
                      {'name': 'ev_in',        'src': 'out',          'dst': 'in'},
                      {'name': 'ev_out',       'src': 'out',          'dst': 'out'},
                      {'name': 'ev_in',        'src': 'in',           'dst': 'in'},
                      {'name': 'ev_out',       'src': 'in',           'dst': 'out'}],
                 'callbacks': 
                     {'oninit'        : self.on_init,
                      'onout'         : self.on_out,
                      'onin'          : self.on_in}})

        def log(e):
            print 'event: %s, src: %s, dst: %s, motion:%s' % (e.event, e.src, e.dst, self.current_order[0])
        self.fsm.onchangestate = log
    
    def progress(self, lines):
        centre_row = lines[0]
        centre_line = [line for line in centre_row if line[0] <= 51 and line[1] >= 49] 
        if len(centre_line) == 1:
            self.fsm.ev_in(centre_line, lines)
        else:
            self.fsm.ev_out(centre_row, lines)
        self.current_order[0](*self.current_order[1])

if __name__ == '__main__':
    # TODO
    pass

