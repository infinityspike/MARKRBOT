from abc import ABC, abstractmethod
import xml.etree.ElementTree as ET
from svg_to_gcode.svg_parser import parse_string
from svg_to_gcode.compiler import Compiler, interfaces

from MovementCommandCompiler import MovementCommandCompiler
import MovementCommands as MC
import Constants

class Widget(ABC) :

    position_x:int
    position_y:int
    SVG:ET.Element

    def __init__(self, pos_x:int, pos_y:int, svg:ET.Element) :
        self.position_x = pos_x
        self.position_y = pos_y
        self.SVG = svg

    def parseMovementCommands(self) -> list :
        result_list = list()

        compiler = Compiler(MovementCommandCompiler, movement_speed=Constants.MOVE_SPEED, cutting_speed=Constants.DRAW_SPEED, pass_depth=0)
        curves = parse_string(ET.tostring(self.SVG, encoding='unicode'))
        compiler.append_curves(curves)

        for item in compiler.body :
            if isinstance(item, MC.LinearMovementCommand) :
                item.setRefrenceX(self.position_x)
                item.setRefrenceY(self.position_y)
                result_list.append(item)
            elif isinstance(item, (MC.DrawCommand,MC.MoveCommand,MC.EraseCommand) ) :
                result_list.append(item)
            
        return result_list
    
if __name__ == '__main__' :
    test_widget = Widget(0,0,ET.parse('./proof_of_concept/test-svgs/drawing.svg').getroot())
    result = test_widget.parseMovementCommands()