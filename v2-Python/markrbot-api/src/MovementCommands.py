import src.Constants as Constants

from svg_to_gcode.geometry import Vector
import math
import gpiozero



class LinearMovementCommand :

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
        return " start: (" + str(self.start.x) + ", " + str(self.start.y) + ") end: (" + str(self.end.x) + ", " + str(self.end.y) + ") length: " + str(round(self.findLength(), 3))
        



class LinearMoveCommand(LinearMovementCommand) :

    def __init__(self, MovementCommand:LinearMovementCommand) :
        self.start = MovementCommand.start
        self.end = MovementCommand.end
        self.reference = MovementCommand.reference

    def toGcode(self) -> tuple[Vector,str] :

        draw_string =  "G1 F" + str(Constants.MOVE_SPEED) + " X" + str(self.end.x) + " Y" + str(self.end.y) + ";"

        return (self.start, draw_string)
    
    def __repr__(self) :
        return "MOVE start: (" + str(self.start.x) + ", " + str(self.start.y) + ") end: (" + str(self.end.x) + ", " + str(self.end.y) + ") length: " + str(round(self.findLength(), 3)) 



class LinearDrawCommand(LinearMovementCommand) :

    def __init__(self, MovementCommand:LinearMovementCommand) :
        self.start = MovementCommand.start
        self.end = MovementCommand.end
        self.reference = MovementCommand.reference

    def toGcode(self) -> tuple[Vector,str] :

        draw_string =  "G1 F" + str(Constants.DRAW_SPEED) + " X" + str(self.end.x) + " Y" + str(self.end.y) + ";"

        return (self.start, draw_string)

    def __repr__(self) :
        return "DRAW start: (" + str(self.start.x) + ", " + str(self.start.y) + ") end: (" + str(self.end.x) + ", " + str(self.end.y) + ") length: " + str(round(self.findLength(), 3))
        


class LinearEraseCommand(LinearMovementCommand) :

    def __init__(self, MovementCommand:LinearMovementCommand) :
        self.start = MovementCommand.start
        self.end = MovementCommand.end
        self.reference = MovementCommand.reference

    def toGcode(self) -> tuple[Vector,str] :

        erase_start_x = (self.start.x+Constants.MARKER_ERASER_DIST_X) 
        erase_start_y = (self.start.y+Constants.MARKER_ERASER_DIST_Y)
        erase_string =  "G1 F" + str(Constants.ERASE_SPEED) + " X" + str(self.end.x+Constants.MARKER_ERASER_DIST_X) + " Y" + str(self.end.y+Constants.MARKER_ERASER_DIST_Y) + ";"
        
        return (Vector(erase_start_x, erase_start_y), erase_string)
    
    def __repr__(self) :
        return "ERASE start: (" + str(self.start.x) + ", " + str(self.start.y) + ") end: (" + str(self.end.x) + ", " + str(self.end.y) + ") length: " + str(round(self.findLength(), 3))
        


class DrawCommand :

    def __init__(self) :
        return
    
    def execute(self, servo:gpiozero.AngularServo) :
        servo.angle = Constants.SERVO_ANGLE_DRAW

    def toGcode(self):
        return (None, "; MARKER DOWN")

    def __repr__(self) :
        return "TOOLHEAD DRAW"

class EraseCommand :

    def __init__(self) :
        return

    def execute(self, servo:gpiozero.AngularServo) :
        servo.angle = Constants.SERVO_ANGLE_ERASE

    def toGcode(self):
        return (None, "; ERASER DOWN")

    def __repr__(self) :
        return "TOOLHEAD ERASE"

class MoveCommand :

    def __init__(self) :
        return

    def execute(self, servo:gpiozero.AngularServo) :
        servo.angle = Constants.SERVO_ANGLE_MOVE

    def toGcode(self):
        return (None, "; MARKER/ERASER UP")

    def __repr__(self) :
        return "TOOLHEAD STANDBY"
