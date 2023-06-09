import src.Constants as Constants

import math
import gpiozero

from svg_to_gcode.geometry import Vector as Vect

class Vector(Vect) :
    def __key(self):
        return (self.x, self.y)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Vector):
            return self.__key() == other.__key()
        return NotImplemented


class LineSegment :

    __slots__ = ("start", "end","reference")

    def __init__(self, start_x:float, start_y:float, end_x:float, end_y:float) :
        self.start = Vector(start_x, start_y)
        self.end = Vector(end_x, end_y)
        self.reference = Vector(0,0)

    def setReference(self, point:Vector) :
        if self.reference != Vector(0,0) :
            self.start -= self.reference
            self.end -= self.reference
        self.reference = point
        self.start += self.reference
        self.end += self.reference
    
    def findLength(self) -> float :
        return math.sqrt( ((self.start.x-self.end.x)**2) + ((self.start.y-self.end.y)**2) )
    
    def __repr__(self) :
        return "(" + str(self.start.x) + ", " + str(self.start.y) + ")->(" + str(self.end.x) + ", " + str(self.end.y) + ")"# length: " + str(round(self.findLength(), 3))
        



class LinearMoveCommand(LineSegment) :

    def __init__(self, MovementCommand:LineSegment) :
        self.start = MovementCommand.start
        self.end = MovementCommand.end
        self.reference = MovementCommand.reference

    def toGcode(self) -> tuple[Vector, str] :

        draw_string =  "G0 X" + str(self.end.x) + " Y" + str(self.end.y) + " F" + str(Constants.MOVE_SPEED) + ";"

        return (self.start, draw_string)
    
    def __repr__(self) :
        return "MOVE (" + str(self.start.x) + ", " + str(self.start.y) + ")->(" + str(self.end.x) + ", " + str(self.end.y) + ")"# length: " + str(round(self.findLength(), 3)) 



class LinearDrawCommand(LineSegment) :

    def __init__(self, MovementCommand:LineSegment) :
        self.start = MovementCommand.start
        self.end = MovementCommand.end
        self.reference = MovementCommand.reference

    def toGcode(self) -> tuple[Vector,str] :

        draw_string =  "G0 X" + str(self.end.x) + " Y" + str(self.end.y) + " F" + str(Constants.DRAW_SPEED) + ";"

        return (self.start, draw_string)

    def __repr__(self) :
        return "DRAW (" + str(self.start.x) + ", " + str(self.start.y) + ")->(" + str(self.end.x) + ", " + str(self.end.y) + ")"# length: " + str(round(self.findLength(), 3))
        


class LinearEraseCommand(LineSegment) :

    def __init__(self, MovementCommand:LineSegment) :
        self.start = MovementCommand.start
        self.end = MovementCommand.end
        self.reference = MovementCommand.reference

    def toGcode(self) -> tuple[Vector,str] :

        erase_start_x = (self.start.x+Constants.MARKER_ERASER_DIST_X) 
        erase_start_y = (self.start.y+Constants.MARKER_ERASER_DIST_Y)
        erase_string =  "G0 X" + str(self.end.x+Constants.MARKER_ERASER_DIST_X) + " Y" + str(self.end.y+Constants.MARKER_ERASER_DIST_Y) + " F" + str(Constants.ERASE_SPEED) + ";"
        
        return (Vector(erase_start_x, erase_start_y), erase_string)
    
    def __repr__(self) :
        return "ERASE (" + str(self.start.x) + ", " + str(self.start.y) + ")->(" + str(self.end.x) + ", " + str(self.end.y) + ")"# length: " + str(round(self.findLength(), 3))
        
class ToolheadCommand :

    __slots__ = ("servo")
    
    def setServo(self, servo:gpiozero.AngularServo) :
        self.servo = servo




class ToolheadDraw(ToolheadCommand) :
    
    def execute(self) :
        self.servo.angle = Constants.SERVO_ANGLE_DRAW

    def toGcode(self):
        return (None, "; MARKER DOWN")

    def __repr__(self) :
        return "TOOLHEAD DRAW"

class ToolheadErase(ToolheadCommand) :

    def execute(self) :
        self.servo.angle = Constants.SERVO_ANGLE_ERASE

    def toGcode(self):
        return (None, "; ERASER DOWN")

    def __repr__(self) :
        return "TOOLHEAD ERASE"

class ToolheadStandby(ToolheadCommand) :

    def execute(self) :
        self.servo.angle = Constants.SERVO_ANGLE_MOVE

    def toGcode(self):
        return (None, "; MARKER/ERASER UP")

    def __repr__(self) :
        return "TOOLHEAD STANDBY"
