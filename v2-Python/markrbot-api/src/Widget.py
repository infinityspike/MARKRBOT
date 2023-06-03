from abc import ABC, abstractmethod
import xml.etree.ElementTree as ET
from svg_to_gcode.svg_parser import parse_string
from svg_to_gcode.compiler import Compiler
from svg_to_gcode.geometry import Vector

import ziafont
ziafont.config.svg2 = False

from src.MovementCommandCompiler import MovementCommandCompiler
import src.MovementCommands as MC
import src.Constants as Constants



REQUIRED_TEXT_PARAMETERS = [
    ('textstring',str),
    ('size',float),
    ('linespacing', float),
    ('halign', str), #Literal['left', 'center', 'right']
    ('valign', str), #Literal['base', 'center', 'top']
    ('rotation', float),
    ('font',str)
]
REQUIRED_TEXT_COUNTER_PARAMETERS = [
    ('count', int),
    ('size',float),
    ('linespacing', float),
    ('halign', str), #Literal['left', 'center', 'right']
    ('valign', str), #Literal['base', 'center', 'top']
    ('rotation', float),
    ('font',str)
]
AVAILABLE_FONT_LIBRARY = {
    'Oswald' : ziafont.Font(),
    'Arizona' : ziafont.Font('./src/fonts/Arizonia-Regular.ttf'),
    'Great Vibes' : ziafont.Font('./src/fonts/GreatVibes-Regular.otf'),
    'Open Sans' : ziafont.Font('./src/fonts/OpenSans-Regular.ttf'),
    'Roman' : ziafont.Font('./src/fonts/roman_font_7.ttf')
}




class Widget(ABC) :

    __slots__ = ("position","SVG","details")

    def __init__(self, pos_x:int, pos_y:int, svg:ET.Element, deetz:dict=None) :
        self.position = Vector(pos_x,pos_y)
        self.SVG = svg
        self.details = deetz


    def parseMovementCommands(self) -> set :
        result_set = set()

        if not self.SVG : raise Exception("cannot parse commands for empty svg")
        
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
    
    def __eq__(self, other) :
        if not isinstance(other, Widget) : return False
        if not (self.position.x == other.position.x) : return False
        if not (self.position.y == other.position.y) : return False
        if not (self.details == other.details) : return False
        if not (self.SVG.__eq__(other.SVG)) : return False

        return True
    
    def __hash__(self) -> int:
        return super().__hash__()
    
    def toJson(self) -> dict :
        return {
            'pos_x' : self.position.x,
            'pos_y' : self.position.y,
            'svg' : ET.tostring(self.SVG,encoding='unicode'),
            'details' : self.details
            }

    
class TextWidget(Widget) :

    NAME = 'text'
    PARAMS = REQUIRED_TEXT_PARAMETERS

    def checkType(self, details:dict) :
        if not details : raise Exception(f"{self.NAME} widget made without any details")
        if details.get('type') != self.NAME : raise Exception(f"{self.NAME} widget made without proper type specification")

    def __init__(self, pos_x:int, pos_y:int, deetz:dict, svg:ET.Element=None) :
        self.checkType(deetz)
        super().__init__(pos_x, pos_y, svg, deetz)
        self.parseTextSVG()

    def __eq__(self, other) :
        if not isinstance(other, TextWidget) : return False
        if not (self.position.x == other.position.x) : return False
        if not (self.position.y == other.position.y) : return False
        if not (self.details == other.details) : return False

        return True
    
    def __hash__(self) -> int:
        return super().__hash__()

    def checkParamter(self, params:tuple[str,type]) -> bool :
        return isinstance(self.details[params[0]], params[1])

    def checkParameters(self) :
        for param in self.PARAMS :
            if not self.checkParamter(param) : raise Exception(f"{self.NAME} widget is missing one of the required parameters, {param}")

        halign:str = self.details['halign']
        valign:str = self.details['valign']
        if not (halign == 'left' or halign == 'right' or halign == 'center') : raise Exception('halign must ne \"left\", \"right\", or \"center\"')
        if not (valign == 'base' or valign == 'top' or valign == 'center') : raise Exception('halign must ne \"base\", \"top\", or \"center\"')

        font:str = self.details['font']
        if AVAILABLE_FONT_LIBRARY[font] == None : raise Exception(f"{font} is not an available font")

        
    def parseTextSVG(self) :
        self.checkParameters()
        font = AVAILABLE_FONT_LIBRARY[self.details['font']]

        self.SVG = font.text(
            s           =self.details['textstring'],
            size        =self.details['size'],
            linespacing =self.details['linespacing'],
            halign      =self.details['halign'],
            valign      =self.details['valign'],
            rotation    =self.details['rotation']
        ).svgxml()

class NumberCounterWidget(Widget) :

    NAME = 'number-counter'
    PARAMS = REQUIRED_TEXT_COUNTER_PARAMETERS

    def checkType(self, details:dict) :
        if not details : raise Exception(f"{self.NAME} widget made without any details")
        if details.get('type') != self.NAME : raise Exception(f"{self.NAME} widget made without proper type specification")

    def __init__(self, pos_x:int, pos_y:int, deetz:dict, svg:ET.Element=None) :
        self.checkType(deetz)
        super().__init__(pos_x, pos_y, svg, deetz)
        self.parseTextSVG()

    def __eq__(self, other) :
        if not isinstance(other, NumberCounterWidget) : return False
        if not (self.position.x == other.position.x) : return False
        if not (self.position.y == other.position.y) : return False
        if not (self.details == other.details) : return False

        return True
    
    def __hash__(self) -> int:
        return super().__hash__()

    def checkParamter(self, params:tuple[str,type]) -> bool :
        return isinstance(self.details[params[0]], params[1])

    def checkParameters(self) :
        for param in self.PARAMS :
            if not self.checkParamter(param) : raise Exception(f"{self.NAME} widget is missing one of the required parameters, {param}")

        halign:str = self.details['halign']
        valign:str = self.details['valign']
        if not (halign == 'left' or halign == 'right' or halign == 'center') : raise Exception('halign must ne \"left\", \"right\", or \"center\"')
        if not (valign == 'base' or valign == 'top' or valign == 'center') : raise Exception('halign must ne \"base\", \"top\", or \"center\"')

        font:str = self.details['font']
        if AVAILABLE_FONT_LIBRARY[font] == None : raise Exception(f"{font} is not an available font")

        
    def parseTextSVG(self) :
        self.checkParameters()
        font = AVAILABLE_FONT_LIBRARY[self.details['font']]

        self.SVG = font.text(
            s           =str(self.details['count']),
            size        =self.details['size'],
            linespacing =self.details['linespacing'],
            halign      =self.details['halign'],
            valign      =self.details['valign'],
            rotation    =self.details['rotation']
        ).svgxml()

    
    
    
if __name__ == '__main__' :
    test_widget = Widget(0,0,ET.parse('./proof_of_concept/test-svgs/drawing.svg').getroot())
    result = test_widget.parseMovementCommands()

    for command in result :
        print(command)
    print(test_widget.toJson())