import Constants
import math
#import gpiozero

class LinearMovementCommand :


    __slots__ = ("true_start_x", "true_start_y", "true_end_x", "true_end_y",)


    def __init__(self, start_x:float, start_y:float, end_x:float, end_y:float, ref_x:float=Constants.MIN_X, ref_y:float=Constants.MIN_Y) :
        self.true_start_x = start_x + ref_x
        self.true_start_y = start_y + ref_y
        self.true_end_x = end_x + ref_x
        self.true_end_y = end_y + ref_y

    def __init__(self, start_x:float, start_y:float, end_x:float, end_y:float) :
        self.true_start_x = start_x
        self.true_start_y = start_y
        self.true_end_x = end_x
        self.true_end_y = end_y

    def setRefrenceX(self, x:float) :
        self.true_start_x += x
        self.true_end_x += x

    def setRefrenceY(self, y:float) :
        self.true_start_y += y
        self.true_end_y += y

    def toMoveGcode(self) -> tuple[float,float,str] :

        draw_string =  "G1 F" + str(Constants.MOVE_SPEED) + " X" + str(self.true_end_x) + " Y" + str(self.true_end_y) + ";"

        return (self.true_start_x, self.true_start_y, draw_string)

    def toDrawGcode(self) -> tuple[float,float,str] :

        draw_string =  "G1 F" + str(Constants.DRAW_SPEED) + " X" + str(self.true_end_x) + " Y" + str(self.true_end_y) + ";"

        return (self.true_start_x, self.true_start_y, draw_string)
    
    def toEraseGcode(self) -> tuple[float,float,str] :

        erase_start_x = (self.true_start_x+Constants.MARKER_ERASER_DIST_X) 
        erase_start_y = (self.true_start_y+Constants.MARKER_ERASER_DIST_Y)
        erase_string =  "G1 F" + str(Constants.ERASE_SPEED) + " X" + str(self.true_end_x+Constants.MARKER_ERASER_DIST_X) + " Y" + str(self.true_end_y+Constants.MARKER_ERASER_DIST_Y) + ";"
        
        return (erase_start_x, erase_start_y, erase_string)
    
    def findLength(self) -> float :
        return math.sqrt( ((self.true_start_x-self.true_end_x)**2) + ((self.true_start_y-self.true_end_y)**2) )
    


class DrawCommand :


    def __init__(self) :
        return
    

    # def execute(self, servo:gpiozero.AngularServo) :
    #     self.servo.angle = Constants.SERVO_ANGLE_DRAW



class EraseCommand :


    def __init__(self) :
        return
    

    # def execute(self, servo:gpiozero.AngularServo) :
    #     self.servo.angle = Constants.SERVO_ANGLE_ERASE



class MoveCommand :


    def __init__(self) :
        return
    

    # def execute(self, servo:gpiozero.AngularServo) :
    #     self.servo.angle = Constants.SERVO_ANGLE_MOVE
