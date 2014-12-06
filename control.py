import sys

import line_analysis
import fysom

from datetime import datetime
from compiler.ast import flatten

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
            assert 320 >= param > 0, 'Param can only be in the range 0-320'
        
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
    
    LEFT = 1
    RIGHT = 2

    def on_init(self, e):
        pass
    
    def on_out(self, e):
        direction = e.args[0]
        lines = e.args[1]
        # Can't see any lines
        if direction is None:
            direction = self.last_turn
            # self.backwards_turn(direction)
            # self.current_order = (self.motion.backward,
            #                       (self.params.reversing_steps,
            #                        self.params.reversing_speed))
            self.fsm.ev_reversing()
        elif direction is Control.LEFT:
            self.current_order = (self.motion.rotate_left,
                                  (self.params.turning_steps,
                                   self.params.turning_speed))
            self.last_turn = direction
        else:
            self.current_order = (self.motion.rotate_right,
                                  (self.params.turning_steps,
                                   self.params.turning_speed))
            self.last_turn = direction

    def on_reversing(self, e):
        self.current_order = (self.motion.backward,
                              (self.params.reversing_steps,
                               self.params.reversing_speed))

    def on_perturbing(self, e):
        if self.last_turn == Control.LEFT:
            self.current_order = (self.motion.rotate_left,
                                  (self.params.turning_steps,
                                   self.params.turning_speed))
        else:
            self.current_order = (self.motion.rotate_right,
                                  (self.params.turning_steps,
                                   self.params.turning_speed))

    def on_in_top(self, e):
        self.current_order = (self.motion.forward,
                              (self.params.forward_steps,
                               self.params.forward_speed))
    
    def backwards_turn(self, direction):
        if direction is Control.LEFT:
            self.current_order = (self.motion.specific_move,
                                  (self.motion.BACKWARD,
                                   self.params.finding_bend_steps,
                                   self.params.finding_bend_speed,
                                   self.motion.FORWARD,
                                   self.params.finding_bend_steps,
                                   int(self.params.finding_bend_speed*0.2)))
            self.last_turn = direction
        else:
            self.current_order = (self.motion.specific_move,
                                  (self.motion.FORWARD,
                                   self.params.finding_bend_steps,
                                   int(self.params.finding_bend_speed*0.2),
                                   self.motion.BACKWARD,
                                   self.params.finding_bend_steps,
                                   self.params.finding_bend_speed))
            self.last_turn = direction
    
    def on_in_bottom(self, e):
        direction = e.args[0]
        print("Moving in old direction {0}".format(direction))
        self.backwards_turn(direction)

    def __init__(self, motion, parameters):
        self.log_file = open('/root/log.file', 'w')
        self.motion = motion
        self.params = parameters
        self.current_order = (None, (None, None))
        self.last_turn = Control.RIGHT
        self.fsm = \
            fysom.Fysom(
                {'initial': 'init',
                 'events':
                     [{'name': 'ev_in_top',        'src': 'init',         'dst': 'in_top'},
                      {'name': 'ev_in_bottom',     'src': 'init',         'dst': 'in_bottom'},
                      {'name': 'ev_out',           'src': 'init',         'dst': 'out'},
                      {'name': 'ev_in_top',        'src': 'out',          'dst': 'in_top'},
                      {'name': 'ev_in_bottom',     'src': 'out',          'dst': 'in_bottom'},
                      {'name': 'ev_out',           'src': 'out',          'dst': 'out'},
                      {'name': 'ev_reversing',     'src': 'out',          'dst': 'reversing'},
                      {'name': 'ev_in_top',        'src': 'in_top',       'dst': 'in_top'},
                      {'name': 'ev_in_bottom',     'src': 'in_top',       'dst': 'in_bottom'},
                      {'name': 'ev_out',           'src': 'in_top',       'dst': 'out'},
                      {'name': 'ev_in_top',        'src': 'reversing',    'dst': 'perturbing'},
                      {'name': 'ev_in_bottom',     'src': 'reversing',    'dst': 'perturbing'},
                      {'name': 'ev_out',           'src': 'reversing',    'dst': 'reversing'},
                      {'name': 'ev_in_top',        'src': 'perturbing',   'dst': 'in_top'},
                      {'name': 'ev_in_bottom',     'src': 'perturbing',   'dst': 'in_bottom'},
                      {'name': 'ev_out',           'src': 'perturbing',   'dst': 'out'},
                      {'name': 'ev_in_top',        'src': 'in_bottom',    'dst': 'in_top'},
                      {'name': 'ev_in_bottom',     'src': 'in_bottom',    'dst': 'in_bottom'},
                      {'name': 'ev_out',           'src': 'in_bottom',    'dst': 'out'}],
                 'callbacks': 
                     {'onperturbing'  : self.on_perturbing,
                      'onreversing'   : self.on_reversing,
                      'oninit'        : self.on_init,
                      'onout'         : self.on_out,
                      'onin_top'      : self.on_in_top,
                      'onin_bottom'   : self.on_in_top}})

        def log(e):
            self.log_file.write('event: %s, src: %s, dst: %s, time:%s\n' % (e.event, e.src, e.dst, datetime.now()))
            self.log_file.flush()
            print 'event: %s, src: %s, dst: %s, motion:%s' % (e.event, e.src, e.dst, self.current_order[0])
        self.fsm.onchangestate = log

    def find_centre_line(self, lines):
        intersections = [intersect for intersect in [[line for line in row if line[0] <= 52 and line[1] >= 48] for row in lines.values()] if len(intersect) > 0]
        if(len(intersections) > 0):
            return intersections[0]
        return None
    
    def find_closest_line(self, lines):
        closest_lefts =  flatten([intersect for intersect in [[line[1] for line in row if line[1] <= 50] for row in lines.values()] if len(intersect) > 0])
        closest_rights = flatten([intersect for intersect in [[line[0] for line in row if line[0] >= 50] for row in lines.values()] if len(intersect) > 0])
        
        len_left = len(closest_lefts)
        len_right = len(closest_rights)

        if len_left == 0 and len_right == 0:
            return None
        if len_left > 0 and len_right == 0:
            return Control.LEFT
        if len_left == 0 and len_right > 0:
            return Control.RIGHT
        print 'closest lefts then rights'
        print closest_lefts
        print closest_rights 
        if((50 - max(closest_lefts)) > (min(closest_rights) - 50)):
            return Control.RIGHT
        else:
            return Control.LEFT
   
    def progress(self, lines):
        centre_line = self.find_centre_line({item:val for (item,val) in lines.items() if item >= 0})
        if centre_line is None:
            print {item:val for (item,val) in lines.items() if item < 0}
            centre_line = self.find_centre_line({item:val for (item,val) in lines.items() if item < 0})
            if centre_line is None:
                print("OUT")
                closest_line = self.find_closest_line(lines)
                self.fsm.ev_out(closest_line, lines)
            else:
                print("IN BOTTOM")
                self.fsm.ev_in_bottom(self.last_turn, lines) 
        else:
            print("IN TOP")
            self.fsm.ev_in_top(centre_line, lines)

        self.current_order[0](*self.current_order[1])

