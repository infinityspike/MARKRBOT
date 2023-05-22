from abc import ABC, abstractmethod
import xml.etree.ElementTree as ET
from svg_to_gcode.svg_parser import parse_string
from svg_to_gcode.compiler import Compiler
from svg_to_gcode.geometry import Vector

from MovementCommandCompiler import MovementCommandCompiler
import MovementCommands as MC
import Constants

class Widget(ABC) :

    __slots__ = ("position","SVG")

    def __init__(self, pos_x:int, pos_y:int, svg:ET.Element) :
        self.position = Vector(pos_x,pos_y)
        self.SVG = svg

    def parseMovementCommands(self) -> set[MC.LinearMovementCommand] :
        result_set = set()

        compiler = Compiler(MovementCommandCompiler, movement_speed=Constants.MOVE_SPEED, cutting_speed=Constants.DRAW_SPEED, pass_depth=0)
        curves = parse_string(ET.tostring(self.SVG, encoding='unicode'))
        compiler.append_curves(curves)

        #traverse through commands
        current_toolhead_action = None
        for item in compiler.body :

            #if toolhead change occurs, remember it
            if isinstance(item, (MC.DrawCommand,MC.MoveCommand,MC.EraseCommand) ) :
                current_toolhead_action = item

            if isinstance(item, MC.LinearMovementCommand) :
                item.setReference(self.position)

                #Only record the actual movements that make lines on the board. 
                #The Gcode to get into the starting position for all of the segments happens in the commandqueue
                if isinstance(current_toolhead_action, MC.DrawCommand) :
                    result_set.add(item)

            
        return result_set
    
if __name__ == '__main__' :
    test_widget = Widget(0,0,ET.parse('./proof_of_concept/test-svgs/drawing.svg').getroot())
    result = test_widget.parseMovementCommands()

    for command in result :
        print(command)