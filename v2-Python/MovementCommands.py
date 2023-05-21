import Constants
import math
#import gpiozero

class LinearMovementCommand :

    __slots__ = ("true_start_x", "true_start_y", "true_end_x", "true_end_y","refrence_x","refrence_y")

    def __init__(self, start_x:float, start_y:float, end_x:float, end_y:float) :
        self.true_start_x = start_x
        self.true_start_y = start_y
        self.true_end_x = end_x
        self.true_end_y = end_y
        self.refrence_x = 0
        self.refrence_y = 0

    def setRefrenceX(self, x:float) :
        if self.refrence_x != 0 :
            self.true_start_x -= self.refrence_x
            self.true_end_x -= self.refrence_x
        self.refrence_x = x
        self.true_start_x += self.refrence_x
        self.true_end_x += self.refrence_x

    def setRefrenceY(self, y:float) :
        if self.refrence_y != 0 :
            self.true_start_y -= self.refrence_y
            self.true_end_y -= self.refrence_y
        self.refrence_y = y
        self.true_start_y += self.refrence_y
        self.true_end_y += self.refrence_y
    
    def findLength(self) -> float :
        return math.sqrt( ((self.true_start_x-self.true_end_x)**2) + ((self.true_start_y-self.true_end_y)**2) )
    
    def __str__(self) :
        return " start: (" + str(self.true_start_x) + ", " + str(self.true_start_y) + ") end: (" + str(self.true_end_x) + ", " + str(self.true_end_y) + ") length: " + str(round(self.findLength(), 3))
        



class LinearMoveCommand(LinearMovementCommand) :

    def __init__(self, MovementCommand:LinearMovementCommand) :
        self.true_start_x = MovementCommand.true_start_x
        self.true_start_y = MovementCommand.true_start_y
        self.true_end_x = MovementCommand.true_end_x
        self.true_end_y = MovementCommand.true_end_y
        self.refrence_x = MovementCommand.refrence_x
        self.refrence_y = MovementCommand.refrence_y

    def toGcode(self) -> tuple[float,float,str] :

        draw_string =  "G1 F" + str(Constants.MOVE_SPEED) + " X" + str(self.true_end_x) + " Y" + str(self.true_end_y) + ";"

        return (self.true_start_x, self.true_start_y, draw_string)
    
    def __str__(self) :
        return "MOVE start: (" + str(self.true_start_x) + ", " + str(self.true_start_y) + ") end: (" + str(self.true_end_x) + ", " + str(self.true_end_y) + ") length: " + str(round(self.findLength(), 3))
        



class LinearDrawCommand(LinearMovementCommand) :

    def __init__(self, MovementCommand:LinearMovementCommand) :
        self.true_start_x = MovementCommand.true_start_x
        self.true_start_y = MovementCommand.true_start_y
        self.true_end_x = MovementCommand.true_end_x
        self.true_end_y = MovementCommand.true_end_y
        self.refrence_x = MovementCommand.refrence_x
        self.refrence_y = MovementCommand.refrence_y

    def toGcode(self) -> tuple[float,float,str] :

        draw_string =  "G1 F" + str(Constants.DRAW_SPEED) + " X" + str(self.true_end_x) + " Y" + str(self.true_end_y) + ";"

        return (self.true_start_x, self.true_start_y, draw_string)

    def __str__(self) :
        return "DRAW start: (" + str(self.true_start_x) + ", " + str(self.true_start_y) + ") end: (" + str(self.true_end_x) + ", " + str(self.true_end_y) + ") length: " + str(round(self.findLength(), 3))
        
    


class LinearEraseCommand(LinearMovementCommand) :

    def __init__(self, MovementCommand:LinearMovementCommand) :
        self.true_start_x = MovementCommand.true_start_x
        self.true_start_y = MovementCommand.true_start_y
        self.true_end_x = MovementCommand.true_end_x
        self.true_end_y = MovementCommand.true_end_y
        self.refrence_x = MovementCommand.refrence_x
        self.refrence_y = MovementCommand.refrence_y

    def toGcode(self) -> tuple[float,float,str] :

        erase_start_x = (self.true_start_x+Constants.MARKER_ERASER_DIST_X) 
        erase_start_y = (self.true_start_y+Constants.MARKER_ERASER_DIST_Y)
        erase_string =  "G1 F" + str(Constants.ERASE_SPEED) + " X" + str(self.true_end_x+Constants.MARKER_ERASER_DIST_X) + " Y" + str(self.true_end_y+Constants.MARKER_ERASER_DIST_Y) + ";"
        
        return (erase_start_x, erase_start_y, erase_string)
    
    def __str__(self) :
        return "ERASE start: (" + str(self.true_start_x) + ", " + str(self.true_start_y) + ") end: (" + str(self.true_end_x) + ", " + str(self.true_end_y) + ") length: " + str(round(self.findLength(), 3))
        
    


class DrawCommand :

    def __init__(self) :
        return
    
    # def execute(self, servo:gpiozero.AngularServo) :
    #     self.servo.angle = Constants.SERVO_ANGLE_DRAW

    def toGcode(self):
        return (None, None,"; MARKER DOWN")



class EraseCommand :

    def __init__(self) :
        return

    # def execute(self, servo:gpiozero.AngularServo) :
    #     self.servo.angle = Constants.SERVO_ANGLE_ERASE

    def toGcode(self):
        return (None, None, "; ERASER DOWN")



class MoveCommand :

    def __init__(self) :
        return

    # def execute(self, servo:gpiozero.AngularServo) :
    #     self.servo.angle = Constants.SERVO_ANGLE_MOVE

    def toGcode(self):
        return (None, None, "; MARKER/ERASER UP")
